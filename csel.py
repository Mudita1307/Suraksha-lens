import streamlit as st
import pandas as pd
import plotly.express as px

import chat_bot
from i18n import inject_sidebar_layout_fix, inject_font_css, t

st.set_page_config(page_title="CSEL", layout="wide")
inject_font_css()
inject_sidebar_layout_fix()

st.session_state["_current_page"] = "csel"
st.session_state["tier"] = "CSEL"

chat_bot.clear_chart_context()

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
st.header(t("csel.header"))
st.subheader(t("csel.subheader"))
st.write(t("csel.intro"))

# Sidebar
st.sidebar.title(t("csel.filters_title"))

district_choice = st.sidebar.multiselect(
    t("csel.select_district"),
    sorted(stage2["District"].unique().tolist()),
)
theme_choice = st.sidebar.multiselect(
    t("csel.select_theme"),
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
    {t("csel.sample_notice", interviews=stage2['Interview_ID'].nunique(), segments=len(stage2))}
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()

# Section 1: Theme frequency (lollipop chart)
st.subheader(t("csel.section1_title"))

theme_freq_filtered = filtered["Code"].value_counts().reset_index()
theme_freq_filtered.columns = ["Code", "Mentions"]
theme_freq_filtered = theme_freq_filtered.merge(
    stage2[["Code", "CSEL_Pillar"]].drop_duplicates(), on="Code", how="left"
).sort_values("Mentions")

fig1 = px.scatter(
    theme_freq_filtered, x="Mentions", y="Code", size="Mentions", color="CSEL_Pillar",
    size_max=22,
    labels={
        "Mentions": t("csel.label_mentions"),
        "Code": t("csel.label_theme"),
        "CSEL_Pillar": t("csel.label_pillar"),
    },
)
for _, row in theme_freq_filtered.iterrows():
    fig1.add_shape(
        type="line", x0=0, x1=row["Mentions"], y0=row["Code"], y1=row["Code"],
        line=dict(color="rgba(255,255,255,0.25)", width=2),
    )
fig1.update_layout(
    paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e", font_color="#f0f0f0",
    legend=dict(font=dict(color="#f0f0f0"), title=dict(font=dict(color="#f0f0f0"))),
    margin=dict(t=20, l=10, r=10, b=40),
)
fig1.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
fig1.update_yaxes(showgrid=False)
st.plotly_chart(fig1, width="stretch")
st.caption(t("csel.section1_caption"))


# Section 2: District x Pillar severity (sunburst)

st.subheader(t("csel.section2_title"))

pillar_severity_filtered = (
    filtered.groupby(["District", "CSEL_Pillar"])["Severity (0–3)"]
    .mean().round(2).reset_index()
)

if pillar_severity_filtered.empty:
    st.info(t("csel.no_data"))
else:
    fig2 = px.sunburst(
        pillar_severity_filtered, path=["District", "CSEL_Pillar"], values="Severity (0–3)",
        color="Severity (0–3)", color_continuous_scale="Blues",
        labels={
            "District": t("csel.label_district"),
            "CSEL_Pillar": t("csel.label_pillar"),
            "Severity (0–3)": t("csel.label_severity"),
        },
    )
    fig2.update_layout(
        paper_bgcolor="black", plot_bgcolor="black", font_color="white",
        legend=dict(font=dict(color="#f0f0f0")),
        margin=dict(t=20, l=10, r=10, b=10),
    )
    st.plotly_chart(fig2, width="stretch")
    pillar_code_table = (
        filtered[["CSEL_Pillar", "Code"]].drop_duplicates()
        .groupby("CSEL_Pillar")["Code"].apply(lambda c: ", ".join(sorted(c)))
        .reset_index().rename(columns={"CSEL_Pillar": "CSEL Pillar", "Code": "CSEL Codes included"})
    )
    st.dataframe(pillar_code_table, width="stretch", hide_index=True)

st.caption(t("csel.section2_caption"))

# Section 3: What are people actually saying?
st.subheader("3. What are people actually saying?")
st.caption(
    "Real testimony behind the numbers above, the colored bar shows how severe each quote sounds."
)

SEVERITY_COLOR = {0: "#4A5568", 1: "#48BB78", 2: "#ED8936", 3: "#F56565"}  # gray, green, orange, red
SEVERITY_LABEL = {0: "Barely present", 1: "Neutral mention", 2: "Concern", 3: "Severe/urgent"}

quotes_to_show = filtered.sort_values("Severity (0–3)", ascending=False)

st.write(f"**{len(quotes_to_show)}** matching quote(s)")

for _, row in quotes_to_show.iterrows():
    color = SEVERITY_COLOR[row["Severity (0–3)"]]
    label = SEVERITY_LABEL[row["Severity (0–3)"]]
    st.markdown(
        f"""
        <div style="
            border-left: 5px solid {color};
            background-color: #1a1a1a;
            padding: 14px 18px;
            border-radius: 6px;
            margin-bottom: 14px;
        ">
            <div style="color: #a0a0a0; font-size: 13px; margin-bottom: 6px;">
                {row['District']} &nbsp;·&nbsp; {row['Code']} &nbsp;·&nbsp;
                <span style="color: {color}; font-weight: 600;">{label}</span>
            </div>
            <div style="color: #f0f0f0; font-size: 15px; font-style: italic;">
                "{row['Quote (translated)']}"
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )



# -----------------------------------------------------------------------
# Assistant context
# -----------------------------------------------------------------------
# Registered last so it describes the figures actually on screen, after the
# sidebar filters have been applied. Aggregates only: the underlying rows are
# verbatim interview testimony about violence against women and children, with
# named speakers, and the snapshot is sent to a third-party model every turn.

st.session_state["_active_filters"] = {
    "districts_selected": district_choice or "all",
    "themes_selected": theme_choice or "all",
}

st.session_state["_visible_summary_stats"] = {
    "interviews_in_dataset": int(stage2["Interview_ID"].nunique()),
    "segments_in_dataset": int(len(stage2)),
    "segments_after_filters": int(len(filtered)),
    "districts_covered": sorted(stage2["District"].unique().tolist()),
}

chat_bot.set_dataset_context(
    title=t("csel.header"),
    summary=(
        "CSEL (Community Safety Evidence Layers) is the qualitative layer of "
        "Suraksha Lens. Trained Community Safety Evidence Leaders interview "
        "people locally; each interview is split into segments, and every "
        "segment is human-verified and tagged with a theme from the CSEL "
        "codebook, a broader CSEL_Pillar, a CERI_Tier (Hazard, Exposure or "
        "Vulnerability) and a severity from 0 (barely present) to 3 "
        "(severe/urgent). Unlike tiers 1-4, which come from statistical "
        "datasets, every number here is derived from what people said. "
        "Mentions count how often a theme came up in conversation and are not "
        "a severity measure. The district-level CSEL_Hazard, CSEL_Exposure and "
        "CSEL_Vulnerability scores are mean segment severity rescaled to 0-1 "
        "for that CERI tier, and CSEL_Risk is the three multiplied together "
        "rather than averaged, because real risk needs all three present at "
        "once."
    ),
    charts=[
        {
            "title": t("csel.section1_title"),
            "kind": "lollipop / scatter",
            "shows": "how many interview segments mentioned each codebook "
                     "theme, coloured by pillar (see the theme_mentions table)",
        },
        {
            "title": t("csel.section2_title"),
            "kind": "sunburst",
            "shows": "mean severity (0-3) per district per pillar, darker "
                     "meaning more serious (see the pillar_severity_by_district "
                     "table)",
        },
        {
            "title": t("csel.section3_title"),
            "kind": "faceted bar",
            "shows": "CSEL_Hazard, CSEL_Exposure, CSEL_Vulnerability and the "
                     "derived CSEL_Risk per district on a 0-1 scale, with the "
                     "number of backing segments (see the district_scores table)",
        },
    ],
    tables={
        "theme_mentions": theme_freq_filtered[
            ["Code", "Mentions", "CSEL_Pillar"]
        ].to_dict(orient="records"),
        "pillar_severity_by_district": pillar_severity_filtered.to_dict(
            orient="records"
        ),
        "district_scores": (
            stage3_ceri_filtered.where(pd.notna(stage3_ceri_filtered), None)
            .to_dict(orient="records")
            if not stage3_ceri_filtered.empty
            else []
        ),
    },
    caveat=(
        f"Very small sample: {stage2['Interview_ID'].nunique()} interviews and "
        f"{len(stage2)} verified segments in total, covering only "
        f"{', '.join(sorted(stage2['District'].unique().tolist()))}. "
        f"{len(filtered)} segments match the current filters. Any single "
        "district or single interview figure is early signal, not a confirmed "
        "pattern, and a score backed by only a handful of segments is far less "
        "certain than one backed by many. Say this plainly whenever an answer "
        "would otherwise imply the numbers are representative. The assistant "
        "receives aggregates only and cannot quote the interview testimony "
        "itself."
    ),
)
