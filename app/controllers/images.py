from fastapi import APIRouter, UploadFile, File, Depends

from app.schemas.images import ImageResponse
from app.services.images import ImageService


router = APIRouter(tags=["storage"])

def get_image_service() -> ImageService:
    return ImageService()

@router.post("/upload", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    image_service: ImageService = Depends(get_image_service)
):
    url = await image_service.save_image(file)
    return ImageResponse(url=url)