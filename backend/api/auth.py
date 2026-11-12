from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user
)

router = APIRouter()


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends()):

    user = authenticate_user(
        form.username,
        form.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(user["username"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


@router.get("/me")
def get_profile(user=Depends(get_current_user)):

    return user