from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from ..database import get_db
from ..models.questionnaire_versions import QuestionnaireVersion
from ..models.schemas import QuestionnaireList
#from src.auth import get_api_key

router = APIRouter()

@router.get("/questionnaires", response_model=QuestionnaireList)
async def get_questionnaires(db=Depends(get_db)):
    """Logic to retrieve questionnaires from the database"""

    rows = db.scalars(
        select(QuestionnaireVersion).order_by(
            QuestionnaireVersion.questionnaire_id,
            QuestionnaireVersion.created_at.desc()
        )
    ).all()

    grouped: dict[str, dict] = {}
    for row in rows:
        q = grouped.setdefault(
            row.questionnaire_id,
            {
                "id": row.questionnaire_id,
                "name": row.name,
                "versions": [],
            }
        )
        q["name"] = row.name
        q["versions"].append({"version": row.version, "languages": list(row.languages)})

    
    return {"questionnaires": list(grouped.values())}