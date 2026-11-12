from backend.core.supabase_client import supabase


def test_connection():

    try:
        print("Connecting to Supabase...")

        response = (
            supabase.table("users")
            .select("username, role")
            .execute()
        )

        print("Supabase Connected Successfully!")
        print("Users Table Accessible!")

        users = response.data or []

        print("Total Users:", len(users))

        for user in users:
            print(
                f"Username: {user['username']} | Role: {user['role']}"
            )

    except Exception as error:
        print("Supabase Connection Failed!")
        print("Error:", type(error).__name__)


if __name__ == "__main__":
    test_connection()