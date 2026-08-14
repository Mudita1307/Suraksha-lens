import streamlit as st
import chat_bot
from i18n import inject_sidebar_layout_fix, t, language_selector, inject_font_css

# MUST be first Streamlit command
st.set_page_config(page_title="Suraksha Lens Dashboard", layout="wide")
inject_font_css()
inject_sidebar_layout_fix()

# ---- Initialize session ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""


# ---- Login function ----
def login():
    # Let people pick a language before they even log in
    language_selector(st.sidebar)

    st.title(t("common.login_title"))

    with st.form("login_form"):
        username = st.text_input(
            t("common.username_label"),
            key="username",
        )
        password = st.text_input(
            t("common.password_label"),
            type="password",
            key="password",
        )
        submit = st.form_submit_button(
            t("common.login_button")
        )

    # 👇 User credentials
    users = {
        "admin": "1234",
        "chaitra": "abcd",
        "Ntasha.bhardwaj@saicjs.com": "nbm@sl",
        "Bushra.khan@saicjs.com": "nbm@sl",
        "Mudita.sharma@saicjs.com": "nbm@sl",
        "aanchal.modani@saicjs.com": "sl@2026",
        "consultantai@saicjs.com": "ai@sl",
        "lawofficersv@gmail.com": "sv@sl2026",
        "maya.singh@nhrf.no": "nhrf@sl2026",
        "consultant.india@nhrf.no": "nhrf@sl2026",
        "reidun.ryland@nhrf.no": "nhrf@sl2026",
        "consultant.srilanka@nhrf.no": "nhrf@sl2026",
        "ipenprogram@gmail.com": "nhrf@sl2026",
        "munnadeblr@gmail.com": "mn@sl2026",
        "mail2heo@gmail.com": "heo@sl2026",
        "standupmovementlka@gmail.com": "suml@sl2026",
        "tndwwtsolidarity@gmail.com": "tndwwt@sl2026",
        "preeti@sevamandir.org": "sm@sl2026",
        "rajesh.sen@sevamandir.org": "sm@sl2026",
        "archanajjpt@gmail.com": "awc@sl2026",
        "samankh2h@gmail.com": "hthl@sl2026",
    }

    if submit:
        # Optional: normalize username
        username = username.strip()

        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(t("common.login_success"))
            st.rerun()
        else:
            st.error(t("common.login_error"))


if not st.session_state.logged_in:
    login()

else:
    # ---- Sidebar ----
    language_selector(st.sidebar)
    st.sidebar.success(t("common.logged_in_badge"))
    st.sidebar.write(
        t("common.welcome", user=st.session_state.user)
    )

    # ---- Navigation pages ----

    # main_page = st.Page(
    #     "main.py",
    #     title=t("nav.main_page"),
    #     icon="🎈"
    # )

    page_1 = st.Page(
        "Suraksha_Lens.py",
        title=t("nav.discover"),
        icon="❄️",
        url_path="discover",
    )

    page_2 = st.Page(
        "tier1_dashboard.py",
        title=t("nav.tier1"),
        icon="❄️",
        url_path="tier1",
    )

    page_3 = st.Page(
        "tier2_dashboard.py",
        title=t("nav.tier2"),
        icon="❄️",
        url_path="tier2",
    )

    page_4 = st.Page(
        "tier3_dashboard.py",
        title=t("nav.tier3"),
        icon="❄️",
        url_path="tier3",
    )

    page_5 = st.Page(
        "tier4_dashboard.py",
        title=t("nav.tier4"),
        icon="❄️",
        url_path="tier4",
    )

    page_6 = st.Page(
        "scam.py",
        title=t("nav.scam"),
        icon="❄️",
        url_path="scam",
    )

    pg = st.navigation(
        [
            page_1,
            page_2,
            page_3,
            page_4,
            page_5,
            page_6,
        ]
    )

    # ---- Page context ----
    PAGE_CONTEXT = {
        "discover": {
            "page": "discover",
            "tier": None,
        },
        "tier1": {
            "page": "tier1",
            "tier": "T1",
        },
        "tier2": {
            "page": "tier2",
            "tier": "T2",
        },
        "tier3": {
            "page": "tier3",
            "tier": "T3",
        },
        "tier4": {
            "page": "tier4",
            "tier": "T4",
        },
        "scam": {
            "page": "scam",
            "tier": None,
        },
    }

    page_context = PAGE_CONTEXT.get(
        pg.url_path,
        {
            "page": "unknown",
            "tier": None,
        },
    )

    st.session_state["_current_page"] = page_context["page"]
    st.session_state["tier"] = page_context["tier"]

    # ---- Chat ----
    chat_bot.init_chat_state()
    chat_bot.render_chat_toggle_button()

    if st.session_state.chat_panel_open:
        col_main, col_chat = st.columns([3, 2])

        with col_main:
            pg.run()

        with col_chat:
            chat_bot.render_chat_panel()

    else:
        pg.run()

    # ---- Logout ----
    # Placed after both branches above, so it always renders
    # regardless of whether the chat panel is open or closed.
    st.sidebar.markdown(
        '<div class="sidebar-bottom-anchor"></div>',
        unsafe_allow_html=True,
    )

    if st.sidebar.button(t("common.logout")):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()