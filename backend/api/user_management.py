from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.core.security import (
    require_admin,
    password_hasher
)

from backend.core.supabase_client import supabase


router = APIRouter()


# ----------------------------------
# Request Models
# ----------------------------------

class EmployeeCreate(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
    )

    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserStatusUpdate(BaseModel):

    is_active: bool


# ----------------------------------
# 1. Get All Users
# ----------------------------------

@router.get("/")
def list_users(
    admin=Depends(require_admin)
):

    try:

        response = (
            supabase.table("users")
            .select(
                "id, username, role, is_active, created_at"
            )
            .order("created_at", desc=True)
            .limit(500)
            .execute()
        )

        users = response.data or []

        return {
            "total_users": len(users),
            "users": users
        }

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail="Unable to fetch users"
        ) from error


# ----------------------------------
# 2. Create New Employee
# ----------------------------------

@router.post("/")
def create_employee(
    employee: EmployeeCreate,
    admin=Depends(require_admin)
):

    username = employee.username.strip().lower()

    if not employee.password.strip():

        raise HTTPException(
            status_code=422,
            detail="Password cannot be empty"
        )

    # Hash password before saving
    hashed_password = password_hasher.hash(
        employee.password
    )

    user_data = {

        "username": username,

        "password_hash": hashed_password,

        "role": "employee",

        "is_active": True

    }

    try:

        response = (
            supabase.table("users")
            .insert(user_data)
            .select(
                "id, username, role, is_active, created_at"
            )
            .execute()
        )

        created_users = response.data or []

        if not created_users:

            raise HTTPException(
                status_code=500,
                detail="Employee creation could not be confirmed"
            )

        return {
            "message": "Employee created successfully",
            "user": created_users[0]
        }

    except HTTPException:
        raise

    except Exception as error:

        # PostgreSQL unique constraint violation
        if getattr(error, "code", None) == "23505":

            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            ) from error

        raise HTTPException(
            status_code=503,
            detail="Unable to create employee"
        ) from error


# ----------------------------------
# 3. Activate / Deactivate Employee
# ----------------------------------

@router.patch("/{username}/status")
def update_employee_status(
    username: str,
    status: UserStatusUpdate,
    admin=Depends(require_admin)
):

    username = username.strip().lower()

    try:

        # Check whether employee exists
        response = (
            supabase.table("users")
            .select("username, role")
            .eq("username", username)
            .limit(1)
            .execute()
        )

        users = response.data or []

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail="Unable to fetch user"
        ) from error

    if not users:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user = users[0]

    # Only employee accounts can be modified
    if user["role"] != "employee":

        raise HTTPException(
            status_code=403,
            detail="Admin account cannot be modified here"
        )

    try:

        response = (
            supabase.table("users")
            .update({
                "is_active": status.is_active
            })
            .eq("username", username)
            .select(
                "username, role, is_active"
            )
            .execute()
        )

        updated_users = response.data or []

        if not updated_users:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return {
            "message": "User status updated successfully",
            "user": updated_users[0]
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail="Unable to update user status"
        ) from error