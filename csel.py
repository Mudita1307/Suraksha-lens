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
# Section 1: Theme frequency (lollipop chart)
st.subheader("1. What are communities talking about?")

theme_freq_filtered = filtered["Code"].value_counts().reset_index()
theme_freq_filtered.columns = ["Code", "Mentions"]
theme_freq_filtered = theme_freq_filtered.merge(
    stage2[["Code", "CSEL_Pillar"]].drop_duplicates(), on="Code", how="left"
).sort_values("Mentions")

fig1 = px.scatter(
    theme_freq_filtered, x="Mentions", y="Code", size="Mentions", color="CSEL_Pillar",
    size_max=22,
)
for _, row in theme_freq_filtered.iterrows():
    fig1.add_shape(
        type="line", x0=0, x1=row["Mentions"], y0=row["Code"], y1=row["Code"],
        line=dict(color="rgba(255,255,255,0.25)", width=2),
    )
fig1.update_layout(
    paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e", font_color="#f0f0f0",
    margin=dict(t=20, l=10, r=10, b=40),
)
fig1.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
fig1.update_yaxes(showgrid=False)
st.plotly_chart(fig1, width="stretch")
st.caption(
    "Each dot is one theme from the CSEL codebook. Its position and size show how many "
    "separate interview segments mentioned it — a count of how often something came up "
    "in conversation, not a severity score. Color shows which broader pillar it belongs to."
)


# Section 2: District x Pillar severity (sunburst)
st.subheader("2. Where does it hurt most, and in what way?")

fig2 = px.sunburst(
    pillar_severity, path=["District", "CSEL_Pillar"], values="Severity (0–3)",
    color="Severity (0–3)", color_continuous_scale="Blues",
)
fig2.update_layout(
    paper_bgcolor="black", plot_bgcolor="black", font_color="white",
    margin=dict(t=20, l=10, r=10, b=10),
)
st.plotly_chart(fig2, width="stretch")
st.caption(
    "Each slice shows the average severity (0 = barely present, 3 = severe/urgent) of "
    "everything said about that broader life-area (\"pillar\"), in that district. Darker "
    "blue means the hardship described there tends to sound more serious. A pillar groups "
    "several related themes together — for example, \"Livelihood Changes\" combines labour "
    "and income-related themes into one figure."
)


# Section 3: CSEL-derived risk scores, by district
st.subheader("3. CSEL-derived risk scores, by district")

rows = []
for _, r in stage3_ceri.iterrows():
    rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                 "Dimension": "CSEL_Hazard", "Score": r["CSEL_Hazard"], "Segments (n)": r["Hazard_segments (n)"]})
    rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                 "Dimension": "CSEL_Exposure", "Score": r["CSEL_Exposure"], "Segments (n)": r["Exposure_segments (n)"]})
    rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                 "Dimension": "CSEL_Vulnerability", "Score": r["CSEL_Vulnerability"], "Segments (n)": r["Vulnerability_segments (n)"]})
    rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                 "Dimension": "CSEL_Risk", "Score": r["CSEL_Risk"], "Segments (n)": None})
full_df = pd.DataFrame(rows)

full_df["facet_label"] = full_df["District"] + " (Interviews: " + full_df["Interviews (n)"].astype(str) + ")"
full_df["bar_text"] = full_df.apply(
    lambda r: f"{r['Score']}  (n={int(r['Segments (n)'])})" if pd.notna(r["Segments (n)"]) else f"{r['Score']} (derived, no direct n)",
    axis=1
)

DIMENSION_COLORS = {
    "CSEL_Hazard": "#4FD1C5",
    "CSEL_Exposure": "#F6AD55",
    "CSEL_Vulnerability": "#FC8181",
    "CSEL_Risk": "#B794F4",
}

fig3 = px.bar(
    full_df, x="Dimension", y="Score", color="Dimension",
    facet_col="facet_label", text="bar_text",
    color_discrete_map=DIMENSION_COLORS,
)
fig3.update_traces(
    textposition="outside",
    marker_line_color="rgba(255,255,255,0.25)",
    marker_line_width=1,
    textfont_size=13,
)
fig3.update_layout(
    paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
    font_color="#f0f0f0", font_family="Arial",
    showlegend=False, bargap=0.25,
    margin=dict(t=40, l=60, r=30, b=60),
)
fig3.update_yaxes(range=[0, 0.9], gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.2)")
fig3.update_xaxes(showgrid=False)
fig3.for_each_annotation(lambda a: a.update(text=a.text.split("=", 1)[-1], font=dict(size=15, color="#f0f0f0")))
st.plotly_chart(fig3, width="stretch")

with st.expander("See exact numbers"):
    st.dataframe(stage3_ceri, width="stretch")

st.caption(
    "Hazard, Exposure, and Vulnerability are each the average severity (0-1 scale) of "
    "everything said on that specific dimension, per district. Risk is Hazard × Exposure "
    "× Vulnerability multiplied together, not averaged — because real risk needs all three "
    "conditions present at once; a severe hazard nobody is exposed to isn't a big real risk. "
    "The \"(n)\" shown on each bar is how many individual quotes back that number — a score "
    "built from just a few quotes is far less certain than one built from many. This will sit "
    "side-by-side with CERI's own official scores once that comparison is finalized."
)
