from fastapi import FastAPI
from .routes import user, auth, question, answer
from .config import settings
from . import models
from .database import engine

app = FastAPI()

print(settings.database_username)

models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(question.router)
app.include_router(answer.router)

@app.get("/")
def getHome():
    return {"message": "Hello World"}

