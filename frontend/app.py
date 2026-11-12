import streamlit as st
import requests
import os
from UI.header import header_homes
from UI.fonts import Fonts_styling


API_URL = os.getenv("API_URL","http://127.0.0.1:8000")



# PAGE CONFIGURATION


st.set_page_config(
    page_title="TrueNode-enterprise knowledge AI",
    page_icon="https://i.ibb.co/Zzkcb47T/truenode-AI-logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>

/* Move description and login info upward */
.st-key-header_info {
    transform: translateY(-55px) !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>

/* Move Ask Your Questions section upward */
.st-key-question_section {
    transform: translateY(-70px) !important;
}

</style>
""", unsafe_allow_html=True)






# SESSION STATE


if "token" not in st.session_state:
    st.session_state.token = None

if "messages" not in st.session_state:
    st.session_state.messages = []



# AUTHENTICATION HELPERS

def get_headers():

    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


def logout():

    st.session_state.token = None

    st.session_state.messages = []

    st.rerun()


def check_session(response):

    if response.status_code == 401:

        st.session_state.token = None
        st.session_state.messages = []

        st.rerun()


def get_error_message(response):

    try:

        data = response.json()

        return str(
            data.get("detail", "Request failed")
        )

    except ValueError:

        return f"Request failed: {response.status_code}"


# LOGIN PAGE



st.markdown("""
<style>

/* Main page spacing */
.block-container {
    padding-top: 1rem;
}

/* Hide menu button */
#MainMenu {
    visibility: hidden;
}

/* Hide footer */
footer {
    visibility: hidden;
}

/* Hide deploy button */
.stAppDeployButton {
    display: none;
}

/* Keep Streamlit header visible */
header[data-testid="stHeader"] {
    visibility: visible !important;
}

</style>
""", unsafe_allow_html=True)


# Login page only when user is not logged in
if st.session_state.token is None:

    # Header and fonts
    header_homes()
    Fonts_styling()
    

    # Login styling
    st.markdown("""
    <style>

    .st-key-login_section {
        transform: translateY(-140px) !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # Login form
    with st.container(key="login_section"):

        st.subheader("➡️ Login to Continue")

        with st.form("login_form", width="stretch"):

            username = st.text_input(
                "Username"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                shortcut="enter"
            )

        # Login button clicked
        if login_button:

            if not username or not password:

                st.warning(
                    "Please enter username and password."
                )

            else:

                try:

                    with st.spinner("Logging in..."):

                        response = requests.post(
                            API_URL + "/auth/login",
                            data={
                                "username": username,
                                "password": password
                            },
                            timeout=30
                        )

                    if response.status_code == 200:

                        data = response.json()

                        st.session_state.token = data[
                            "access_token"
                        ]

                        st.session_state.messages = []

                        st.rerun()

                    elif response.status_code == 401:

                        st.error(
                            "Invalid username or password."
                        )

                    else:

                        st.error(
                            get_error_message(response)
                        )

                except requests.exceptions.RequestException:

                    st.error(
                        "Cannot connect to FastAPI backend."
                    )

    # Stop execution only for unauthenticated users
    st.stop()


# VERIFY AUTHENTICATED USER

try:

    response = requests.get(
        API_URL + "/auth/me",
        headers=get_headers(),
        timeout=30
    )

    check_session(response)

    if response.status_code != 200:

        st.error(
            "Unable to verify user."
        )

        st.stop()

    user = response.json()

    username = user["username"]

    role = user["role"]

except requests.exceptions.RequestException:

    st.error(
        "Cannot connect to FastAPI backend."
    )

    st.stop()


# MAIN PAGE



header_homes()
Fonts_styling()

with st.container(key="header_info"):

    st.markdown(
        "<p style='text-align:center; font-weight:600;'>"
        "Upload company documents(Admins only) and ask questions using AI."
        "</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center; color:gray;'>"
        f"Logged in as: {username} | Role: {role}"
        "</p>",
        unsafe_allow_html=True
    )

# SIDEBAR

with st.sidebar:

    st.header("👤 User Profile")

    st.success(
        f"Welcome, {username}"
    )

    st.info(
        f"Role: {role.upper()}"
    )

    if st.button("🚪 Logout"):

        logout()

    st.divider()

    st.header("📂 Document Management")


    # DOCUMENT UPLOAD - ADMIN ONLY

    if role == "admin":

        st.subheader("Upload Document")

        uploaded_file = st.file_uploader(
            "Choose Document",
            type=["pdf", "docx", "txt"]
        )

        if st.button("Upload Document"):

            if uploaded_file is not None:

                if uploaded_file.size > 10 * 1024 * 1024:

                    st.error(
                        "Maximum allowed file size is 10 MB."
                    )

                else:

                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )
                    }

                    try:

                        with st.spinner(
                            "Uploading document..."
                        ):

                            response = requests.post(
                                API_URL + "/documents/upload",
                                files=files,
                                headers=get_headers(),
                                timeout=120
                            )

                        check_session(response)

                        if response.status_code in [200, 201]:

                            data = response.json()

                            st.success(
                                "Document uploaded successfully!"
                            )

                            st.write(
                                "Filename:",
                                data["filename"]
                            )

                            st.write(
                                "Total Chunks:",
                                data["total_chunks"]
                            )

                        elif response.status_code == 409:

                            st.warning(
                                "This document already exists."
                            )

                        elif response.status_code == 403:

                            st.error(
                                "Admin permission required."
                            )

                        else:

                            st.error(
                                get_error_message(response)
                            )

                    except requests.exceptions.RequestException:

                        st.error(
                            "Cannot connect to FastAPI backend."
                        )

            else:

                st.warning(
                    "Please select a document."
                )

    else:

        st.caption(
            "Document upload is available to Admin only."
        )


    # DOCUMENT LISTING

    st.divider()

    st.header("📄 Uploaded Documents")

    if st.button("🔄 Refresh Documents"):

        st.rerun()

    try:

        response = requests.get(
            API_URL + "/documents/",
            headers=get_headers(),
            timeout=30
        )

        check_session(response)

        if response.status_code == 200:

            data = response.json()

            documents = data.get(
                "documents",
                []
            )

            st.write(
                "Total Documents:",
                data.get("total_documents", len(documents))
            )

            if not documents:

                st.info(
                    "No documents uploaded yet."
                )

            for document in documents:

                filename = document.get(
                    "filename",
                    "Unknown"
                )

                total_chunks = document.get(
                    "total_chunks",
                    0
                )

                document_id = document.get(
                    "document_id"
                )

                st.write(
                    "📄",
                    filename
                )

                st.caption(
                    f"Chunks: {total_chunks}"
                )

                # DELETE - ADMIN ONLY

                if role == "admin":

                    if document_id is not None:

                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{document_id}"
                        ):

                            try:

                                delete_response = requests.delete(
                                    API_URL + "/documents/" + document_id,
                                    headers=get_headers(),
                                    timeout=30
                                )

                                check_session(delete_response)

                                if delete_response.status_code in [200, 204]:

                                    st.success(
                                        "Document deleted successfully!"
                                    )

                                    st.rerun()

                                elif delete_response.status_code == 403:

                                    st.error(
                                        "Admin permission required."
                                    )

                                else:

                                    st.error(
                                        get_error_message(delete_response)
                                    )

                            except requests.exceptions.RequestException:

                                st.error(
                                    "Document deletion failed."
                                )

                    else:

                        st.caption(
                            "Legacy document - deletion unavailable."
                        )

                st.divider()

        else:

            st.error(
                get_error_message(response)
            )

    except requests.exceptions.RequestException:

        st.error(
            "Unable to load documents."
        )


