from fastapi import APIRouter, HTTPException, Depends, Path, File, UploadFile
from .. import schema, oauth, models, database
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter()

@router.post("/post/question", response_model=schema.Questiondb)
async def post_question(question: schema.Question,  user_id :Optional[int] =  Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    if user_id is None: 
        raise HTTPException(status_code=402, detail="Not Authenticated")
    question1 = models.Question(owner_id = user_id, **question.model_dump())
    db.add(question1)
    db.commit()
    db.refresh(question1)
    return question1

@router.post("/post/anoymous/question", response_model=schema.Questiondb)
def post_anoymous_question(question: schema.Question, db: Session = Depends(database.get_db)):
    question1 = models.Question(owner_id = None, **question.model_dump())
    db.add(question1)
    db.commit()
    db.refresh(question1)
    return question1

@router.get("/get/question", response_model = list[schema.Questiondb])
def get_my_question(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    questions = db.query(models.Question).filter(models.Question.owner_id == user_id).all()
    return questions

@router.get("/get/other/question", response_model = list[schema.Questiondb])
def get_my_question(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    questions = db.query(models.Question).filter(models.Question.owner_id != user_id).all()
    return questions

@router.patch("/solve/question")
def toggle_solve(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db), q_id: int = 0):
    question = db.query(models.Question).filter(models.Question.id == q_id , models.Question.owner_id == user_id).first()
    question.isSolved = not question.isSolved
    db.commit()
    db.refresh(question)
    return {"detail": "Success"}
