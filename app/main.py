from fastapi import FastAPI
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

    
    

