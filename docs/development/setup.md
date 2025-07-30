# Jaaz 開發環境設定指南

本指南將引導您完成在本地計算機上設置 Jaaz 開發環境所需的所有步驟。

## 1. 先決條件

在開始之前，請確保您的系統上已安裝以下軟件：

*   **Git**: 用於版本控制。
*   **Node.js**: `v18.x` 或更高版本。
*   **npm**: Node.js 的包管理器（通常隨 Node.js 一起安裝）。
*   **Python**: `v3.12.x` 或更高版本。
*   **pip**: Python 的包管理器（通常隨 Python 一起安裝）。
*   **VSCode (推薦)**: 以及推薦的擴展 `ms-python.black-formatter` 用於代碼格式化。

## 2. 克隆代碼倉庫

首先，使用 Git 克隆 Jaaz 的主代碼倉庫到您的本地機器。

```bash
git clone https://github.com/11cafe/jaaz.git
cd jaaz
```

## 3. 後端設置 (Python Server)

後端是一個 FastAPI 服務，負責所有核心邏輯。

1.  **進入 server 目錄**:
    ```bash
    cd server
    ```

2.  **創建並激活虛擬環境 (推薦)**:
    使用虛擬環境可以將項目依賴與您的全局 Python 環境隔離開。

    ```bash
    # 創建一個名為 .venv 的虛擬環境
    python -m venv .venv

    # 激活虛擬環境
    # 在 macOS/Linux 上:
    source .venv/bin/activate
    # 在 Windows 上:
    # .\.venv\Scripts\activate
    ```
    激活後，您應該會在終端提示符前看到 `(.venv)`。

3.  **安裝 Python 依賴**:
    `requirements.txt` 文件列出了所有必需的 Python 包。

    ```bash
    pip install -r requirements.txt
    ```

4.  **運行後端開發服務器**:
    ```bash
    python main.py
    ```
    如果一切順利，您應該會看到 Uvicorn 服務器啟動的日誌，並在 `http://127.0.0.1:10001` 上監聽請求。請保持此終端窗口運行。

    > **注意**: 後端服務器默認在 `10001` 端口運行。

## 4. 前端設置 (React App)

前端是一個使用 Vite 構建的 React 應用。您需要打開**一個新的終端窗口**來運行它。

1.  **進入 react 目錄**:
    確保您在項目的根目錄下打開一個新的終端，然後進入 `react` 目錄。
    ```bash
    cd react
    ```

2.  **安裝 Node.js 依賴**:
    `package.json` 文件列出了所有必需的 npm 包。`--force` 標誌有助於解決一些潛在的依賴衝突。

    ```bash
    npm install --force
    ```

3.  **運行前端開發服務器**:
    此命令會啟動 Vite 開發服務器，它支持熱模塊重載（HMR），這意味著當您修改源代碼時，網頁會自動更新，無需手動刷新。

    ```bash
    npm run dev
    ```
    Vite 通常會在 `http://localhost:5173` 或另一個可用端口上啟動服務。終端輸出會顯示確切的地址。

## 5. 訪問應用

現在，您的開發環境已經完全運行：
*   後端服務器在 `http://127.0.0.1:10001`
*   前端開發服務器在 `http://localhost:5173` (或其他端口)

前端應用已經配置好代理，會將 `/api` 的請求轉發到後端服務器，所以您無需擔心跨域問題。

**打開您的瀏覽器，訪問 Vite 終端輸出的地址（例如 `http://localhost:5173`），您就應該能看到 Jaaz 的用戶界面了。**

## 6. Electron 開發 (可選)

如果您需要對 Electron 的主進程邏輯（例如窗口管理、IPC 通信、本地文件操作）進行開發，您需要運行 Electron 應用本身，而不是在瀏覽器中訪問前端。

1.  **確保前端和後端開發服務器都在運行。**

2.  **安裝根目錄的依賴**:
    在**第三個終端窗口**中，回到項目的根目錄，並安裝頂層的 `package.json` 中的依賴。
    ```bash
    cd .. # 回到根目錄
    npm install --force
    ```

3.  **啟動 Electron 應用**:
    ```bash
    npm run electron:dev
    ```
    此命令會啟動 Electron 應用，它會加載運行在 `http://localhost:5173` 上的前端頁面，同時後端的 Python 服務也已經在獨立運行。這最完整地模擬了生產環境的架構，允許您測試端到端的流程。

---

**開發流程總結**:

對於大部分前端或後端的開發工作，您只需要運行**後端 Python 服務**和**前端 Vite 服務**即可。只有在需要修改 Electron 特定功能時，才需要運行 `npm run electron:dev`。 