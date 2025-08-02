import os
import sys
import io
# Ensure stdout and stderr use utf-8 encoding to prevent emoji logs from crashing python server
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
print('Importing websocket_router')
from routers.websocket_router import *  # DO NOT DELETE THIS LINE, OTHERWISE, WEBSOCKET WILL NOT WORK
print('Importing routers')
from routers import config_router, image_router, root_router, workspace, canvas, ssl_test, chat_router, settings, tool_confirmation
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import argparse
from contextlib import asynccontextmanager
from starlette.types import Scope
from starlette.responses import Response
import socketio # type: ignore
from fastapi.middleware.cors import CORSMiddleware
print('Importing websocket_state')
from services.websocket_state import sio
print('Importing websocket_service')
from services.websocket_service import broadcast_init_done
print('Importing config_service')
from services.config_service import config_service
print('Importing tool_service')
from services.tool_service import tool_service
print('Importing db_adapter')
from services.db_adapter import db_adapter
print('Importing supabase_storage')
from services.supabase_storage_service import supabase_storage

async def initialize():
    print('Initializing config_service')
    await config_service.initialize()
    
    # Initialize database connection
    print('Initializing database connection')
    
    # Force Supabase in cloud deployment
    is_cloud_deployment = os.environ.get('CLOUD_DEPLOYMENT', 'false').lower() == 'true'
    use_supabase = os.environ.get('USE_SUPABASE', 'false').lower() == 'true' or is_cloud_deployment
    
    if use_supabase:
        database_url = os.environ.get('SUPABASE_DATABASE_URL')
        if database_url:
            print('🗄️ Using Supabase database')
            await db_adapter.initialize_supabase(database_url)
            
            # Initialize Supabase Storage
            supabase_url = os.environ.get('SUPABASE_URL')
            # Try Service Role Key first, fallback to Anon Key
            supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_ANON_KEY')
            
            if supabase_url and supabase_key:
                print('📁 Initializing Supabase Storage')
                key_type = "Service Role" if os.environ.get('SUPABASE_SERVICE_ROLE_KEY') else "Anon"
                print(f'🔑 Using {key_type} key for Storage operations')
                supabase_storage.initialize(supabase_url, supabase_key, "images")
                # Only try to create bucket if using Service Role key
                if os.environ.get('SUPABASE_SERVICE_ROLE_KEY'):
                    await supabase_storage.create_bucket_if_not_exists()
                else:
                    print('📦 Using existing Storage bucket (Anon key cannot create buckets)')
            else:
                print('⚠️ SUPABASE_URL or SUPABASE keys not found, Storage disabled')
        else:
            if is_cloud_deployment:
                raise ValueError("SUPABASE_DATABASE_URL is required for cloud deployment")
            else:
                print('⚠️ SUPABASE_DATABASE_URL not found, using SQLite')
    else:
        print('📝 Using SQLite database (development mode)')
    
    print('Initializing broadcast_init_done')
    await broadcast_init_done()

root_dir = os.path.dirname(__file__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # onstartup
    # TODO: Check if there will be racing conditions when user send chat request but tools and models are not initialized yet.
    await initialize()
    await tool_service.initialize()
    yield
    # onshutdown

print('Creating FastAPI app')
app = FastAPI(lifespan=lifespan)

# Set up CORS middleware
frontend_url = os.environ.get('FRONTEND_URL')
origins = []
if frontend_url:
    origins.append(frontend_url)
else:
    # Default origins for development
    origins = [
        "http://localhost:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
print('Including routers')
app.include_router(config_router.router)
app.include_router(settings.router)
app.include_router(root_router.router)
app.include_router(canvas.router)
app.include_router(workspace.router)
app.include_router(image_router.router)
app.include_router(ssl_test.router)
app.include_router(chat_router.router)
app.include_router(tool_confirmation.router)

print('Creating socketio app')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path='/socket.io')

if __name__ == "__main__":
    # bypass localhost request for proxy, fix ollama proxy issue
    _bypass = {"127.0.0.1", "localhost", "::1"}
    current = set(os.environ.get("no_proxy", "").split(",")) | set(
        os.environ.get("NO_PROXY", "").split(","))
    os.environ["no_proxy"] = os.environ["NO_PROXY"] = ",".join(
        sorted(_bypass | current - {""}))

    parser = argparse.ArgumentParser()
    # Cloud Run provides PORT environment variable
    default_port = int(os.environ.get('PORT', 57988))
    parser.add_argument('--port', type=int, default=default_port,
                        help='Port to run the server on')
    args = parser.parse_args()
    import uvicorn
    print("🌟Starting server, UI_DIST_DIR:", os.environ.get('UI_DIST_DIR'))
    print(f"🌟Server will run on host: 0.0.0.0, port: {args.port}")

    uvicorn.run(socket_app, host="0.0.0.0", port=args.port)