# EMPLOYEE MANAGEMENT - ADMIN ONLY

if role == "admin":

    st.divider()

    st.header("👥 Employee Management")

    st.caption(
        "Create employee accounts and activate or deactivate existing employees."
    )

    # ADD NEW EMPLOYEE
    with st.expander("➕ Add New Employee", expanded=False):

        with st.form("add_employee_form", clear_on_submit=True):

            new_username = st.text_input(
                "Employee Username",
                max_chars=100
            )

            new_password = st.text_input(
                "Temporary Password",
                type="password",
                max_chars=128,
                help="Password must contain at least 8 characters."
            )

            create_employee_button = st.form_submit_button(
                "Create Employee"
            )

        if create_employee_button:

            if not new_username.strip() or not new_password:

                st.warning("Please enter both username and password.")

            else:

                try:

                    with st.spinner("Creating employee account..."):

                        create_response = requests.post(
                            API_URL + "/users/",
                            json={
                                "username": new_username.strip(),
                                "password": new_password
                            },
                            headers=get_headers(),
                            timeout=30
                        )

                    check_session(create_response)

                    if create_response.status_code in [200, 201]:

                        created_user = create_response.json().get("user", {})

                        st.success(
                            f"Employee '{created_user.get('username', new_username)}' created successfully!"
                        )

                        st.rerun()

                    elif create_response.status_code == 409:

                        st.warning("This username already exists.")

                    elif create_response.status_code == 403:

                        st.error("Admin permission required.")

                    else:

                        st.error(get_error_message(create_response))

                except requests.exceptions.RequestException:

                    st.error("Unable to connect to the backend.")

    st.subheader("Employee Accounts")

    if st.button("🔄 Refresh Employees", key="refresh_employees"):
        st.rerun()

    # FETCH EMPLOYEES FROM BACKEND
    try:

        users_response = requests.get(
            API_URL + "/users/",
            headers=get_headers(),
            timeout=30
        )

        check_session(users_response)

        if users_response.status_code == 200:

            users_data = users_response.json()
            all_users = users_data.get("users", [])

            employees = [
                account
                for account in all_users
                if account.get("role") == "employee"
            ]

            st.metric("Total Employees", len(employees))

            if not employees:

                st.info("No employees found. Create the first employee above.")

            else:

                for employee in employees:

                    employee_username = employee.get("username", "Unknown")
                    employee_is_active = bool(employee.get("is_active", False))

                    username_column, status_column, action_column = st.columns(
                        [3, 2, 2]
                    )

                    with username_column:
                        st.markdown(f"**{employee_username}**")

                    with status_column:
                        if employee_is_active:
                            st.success("Active")
                        else:
                            st.warning("Inactive")

                    with action_column:

                        button_label = (
                            "Deactivate" if employee_is_active else "Activate"
                        )

                        if st.button(
                            button_label,
                            key=f"toggle_employee_{employee_username}"
                        ):

                            try:

                                status_response = requests.patch(
                                    API_URL + f"/users/{employee_username}/status",
                                    json={
                                        "is_active": not employee_is_active
                                    },
                                    headers=get_headers(),
                                    timeout=30
                                )

                                check_session(status_response)

                                if status_response.status_code == 200:

                                    new_status = (
                                        "activated"
                                        if not employee_is_active
                                        else "deactivated"
                                    )

                                    st.success(
                                        f"Employee '{employee_username}' {new_status} successfully."
                                    )

                                    st.rerun()

                                elif status_response.status_code == 403:

                                    st.error("Admin permission required.")

                                else:

                                    st.error(get_error_message(status_response))

                            except requests.exceptions.RequestException:

                                st.error("Unable to update employee status.")

                    st.divider()

        elif users_response.status_code == 403:

            st.error("Admin permission required to view employees.")

        else:

            st.error(get_error_message(users_response))

    except requests.exceptions.RequestException:

        st.error("Unable to load employee accounts.")

