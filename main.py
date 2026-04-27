import streamlit as st

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="Suraksha Lens Dashboard", layout="wide")

# ---- Initialize session ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---- Login function ----
def login():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # 👇 Add multiple users here
    users = {
        "admin": "1234",
        "chaitra": "abcd",
        "mudita": "pass123",
        "Ntasha.bhardwaj@saicjs.com":"nbm@sl",
        
        "Bushra.khan@saicjs.com":"nbm@sl",
        "Mudita.sharma@saicjs.com":"nbm@sl"
    }

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username   # optional
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---- Show login OR app ----
if not st.session_state.logged_in:
    login()

else:
    st.sidebar.success("Logged in ✅")

    # ---- Define pages ----
    main_page = st.Page(r"main.py", title="Main Page", icon="🎈")
    page_1 = st.Page(r"Suraksha_Lens.py", title="Discover Suraksha Lens with us", icon="❄️")
    page_2 = st.Page(r"tier1_india_srilanka_copy_2.py", title=" Tier 1: Hazard", icon="❄️")
    page_3 = st.Page(r"tier2_india_srilanka.py", title="Tier 2: Exposure", icon="❄️")
    page_4 = st.Page(r"tier3_india_srilanka.py", title="Tier 3: Vulnerability", icon="❄️")
    page_5 = st.Page(r"tier4_india_srilanka.py", title="Tier 4: Climate Exploitation Risk Index", icon="❄️")

    # ---- Navigation ----
    pg = st.navigation([page_1, page_2, page_3, page_4, page_5])
    pg.run()

    # ---- Logout ----
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
