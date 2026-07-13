from fastapi import APIRouter, HTTPException, Depends
from .. import schema, oauth, models, database
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func

router = APIRouter()

@router.post("/post/answer", response_model=schema.Answerdb)
def post_answer(answer: schema.Answer, db: Session = Depends(database.get_db), user_id: Optional[int] = Depends(oauth.get_current_user)):
    answer1 = models.Answer(owner_id=user_id, **answer.model_dump())
    db.add(answer1)
    db.commit()
    db.refresh(answer1)
    return answer1

@router.post("/vote/answer")
def post_vote(votes: schema.Votes, db: Session = Depends(database.get_db), user_id = Depends(oauth.get_current_user)):
    answer = db.query(models.Answer).filter(models.Answer.id == votes.answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail=f"Post with {votes.answer_id} is not found")
    vote_query = db.query(models.Vote).filter(models.Vote.answer_id == votes.answer_id, models.Vote.user_id == user_id)
    voted = vote_query.first()
    if voted is None:
        content = models.Vote(**votes.model_dump(), user_id=user_id)
        db.add(content)
        db.commit()
        db.refresh(content)
        return {"message": "Successfully voted"}
    if voted.vote_dir == votes.vote_dir:
        return
    voted.vote_dir = votes.vote_dir
    db.commit()
    db.refresh(voted)
    return {"message": "Successfully voted"}

@router.get("/get/votes")
def count_votes(id: int, db: Session = Depends(database.get_db)):
    total_votes = db.query(
        func.sum(models.Vote.vote_dir)
    ).filter(
        models.Vote.answer_id == id
    ).scalar() or 0
    return {"votes": total_votes}

@router.get("/question/answers/{question_id}", response_model=list[schema.Answerdb])
def get_answers(
    question_id: int,
    db: Session = Depends(database.get_db)
):
    question = db.query(models.Question).filter(
        models.Question.id == question_id
    ).first()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found"
        )

    return db.query(models.Answer).filter(
        models.Answer.question_id == question_id
    ).all()


@router.get("/votes/me", response_model=list[schema.UserVoteOut])
def get_my_votes(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth.get_current_user)
):
    votes = db.query(models.Vote).filter(
        models.Vote.user_id == current_user
    ).all()

    return votes