import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException

from app.config.settings import settings

class ImageService:
    def __init__(self):
        self.storage_path = settings.IMAGE_STORAGE
        self.base_url = settings.IMAGE_BASE_URL
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def save_image(self, file: UploadFile) -> str:
        # Проверка расширения
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(400, "Invalid image format")
        
        # Проверка размера
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(400, "File too large")

        # Генерация уникального имени
        filename = f"{uuid.uuid4()}{ext}"
        file_path = self.storage_path / filename
        
        # Асинхронное сохранение
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await file.read())
        
        return f"{self.base_url}/{filename}"

    def delete_image(self, url: str) -> None:
        if not url.__contains__(self.base_url):
            return
            
        filename = url.split("/")[-1]
        file_path = self.storage_path / filename
        
        if file_path.exists():
            file_path.unlink()