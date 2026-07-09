"""
Lightweight i18n helper for the Suraksha Lens Streamlit dashboard.

Usage in any page script:

    from i18n import t, language_selector, inject_font_css

    inject_font_css()                 # once per page, after set_page_config
    language_selector(st.sidebar)     # optional - draw a picker on this page too
    st.header(t("tier1.content.India.header"))

Adding a new language later (Sinhala / Tamil / Nepali) only requires:
    1. Drop a new locales/<code>.json file (same keys as en.json).
    2. Add one line to SUPPORTED_LANGUAGES below.
No other code changes are needed.
"""

import json
import os
import streamlit as st

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# Where the locales/ folder might live, tried in this order. Streamlit's
# working directory can vary depending on how the app is launched, so we
# don't rely on a single guess - we search a handful of sane candidates
# relative to this file (i18n.py) instead of relative to cwd.
_CANDIDATE_LOCALE_DIRS = [
    os.path.join(_THIS_DIR, "locales"),
    os.path.join(_THIS_DIR, "locale"),        # tolerate the singular spelling too
    os.path.join(os.getcwd(), "locales"),
    os.path.join(os.getcwd(), "locale"),
    os.path.join(_THIS_DIR, "..", "locales"),
    os.path.join(_THIS_DIR, "..", "locale"),
    _THIS_DIR,  # fallback: json files placed directly next to i18n.py, no subfolder
]

# code -> native display name shown in the picker
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिंदी",
    "si": "සිංහල",
    "ta": "தமிழ்",
    "be": "বাংলা",
    "ka": "ಕನ್ನಡ",
    "ma": "മലയാളം",
    # "ne": "नेपाली",   # add when Nepali translations are ready
}

DEFAULT_LANG = "en"
FALLBACK_LANG = "en"

_missing_locale_paths = []  # populated the first time a lookup fails, for diagnostics


def _resolve_locale_path(lang_code: str):
    """Return the first existing locales/<lang_code>.json path, or None."""
    tried = []
    for d in _CANDIDATE_LOCALE_DIRS:
        path = os.path.normpath(os.path.join(d, f"{lang_code}.json"))
        tried.append(path)
        if os.path.exists(path):
            return path
    _missing_locale_paths.extend(p for p in tried if p not in _missing_locale_paths)
    return None


@st.cache_data(show_spinner=False)
def _read_locale_json(path: str, mtime: float) -> dict:
    # `mtime` is part of the cache key on purpose: if the JSON file on disk
    # changes (a redeploy, a hot-reload, an edit) the cache busts itself
    # automatically instead of silently serving whatever was loaded the
    # first time this Streamlit process started. Without this, a server
    # that doesn't do a full process restart on deploy can keep serving a
    # stale in-memory copy of a locale file indefinitely.
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_locale_file(lang_code: str) -> dict:
    path = _resolve_locale_path(lang_code)
    if path is None:
        return {}
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        mtime = 0
    return _read_locale_json(path, mtime)


def locale_debug_info() -> dict:
    """
    Call this anywhere (e.g. temporarily in main.py) to see exactly which
    paths i18n.py checked and whether each locale file was actually found.
    Handy for diagnosing a "keys showing instead of text" problem.
    """
    info = {}
    for code in SUPPORTED_LANGUAGES:
        info[code] = _resolve_locale_path(code) or f"NOT FOUND (checked: {_missing_locale_paths})"
    return info


def init_language():
    """Make sure st.session_state.lang exists. Safe to call many times."""
    if "lang" not in st.session_state:
        st.session_state.lang = DEFAULT_LANG


def set_language(lang_code: str):
    if lang_code in SUPPORTED_LANGUAGES:
        st.session_state.lang = lang_code


def _lookup(data: dict, dotted_key: str):
    node = data
    for part in dotted_key.split("."):
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def t(key: str, **kwargs) -> str:
    """
    Translate a dotted key, e.g. t("common.login_button").
    Falls back to English, then to the raw key itself, so missing
    translations never crash the app - they just show in English
    (or as the key, in the worst case) until someone fills them in.
    Supports {placeholder} substitution: t("common.welcome", user=name)
    """
    init_language()
    lang = st.session_state.lang

    active_data = _load_locale_file(lang)
    value = _lookup(active_data, key)
    if value is None and lang != FALLBACK_LANG:
        value = _lookup(_load_locale_file(FALLBACK_LANG), key)
    if value is None:
        value = key
        # If even the base English locale is empty, the locales/ folder
        # almost certainly isn't where i18n.py expects it. Surface this
        # loudly, once, instead of silently printing dotted keys everywhere.
        if not _load_locale_file(FALLBACK_LANG) and not st.session_state.get("_locale_warning_shown"):
            st.session_state["_locale_warning_shown"] = True
            st.sidebar.error(
                "⚠️ Translation files not found.\n\n"
                "i18n.py could not locate locales/en.json. Checked:\n"
                + "\n".join(f"- {p}" for p in _missing_locale_paths)
                + "\n\nMake sure the `locales` folder sits in the same "
                "directory as i18n.py, main.py, and the tier*_dashboard.py files."
            )

    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, IndexError):
            return value
    return value


def language_selector(container=None):
    """
    Draw a language picker and store the choice in st.session_state.lang.
    Pass st.sidebar (default) or st (main body) or a column/container.
    """
    init_language()
    target = container if container is not None else st.sidebar
    codes = list(SUPPORTED_LANGUAGES.keys())
    labels = [SUPPORTED_LANGUAGES[c] for c in codes]
    current_index = codes.index(st.session_state.lang) if st.session_state.lang in codes else 0

    def _on_lang_change():
        choice = st.session_state["_lang_selector_widget"]
        st.session_state.lang = codes[labels.index(choice)]

    target.selectbox(
        "🌐 Language / भाषा",
        labels,
        index=current_index,
        key="_lang_selector_widget",
        on_change=_on_lang_change,
    )


def inject_font_css():
    """
    Load Noto Sans fonts covering Devanagari (Hindi/Nepali), Sinhala and
    Tamil scripts so text renders consistently across OS/browsers instead
    of falling back to whatever system font happens to be installed.
    """
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Noto+Sans+Sinhala:wght@400;500;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700&display=swap">
        <style>
        html, body, [class*="css"] {
            font-family: 'Noto Sans', 'Noto Sans Devanagari', 'Noto Sans Sinhala', 'Noto Sans Tamil', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_sidebar_layout_fix():
    """
    Makes the sidebar a full-height flex column so a bottom-anchored
    element (e.g. logout button) can be pushed to the very bottom,
    using the space that would otherwise need a manual spacer div
    to give the last dropdown's popover room to render.
    """
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }
        .sidebar-bottom-anchor {
            margin-top: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )