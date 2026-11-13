from fastapi import FastAPI, Depends


from src.routers import questionnaires, responses, dev_tools


app = FastAPI(title="Questionnaire Module API", version="1.0.0")

app.include_router(questionnaires.router, prefix="/routers")
app.include_router(responses.router, prefix="/routers")

app.include_router(dev_tools.router, prefix="/routers")