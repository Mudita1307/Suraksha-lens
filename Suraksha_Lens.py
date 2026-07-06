import streamlit as st

from i18n import t, inject_font_css

st.set_page_config(page_title="Suraksha Lens", layout="wide")
inject_font_css()

# Language is chosen once, globally, from the sidebar picker in main.py.
# This page just reads whatever st.session_state.lang is currently set to.

st.title(t("discover.title"))
st.subheader(t("discover.subheader"))

st.write(t("discover.intro1"))
st.write(t("discover.intro2"))

st.header(t("discover.powers_header"))
st.subheader(t("discover.ceri_subheader"))

st.write(t("discover.ceri_intro"))

st.markdown(t("discover.pillars_markdown"))

st.write(t("discover.assembly_write"))

st.header(t("discover.action_header"))

st.write(t("discover.action_write"))