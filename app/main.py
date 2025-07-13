from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.config.settings import settings
from app.controllers import images, reviews, users, orders, auth, companies, chat
from app.services.images import ImageService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(chat.router)
app.include_router(images.router)

app.state.image_service = ImageService()
app.mount(
    settings.IMAGE_BASE_URL, 
    StaticFiles(directory=settings.IMAGE_STORAGE), 
    name="images"
)