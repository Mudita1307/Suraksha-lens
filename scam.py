import streamlit as st

from i18n import t, inject_font_css

inject_font_css()

st.header(t("scam.about_header"))
st.write(t("scam.about_write"))

st.header(t("scam.detect_header"))
st.markdown(t("scam.detect_list"))

st.header(t("scam.why_header"))
st.write(t("scam.why_write"))

st.header(t("scam.access_header"))
st.write(t("scam.access_write"))

st.markdown(
    f"""
    <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
    {t("scam.note")}
    </div>
    """,
    unsafe_allow_html=True
)