import os
import asyncio
from typing import Optional, Tuple
import aiofiles
import httpx
from urllib.parse import urlparse
import json

class SupabaseStorageService:
    def __init__(self):
        self.supabase_url = None
        self.supabase_key = None
        self.bucket_name = "images"  # 默認存儲桶名稱
        self.initialized = False
    
    def initialize(self, supabase_url: str, supabase_key: str, bucket_name: str = "images"):
        """Initialize Supabase Storage service"""
        self.supabase_url = supabase_url.rstrip('/')
        self.supabase_key = supabase_key
        self.bucket_name = bucket_name
        self.initialized = True
        print(f"✅ Supabase Storage initialized: {self.supabase_url}, bucket: {self.bucket_name}")
    
    def _get_storage_url(self) -> str:
        """Get the storage API base URL"""
        if not self.initialized:
            raise ValueError("Supabase Storage not initialized")
        return f"{self.supabase_url}/storage/v1"
    
    def _get_headers(self) -> dict:
        """Get headers for Supabase API requests"""
        return {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json"
        }
    
    async def upload_file(self, file_path: str, storage_path: str) -> str:
        """
        Upload a file to Supabase Storage
        
        Args:
            file_path: Local file path
            storage_path: Path in storage (e.g., "images/filename.jpg")
            
        Returns:
            Public URL of the uploaded file
        """
        if not self.initialized:
            raise ValueError("Supabase Storage not initialized")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        async with aiofiles.open(file_path, 'rb') as file:
            file_content = await file.read()
        
        # Determine content type based on file extension
        file_extension = os.path.splitext(storage_path)[1].lower()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.bmp': 'image/bmp'
        }
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Upload to Supabase Storage
        upload_url = f"{self._get_storage_url()}/object/{self.bucket_name}/{storage_path}"
        
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": content_type
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                upload_url,
                content=file_content,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                error_text = response.text
                raise Exception(f"Failed to upload to Supabase Storage: {response.status_code} - {error_text}")
        
        # Generate public URL
        public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
        
        print(f"📤 Uploaded to Supabase Storage: {storage_path} -> {public_url}")
        return public_url
    
    async def upload_file_content(self, file_content: bytes, storage_path: str, content_type: str = None) -> str:
        """
        Upload file content directly to Supabase Storage
        
        Args:
            file_content: File content as bytes
            storage_path: Path in storage (e.g., "images/filename.jpg")
            content_type: MIME type of the file
            
        Returns:
            Public URL of the uploaded file
        """
        if not self.initialized:
            raise ValueError("Supabase Storage not initialized")
        
        # Determine content type if not provided
        if not content_type:
            file_extension = os.path.splitext(storage_path)[1].lower()
            content_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.bmp': 'image/bmp'
            }
            content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Upload to Supabase Storage
        upload_url = f"{self._get_storage_url()}/object/{self.bucket_name}/{storage_path}"
        
        headers = {
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": content_type
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                upload_url,
                content=file_content,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code not in [200, 201]:
                error_text = response.text
                raise Exception(f"Failed to upload to Supabase Storage: {response.status_code} - {error_text}")
        
        # Generate public URL
        public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
        
        print(f"📤 Uploaded content to Supabase Storage: {storage_path} -> {public_url}")
        return public_url
    
    def get_public_url(self, storage_path: str) -> str:
        """
        Get public URL for a file in storage
        
        Args:
            storage_path: Path in storage (e.g., "images/filename.jpg")
            
        Returns:
            Public URL
        """
        if not self.initialized:
            raise ValueError("Supabase Storage not initialized")
        
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{storage_path}"
    
    async def create_bucket_if_not_exists(self) -> bool:
        """
        Create the storage bucket if it doesn't exist
        
        Returns:
            True if bucket was created or already exists
        """
        if not self.initialized:
            raise ValueError("Supabase Storage not initialized")
        
        # Check if bucket exists
        list_url = f"{self._get_storage_url()}/bucket"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(list_url, headers=self._get_headers())
            
            if response.status_code == 200:
                buckets = response.json()
                existing_buckets = [bucket['name'] for bucket in buckets]
                
                if self.bucket_name in existing_buckets:
                    print(f"✅ Storage bucket '{self.bucket_name}' already exists")
                    return True
            
            # Create bucket
            create_url = f"{self._get_storage_url()}/bucket"
            bucket_config = {
                "name": self.bucket_name,
                "public": True,
                "file_size_limit": 52428800,  # 50MB
                "allowed_mime_types": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"]
            }
            
            response = await client.post(
                create_url,
                json=bucket_config,
                headers=self._get_headers()
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ Created storage bucket '{self.bucket_name}'")
                return True
            else:
                error_text = response.text
                print(f"❌ Failed to create bucket: {response.status_code} - {error_text}")
                return False

# Global instance
supabase_storage = SupabaseStorageService() 