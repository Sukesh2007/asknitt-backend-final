from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_str(password: str):
    return pwd_context.hash(password)

def verify(password1, hashedpassword):
    return pwd_context.verify(password1, hashedpassword)