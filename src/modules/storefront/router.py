from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.modules.storefront import service
from src.modules.storefront.exceptions import PackageUnavailableError
from src.modules.storefront.schemas import PackageListingOut, PackagePdpOut

router = APIRouter(prefix="/api/bd/packages", tags=["storefront"])


@router.get("", response_model=list[PackageListingOut])
def list_packages(db: Session = Depends(get_db)):
    return service.list_storefront_packages(db)


@router.get("/{package_id}", response_model=PackagePdpOut)
def get_package(package_id: str, db: Session = Depends(get_db)):
    try:
        return service.get_storefront_package(db, package_id)
    except PackageUnavailableError:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="This course isn't available right now."
        )
