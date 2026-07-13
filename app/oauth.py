from jose import JWTError, jwt 
from datetime import datetime, timedelta, timezone
from . import schema
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_schema = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM=settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes


def create_access_token(id: int):
    payload = {"user_id" : id}
    time_expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = time_expire
    token = jwt.encode(payload, SECRET_KEY , algorithm=ALGORITHM )
    return token

def verify_access_token(token: str, credentails_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")

        if id is None:
            raise credentails_exception
        token_data = schema.TokenData(id=id)
        
    except JWTError:
        raise credentails_exception
    
    return token_data
    
def get_current_user(token: str = Depends(oauth2_schema)):
    credentails_exception = HTTPException(status_code=401, detail="Could not validate credentails", headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token, credentails_exception)

    return token_data.id