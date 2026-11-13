from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from src.database import get_db
from src.models.questionnaire_versions import QuestionnaireVersion
#from src.auth import get_api_key

router = APIRouter()

@router.get("/questionnaires")
async def get_questionnaires(db=Depends(get_db)):
    """Logic to retrieve questionnaires from the database or any other source"""
    stmt = select(QuestionnaireVersion).order_by(QuestionnaireVersion.questionnaire_id, QuestionnaireVersion.version)
    

    return {"questionnaires": db.scalars(stmt).all()}  # Return the retrieved questionnaires