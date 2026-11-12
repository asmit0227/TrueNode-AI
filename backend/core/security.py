import os
from datetime import datetime, timedelta, timezone

import jwt

from dotenv import load_dotenv

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from pwdlib import PasswordHash

from backend.core.supabase_client import supabase


# Step 1: Load Environment Variables
load_dotenv()


# Step 2: JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = "HS256"

TOKEN_EXPIRE_MINUTES = 60

if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY not found")


# Step 3: Password Hasher
password_hasher = PasswordHash.recommended()


# Step 4: OAuth2
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# Step 5: Get User from Supabase
def get_user_from_db(username):

    response = (
        supabase.table("users")
        .select("username, password_hash, role, is_active")
        .eq("username", username)
        .limit(1)
        .execute()
    )

    users = response.data or []

    if not users:
        return None

    return users[0]


# Step 6: Authenticate User
def authenticate_user(username, password):

    try:
        user = get_user_from_db(username)

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable"
        ) from error

    if not user:
        return None

    # Check whether account is active
    if not user.get("is_active"):
        return None

    stored_hash = user.get("password_hash")

    if not stored_hash:
        return None

    # Verify password
    try:
        is_valid = password_hasher.verify(
            password,
            stored_hash
        )

    except Exception:
        return None

    if not is_valid:
        return None

    return {
        "username": user["username"],
        "role": user["role"]
    }


# Step 7: Create JWT Token
def create_access_token(username):

    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    )

    token = jwt.encode(
        {
            "sub": username,
            "exp": expire
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Step 8: Verify Current User
def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_error = HTTPException(
        status_code=401,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if not isinstance(username, str):
            raise credentials_error

    except jwt.InvalidTokenError:
        raise credentials_error

    # Fetch latest user information from Supabase
    try:
        user = get_user_from_db(username)

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Authentication service is temporarily unavailable"
        ) from error

    if not user or not user.get("is_active"):
        raise credentials_error

    return {
        "username": user["username"],
        "role": user["role"]
    }


# Step 9: Admin Permission
def require_admin(
    user=Depends(get_current_user)
):

    if user["role"] != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return user