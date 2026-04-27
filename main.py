import streamlit as st

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="Climate Dashboard", layout="wide")

# ---- Initialize session ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# ---- Login function ----
def login():
    st.title("Login")

    # 👇 Use form for better UX
    with st.form("login_form"):
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        submit = st.form_submit_button("Login")

    # 👇 User credentials
    users = {
        "admin": "1234",
        "chaitra": "abcd",
        "mudita": "pass123",
        "Ntasha.bhardwaj@saicjs.com": "nbm@sl",
        "Bushra.khan@saicjs.com": "nbm@sl",
        "Mudita.sharma@saicjs.com": "nbm@sl"
    }

    if submit:
        # Optional: normalize username
        username = username.strip()

        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success("Login successful ✅")
            st.rerun()
        else:
            st.error("Invalid credentials ❌")


# ---- Show login OR app ----
if not st.session_state.logged_in:
    login()

else:
    # ---- Sidebar ----
    st.sidebar.success("Logged in ✅")
    st.sidebar.write(f"Welcome, {st.session_state.user}")

    # ---- Define pages ----
    main_page = st.Page("main.py", title="Main Page", icon="🎈")
    page_1 = st.Page("Suraksha_Lens.py", title="Discover Suraksha Lens with us", icon="❄️")
    page_2 = st.Page("tier1_india_srilanka_copy_2.py", title="Tier 1: Hazard", icon="❄️")
    page_3 = st.Page("tier2_india_srilanka.py", title="Tier 2: Exposure", icon="❄️")
    page_4 = st.Page("tier3_india_srilanka.py", title="Tier 3: Vulnerability", icon="❄️")
    page_5 = st.Page("tier4_india_srilanka.py", title="Tier 4: Climate Exploitation Risk Index", icon="❄️")

    # ---- Navigation ----
    pg = st.navigation([main_page, page_1, page_2, page_3, page_4, page_5])
    pg.run()

    # ---- Logout ----
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
