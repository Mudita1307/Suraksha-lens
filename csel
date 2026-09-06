import streamlit as st
import pandas as pd
import plotly.express as px

from i18n import inject_sidebar_layout_fix, inject_font_css

st.set_page_config(page_title="CSEL", layout="wide")
inject_font_css()
inject_sidebar_layout_fix()

st.session_state["_current_page"] = "csel"
st.session_state["tier"] = "CSEL"

# Load Data
@st.cache_data
def load_data():
    stage2 = pd.read_csv("csel_stage2_final.csv")
    stage3_ceri = pd.read_csv("csel_stage3_ceri_comparable.csv")
    theme_freq = pd.read_csv("csel_stage3_theme_frequency.csv")
    pillar_severity = pd.read_csv("csel_stage3_pillar_severity.csv")
    return stage2, stage3_ceri, theme_freq, pillar_severity

stage2, stage3_ceri, theme_freq, pillar_severity = load_data()


# Header
st.header("CSEL — Community Safety Evidence Layers")
st.subheader("Ground-level testimony from trained community evidence leaders, layered onto the Climate Exploitation Risk Index")
st.write(
    "CSEL turns hyperlocal evidence — collected and documented by trained Community "
    "Safety Evidence Leaders — into structured data: what people are experiencing, how "
    "severe it sounds, and how it compares to CERI's data-driven risk scores. This layer "
    "exists to surface local realities that official datasets alone can miss."
)

# Sidebar
st.sidebar.title("Filters")

district_choice = st.sidebar.multiselect(
    "Select District",
    sorted(stage2["District"].unique().tolist()),
)
theme_choice = st.sidebar.multiselect(
    "Select Theme",
    sorted(stage2["Code"].unique().tolist()),
)

filtered = stage2.copy()
if district_choice:
    filtered = filtered[filtered["District"].isin(district_choice)]
if theme_choice:
    filtered = filtered[filtered["Code"].isin(theme_choice)]

st.markdown(
    f"""
    <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
    This is based on {stage2['Interview_ID'].nunique()} interviews and {len(stage2)} human-verified
    segments so far. Treat single-district or single-interview figures as early signal, not a
    confirmed pattern — this will grow more reliable as more interviews are reviewed.
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# Section 1: Theme frequency
st.subheader("1. What are communities talking about?")
theme_freq_filtered = filtered["Code"].value_counts().reset_index()
theme_freq_filtered.columns = ["Code", "Mentions"]
fig1 = px.bar(
    theme_freq_filtered.sort_values("Mentions", ascending=True),
    x="Mentions", y="Code", orientation="h",
)
st.plotly_chart(fig1, width="stretch")
st.caption(
    "Each bar is one theme from the CSEL codebook. The length shows how many separate "
    "interview segments mentioned it — a simple count of how often something came up "
    "in conversation, not a severity score."
)

# Section 2: District x Pillar severity heatmap
st.subheader("2. Where does it hurt most, and in what way?")
heatmap_data = filtered.groupby(["District", "CSEL_Pillar"])["Severity (0–3)"].mean().round(2).reset_index()
heatmap_pivot = heatmap_data.pivot(index="District", columns="CSEL_Pillar", values="Severity (0–3)")
fig2 = px.imshow(
    heatmap_pivot,
    color_continuous_scale="Reds",
    labels=dict(color="Avg severity (0-3)"),
    aspect="auto",
    text_auto=True,
)
st.plotly_chart(fig2, width="stretch")
st.caption(
    "Each cell shows the average severity (0 = barely present, 3 = severe/urgent) of "
    "everything said about that broader life-area (\"pillar\"), in that district. Darker "
    "red means the hardship described there tends to sound more serious. A pillar groups "
    "several related themes together — for example, \"Livelihood Changes\" combines labour "
    "and income-related themes into one figure."
)

# Section 3: CERI-comparable scores
st.subheader("3. CSEL-derived risk scores, by district")
st.dataframe(stage3_ceri, width="stretch")
st.caption(
    "Hazard, Exposure, and Vulnerability are each the average severity (0-1 scale) of "
    "everything said on that specific dimension, per district. Risk is Hazard × Exposure "
    "× Vulnerability multiplied together, not averaged — because real risk needs all three "
    "conditions present at once; a severe hazard nobody is exposed to isn't a big real risk. "
    "The \"(n)\" columns show how many individual quotes back each number — a score built "
    "from 1-2 quotes is far less certain than one built from 20. This table exists to sit "
    "side-by-side with CERI's own official scores for the same districts."
)

# Section 4: quote drill-down
st.subheader("4. See the real quotes behind the numbers")
st.caption(
    "Every number above comes from real interview quotes. Expand any row below to read "
    "the actual testimony behind it, in both the original language and English."
)
st.write(f"{len(filtered)} matching segment(s)")
for _, row in filtered.iterrows():
    with st.expander(f"{row['District']} — {row['Code']} (Severity: {row['Severity (0–3)']})"):
        st.write("**Original:**", row["Quote (original)"])
        st.write("**Translated:**", row["Quote (translated)"])
