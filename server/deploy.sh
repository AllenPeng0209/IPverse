# 進入後端程式碼所在資料夾


# ========= 請先替換這三個變數 =========
PROJECT_ID=ipverse-467311SUPABASE_DATABASE_URL=postgresql://postgres:!Ss12369874allenp@db.gypivtzfjlzbzpahybof.supabase.co:5432/postgres

FRONTEND_URL=https://ip-verse-642j65rve-allenpeng0209s-projects.vercel.app
# =====================================

# 一次部署 Cloud Run（Gen2）並寫入環境變數
gcloud run deploy jaaz-backend \
  --source . \
  --project "$PROJECT_ID" \
  --region asia-northeast1 \
  --execution-environment gen2 \
  --allow-unauthenticated \
  --update-env-vars=CLOUD_DEPLOYMENT=true,USE_SUPABASE=true,FRONTEND_URL="$FRONTEND_URL",SUPABASE_DATABASE_URL="$SUPABASE_DATABASE_URL"
