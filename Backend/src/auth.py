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

    """Check the `X-API-KEY` header and return the matching API key row.

    Used as a dependency: it runs before the endpoint, and if it raises, the
    endpoint never executes. The header value is compared directly with the
    stored `key_hash`, and only keys marked `active` are accepted. Endpoints
    that need to know who is calling (for example to store the key that
    started a response) can receive the returned row.

    Args:
        api_key_hash: Value of the `X-API-KEY` header (injected).
        db: Database session (injected).

    Returns:
        The active ApiKey row that matches the header.

    Raises:
        HTTPException: 401 if the header is missing, or if no active key
            matches it.
    """
    
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