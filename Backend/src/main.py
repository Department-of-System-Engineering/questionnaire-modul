from fastapi import FastAPI, Depends

from src.auth import verify_api_key
from src.routers import questionnaires, responses, dev_tools


app = FastAPI(title="Questionnaire Module API", version="1.0.0")

app.include_router(questionnaires.router, dependencies=[Depends(verify_api_key)], tags=["questionnaires"])
app.include_router(responses.router, dependencies=[Depends(verify_api_key)], tags=["responses"])

app.include_router(dev_tools.router, tags=["dev_tools"])