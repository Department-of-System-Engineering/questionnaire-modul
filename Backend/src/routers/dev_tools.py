from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

#from src.auth import generate_api_key
from src.database import get_db
#from src.models.

router = APIRouter()

@router.get("/dev_tools/health")
def health_check(db=Depends(get_db)):
    """Health check endpoint to verify that the API is running"""
    # Perform a simple database query to verify connectivity
    try:
        db.execute(select(1))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

    return {"status": "ok"}



"""
@router.post("/dev_tools/GenerateKey/{key}")
def Generate_Api_Key(key: str, db=Depends(get_db)):
    #Endpoint to generate a new API key
    # Implementation for generating API key
    new_key = generate_api_key(key, db)
    return {"api_key": new_key}
"""