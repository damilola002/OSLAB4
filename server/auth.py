
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()

JWT_SECRET = os.environ.get("SECURECLOUD_JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(
        "SECURECLOUD_JWT_SECRET environment variable is required"
    )

JWT_ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 30


def hash_password(password):
    return password_hasher.hash(password)


def verify_password(password, password_hash):
    return password_hasher.verify(password, password_hash)


def create_access_token(user_id):
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRATION_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expiration
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        return None
