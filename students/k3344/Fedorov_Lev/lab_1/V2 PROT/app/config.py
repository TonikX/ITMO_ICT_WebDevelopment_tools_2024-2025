from dynaconf import Dynaconf
from dotenv import load_dotenv
import os
import uuid
import shutil
from fastapi import UploadFile, HTTPException
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
EXCEL_TEMPLATES_DIR = BASE_DIR / "excel_templates"
FILLED_PROTOCOLS_DIR = BASE_DIR / "filled_protocols"

os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(EXCEL_TEMPLATES_DIR, exist_ok=True)
os.makedirs(FILLED_PROTOCOLS_DIR, exist_ok=True)

TEMPLATE_EXCEL_PATH = EXCEL_TEMPLATES_DIR / "Протокол.xlsx"

HERE = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="project_name",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="project_name_env",
    load_dotenv=True,
)

settings.database_url = os.getenv('DATABASE_URL')
DATABASE_URL = settings.database_url
settings.security = {
    'secret_key': os.getenv('SECRET_KEY'),
    'algorithm': os.getenv('ALGORITHM'),
    'access_token_expire_minutes': int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')),
    'refresh_token_expire_minutes': int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))
}

UPLOAD_DIR = BASE_DIR / "uploads"
PLAYER_PHOTOS_DIR = UPLOAD_DIR / "photos"
PLAYER_CERTIFICATES_DIR = UPLOAD_DIR / "certificates"
TEAM_LOGOS_DIR = UPLOAD_DIR / "team_logos"

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PLAYER_PHOTOS_DIR, exist_ok=True)
os.makedirs(PLAYER_CERTIFICATES_DIR, exist_ok=True)
os.makedirs(TEAM_LOGOS_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
ALLOWED_DOCUMENT_TYPES = ["application/pdf"]


def validate_file_type(file: UploadFile, allowed_types: list):
    """Validate file extension"""
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_types:
        allowed_ext_str = ", ".join(allowed_types)
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {allowed_ext_str}"
        )
    return file_ext


async def save_upload_file(
        file: UploadFile,
        directory: str,
        allowed_types: list,
        filename: str = None
) -> str:
    content_type = file.content_type
    if content_type not in allowed_types:
        allowed = ", ".join(allowed_types)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Allowed types: {allowed}"
        )

    import os
    os.makedirs(directory, exist_ok=True)

    if not filename:
        filename = str(uuid.uuid4())

    extension = content_type.split("/")[-1]
    file_path = f"{directory}/{filename}.{extension}"

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path
