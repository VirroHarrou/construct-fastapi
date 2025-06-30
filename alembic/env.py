import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from alembic.config import Config
from alembic import command
from fastapi.logger import logger
from app.config.settings import settings
from app.controllers import reviews, users, orders, auth, companies, chat
import asyncio

async def run_migrations():
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        alembic_ini_path = os.path.join(project_root, "alembic.ini")
        alembic_cfg = Config(alembic_ini_path)
        script_location = os.path.join(project_root, "alembic")
        alembic_cfg.set_main_option("script_location", script_location)
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup initiated")
    await run_migrations()
    logger.info("Application startup completed")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(companies.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(chat.router)