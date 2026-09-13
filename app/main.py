from fastapi import FastAPI
from .routes import user, auth, question, answer, attachment
from .config import settings
from . import models
from .database import engine

app = FastAPI()

print("DB HOST:", settings.database_hostname)
print("DB PORT:", settings.database_port)
print("DB USER:", settings.database_username)
print("DB NAME:", settings.database_name)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(question.router)
app.include_router(answer.router)
app.include_router(attachment.router)

@app.get("/")
def getHome():
    return {"message": "Hello World"}

