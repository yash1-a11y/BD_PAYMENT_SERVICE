import logging

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config.settings import get_settings
from src.db.base import get_db
from src.modules.admin_auth.router import router as admin_auth_router
from src.modules.admin_dashboard.router import router as admin_dashboard_router
from src.modules.admin_users.router import router as admin_users_router
from src.modules.catalogue.router import router as catalogue_router
from src.modules.checkout.router import router as checkout_router
from src.modules.storefront.router import router as storefront_router
from src.modules.webhooks.router import router as webhooks_router

logging.basicConfig(level=get_settings().log_level)

app = FastAPI(title="BD Payment Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_auth_router)
app.include_router(admin_dashboard_router)
app.include_router(admin_users_router)
app.include_router(catalogue_router)
app.include_router(storefront_router)
app.include_router(checkout_router)
app.include_router(webhooks_router)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy"},
        )
    return {"status": "ok"}
