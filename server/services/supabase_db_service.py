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
        """Save a new chat session"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO chat_sessions (id, model, provider, canvas_id, title)
                VALUES ($1, $2, $3, $4, $5)
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

                message = {
                    "role": row['role'],
                    "content": content
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

    # IP Management Methods
    async def get_top_ips(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top IPs by heat score"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    i.id, i.name, i.description, i.image_url, i.heat_score, 
                    i.view_count, i.like_count, i.tags,
                    c.name as category_name
                FROM ips i
                LEFT JOIN ip_categories c ON i.category_id = c.id
                ORDER BY i.heat_score DESC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]

    async def get_ip_by_id(self, ip_id: int) -> Optional[Dict[str, Any]]:
        """Get IP details by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    i.*, 
                    c.name as category_name,
                    c.description as category_description
                FROM ips i
                LEFT JOIN ip_categories c ON i.category_id = c.id
                WHERE i.id = $1
            """, ip_id)
            return dict(row) if row else None

    async def record_ip_interaction(self, ip_id: int, interaction_type: str, user_identifier: str = None):
        """Record an IP interaction (view, like, share, comment)"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO ip_interactions (ip_id, interaction_type, user_identifier)
                VALUES ($1, $2, $3)
            """, ip_id, interaction_type, user_identifier)

    async def get_ip_categories(self) -> List[Dict[str, Any]]:
        """Get all IP categories"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, name, description, created_at, updated_at
                FROM ip_categories
                ORDER BY name
            """)
            return [dict(row) for row in rows]

    async def search_ips(self, query: str = None, category_id: int = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search IPs by name, description, or category"""
        async with self.pool.acquire() as conn:
            where_conditions = []
            params = []
            param_count = 0

            if query:
                param_count += 1
                where_conditions.append(f"(i.name ILIKE ${param_count} OR i.description ILIKE ${param_count})")
                params.append(f"%{query}%")

            if category_id:
                param_count += 1
                where_conditions.append(f"i.category_id = ${param_count}")
                params.append(category_id)

            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            param_count += 1
            params.append(limit)

            query_sql = f"""
                SELECT 
                    i.id, i.name, i.description, i.image_url, i.heat_score, 
                    i.view_count, i.like_count, i.tags,
                    c.name as category_name
                FROM ips i
                LEFT JOIN ip_categories c ON i.category_id = c.id
                {where_clause}
                ORDER BY i.heat_score DESC
                LIMIT ${param_count}
            """
            
            rows = await conn.fetch(query_sql, *params)
            return [dict(row) for row in rows]

# Create a singleton instance - will be initialized in main.py
supabase_service = SupabaseService()