from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_str(password: str):
    return pwd_context.hash(password)

def verify(password1, hashedpassword):
    return pwd_context.verify(password1, hashedpassword)

def create_signed_url(storage_path: str):
    response = supabase.storage \
        .from_(SUPABASE_BUCKET) \
        .create_signed_url(storage_path, 3600)

    return response["signedURL"]