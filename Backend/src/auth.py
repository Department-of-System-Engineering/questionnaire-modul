from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.api_key import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(
        api_key_hash: str | None = Security(api_key_header), 
        db: Session = Depends(get_db),
    ) -> None:
    if not api_key_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )
    key = db.scalar(
        select(ApiKey).where(
            ApiKey.key_hash == api_key_hash,
            ApiKey.active == True,
        )
    )
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return key