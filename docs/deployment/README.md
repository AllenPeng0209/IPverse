# Jaaz 部署指南

本指南涵蓋了將 Jaaz 應用程序打包用於生產環境分發的步驟，以及關於私有化部署的一些說明。

## 1. 打包桌面應用程序

Jaaz 使用 `electron-builder` 將應用打包成適用於 macOS 和 Windows 的可執行文件。打包過程會將 React 前端應用、Python 後端服務以及 Electron 容器捆綁在一起。

### 1.1 先決條件

*   您已經根據 [開發環境設定指南](../development/setup.md) 成功配置了本地環境。
*   對於跨平台打包（例如在 macOS 上打包 Windows 應用），可能需要額外的工具鏈，請參考 `electron-builder` 的官方文檔。

### 1.2 構建流程

打包過程由根目錄下的 `package.json` 中的 `scripts` 定義。核心命令是 `npm run dist`。

#### 第 1 步: 構建 React 前端

首先，需要將 React 應用編譯成靜態的 HTML, CSS 和 JavaScript 文件。

```bash
cd react
npm run build
```
此命令會執行 `vite build`，並將輸出結果存放在 `react/dist/` 目錄中。Electron 在打包時會加載這些靜態文件。

#### 第 2 步: 安裝根目錄依賴

回到項目根目錄，確保所有用於構建的依賴都已安裝。

```bash
cd ..
npm install --force
```

#### 第 3 步: 執行打包命令

運行 `dist` 腳本來為您當前的操作系統觸發打包流程。

```bash
npm run dist
```

這個命令會：
1.  找到已經構建好的前端靜態文件。
2.  將 `server/` 目錄下的 Python 代碼和相關資源作為應用的一部分包含進去。`electron-builder` 的配置（在 `package.json` 的 `build` 部分）會確保這些文件被正確打包。
3.  `electron-builder` 會處理 Python 環境的問題。通常，它會將 Python 解釋器和必要的依賴一起打包，或者依賴於在目標機器上安裝的 Python 環境。
4.  處理代碼簽名和公證（如果已配置）。
5.  在項目根目錄下的 `dist/` 目錄中生成最終的安裝包（例如 `.dmg` for macOS, `.exe` for Windows）。

### 1.3 代碼簽名與公證 (macOS)

為了在 macOS 上順利分發應用並避免安全警告，您需要對應用進行簽名和公證。

*   **簽名**: 需要一個 Apple Developer ID 證書。
*   **公證**: 在簽名後，需要將應用上傳到 Apple 的公證服務進行掃描。

`scripts/notarize.js` 文件包含了使用 `electron-notarize` 進行公證的邏輯。您需要在 `package.json` 的 `build.mac.afterSign`鉤子中觸發這個腳本，並在環境變量中配置您的 Apple ID 和密碼。

## 2. 私有化服務器部署

對於需要在團隊或企業內部私有化部署 Jaaz 的場景，您可以不打包桌面應用，而是將後端服務部署在一台中央服務器上。

### 2.1 架構

*   **後端服務**: 將 `server/` 目錄下的 FastAPI 應用部署到一台 Linux 或 Windows 服務器上。推薦使用 Gunicorn + Uvicorn Worker 來運行生產環境的 Python 應用。
*   **前端服務**: 將 `react/dist/` 目錄下的靜態文件通過 Nginx 或其他 Web 服務器提供服務。
*   **數據庫**: 服務器上的後端服務會使用其本地文件系統上的 SQLite 數據庫。對於更大規模的部署，可以考慮將 `db_service.py` 修改為連接到一個集中的 PostgreSQL 或 MySQL 數據庫。

### 2.2 部署步驟 (概念性)

1.  **準備服務器**: 設置一台具有 Python 3.12+ 環境的服務器。
2.  **部署後端**:
    *   將 `server/` 目錄複製到服務器。
    *   安裝 `requirements.txt` 中的依賴。
    *   使用 `gunicorn` 運行 FastAPI 應用:
        ```bash
        gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
        ```
3.  **部署前端**:
    *   構建 React 應用 (`npm run build`)。
    *   將 `react/dist` 的內容複製到服務器的 Web 根目錄。
    *   配置 Nginx 將請求代理到後端的 Gunicorn 服務，並提供前端靜態文件。

    *   **Nginx 示例配置**:
        ```nginx
        server {
            listen 80;
            server_name jaaz.yourcompany.com;

            location / {
                root /var/www/jaaz-frontend;
                try_files $uri /index.html;
            }

            location /api {
                proxy_pass http://127.0.0.1:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            }

            location /ws {
                proxy_pass http://127.0.0.1:8000/ws;
                proxy_http_version 1.1;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "Upgrade";
                proxy_set_header Host $host;
            }
        }
        ```
4.  **用戶訪問**: 用戶現在可以通過瀏覽器直接訪問 `http://jaaz.yourcompany.com` 來使用 Jaaz，而無需安裝桌面應用。所有的計算和數據都集中在內部服務器上，保證了數據安全。 