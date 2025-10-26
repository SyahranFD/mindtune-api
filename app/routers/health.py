from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db

router = APIRouter(
    prefix="/api/health",
    tags=["health"],
)


@router.get("", status_code=status.HTTP_200_OK)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint untuk memastikan API dan database berjalan dengan baik.
    Endpoint ini digunakan oleh script monitoring untuk memverifikasi status aplikasi.
    """
    try:
        # Periksa koneksi database
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API berjalan dengan baik"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"API tidak sehat: {str(e)}"
        )