import os
from fastapi import FastAPI
import asyncio
from alembic.config import Config
from alembic import command
from fastapi.logger import logger
from app.config.settings import settings
from app.controllers import reviews, users, orders, auth, companies, chat

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

# @app.on_event("startup")
# async def startup_event():
#     logger.info("Application startup initiated")
#     loop = asyncio.get_event_loop()
#     await loop.run_in_executor(None, run_migrations)
#     logger.info("Application startup completed")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated")
    await asyncio.to_thread(run_migrations)
    logger.info("Application startup completed")
    
def run_migrations():
    try:
        # Получаем абсолютный путь к корню проекта
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        alembic_ini_path = os.path.join(project_root, "alembic.ini")
        
        logger.info(f"Loading Alembic config from: {alembic_ini_path}")
        alembic_cfg = Config(alembic_ini_path)
        
        # Устанавливаем расположение скриптов миграции
        script_location = os.path.join(project_root, "alembic")
        alembic_cfg.set_main_option("script_location", script_location)
        logger.info(f"Set script location to: {script_location}")
        
        # Применяем миграции
        logger.info("Starting database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
