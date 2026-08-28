from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import models, schema, utils, database, oauth
from typing import List
from sqlalchemy import func

router = APIRouter()

@router.post("/register", status_code=201, response_model=schema.Register)
def register(signup: schema.Send_Register, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.rollno == signup.rollno).first()
    if not user is None:
        raise HTTPException(status_code=402, detail="Already a user present with that rollno")
    hashpassword = utils.hash_str(signup.password)
    loading = signup.model_dump()
    loading["password"] = hashpassword
    new_reg = models.User(**loading)
    db.add(new_reg)
    db.commit()
    db.refresh(new_reg)
    return new_reg

@router.get("/all/users", response_model = List[schema.Register])
def get_all_users(db: Session = Depends(database.get_db)):
    user_query = db.query(models.User)
    return user_query.all()

@router.patch("/follow/accept")
def accept_request(id: int, user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    content = db.query(models.Follow).filter(models.Follow.receiver_id == user_id, models.Follow.requester_id == id).first()
    if not content:
        raise HTTPException(status_code=404, detail=f"No requests are there from {id}")
    content.status = "accepted"
    db.commit()
    db.refresh(content)
    return {"detail": "Request Taken"}

@router.delete("/follow/reject")
def reject_requst(id: int, user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    content = db.query(models.Follow).filter(models.Follow.receiver_id == user_id, models.Follow.requester_id == id).first()
    if not content:
        raise HTTPException(status_code=404, detail="No reuests are there from {id}")
    content_query = db.query(models.Follow).filter(models.Follow.receiver_id == user_id, models.Follow.requester_id == id)
    content_query.delete(synchronize_session=False)
    db.commit()
    return {"detail": "rejected successfully"}

@router.get("/follow/request")
def request_follow(id: int, user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    content = db.query(models.Follow).filter(models.Follow.receiver_id == id, models.Follow.requester_id == user_id).first()
    if content:
        raise HTTPException(status_code=404, detail=f"Already there is a relation {content.status}")
    if id == user_id:
        raise HTTPException(
            status_code=400,
            detail="You cannot follow yourself."
        )
    extra_query = models.Follow(requester_id = user_id, receiver_id=id, status="pending")
    db.add(extra_query)
    db.commit()
    db.refresh(extra_query)
    return {"detail": f"requested {id} by {user_id}"}

@router.delete("/unfollow")
def unfollow(id: int, user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    content = db.query(models.Follow).filter(models.Follow.receiver_id == id, models.Follow.requester_id == user_id)
    if not content.first():
        raise HTTPException(status_code=404, detail="there is no relation")
    content.delete(synchronize_session=False)
    db.commit()
    return {"detail": f"Unfollowed the user {id}"}

@router.get("/user/followers", response_model=List[schema.Register])
def followers(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    content = db.query(models.Follow).filter(models.Follow.receiver_id == user_id, models.Follow.status == "accepted").all()
    a = []
    if len(content) == 0:
        return []
    for p in content:
        item = db.query(models.User).filter(models.User.id == p.requester_id).first()
        a.append(item)
    return a

@router.get("/user/following", response_model=List[schema.Register])
def following(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    content = db.query(models.Follow).filter(models.Follow.requester_id == user_id, models.Follow.status == "accepted").all()
    a = []
    if len(content) == 0:
        return []
    for p in content:
        item = db.query(models.User).filter(models.User.id == p.receiver_id).first()
        a.append(item)
    return a

@router.get("/user/discover", response_model=List[schema.DiscoverUser])
def discover_users(
    user_id=Depends(oauth.get_current_user),
    db: Session = Depends(database.get_db)
):
    users = db.query(models.User).filter(
        models.User.id != user_id
    ).all()

    result = []

    for user in users:

        # Check whether the current user already follows this user
        my_relation = db.query(models.Follow).filter(
            models.Follow.requester_id == user_id,
            models.Follow.receiver_id == user.id
        ).first()

        # Already following -> don't show
        if my_relation is not None:
            continue

        # Check whether the other user follows the current user
        their_relation = db.query(models.Follow).filter(
            models.Follow.requester_id == user.id,
            models.Follow.receiver_id == user_id
        ).first()

        if their_relation is not None:
            follow_status = "followed_by"
        else:
            follow_status = "none"

        result.append(
            schema.DiscoverUser(
                id=user.id,
                name=user.name,
                rollno=user.rollno,
                department=user.department,
                follow_status=follow_status
            )
        )

    return result

@router.get("/user/requests", response_model=List[schema.Register])
def get_follow_requests(
    user_id=Depends(oauth.get_current_user),
    db: Session = Depends(database.get_db)
):

    users = (
        db.query(models.User)
        .join(
            models.Follow,
            models.User.id == models.Follow.requester_id
        )
        .filter(
            models.Follow.receiver_id == user_id,
            models.Follow.status == "pending"
        )
        .all()
    )

    return users


@router.get("/user/follow/count")
def follow_count(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    followers = (
        db.query(func.count(models.Follow.receiver_id))
        .filter(models.Follow.receiver_id == user_id)
        .scalar()
    )

    following = (
        db.query(func.count(models.Follow.receiver_id))
        .filter(models.Follow.requester_id == user_id)
        .scalar()
    )

    return {
        "followers": followers,
        "following": following
    }


@router.get("/user/questions/other", response_model=list[schema.UserQuestions])
def get_other_questions(user_id = Depends(oauth.get_current_user), db: Session = Depends(database.get_db)):
    questions = db.query(models.User).filter(models.User.id != user_id).all()
    return questions
