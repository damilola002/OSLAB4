
import sqlite3
import uuid
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends,
    status
)
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from server.database import get_connection, initialize_database
from server.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


app = FastAPI(title="Secure Cloud Storage API")

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

security = HTTPBearer(auto_error=False)

initialize_database()


# =====================================
# USER MODEL
# =====================================

class UserCredentials(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


# =====================================
# AUTHENTICATION VERIFICATION
# =====================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    with get_connection() as connection:
        user = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user_id


# =====================================
# HOME ENDPOINT
# =====================================

@app.get("/")
def home():
    return {
        "message": "Secure Cloud Storage Server is running!"
    }


# =====================================
# USER REGISTRATION
# =====================================

@app.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(credentials: UserCredentials):
    username = credentials.username.strip()

    if len(username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must contain at least 3 characters"
        )

    password_hash = hash_password(credentials.password)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (username, password_hash)
            )

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    return {
        "message": "User registered successfully"
    }


# =====================================
# USER LOGIN
# =====================================

@app.post("/login")
def login(credentials: UserCredentials):
    username = credentials.username.strip()

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT id, password_hash
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

    if user is None or not verify_password(
        credentials.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(user["id"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =====================================
# UPLOAD ENCRYPTED FILE
# =====================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    original_name: str = Form(...),
    user_id: int = Depends(get_current_user)
):
    filename = Path(
        original_name.replace("\\", "/")
    ).name

    if filename in ("", ".", ".."):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename"
        )

    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / file_id

    try:
        with open(file_path, "xb") as output:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                output.write(chunk)

        file_size = file_path.stat().st_size

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO files (
                    file_id,
                    owner_id,
                    original_filename,
                    size
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_id,
                    user_id,
                    filename,
                    file_size
                )
            )

    except Exception:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Upload failed"
        )

    finally:
        await file.close()

    return {
        "message": "File uploaded successfully",
        "file_id": file_id,
        "filename": filename
    }


# =====================================
# LIST USER'S FILES
# =====================================

@app.get("/files")
def list_files(
    user_id: int = Depends(get_current_user)
):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                file_id,
                original_filename,
                size
            FROM files
            WHERE owner_id = ?
            ORDER BY created_at DESC, rowid DESC
            """,
            (user_id,)
        ).fetchall()

    files = []

    for row in rows:
        file_path = UPLOAD_DIR / row["file_id"]

        if file_path.is_file():
            files.append({
                "file_id": row["file_id"],
                "filename": row["original_filename"],
                "size": row["size"]
            })

    return {
        "files": files
    }


# =====================================
# DOWNLOAD USER'S FILE
# =====================================

@app.get("/download/{file_id}")
def download_file(
    file_id: uuid.UUID,
    user_id: int = Depends(get_current_user)
):
    file_id_string = str(file_id)

    with get_connection() as connection:
        file_record = connection.execute(
            """
            SELECT file_id
            FROM files
            WHERE file_id = ?
            AND owner_id = ?
            """,
            (
                file_id_string,
                user_id
            )
        ).fetchone()

    if file_record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    file_path = UPLOAD_DIR / file_id_string

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    return FileResponse(
        path=file_path,
        filename=f"{file_id_string}.bin",
        media_type="application/octet-stream"
    )
