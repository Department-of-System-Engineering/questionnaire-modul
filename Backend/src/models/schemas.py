from enum import Enum
from typing import Annotated, Any, Literal
from datetime import datetime
from pydantic import BaseModel, StringConstraints

Identifier = Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]+$")]
Text = dict[str, str]  # {"en": "...", "hu": "..."}

class Status(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    aborted = "aborted"

class QuestionnaireVersion(BaseModel):
    version: str
    languages: list[str]

class QuestionnaireItem(BaseModel):
    id: Identifier
    name: Text
    versions: list[QuestionnaireVersion]

class QuestionnaireList(BaseModel):
    questionnaires: list[QuestionnaireItem]

class StartResponseRequest(BaseModel):
    version: str | None = None
    participant_pseudonym: str
    session_ref: str | None = None
    group_ref: str | None = None
    language: str
    occasion: Literal["pre", "post", "between_cycles"]
    cycle_number: int | None = None

class StartResponseResult(BaseModel):
    response_id: str
    status: Status
    display_url: str

class ResponseStatus(BaseModel):
    response_id: str
    status: Status
    started_at: datetime
    ended_at: datetime | None = None

class QuestionnaireRef(BaseModel):
    id: Identifier
    name: Text
    version: str
    hash: str

AnswerType = Literal[
    "likert", "matrix", "semantic_differential", "slider", "vas", "pictorial",
    "single_choice", "multi_choice", "dropdown", "numeric", "text_short",
    "text_long", "datetime", "ranking", "pairwise",
]

class Answer(BaseModel):
    item: str
    type: AnswerType
    value: Any | None          # shape depends on type, null if skipped
    skipped: bool
    first_answer_ms: int | None = None
    last_answer_ms: int | None = None
    changes: int | None = None

class Answers(BaseModel):
    response_id: str
    questionnaire: QuestionnaireRef
    source: str                # name of the API key that started it
    participant_pseudonym: str
    session_ref: str | None = None
    group_ref: str | None = None
    status: Status
    answers: list[Answer]

class GroupResponses(BaseModel):
    group_ref: str
    responses: list[Answers]

class Event(BaseModel):
    t_utc_ns: int
    t_mono_ns: int
    type: Literal["questionnaire_start", "page_shown", "item_answered",
                  "page_submitted", "questionnaire_end", "questionnaire_aborted"]
    payload: dict[str, Any]