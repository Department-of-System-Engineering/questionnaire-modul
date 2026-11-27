import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

#from src.auth import generate_api_key
from src.database import get_db
#from src.models.

router = APIRouter()

@router.get("/dev_tools/health")
def health_check(db=Depends(get_db)):

    """Check that the API is running and can reach the database.

    Runs a trivial query (`SELECT 1`) against the database. Intended for
    development and monitoring, not as part of the questionnaire API.

    Args:
        db: Database session (injected).

    Returns:
        `{"status": "ok"}` if the database answered.

    Raises:
        HTTPException: 503 if the database query fails.
    """
    # Perform a simple database query to verify connectivity
    try:
        db.execute(select(1))
    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {"status": "ok"}
