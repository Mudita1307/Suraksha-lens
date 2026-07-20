import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import st_folium

from i18n import inject_sidebar_layout_fix, t, inject_font_css

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")
inject_font_css()
inject_sidebar_layout_fix()

COUNTRY_CODES = ["India", "Sri Lanka"]

if "country" not in st.session_state or st.session_state.country not in COUNTRY_CODES:
    st.session_state.country = COUNTRY_CODES[0]

country = st.sidebar.selectbox(
    t("common.select_country"),
    COUNTRY_CODES,
    format_func=lambda c: t("common.india") if c == "India" else t("common.sri_lanka"),
    key="country",
)

# -----------------------
# File Paths
# -----------------------
data_files = {
    "India": "IND_T1.csv",
    "Sri Lanka": "SL_T1.csv"
}

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding="latin1")
    print(df.columns)
    return df

df = load_data(data_files[country])

# -----------------------
# Reset Filters
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.State = []
    st.session_state.District = []
    st.session_state.metric = None
    st.session_state.prev_country = country

# -----------------------
# Dynamic Content (Header + Note)
# -----------------------
st.header(t(f"tier1.content.{country}.header"))
st.subheader(t(f"tier1.content.{country}.subheader"))
st.write(t(f"tier1.content.{country}.write"))

# -----------------------
# Indicator Column Mapping (technical - CSV column names, not translated)
# -----------------------
INDICATOR_COLUMNS = {
    "India": {
        "hazard_score": "Hazard Score",
        "annual_total_rainfall": "Annual Total Rainfall (mm)",
        "rainfall_anomaly": "Annual Rainfall Anomaly (mm)",
        "extreme_rainfall_days": "Extreme Rainfall Days (90th Percentile)",
        "very_heavy_rainfall_days": "Very Heavy Rainfall Days (>50mm)",
        "longest_dry_spell": "Longest Consecutive Dry Spell (days)",
        "longest_wet_spell": "Longest Consecutive Wet Spell (days)",
        "max_daily_rainfall": "Maximum Daily Rainfall (mm)",
    },
    "Sri Lanka": {
        "hazard_score": "Hazard Score",
        "annual_total_rainfall": "Annual Total Rainfall (mm)",
        "rainfall_anomaly": "Annual Rainfall Anomaly (mm)",
        "extreme_rainfall_days": "Extreme Rainfall Days (90th Percentile)",
        "very_heavy_rainfall_days": "Very Heavy Rainfall Days (>50mm)",
        "longest_dry_spell": "Longest Consecutive Dry Spell (days)",
        "longest_wet_spell": "Longest Consecutive Wet Spell (days)",
        "max_daily_rainfall": "Maximum Daily Rainfall (mm)",
    },
}

indicator_ids = list(INDICATOR_COLUMNS[country].keys())

def indicator_label(ind_id):
    return t(f"tier1.indicators.{country}.{ind_id}.label")

# -----------------------
# Filters
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.states = []
    st.session_state.districts = []
    st.session_state.prev_country = country   # ❌ DO NOT reset metric

st.sidebar.title(t("common.filters"))

filtered_df = df.copy()

state_label = t("common.select_state") if country == "India" else t("common.select_province")

# State filter (safe)
if "State" in df.columns:
    states = st.sidebar.multiselect(
        state_label,
        sorted(df["State"].dropna().unique()),
        key="states"
    )

    if states:
        filtered_df = filtered_df[filtered_df["State"].isin(states)]

# District filter
district_col = "District" if "District" in df.columns else "District"

districts = st.sidebar.multiselect(
    t("common.select_district"),
    sorted(filtered_df[district_col].dropna().unique()),
    key="districts"
)

if districts:
    filtered_df = filtered_df[filtered_df[district_col].isin(districts)]

# -----------------------
# Indicator Selection (SAFE)
# -----------------------
if "metric" not in st.session_state or st.session_state.metric not in indicator_ids:
    st.session_state.metric = indicator_ids[0]

metric_id = st.sidebar.selectbox(
    t("common.select_indicator"),
    options=indicator_ids,
    format_func=indicator_label,
    key="metric",
)

st.sidebar.markdown("<div style='height: 400px;'></div>", unsafe_allow_html=True)

metric_column = INDICATOR_COLUMNS[country][metric_id]
chart_title = t(f"tier1.indicators.{country}.{metric_id}.chart_title")
chart_desc = t(f"tier1.indicators.{country}.{metric_id}.chart_desc")

# -----------------------
# Charting
# -----------------------
st.divider()
st.subheader(chart_title)

year_col = "year" if "year" in filtered_df.columns else "Year"

if metric_column not in filtered_df.columns:
    st.error(t("common.column_not_found", column=metric_column))
else:
    trend_df = (
        filtered_df.groupby([year_col, district_col])[metric_column]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x=year_col,
        y=metric_column,
        color=district_col,
        markers=True
    )

    st.plotly_chart(fig, width="stretch")
    st.write(chart_desc)

if country == "India":
    st.markdown(
        f"""
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        {t("tier1.notes.india")}
        </div>
        """,
        unsafe_allow_html=True
    )
