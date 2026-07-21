from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.middleware.auth import require_super_admin
from src.modules.admin_dashboard import service
from src.modules.admin_dashboard.schemas import DashboardStatsOut

router = APIRouter(
    prefix="/bd-admin/api/dashboard",
    tags=["admin-dashboard"],
    dependencies=[Depends(require_super_admin)],
)


@router.get("/stats", response_model=DashboardStatsOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    return service.get_dashboard_stats(db)
