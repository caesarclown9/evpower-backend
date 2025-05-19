from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from app.api import auth, clients, stations, locations, ocpp
from fastapi.middleware.cors import CORSMiddleware

# --- Импорт для автоматического создания полей ---
from app.db.base_class import Base
from app.db.session import engine
from app.db import models  # noqa: F401, чтобы зарегистрировать все модели

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="EV Power Backend API", version="1.0.0")

# --- Кастомизация OpenAPI для поддержки Bearer Auth ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # По умолчанию требовать авторизацию для всех эндпоинтов (можно убрать если не нужно)
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS (разрешить всё для разработки)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(stations.router)
app.include_router(locations.router)
app.include_router(ocpp.router)

# TODO: добавить остальные роутеры (locations, maintenance, reports, ocpp)

# --- Автоматическое создание полей в таблицах ---
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

