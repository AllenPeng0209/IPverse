
#!/bin/bash

# Go to https://cloud.google.com/run/docs/troubleshooting#service-agent-errors
# to fix permission error
# 遇到權限錯誤時，請參考以上網址修復

# Exit immediately if a command exits with a non-zero status.
set -e

# --- 請在這裡填寫你的配置 ---
# 1. 填寫你的 GCP Project ID
PROJECT_ID="ipverse-467311"

# 2. 填寫你的 Supabase 資料庫連線字串 (psycopg2)
#    - 從 Supabase > Project Settings > Database > Connection string 複製
#    - 務必用雙引號 "" 包起來
SUPABASE_DATABASE_URL='postgresql://postgres:!Ss12369874allenp@db.gypivtzfjlzbzpahybof.supabase.co:5432/postgres'
# 3. 填寫你部署在 Vercel 上的前端網址
FRONTEND_URL="https://ip-verse-642j65rve-allenpeng0209s-projects.vercel.app"

# --- 以下是部署腳本，通常不需要修改 ---
REGION="asia-northeast1"
SERVICE_NAME="jaaz-backend"
SOURCE_DIR="./server" # 包含 Dockerfile 的目錄

echo "🚀 準備部署服務 '$SERVICE_NAME' 到 Cloud Run..."
echo "GCP Project: $PROJECT_ID"
echo "Region: $REGION"
echo "-----------------------------------------------------"

# 執行部署指令
gcloud run deploy "$SERVICE_NAME" \
  --source "$SOURCE_DIR" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --execution-environment gen2 \
  --allow-unauthenticated \
  --update-env-vars="CLOUD_DEPLOYMENT=true,USE_SUPABASE=true,FRONTEND_URL=$FRONTEND_URL,SUPABASE_DATABASE_URL=$SUPABASE_DATABASE_URL"

echo "✅ 部署指令執行完畢。"
echo "-----------------------------------------------------"

# --- 部署後自動驗證 ---
echo "🔍 正在驗證部署狀態..."

# 取得服務網址
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --format 'value(status.url)')
echo "✅ 服務網址: $SERVICE_URL"

echo "📝 正在讀取最新的 50 行日誌..."
gcloud run services logs read "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --limit 50

echo "🎉 --- 驗證完畢 ---"
echo "請檢查上方日誌，若看到 '✅ Successfully connected to Supabase' 字樣，代表後端已成功啟動。"
echo "現在可以去前端頁面測試功能了。" 