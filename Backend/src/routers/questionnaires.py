from fastapi import APIRouter, Depends
from sqlalchemy import select

from ..database import get_db
from ..models.questionnaire_versions import QuestionnaireVersion
from ..models.schemas import QuestionnaireList
#from src.auth import get_api_key

router = APIRouter()

@router.get("/questionnaires",
            response_model=QuestionnaireList,
            responses={401:{"description": "Missing or invalid API key"}})
def get_questionnaires(db=Depends(get_db)):

    """Return the list of available questionnaires.

    Each questionnaire appears once, with all of its uploaded versions and the
    languages available in each. Versions are ordered oldest to newest, so the
    latest version is at the end of the list, and the questionnaire's name is
    taken from that latest version. Questionnaires are not created through the
    API; they come from the uploaded definition files.

    Args:
        db: Database session (injected).

    Returns:
        The list of questionnaires, each with its id, name and versions.
    """

    rows = db.scalars(
        select(QuestionnaireVersion).order_by(
            QuestionnaireVersion.questionnaire_id,
            QuestionnaireVersion.created_at
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