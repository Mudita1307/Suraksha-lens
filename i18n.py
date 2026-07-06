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

LOCALES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")

# code -> native display name shown in the picker
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिंदी",
    "sl": "සිංහල",
    "ta": "தமிழ்",    # add when Tamil translations are ready
    # "ne": "नेपाली",   # add when Nepali translations are ready
}

DEFAULT_LANG = "en"
FALLBACK_LANG = "en"


@st.cache_data(show_spinner=False)
def _load_locale_file(lang_code: str) -> dict:
    path = os.path.join(LOCALES_DIR, f"{lang_code}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    value = _lookup(_load_locale_file(lang), key)
    if value is None and lang != FALLBACK_LANG:
        value = _lookup(_load_locale_file(FALLBACK_LANG), key)
    if value is None:
        value = key

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

    choice = target.selectbox(
        "🌐 Language / भाषा",
        labels,
        index=current_index,
        key="_lang_selector_widget",
    )
    st.session_state.lang = codes[labels.index(choice)]


def inject_font_css():
    """
    Load Noto Sans fonts covering Devanagari (Hindi/Nepali), Sinhala and
    Tamil scripts so text renders consistently across OS/browsers instead
    of falling back to whatever system font happens to be installed.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Noto+Sans+Sinhala:wght@400;500;600;700&family=Noto+Sans+Tamil:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Noto Sans', 'Noto Sans Devanagari', 'Noto Sans Sinhala', 'Noto Sans Tamil', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )