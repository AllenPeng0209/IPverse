"""
Database adapter to gradually migrate from SQLite to Supabase
This adapter allows switching between SQLite and Supabase backends
"""
import os
import json
from typing import List, Dict, Any, Optional, Union
from .db_service import DatabaseService
from .supabase_db_service import SupabaseService, supabase_service
import nanoid

class DatabaseAdapter:
    def __init__(self):
        self.sqlite_db = DatabaseService()
        self.supabase_db = supabase_service
        self.use_supabase = False  # Start with SQLite, switch to Supabase when ready
        
    async def initialize_supabase(self, connection_string: str):
        """Initialize Supabase connection"""
        try:
            await self.supabase_db.initialize(connection_string)
            self.use_supabase = True
            print("✅ Successfully connected to Supabase")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            print("📝 Falling back to SQLite")
            self.use_supabase = False

    async def create_canvas(self, id: str, name: str):
        """Create a new canvas"""
        if self.use_supabase:
            return await self.supabase_db.create_canvas(id, name)
        else:
            return await self.sqlite_db.create_canvas(id, name)

    async def list_canvases(self) -> List[Dict[str, Any]]:
        """Get all canvases"""
        if self.use_supabase:
            return await self.supabase_db.list_canvases()
        else:
            return await self.sqlite_db.list_canvases()

    async def create_chat_session(self, id: str, model: str, provider: str, canvas_id: str, title: Optional[str] = None):
        """Save a new chat session"""
        if self.use_supabase:
            return await self.supabase_db.create_chat_session(id, model, provider, canvas_id, title)
        else:
            return await self.sqlite_db.create_chat_session(id, model, provider, canvas_id, title)

    async def create_message(self, session_id: str, role: str, message: Union[str, Dict[str, Any]], **kwargs):
        """Save a chat message - handles both old and new formats"""
        if self.use_supabase:
            # Generate ID for new message
            message_id = nanoid.generate()
            
            # Convert old string format to new dict format
            if isinstance(message, str):
                try:
                    content = json.loads(message)
                except:
                    content = {"text": message}
            else:
                content = message
            
            # Extract additional parameters for Supabase
            tool_calls = kwargs.get('tool_calls')
            tool_call_id = kwargs.get('tool_call_id')
            
            return await self.supabase_db.create_message(
                message_id, session_id, role, content, tool_calls, tool_call_id
            )
        else:
            # For SQLite, use the old format
            message_str = json.dumps(message) if isinstance(message, dict) else message
            return await self.sqlite_db.create_message(session_id, role, message_str)

    async def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        if self.use_supabase:
            return await self.supabase_db.get_chat_history(session_id)
        else:
            return await self.sqlite_db.get_chat_history(session_id)

    async def list_sessions(self, canvas_id: str) -> List[Dict[str, Any]]:
        """List all chat sessions"""
        if self.use_supabase:
            return await self.supabase_db.list_sessions(canvas_id)
        else:
            return await self.sqlite_db.list_sessions(canvas_id)

    async def save_canvas_data(self, id: str, data: str, thumbnail: str = None):
        """Save canvas data"""
        if self.use_supabase:
            return await self.supabase_db.save_canvas_data(id, data, thumbnail)
        else:
            return await self.sqlite_db.save_canvas_data(id, data, thumbnail)

    async def get_canvas_data(self, id: str) -> Optional[Dict[str, Any]]:
        """Get canvas data"""
        if self.use_supabase:
            return await self.supabase_db.get_canvas_data(id)
        else:
            return await self.sqlite_db.get_canvas_data(id)

    async def get_or_create_canvas(self, canvas_id: str, canvas_name: str = "Untitled") -> Dict[str, Any]:
        """
        Tries to fetch a canvas by its ID. If it doesn't exist, creates a new one.
        Returns the canvas data.
        """
        if self.use_supabase:
            return await self.supabase_db.get_or_create_canvas(canvas_id, canvas_name)
        else:
            # Fallback for SQLite
            canvas_data = await self.sqlite_db.get_canvas_data(canvas_id)
            if canvas_data is None:
                await self.sqlite_db.create_canvas(canvas_id, canvas_name)
                # Fetch again to ensure consistent return format
                return await self.sqlite_db.get_canvas_data(canvas_id)
            return canvas_data

    async def delete_canvas(self, id: str):
        """Delete canvas and related data"""
        if self.use_supabase:
            return await self.supabase_db.delete_canvas(id)
        else:
            return await self.sqlite_db.delete_canvas(id)

    async def rename_canvas(self, id: str, name: str):
        """Rename canvas"""
        if self.use_supabase:
            return await self.supabase_db.rename_canvas(id, name)
        else:
            return await self.sqlite_db.rename_canvas(id, name)

    async def create_comfy_workflow(self, name: str, api_json: str, description: str, inputs: str, outputs: str = None):
        """Create a new comfy workflow"""
        if self.use_supabase:
            return await self.supabase_db.create_comfy_workflow(name, api_json, description, inputs, outputs)
        else:
            return await self.sqlite_db.create_comfy_workflow(name, api_json, description, inputs, outputs)

    async def list_comfy_workflows(self) -> List[Dict[str, Any]]:
        """List all comfy workflows"""
        if self.use_supabase:
            return await self.supabase_db.list_comfy_workflows()
        else:
            return await self.sqlite_db.list_comfy_workflows()

    async def delete_comfy_workflow(self, id: int):
        """Delete a comfy workflow"""
        if self.use_supabase:
            return await self.supabase_db.delete_comfy_workflow(id)
        else:
            return await self.sqlite_db.delete_comfy_workflow(id)

    async def get_comfy_workflow(self, id: int):
        """Get comfy workflow dict"""
        if self.use_supabase:
            return await self.supabase_db.get_comfy_workflow(id)
        else:
            return await self.sqlite_db.get_comfy_workflow(id)

    # Supabase-only methods
    async def save_generated_image(self, session_id: str, canvas_id: str, file_url: str, 
                                 file_id: str, element_data: Dict[str, Any], prompt: str):
        """Save generated image information (Supabase only)"""
        if self.use_supabase:
            return await self.supabase_db.save_generated_image(
                session_id, canvas_id, file_url, file_id, element_data, prompt
            )
        else:
            # For SQLite, we could implement a basic version or just skip
            print("Generated image tracking not available in SQLite mode")

    async def get_generated_images(self, session_id: str = None, canvas_id: str = None) -> List[Dict[str, Any]]:
        """Get generated images (Supabase only)"""
        if self.use_supabase:
            return await self.supabase_db.get_generated_images(session_id, canvas_id)
        else:
            return []

# Create a singleton instance
db_adapter = DatabaseAdapter()