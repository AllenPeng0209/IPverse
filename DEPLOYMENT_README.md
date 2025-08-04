# 🚀 Jaaz 部署說明

## 📍 正確的部署位置

**部署腳本位置**：`/Users/pengyanlun/workdir/jaaz/deploy.sh`（項目根目錄）

## 🏗️ 項目結構說明

```
jaaz/                    <- 你在這裡執行部署
├── deploy.sh           <- 部署腳本 ✅
├── Dockerfile          <- 用於 Cloud Run 構建 ✅
├── server/             <- 後端代碼
│   ├── main.py
│   ├── requirements.txt
│   └── ...
└── react/              <- 前端代碼
    └── ...
```

## ✅ 部署步驟

### 1. 確認位置
```bash
cd /Users/pengyanlun/workdir/jaaz  # 確保在項目根目錄
pwd  # 應該顯示：/Users/pengyanlun/workdir/jaaz
```

### 2. 獲取 Service Role Key（可選但推薦）
- 前往 https://supabase.com/dashboard
- 選擇項目 (gypivtzfjlzbzpahybof)
- Settings → API → 複製 `service_role` key
- 編輯 `deploy.sh` 更新 `SUPABASE_SERVICE_ROLE_KEY`

### 3. 執行部署
```bash
./deploy.sh
```

## 🔧 已配置的環境變量

通過 MCP Supabase 自動獲取：
- ✅ `SUPABASE_URL`: https://gypivtzfjlzbzpahybof.supabase.co
- ✅ `SUPABASE_ANON_KEY`: 已自動填入
- ✅ `FRONTEND_URL`: https://ip-verse.vercel.app
- ✅ `SUPABASE_DATABASE_URL`: 已配置

## 🎯 部署後的效果

- ✅ 修復 CORS 問題
- ✅ 圖片上傳功能正常
- ✅ 所有 API 端點可訪問
- ✅ WebSocket 連接正常

## ❓ 常見問題

**Q: 為什麼要在根目錄執行？**
A: 因為根目錄的 Dockerfile 設計用於複製 `./server/` 內容，Cloud Run 需要完整的項目上下文。

**Q: 如果沒有 Service Role Key 會怎樣？**
A: 基本功能正常，但圖片上傳到 Supabase Storage 功能可能受限。 