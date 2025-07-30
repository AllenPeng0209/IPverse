# Jaaz API 參考文檔

## 1. 概述

Jaaz 的後端 API 是基於 **FastAPI** 構建的，提供了清晰、高性能的接口。API 主要通過兩種方式與前端通信：
*   **RESTful HTTP/HTTPS 端點**：用於處理狀態變更請求，如 CRUD 操作。
*   **WebSocket**：用於實時、雙向的通信，主要是聊天和內容生成流程。

所有 API 的定義都可以在 `server/routers/` 目錄中找到。本文檔將概述主要的 API 端點。

---

## 2. WebSocket API

WebSocket 是 Jaaz 實時交互的核心。它處理了所有與 AI 代理的對話和工具調用。

*   **路徑**: `/ws/{client_id}`
*   **通信流程**:
    1.  前端通過此端點建立一個持久的 WebSocket 連接。
    2.  前端發送一個 JSON 消息來啟動一個聊天會話或發送一個新的用戶消息。消息格式通常包含 `type` 和 `data` 字段。
        *   **示例 (發送消息)**:
            ```json
            {
              "type": "chat",
              "data": {
                "message": "幫我生成一張貓咪的圖片",
                "canvas_id": "some-canvas-uuid",
                "history": [...]
              }
            }
            ```
    3.  後端 `websocket_router.py` 接收消息，並將其傳遞給 `langgraph_service`。
    4.  在 AI 代理處理請求的過程中，後端會通過同一個 WebSocket 連接，向前端**流式發送**一系列的 JSON 消息來報告進度。這些消息的 `type` 可以是：
        *   `stream_chunk`: LLM 生成的文本流。
        *   `tool_call`: AI 代理決定調用一個工具。
        *   `tool_output`: 工具執行的結果。
        *   `image_generation_progress`: 圖像生成進度更新。
        *   `final_response`: 最終的完整響應。
    5.  前端根據接收到的不同類型的消息，動態地更新 UI。

---

## 3. 畫布 API (`canvas.py`)

管理無限畫布的數據。

### `GET /api/canvases`
*   **描述**: 獲取所有畫布的列表。
*   **響應 (200 OK)**:
    ```json
    [
      {
        "id": "uuid-1",
        "name": "我的第一個畫布",
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

### `POST /api/canvases`
*   **描述**: 創建一個新的畫布。
*   **請求體**:
    ```json
    {
      "name": "新的故事板"
    }
    ```
*   **響應 (201 Created)**: 返回新創建的畫布對象。

### `GET /api/canvases/{canvas_id}`
*   **描述**: 獲取特定畫布的詳細內容，包括其中的所有元素。
*   **響應 (200 OK)**:
    ```json
    {
      "id": "uuid-1",
      "name": "我的第一個畫布",
      "elements": [...] // Excalidraw 元素數組
    }
    ```

### `PUT /api/canvases/{canvas_id}`
*   **描述**: 更新一個畫布的內容（例如，保存用戶在畫布上的更改）。
*   **請求體**:
    ```json
    {
      "name": "更新後的畫布名稱",
      "elements": [...] // 更新後的 Excalidraw 元素數組
    }
    ```
*   **響應 (200 OK)**: 返回更新後的畫布對象。

### `DELETE /api/canvases/{canvas_id}`
*   **描述**: 刪除一個畫布。
*   **響應 (204 No Content)**

---

## 4. 設置 API (`settings.py`)

管理用戶的應用設置，如 API 金鑰。

### `GET /api/settings`
*   **描述**: 獲取當前的用戶設置。
*   **響應 (200 OK)**:
    ```json
    {
      "openai_api_key": "sk-...",
      "replicate_api_key": "r8_...",
      "local_model_provider": "ollama"
      // ... 其他設置
    }
    ```

### `POST /api/settings`
*   **描述**: 保存用戶設置。
*   **請求體**: 包含要更新的設置項的 JSON 對象。
    ```json
    {
      "openai_api_key": "sk-newkey...",
      "local_model_provider": "comfyui"
    }
    ```
*   **響應 (200 OK)**: 返回更新後的完整設置對象。

---

## 5. ComfyUI 工作流 API (`comfyui_execution.py`)

管理和執行 ComfyUI 工作流。

### `GET /api/comfy_workflows`
*   **描述**: 獲取所有已保存的 ComfyUI 工作流列表。
*   **響應 (200 OK)**:
    ```json
    [
      {
        "id": "uuid-workflow-1",
        "name": "基礎文生圖",
        "description": "一個標準的 text-to-image 工作流"
      }
    ]
    ```

### `POST /api/comfy_workflows`
*   **描述**: 上傳並保存一個新的 ComfyUI 工作流（從 JSON 文件）。
*   **請求體 (`multipart/form-data`)**:
    *   `file`: 包含工作流的 `.json` 文件。
    *   `name`: 工作流的名稱。
    *   `description`: 工作流的描述。
*   **響應 (201 Created)**: 返回新保存的工作流的元數據。

### `DELETE /api/comfy_workflows/{workflow_id}`
*   **描述**: 刪除一個已保存的 ComfyUI 工作流。
*   **響應 (204 No Content)**

---

## 6. 認證 API (Jaaz 託管服務)

這些端點用於與 Jaaz 的雲服務進行認證，以使用託管的 API 點數。

### `POST /api/auth/request-login-code`
*   **描述**: 向用戶的電子郵箱發送一個一次性登錄驗證碼。
*   **請求體**:
    ```json
    {
      "email": "user@example.com"
    }
    ```
*   **響應 (200 OK)**

### `POST /api/auth/exchange-code`
*   **描述**: 使用郵箱和驗證碼來換取一個 JWT (JSON Web Token)。
*   **請求體**:
    ```json
    {
      "email": "user@example.com",
      "code": "123456"
    }
    ```
*   **響應 (200 OK)**:
    ```json
    {
      "access_token": "ey...",
      "refresh_token": "ey..."
    }
    ```
    *前端會將這些 token 保存起來，並在後續對需要認證的 Jaaz 雲服務的請求中攜帶 `access_token`。* 