else:

    st.caption("Employee management is available to Admin only.")


# CHAT SECTION

st.divider()

with st.container(key="question_section"):

    st.markdown(
        "<h2 style='text-align:center;'>💬 Ask Your Questions</h2>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>"
        "Ask questions about company policies and documents."
        "</p>",
        unsafe_allow_html=True
    )

    # Yahan apna existing question input code rakho


# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message.get("sources"):

            st.caption(
                "Sources: " + ", ".join(
                    message["sources"]
                )
            )


# AI CHAT

question = st.chat_input(
    "Ask a question about company......"
)


if question:

    # Save user message

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)


    # GENERATE AI RESPONSE

    with st.chat_message("assistant"):

        try:

            with st.spinner(
                "Searching documents..."
            ):

                response = requests.post(
                    API_URL + "/chat/query",
                    json={
                        "question": question
                    },
                    headers=get_headers(),
                    timeout=120
                )

            check_session(response)

            if response.status_code == 200:

                result = response.json()

                answer = result.get(
                    "answer",
                    "No answer generated."
                )

                sources = result.get(
                    "sources",
                    []
                )

                st.markdown(answer)

                if sources:

                    st.caption(
                        "Sources: " + ", ".join(sources)
                    )

                else:

                    st.caption(
                        "No supporting sources found."
                    )

                # Save assistant response

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })

            elif response.status_code == 403:

                st.error(
                    "You do not have permission to access this feature."
                )

            else:

                st.error(
                    get_error_message(response)
                )

        except requests.exceptions.RequestException:

            st.error(
                "Unable to get response from AI backend."
            )