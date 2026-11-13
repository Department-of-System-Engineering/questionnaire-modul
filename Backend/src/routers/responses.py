from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from src.database import get_db
#from src.auth import get_api_key
#from src.models.

router = APIRouter()

@router.post("/responses/{questionnaire_id}")
async def submit_response(questionnaire_id: int, response_data: dict, db=Depends(get_db)):
    """Logic to begin the session for the form given in the URL path"""

    stmt = select
    
    return {}


@router.get("/responses")
async def get_responses(group_ref: str, db=Depends(get_db)):
    """Logic to retrieve all the answers for a specific group reference from the database"""
    
    return {}


@router.get("/responses/{id}")
async def get_response_by_id(id: int, db=Depends(get_db)):
    """Logic to retrieve the status of a session from its ID"""
    
    return {}

@router.post("/responses/{id}/abort")
async def abort_response(id: int, db=Depends(get_db)):
    """Logic to abort a session given its ID"""
    
    return {}


@router.get("/responses/{id}/answers")
async def get_answers(id: int, db=Depends(get_db)):
    """Logic to retrieve the answers of a session from its ID"""
    
    return {}


@router.get("/responses/{id}/events")
async def get_events(id: int, db=Depends(get_db)):
    """Logic to retrieve the events and their timestamps of a session from its ID"""
    
    return {}