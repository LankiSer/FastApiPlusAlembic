from fastapi import FastAPI
from app.api.v1 import auth

app = FastAPI()

# Подключаем роутер авторизации с префиксом /api/v1
app.include_router(auth.router, prefix="/api/v1")