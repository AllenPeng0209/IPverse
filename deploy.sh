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

# 3. Supabase 配置 (已自動從 MCP 獲取)
# 設置環境變量
SUPABASE_URL="https://gypivtzfjlzbzpahybof.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cGl2dHpmamx6YnpwYWh5Ym9mIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2OTIwNDYsImV4cCI6MjA2OTI2ODA0Nn0.CMvZyXXwZAfRE9ut6KlOqzplUw7rksc55CQUCuqwt3Q"
SUPABASE_SERVICE_ROLE_KEY="⚠️請手動設置正確的service_role_key⚠️"

# 4. 填寫你部署在 Vercel 上的前端網址
FRONTEND_URL="https://ip-verse.vercel.app"
JAAZ_API_KEY="test-demo-key-for-tools"

# --- 以下是部署腳本，通常不需要修改 ---
REGION="asia-northeast1"
SERVICE_NAME="jaaz-backend"
SOURCE_DIR="." # 包含 Dockerfile 的目錄

echo "🚀 準備部署服務 'jaaz-backend' 到 Cloud Run..."
echo "GCP Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Supabase URL: ${SUPABASE_URL}"
echo "Frontend URL: ${FRONTEND_URL}"
echo "Jaaz API Key: ${JAAZ_API_KEY}"
echo "-----------------------------------------------------"

# 檢查 service_role key 是否已設置
if [[ "$SUPABASE_SERVICE_ROLE_KEY" == *"請手動"* ]]; then
    echo "⚠️  警告：SUPABASE_SERVICE_ROLE_KEY 尚未設置"
    echo "   圖片上傳功能可能無法正常工作"
    echo "   請前往 Supabase Dashboard > Settings > API 獲取 service_role key"
    read -p "是否繼續部署？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 部署已取消"
        exit 1
    fi
fi

# 執行部署指令
gcloud run deploy "$SERVICE_NAME" \
  --source "$SOURCE_DIR" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --execution-environment gen2 \
  --allow-unauthenticated \
  --cpu=2 \
  --memory=2Gi \
  --timeout=900 \
  --set-env-vars \
    USE_SUPABASE=true,\
    SUPABASE_DATABASE_URL="postgresql://postgres:!Ss12369874allenp@db.gypivtzfjlzbzpahybof.supabase.co:5432/postgres",\
    SUPABASE_URL="$SUPABASE_URL",\
    SUPABASE_ANON_KEY="$SUPABASE_ANON_KEY",\
    SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY",\
    FRONTEND_URL="$FRONTEND_URL",\
    JAAZ_API_KEY="$JAAZ_API_KEY",\
    CLOUD_DEPLOYMENT=true

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