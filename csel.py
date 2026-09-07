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

# Drops whatever the tier pages left behind, so a question asked here is not
# answered from Tier 3's chart. Re-registered at the bottom of this script
# once the filtered aggregates exist.
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

st.caption(t("csel.section2_caption"))

# Section 3: CSEL-derived risk scores, by district
st.subheader(t("csel.section3_title"))

expanded_rows = []
for _, row in filtered.iterrows():
    codes = [c.strip() for c in str(row["Code"]).split(",")]
    tiers = [t_.strip() for t_ in str(row["CERI_Tier"]).split(";")] if isinstance(row["CERI_Tier"], str) else [row["CERI_Tier"]]
    for code, tier in zip(codes, tiers):
        expanded_rows.append({
            "Interview_ID": row["Interview_ID"], "District": row["District"],
            "CERI_Tier": tier, "severity_0to1": row["Severity (0–3)"] / 3,
        })
expanded_filtered = pd.DataFrame(expanded_rows)

def build_district_row(district_name, group):
    n_interviews = group["Interview_ID"].nunique()
    hazard = group[group["CERI_Tier"] == "Hazard"]["severity_0to1"]
    exposure = group[group["CERI_Tier"] == "Exposure"]["severity_0to1"]
    vulnerability = group[group["CERI_Tier"] == "Vulnerability"]["severity_0to1"]
    h = round(hazard.mean(), 2) if len(hazard) else None
    e = round(exposure.mean(), 2) if len(exposure) else None
    v = round(vulnerability.mean(), 2) if len(vulnerability) else None
    risk = round(h * e * v, 3) if (h is not None and e is not None and v is not None) else None
    return {"District": district_name, "Interviews (n)": n_interviews,
            "CSEL_Hazard": h, "Hazard_segments (n)": len(hazard),
            "CSEL_Exposure": e, "Exposure_segments (n)": len(exposure),
            "CSEL_Vulnerability": v, "Vulnerability_segments (n)": len(vulnerability),
            "CSEL_Risk": risk}

stage3_ceri_filtered = pd.DataFrame(
    [build_district_row(d, g) for d, g in expanded_filtered.groupby("District")]
    if not expanded_filtered.empty else []
)

if stage3_ceri_filtered.empty:
    st.info(t("csel.no_data"))
else:
    rows = []
    for _, r in stage3_ceri_filtered.iterrows():
        rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                     "Dimension": "CSEL_Hazard", "Score": r["CSEL_Hazard"], "Segments (n)": r["Hazard_segments (n)"]})
        rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                     "Dimension": "CSEL_Exposure", "Score": r["CSEL_Exposure"], "Segments (n)": r["Exposure_segments (n)"]})
        rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                     "Dimension": "CSEL_Vulnerability", "Score": r["CSEL_Vulnerability"], "Segments (n)": r["Vulnerability_segments (n)"]})
        rows.append({"District": r["District"], "Interviews (n)": r["Interviews (n)"],
                     "Dimension": "CSEL_Risk", "Score": r["CSEL_Risk"], "Segments (n)": None})
    full_df = pd.DataFrame(rows)

    full_df["facet_label"] = (
        full_df["District"] + " (" + t("csel.label_interviews") + ": "
        + full_df["Interviews (n)"].astype(str) + ")"
    )
    full_df["bar_text"] = full_df.apply(
        lambda r: f"{r['Score']}  (n={int(r['Segments (n)'])})" if pd.notna(r["Segments (n)"]) else f"{r['Score']} (derived, no direct n)",
        axis=1
    )

    DIMENSION_COLORS = {
        "CSEL_Hazard": "#4FD1C5", "CSEL_Exposure": "#F6AD55",
        "CSEL_Vulnerability": "#FC8181", "CSEL_Risk": "#B794F4",
    }

    fig3 = px.bar(
        full_df, x="Dimension", y="Score", color="Dimension",
        facet_col="facet_label", text="bar_text",
        color_discrete_map=DIMENSION_COLORS,
        labels={
            "Dimension": t("csel.label_dimension"),
            "Score": t("csel.label_score"),
        },
    )
    fig3.update_traces(textposition="outside", marker_line_color="rgba(255,255,255,0.25)",
                        marker_line_width=1, textfont_size=13)
    fig3.update_layout(
        paper_bgcolor="#0e0e0e", plot_bgcolor="#0e0e0e",
        font_color="#f0f0f0", font_family="Arial",
        legend=dict(font=dict(color="#f0f0f0")),
        showlegend=False, bargap=0.25,
        margin=dict(t=40, l=60, r=30, b=60),
    )
    fig3.update_yaxes(range=[0, 0.9], gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.2)")
    fig3.update_xaxes(showgrid=False)
    fig3.for_each_annotation(lambda a: a.update(text=a.text.split("=", 1)[-1], font=dict(size=15, color="#f0f0f0")))
    st.plotly_chart(fig3, width="stretch")

    with st.expander(t("csel.exact_numbers")):
        st.dataframe(stage3_ceri_filtered, width="stretch")

st.caption(t("csel.section3_caption"))


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
