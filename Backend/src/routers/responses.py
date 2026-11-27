import secrets
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import select, and_, func, update
from sqlalchemy.orm import Session
from typing import Annotated

from ..auth import verify_api_key
from ..models.schemas import StartResponseResult, StartResponseRequest, GroupResponses, ResponseStatus, Answers, Event
from ..models.response import Response
from ..models.questionnaire_versions import QuestionnaireVersion
from ..models.api_key import ApiKey
from ..models.response_event import ResponseEvent
from ..database import get_db
from config import settings

router = APIRouter()

#region helpers

#GET /responses/{id}/answers.
#GET /responses
def build_answers(resp: Response, qv: QuestionnaireVersion, api_key:ApiKey) -> dict:
    
    """Build one `Answers` object, as defined in the API spec.

    Combines the response row with the questionnaire version it was started
    with (for id, name, version and hash) and the API key that started it
    (for `source`). The stored `answers` list is passed through unchanged, so
    it must already match the `Answer` schema. Used by both
    `GET /responses/{id}/answers` and `GET /responses`, so the two always
    return the same structure.

    Args:
        resp: The response row.
        qv: The exact questionnaire version the response belongs to.
        api_key: The API key row referenced by `resp.api_key_id`.

    Returns:
        A dict that validates against the `Answers` schema.
    """

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

    """Load a response by its id, or raise 404 if there is no such response.

    The id arrives from the URL as a string. A value that is not a valid UUID
    cannot exist in the database, so it is treated the same as a missing
    response and also gives 404 (not FastAPI's 422).

    Args:
        db: Database session.
        id: The response_id from the URL path.

    Returns:
        The matching Response row.

    Raises:
        HTTPException: 404 if the id is malformed or no response has it.
    """
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

R400 = {400: {"description": "Bad request"}}
R401 = {401: {"description": "Missing or invalid API key"}}
R404 = {404: {"description": "Response not found"}}

@router.post("/responses/{questionnaire_id}",
            response_model=StartResponseResult,
            status_code=201,
            responses={**R400, **R401,
                        404:{"description": "Questionnaire not found"}
                    })
def submit_response(
    questionnaire_id: Annotated[str, Path(pattern=r"^[a-z0-9_]+$")],
    response_data: StartResponseRequest, 
    db=Depends(get_db),
    key: ApiKey = Depends(verify_api_key)):

    """Start a new response for the questionnaire given in the URL path.

    Creates a new response with status `in_progress`. If no `version` is sent,
    the latest uploaded version of the questionnaire is used. The response is
    tied to that exact version, and to the API key that started it. This
    endpoint only ever inserts a new row and never changes an existing
    response.

    Args:
        questionnaire_id: The questionnaire's id, from the `GET /questionnaires` list.
        response_data: Participant pseudonym, language, occasion and the
            optional version, session_ref, group_ref and cycle_number.
        db: Database session (injected).
        key: The API key row of the caller (injected), stored as the
            source of the response.

    Returns:
        The new response_id, its status, and the display_url where the
        questionnaire opens on the participant's screen.

    Raises:
        HTTPException: 404 if the questionnaire or the requested version
            does not exist.
        HTTPException: 400 if the language is not available for the
            questionnaire, or if `occasion` is `between_cycles` and no
            `cycle_number` is given.
    """


    #Finding the requested version, or the latest one if none was provided
    stmt = select(QuestionnaireVersion).where(
        QuestionnaireVersion.questionnaire_id == questionnaire_id
    )
    if response_data.version:
        stmt = stmt.where(QuestionnaireVersion.version == response_data.version)
    qv = db.scalars(stmt.order_by(QuestionnaireVersion.created_at.desc())).first()

    if qv is None:
        raise HTTPException(404, "Questionnaire or version not found")

    if response_data.language not in qv.languages:
        raise HTTPException(400, f"Language '{response_data.language}' is not available")
    if response_data.occasion == "between_cycles" and response_data.cycle_number is None:
        raise HTTPException(400, "cycle_number is required for between_cycles")

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
        "display_url": f"{settings.base_url}/r/{resp.id}",
        }


@router.get("/responses",
            response_model=GroupResponses,
            responses={**R400, **R401})
