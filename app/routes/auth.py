from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import models, schema, utils, database, oauth
from typing import Optional

router = APIRouter()

@router.post("/login", response_model=schema.Token)
def login(user_login: schema.Send_Register, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.rollno == user_login.rollno).first()

    if user == None:
        raise HTTPException(status_code=403, detail="No user found with this rollno")
    
    if not utils.verify(user_login.password, user.password):
        raise HTTPException(status_code=403, detail="Invalid Password!")
    
    encoded_token = oauth.create_access_token(user.id)

    return {"encode_token": encoded_token, "type": "bearer"}

@router.get("/dashboard", response_model = schema.Register)
def search_user(user_id: Optional[int] = Depends(oauth.get_current_user) ,db: Session = Depends(database.get_db)):
    user_query = db.query(models.User).filter(models.User.id == user_id).first()

    if user_query is None:
        raise HTTPException(status_code=402, detail="Not Authenticated")
    
    return user_query