from supabase import create_client, Client
from app.config import settings

sup: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

bucket = sup.storage.from_(settings.supabase_bucket_name)

SUPABASE_BUCKET = "asknitt-files"

def upload_file(
    file_bytes: bytes,
    storage_path: str,
    content_type: str
):
    return bucket.upload(
        storage_path,
        file_bytes,
        {
            "content-type": content_type,
            "upsert": "false"
        }
    )

def delete_file(storage_path: str):
    return bucket.remove([storage_path])

def create_signed_url(storage_path: str):
    response = sup.storage \
        .from_(SUPABASE_BUCKET) \
        .create_signed_url(storage_path, 3600)

    return response["signedURL"]