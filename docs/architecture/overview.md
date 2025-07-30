# Jaaz 技術架構概覽

## 1. 總體架構

Jaaz 採用了現代化的混合桌面應用架構，結合了 Web 技術的靈活性和本地應用的性能與整合能力。整個系統由三個核心部分組成：

1.  **前端 (Frontend)**：一個使用 **React** 和 **Vite** 構建的單頁應用（SPA），負責所有用戶界面的渲染和交互。
2.  **後端 (Backend)**：一個使用 **Python** 和 **FastAPI** 構建的高性能 API 服務，負責處理所有業務邏輯、AI 模型調用和數據持久化。
3.  **桌面容器 (Desktop Shell)**：一個 **Electron** 應用，將前端和後端打包成一個跨平台的桌面應用程序，並提供與操作系統底層 API 的交互能力。

下圖展示了這三個部分如何協同工作：

```mermaid
graph TD
    subgraph Jaaz 桌面應用
        subgraph Electron 主進程
            direction LR
            A[Main Process (main.js)]
            A -- 创建窗口 --> B[BrowserWindow]
            A -- 管理後端生命周期 --> C{Python Server}
            A -- IPC 通信 --> D[Preload Script (preload.js)]
        end

        subgraph Electron 渲染器進程
            direction LR
            B -- 加載 --> E[React App]
            D -- 暴露 API --> E
        end
    end

    subgraph 外部服務
        direction TD
        F[Ollama]
        G[ComfyUI]
        H[OpenAI API]
        I[Replicate API]
        J[...]
    end

    E -- HTTP/WebSocket --> C
    C -- API 調用 --> F
    C -- API 調用 --> G
    C -- API 調用 --> H
    C -- API 調用 --> I
    C -- API 調用 --> J

    style Electron 主進程 fill:#f9f,stroke:#333,stroke-width:2px
    style Electron 渲染器進程 fill:#ccf,stroke:#333,stroke-width:2px
    style C fill:#cfc,stroke:#333,stroke-width:2px
```

## 2. 前端架構 (react/)

前端是一個功能豐富的反應式應用，負責用戶體驗的核心。

*   **技術棧**:
    *   **框架**: React 18
    *   **構建工具**: Vite
    *   **語言**: TypeScript
    *   **路由**: TanStack Router (`@tanstack/react-router`)
    *   **狀態管理**: Zustand, React Context
    *   **UI 組件庫**: Shadcn UI
    *   **國際化**: i18next
    *   **畫布**: Excalidraw

*   **目錄結構亮點**:
    *   `src/api/`: 封裝了所有與後端 FastAPI 服務的 HTTP 請求。
    *   `src/components/`: 包含可重用的 UI 組件，按功能（如 `auth`, `canvas`, `chat`）組織。
    *   `src/contexts/`: 提供全局狀態，如認證信息 (`AuthContext`) 和主題 (`ThemeProvider`)。
    *   `src/routes/`: 使用 TanStack Router 進行基於文件的路由定義。
    *   `src/stores/`: 使用 Zustand 進行更複雜的客戶端狀態管理，例如畫布狀態 (`canvas.ts`)。
    *   `src/hooks/`: 存放自定義的 React Hooks，用於封裝常用邏輯。
    *   `src/lib/`: 包含與後端 WebSocket 通信 (`socket.ts`) 和事件處理 (`event.ts`) 的核心邏輯。

*   **數據流**:
    1.  UI 組件觸發事件（例如，用戶點擊“生成圖像”）。
    2.  事件處理函數調用 `api/` 或 `lib/socket.ts` 中的函數。
    3.  通過 HTTP (fetch) 或 WebSocket 向後端發送請求。
    4.  等待後端響應，並使用 Zustand 或 Context 更新應用狀態。
    5.  UI 根據更新後的狀態重新渲染。

## 3. 後端架構 (server/)

後端是 Jaaz 的大腦，負責協調各種 AI 模型和服務來滿足用戶請求。

*   **技術棧**:
    *   **框架**: FastAPI
    *   **語言**: Python 3.12+
    *   **異步處理**: Uvicorn, asyncio
    *   **數據庫**: SQLite (通過 `db_service.py`)
    *   **AI 代理/編排**: LangGraph (`langgraph_service/`)

