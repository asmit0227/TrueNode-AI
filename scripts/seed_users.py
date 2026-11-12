import os

from dotenv import load_dotenv

from backend.core.supabase_client import supabase


# Load environment variables
load_dotenv()


# Get existing password hashes
admin_hash = os.getenv("ADMIN_PASSWORD_HASH")

employee_hash = os.getenv("EMPLOYEE_PASSWORD_HASH")


# Check hashes
if not admin_hash or not employee_hash:

    raise ValueError(
        "Admin or Employee password hash missing from .env"
    )


# Prepare user records
users = [

    {
        "username": "admin",
        "password_hash": admin_hash,
        "role": "admin",
        "is_active": True
    },

    {
        "username": "employee",
        "password_hash": employee_hash,
        "role": "employee",
        "is_active": True
    }

]


# Insert or update users
response = (
    supabase.table("users")
    .upsert(
        users,
        on_conflict="username"
    )
    .execute()
)


print("Users migrated successfully!")

print("Admin and Employee records saved in Supabase.")