def get_responses(
    group_ref: Annotated[str, Query()],
    db=Depends(get_db)):

    """Return all responses that were started with the given group_ref.

    Every questionnaire in the group is included, and so is every status
    (`in_progress`, `completed` and `aborted`). Each item has the same
    structure as the result of `GET /responses/{id}/answers`. The list is
    ordered by start time. A group with no responses returns an empty list,
    not an error.

    Args:
        group_ref: The grouping label the responses were started with. For
            the Experiment module this is the ethics permit number.
        db: Database session (injected).

    Returns:
        The group_ref and the list of responses in that group.
    """

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


@router.get("/responses/{id}",
            response_model=ResponseStatus,
            responses={**R401, **R404})
def get_response_by_id(
    id: str,
    db=Depends(get_db)):

    """Return the current status of a response.

    Reports whether the response is `in_progress`, `completed` or `aborted`,
    when it started, and when it ended. `ended_at` is `null` while the
    response is still running.

    Args:
        id: The response_id returned when the response was started.
        db: Database session (injected).

    Returns:
        The response's id, status, start time and end time (UTC).

    Raises:
        HTTPException: 404 if the response does not exist, or if the id is
            not a valid UUID.
    """

    resp = get_response_or_404(db, id)
    return {
        "response_id": str(resp.id),
        "status": resp.status,
        "started_at": resp.started_at,
        "ended_at": resp.ended_at,
    }


@router.get("/responses/{id}/answers",
            response_model=Answers,
            responses={**R401, **R404})
def get_answers(
    id: str,
    db: Session = Depends(get_db)):
    
    """Return all answers of a response.

    The result includes the exact questionnaire version that was filled in
    (id, name, version, hash), the name of the API key that started the
    response (`source`), and the answers given so far. A response that is
    still running, or has no answers yet, returns an empty `answers` list.

    Args:
        id: The response_id returned when the response was started.
        db: Database session (injected).

    Returns:
        The same structure as one item of `GET /responses`.

    Raises:
        HTTPException: 404 if the response does not exist.
    """

    resp = get_response_or_404(db, id)
    qv = db.get(QuestionnaireVersion, (resp.questionnaire_id, resp.version))
    api_key = db.get(ApiKey, resp.api_key_id)
    
    return build_answers(resp, qv, api_key)


@router.post("/responses/{id}/abort",
            response_model=ResponseStatus,
            responses={**R401, **R404,
                        409:{"description": "Response already completed or aborted"}
                    })
def abort_response(
    id: str,
    db: Session = Depends(get_db)):
    
    """Abort a running response.

    Sets the status to `aborted` and records the end time. Answers that were
    already given are kept. Only responses that are still `in_progress` can
    change: aborting an already aborted response or a completed response is never modified.

    Args:
        id: The response_id returned when the response was started.
        db: Database session (injected).

    Returns:
        The response's status after the call, including `ended_at`.

    Raises:
        HTTPException: 404 if the response does not exist.
        HTTPException: 409 if the response is already completed or aborted.
    """

    resp = get_response_or_404(db, id)

    result = db.execute(
        update(Response)
        .where(Response.id == resp.id, Response.status == "in_progress")
        .values(status="aborted", ended_at=func.now())
    )
    db.commit()
    db.refresh(resp)

    if result.rowcount == 0:
        raise HTTPException(409, f"Response is already {resp.status}")

    return {
        "response_id": str(resp.id),
        "status": resp.status,
        "started_at": resp.started_at,
        "ended_at": resp.ended_at
    }


@router.get("/responses/{id}/events",
            response_model=list[Event],
            responses={**R401, **R404})
def get_events(
    id: str,
    db: Session = Depends(get_db)):

    """Return the events of a response in chronological order.

    Events are sorted by UTC time, with the monotonic clock as a tiebreaker.
    A response with no events returns an empty list.

    Args:
        id: The response_id returned when the response was started.
        db: Database session (injected).

    Raises:
        HTTPException: 404 if the response does not exist.
    """
    resp = get_response_or_404(db, id)

    rows = db.scalars(
        select(ResponseEvent)
        .where(ResponseEvent.response_id == resp.id)
        .order_by(ResponseEvent.t_utc_ns, ResponseEvent.t_mono_ns)
        ).all()
    
    return [
        {
            "t_utc_ns": e.t_utc_ns,
            "t_mono_ns": e.t_mono_ns,
            "type": e.type,
            "payload": e.payload
        }
        for e in rows
    ]

#endregion