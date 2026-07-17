from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.modules.admin_auth.router import router as admin_auth_router
from src.modules.admin_users.router import router as admin_users_router
from src.modules.catalogue.router import router as catalogue_router

app = FastAPI(title="BD Payment Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth_router)
app.include_router(admin_users_router)
app.include_router(catalogue_router)