*   **目錄結構亮點**:
    *   `main.py`: FastAPI 應用的主入口點，負責加載路由、中間件和啟動服務。
    *   `routers/`: 定義了所有 API 端點，按資源（如 `chat_router.py`, `canvas.py`）進行模塊化。
    *   `services/`: 包含了核心的業務邏輯。這是最複雜的部分：
        *   `chat_service.py`: 處理聊天相關的邏輯。
        *   `langgraph_service/`: 使用 LangGraph 構建了複雜的 AI 代理，能夠規劃並執行多步任務（例如，先生成故事板，再為每個場景生成圖像）。
        *   `tool_service.py`: 管理一個可供 AI 代理調用的工具集合。
        *   `websocket_service.py`: 處理與前端的實時 WebSocket 連接。
    *   `tools/`: 定義了具體的“工具”，這些工具是 AI 代理可以執行的原子操作。每個工具通常是對一個外部 API（如 Replicate）或本地服務（如 ComfyUI）的封裝。
        *   `image_providers/`: 包含了與不同圖像生成服務（ComfyUI, OpenAI, Replicate 等）交互的邏輯。
    *   `models/`: 定義了 Pydantic 數據模型，用於 API 請求/響應的驗證和序列化。
    *   `migrations/`: 管理數據庫模式的演進。

*   **核心工作流程 (以生成圖像為例)**:
    1.  前端通過 WebSocket 或 HTTP 發送一個包含用戶提示的請求到 `chat_router.py`。
    2.  路由將請求轉發給 `langgraph_service` 中的 AI 代理。
    3.  AI 代理分析用戶意圖，決定需要使用哪個工具（例如 `generate_image_by_flux_1_1_pro_jaaz`）。
    4.  代理調用 `tool_service.py` 來執行該工具。
    5.  `tool_service` 找到對應的工具實現，例如 `tools/image_providers/jaaz_provider.py`。
    6.  Provider 向 Jaaz API 或其他第三方 API 發送請求。
    7.  獲取到結果後，通過 `websocket_service` 將生成進度或最終結果流式傳回給前端。
    8.  結果同時被保存到數據庫中。

## 4. 桌面容器架構 (electron/)

Electron 層主要扮演“膠水”的角色，將 Web 應用和本地系統能力結合起來。

*   **技術棧**:
    *   **框架**: Electron
    *   **語言**: JavaScript

*   **目錄結構亮點**:
    *   `main.js`: Electron 的主進程。它的職責包括：
        *   創建和管理應用窗口 (`BrowserWindow`)。
        *   在應用啟動時，啟動後端的 Python FastAPI 服務子進程。
        *   在應用退出時，優雅地關閉後端服務。
        *   定義應用菜單、處理更新等。
    *   `preload.js`: 一個特殊的腳本，運行在渲染器進程的 Web 環境中，但在 Node.js 環境中具有更高的權限。它作為一個安全的橋樑，通過 `contextBridge` 向 React 應用暴露特定的 Node.js/Electron API。
    *   `ipcHandlers.js`: 集中處理所有從渲染器進程（React App）發送過來的 IPC（進程間通信）消息。例如，前端可以通過 IPC 請求主進程執行文件操作、讀取本地設置或與 ComfyUI 交互。
    *   `comfyUIInstaller.js` & `comfyUIManager.js`: 封裝了在用戶本地安裝、配置和管理 ComfyUI 實例的複雜邏輯。

## 5. 數據持久化

*   **應用設置**: 用戶的 API 金鑰、模型偏好等設置存儲在本地的 JSON 文件中，通過 `electron/settingsService.js` 進行管理。
*   **用戶數據**: 聊天歷史、畫布內容等核心數據存儲在後端管理的 SQLite 數據庫中。數據庫文件位於用戶的應用數據目錄下，確保了數據的本地性和私密性。數據庫操作由 `server/services/db_service.py` 抽象和管理。

## 6. 通信協議

*   **前端 <-> 後端**:
    *   **HTTP**: 用於常規的、無狀態的 API 請求（例如，獲取歷史記錄、保存畫布）。
    *   **WebSocket**: 用於需要實時、雙向通信的場景，主要是聊天和內容生成。後端可以通過 WebSocket 主動向前端推送生成進度更新、Tool Call 狀態等信息，提供了非常流暢的交互體驗。

*   **前端 <-> Electron 主進程**:
    *   **IPC (Inter-Process Communication)**: 使用 Electron 的 `ipcRenderer` 和 `ipcMain` 模塊。前端通過 `preload.js` 暴露的安全接口發送異步消息，主進程在 `ipcHandlers.js` 中監聽並處理這些消息，然後可以將結果回傳。這用於執行需要 Node.js 權限的操作，如文件系統訪問。 