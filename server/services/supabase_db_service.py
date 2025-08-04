import asyncpg
import json
import os
from typing import List, Dict, Any, Optional
from .config_service import USER_DATA_DIR

class SupabaseService:
    def __init__(self):
        self.pool = None
        self._connection_string = None

    async def initialize(self, connection_string: str):
        """Initialize the connection pool"""
        self._connection_string = connection_string
        self.pool = await asyncpg.create_pool(
            connection_string,
            min_size=1,
            max_size=10,
            command_timeout=60
        )

    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()

    async def create_canvas(self, id: str, name: str):
        """Create a new canvas"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO canvases (id, name)
                VALUES ($1, $2)
            """, id, name)

    async def list_canvases(self) -> List[Dict[str, Any]]:
        """Get all canvases"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, description, thumbnail, created_at, updated_at
                FROM canvases
                ORDER BY updated_at DESC
            """)
            return [dict(row) for row in rows]

    async def create_chat_session(self, id: str, model: str, provider: str, canvas_id: str, title: Optional[str] = None):
        """Save a new chat session, ignoring conflicts if the session already exists."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_sessions (id, model, provider, canvas_id, title)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (id) DO NOTHING
            """, id, model, provider, canvas_id, title)

    async def create_message(self, id: str, session_id: str, role: str, content: Dict[str, Any], tool_calls: Optional[Dict[str, Any]] = None, tool_call_id: Optional[str] = None):
        """Save a chat message"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (id, session_id, role, content, tool_calls, tool_call_id)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, id, session_id, role, json.dumps(content), 
                json.dumps(tool_calls) if tool_calls else None, tool_call_id)

    async def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat history for a session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, role, content, tool_calls, tool_call_id, created_at
                FROM messages
                WHERE session_id = $1
                ORDER BY created_at ASC
            """, session_id)
            
            messages = []
            for row in rows:
                content = row['content']
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        content = {"text": content}
                
                tool_calls = row['tool_calls']
                if tool_calls and isinstance(tool_calls, str):
                    try:
                        tool_calls = json.loads(tool_calls)
                    except:
                        tool_calls = None

                # Handle nested content structure
                if isinstance(content, dict) and 'content' in content and 'role' in content:
                    # If content is nested (contains role and content), extract the inner content
                    actual_content = content['content']
                else:
                    # If content is direct, use it as is
                    actual_content = content
                
                message = {
                    "role": row['role'],
                    "content": actual_content
                }
                
                if tool_calls:
                    message["tool_calls"] = tool_calls
                
                if row['tool_call_id']:
                    message["tool_call_id"] = row['tool_call_id']
                
                messages.append(message)
                
            return messages

    async def list_sessions(self, canvas_id: str) -> List[Dict[str, Any]]:
        """List all chat sessions"""
        async with self.pool.acquire() as conn:
            if canvas_id:
                rows = await conn.fetch("""
                    SELECT id, title, model, provider, created_at, updated_at
                    FROM chat_sessions
                    WHERE canvas_id = $1
                    ORDER BY updated_at DESC
                """, canvas_id)
            else:
                rows = await conn.fetch("""
                    SELECT id, title, model, provider, created_at, updated_at
                    FROM chat_sessions
                    ORDER BY updated_at DESC
                """)
            return [dict(row) for row in rows]

    async def save_canvas_data(self, id: str, data: str, thumbnail: str = None):
        """Save canvas data"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE canvases 
                SET data = $1, thumbnail = $2, updated_at = NOW()
                WHERE id = $3
            """, json.dumps(data) if isinstance(data, (dict, list)) else data, thumbnail, id)

    async def get_canvas_data(self, id: str) -> Optional[Dict[str, Any]]:
        """Get canvas data"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT data, name
                FROM canvases
                WHERE id = $1
            """, id)

            sessions = await self.list_sessions(id)
            
            if row:
                canvas_data = row['data']
                if isinstance(canvas_data, str):
                    try:
                        canvas_data = json.loads(canvas_data)
                    except:
                        canvas_data = {}
                        
                return {
                    'data': canvas_data,
                    'name': row['name'],
                    'sessions': sessions
                }
            return None

    async def get_or_create_canvas(self, canvas_id: str, canvas_name: str) -> Dict[str, Any]:
        """Tries to fetch a canvas by its ID. If it doesn't exist, creates a new one."""
        async with self.pool.acquire() as conn:
            # First, try to get the canvas
            canvas = await conn.fetchrow("SELECT * FROM canvases WHERE id = $1", canvas_id)
            if canvas:
                return dict(canvas)
            
            # If not found, create it
            try:
                await conn.execute("""
                    INSERT INTO canvases (id, name)
                    VALUES ($1, $2)
                """, canvas_id, canvas_name)
            except asyncpg.exceptions.UniqueViolationError:
                # In case of a race condition where another process created it
                # just after our SELECT, we ignore the error and fetch again.
                pass

            # Fetch and return the newly created (or existing) canvas
            new_canvas = await conn.fetchrow("SELECT * FROM canvases WHERE id = $1", canvas_id)
            return dict(new_canvas)

    async def delete_canvas(self, id: str):
        """Delete canvas and related data"""
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM canvases WHERE id = $1", id)

    async def rename_canvas(self, id: str, name: str):
        """Rename canvas"""
        async with self.pool.acquire() as conn:
            await conn.execute("UPDATE canvases SET name = $1 WHERE id = $2", name, id)

    async def create_comfy_workflow(self, name: str, api_json: str, description: str, inputs: str, outputs: str = None):
        """Create a new comfy workflow"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO comfy_workflows (name, api_json, description, inputs, outputs)
                VALUES ($1, $2, $3, $4, $5)
            """, name, json.dumps(api_json) if isinstance(api_json, (dict, list)) else api_json, 
                description, inputs, outputs)

    async def list_comfy_workflows(self) -> List[Dict[str, Any]]:
        """List all comfy workflows"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, description, api_json, inputs, outputs 
                FROM comfy_workflows 
                ORDER BY id DESC
            """)
            return [dict(row) for row in rows]

    async def delete_comfy_workflow(self, id: int):
        """Delete a comfy workflow"""
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM comfy_workflows WHERE id = $1", id)

    async def get_comfy_workflow(self, id: int):
        """Get comfy workflow dict"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT api_json FROM comfy_workflows WHERE id = $1", id
            )
        
        if not row:
            return None
            
        try:
            api_json = row["api_json"]
            if isinstance(api_json, str):
                workflow_json = json.loads(api_json)
            else:
                workflow_json = api_json
            return workflow_json
        except json.JSONDecodeError as exc:
            raise ValueError(f"Stored workflow api_json is not valid JSON: {exc}")

    async def save_generated_image(self, session_id: str, canvas_id: str, file_url: str, 
                                 file_id: str, element_data: Dict[str, Any], prompt: str):
        """Save generated image information"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO generated_images (session_id, canvas_id, file_url, file_id, element_data, prompt)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, session_id, canvas_id, file_url, file_id, 
                json.dumps(element_data), prompt)

    async def get_generated_images(self, session_id: str = None, canvas_id: str = None) -> List[Dict[str, Any]]:
        """Get generated images"""
        async with self.pool.acquire() as conn:
            if session_id:
                rows = await conn.fetch("""
                    SELECT * FROM generated_images 
                    WHERE session_id = $1 
                    ORDER BY created_at DESC
                """, session_id)
            elif canvas_id:
                rows = await conn.fetch("""
                    SELECT * FROM generated_images 
                    WHERE canvas_id = $1 
                    ORDER BY created_at DESC
                """, canvas_id)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM generated_images 
                    ORDER BY created_at DESC
                """)
            
            images = []
            for row in rows:
                image_dict = dict(row)
                # Parse element_data if it's a string
                if isinstance(image_dict['element_data'], str):
                    try:
                        image_dict['element_data'] = json.loads(image_dict['element_data'])
                    except:
                        pass
                images.append(image_dict)
            
            return images

# Create a singleton instance - will be initialized in main.py
supabase_service = SupabaseService()