import secrets
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from typing import Annotated

from ..auth import verify_api_key
from ..models.schemas import StartResponseResult, StartResponseRequest, GroupResponses, ResponseStatus, Answers
from ..models.response import Response
from ..models.questionnaire_versions import QuestionnaireVersion
from ..models.api_key import ApiKey
from ..database import get_db

router = APIRouter()

BASE_URL = "http://localhost:8080"

#region helpers

#GET /responses/{id}/answers.
#GET /responses
def build_answers(resp: Response, qv: QuestionnaireVersion, api_key:ApiKey) -> dict:
    """Builds an 'Answers' object, for the data provided"""

    return {
        "response_id": str(resp.id),
        "questionnaire": {
            "id": qv.questionnaire_id,
            "name": qv.name,
            "version": qv.version,
            "hash": qv.hash,
        },
        "source": api_key.name,
        "participant_pseudonym": resp.participant_pseudonym,
        "session_ref": resp.session_ref,
        "group_ref": resp.group_ref,            #Nem biztos hogy ez a field szükséges
        "status": resp.status,
        "answers": resp.answers
    }

#GET /responses/{id}
#POST /responses/{id}/abort
#GET /responses/{id}/answers
#GET /responses/{id}/events
def get_response_or_404(db: Session, id: str) -> Response:
    try:
        rid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(404, "Response not found")   # malformed id = does not exist
    resp = db.get(Response, rid)
    if resp is None:
        raise HTTPException(404, "Response not found")
    return resp

#endregion

#region endpoints

@router.post("/responses/{questionnaire_id}", response_model=StartResponseResult)
async def submit_response(
    questionnaire_id: Annotated[str, Path(pattern=r"^[a-z0-9_]+$")],
    response_data: StartResponseRequest, 
    db=Depends(get_db),
    key: ApiKey = Depends(verify_api_key)
    ):
    """Logic to begin the session for the form given in the URL path"""


    #Finding the requested version, or the latest one if none was provided
    stmt = select(QuestionnaireVersion).where(
        QuestionnaireVersion.questionnaire_id == questionnaire_id
    )
    if response_data.version:
        stmt = stmt.where(QuestionnaireVersion.version == response_data.version)
    qv = db.scalars(stmt.order_by(QuestionnaireVersion.created_at.desc())).first()

    if qv is None:
        raise HTTPException(404, "Questionnaire or version not found")

    resp = Response(
        questionnaire_id=qv.questionnaire_id,
        version=qv.version,
        participant_pseudonym=response_data.participant_pseudonym,
        session_ref=response_data.session_ref,
        group_ref=response_data.group_ref,
        language=response_data.language,
        occasion=response_data.occasion,
        cycle_number=response_data.cycle_number if response_data.occasion == "between_cycles" else None,
        seed=secrets.randbits(63),
        api_key_id=key.id,
    )
    db.add(resp)
    db.commit()
    db.refresh(resp)

    
    return {
        "response_id": str(resp.id),
        "status": resp.status,
        "display_url": f"{BASE_URL}/r/{resp.id}",
        }


@router.get("/responses",response_model=GroupResponses)
async def get_responses(
    group_ref: Annotated[str, Query()],
    db=Depends(get_db),
    ):
    """Logic to retrieve all the answers for a specific group reference from the database"""

    stmt = (
        select(Response, QuestionnaireVersion, ApiKey)
        .join(
            QuestionnaireVersion,
            and_(
                QuestionnaireVersion.questionnaire_id == Response.questionnaire_id,
                QuestionnaireVersion.version == Response.version,
            ),
        )
        .join(ApiKey, ApiKey.id == Response.api_key_id)
        .where(Response.group_ref == group_ref)
        .order_by(Response.started_at)
    )

    rows = db.execute(stmt).all()

    
    return {
        "group_ref": group_ref,
        "responses": [build_answers(r,qv,k) for r,qv,k in rows]
    }


@router.get("/responses/{id}", response_model=ResponseStatus)
async def get_response_by_id(
    id: str,
    db=Depends(get_db)):
    """Logic to retrieve the status of a session from its ID"""

    resp = get_response_or_404(db, id)
    return {
        "response_id": str(resp.id),
        "status": resp.status,
        "started_at": resp.started_at,
        "ended_at": resp.ended_at,
    }


@router.get("/responses/{id}/answers", response_model=Answers)
async def get_answers(id: str, db: Session = Depends(get_db)):
    """Logic to retrieve the answers of a session from its ID"""

    resp = get_response_or_404(db, id)
    qv = db.get(QuestionnaireVersion, (resp.questionnaire_id, resp.version))
    api_key = db.get(ApiKey, resp.api_key_id)
    
    return build_answers(resp, qv, api_key)


@router.post("/responses/{id}/abort", response_model=ResponseStatus)
async def abort_response(id: str, db: Session = Depends(get_db)):
    """Logic to abort a session given its ID"""
    

    
    return {}


@router.get("/responses/{id}/events")
async def get_events(id: int, db=Depends(get_db)):
    """Logic to retrieve the events and their timestamps of a session from its ID"""
    
    return {}

#endregion