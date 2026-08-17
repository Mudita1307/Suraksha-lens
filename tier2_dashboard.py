import streamlit as st
import pandas as pd
import plotly.express as px

from i18n import inject_sidebar_layout_fix, t, inject_font_css

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")
inject_font_css()
inject_sidebar_layout_fix()

st.session_state["_current_page"] = "tier2_dashboard"
st.session_state["tier"] = "T2"
st.session_state["dashboard_chart_data"] = None

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
    "India": "IND_T2.csv",
    "Sri Lanka": "SL_T2.csv"
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
st.header(t(f"tier2.content.{country}.header"))
st.subheader(t(f"tier2.content.{country}.subheader"))
st.write(t(f"tier2.content.{country}.write"))

# -----------------------
# Indicator Column Mapping (technical - CSV column names, not translated)
# -----------------------
INDICATOR_COLUMNS = {
    "India": {
        "exposure_score": "Exposure Score",
        "anc_visits": "ANC 4+ visits %",
        "child_diet": "Adequate child diet %",
        "child_anaemia": "Child anaemia %",
        "child_stunting": "Child stunting %",
        "clean_fuel": "Clean fuel %",
        "drinking_water": "Drinking water access %",
        "early_marriage": "Early marriage %",
        "electricity_access": "Electricity access %",
        "institutional_births": "Institutional births %",
        "population_below_15": "Population below 15 %",
        "sanitation": "Sanitation %",
        "sex_ratio": "Sex ratio",
        "teen_pregnancy": "Teen pregnancy %",
        "women_schooling": "Women 10+ schooling %",
        "women_anaemia": "Women anaemia %",
        "women_literacy": "Women literacy %",
    },
    "Sri Lanka": {
        "exposure_score": "Exposure Score",
        "population_density": "Population_Density",
        "lfpr_male": "Labour Force Participation rate_M",
        "lfpr_female": "Labour Force Participation rate_F",
        "econ_active_male": "Economically Active Population_M (%)",
        "econ_active_female": "Economically Active Population_F (%)",
        "literacy_female": "Literacy Rate_F",
        "literacy_male": "Literacy Rate_M",
    },
}

indicator_ids = list(INDICATOR_COLUMNS[country].keys())

def indicator_label(ind_id):
    return t(f"tier2.indicators.{country}.{ind_id}.label")

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
    t("common.select_districts"),
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
    key="metric"
)

st.sidebar.markdown("<div style='height: 400px;'></div>", unsafe_allow_html=True)

metric_column = INDICATOR_COLUMNS[country][metric_id]
chart_title = t(f"tier2.indicators.{country}.{metric_id}.chart_title")
chart_desc = t(f"tier2.indicators.{country}.{metric_id}.chart_desc")

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
    st.session_state["dashboard_chart_data"] = {
    "chart_type": "line",
    "year_column": year_col,
    "category_column": district_col,
    "value_column": metric_column,
    "metric": metric_id,
    "data": trend_df.to_dict(orient="records"),
}

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
        {t("tier2.notes.india")}
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        {t("tier2.notes.sri_lanka")}
        </div>
        """,
        unsafe_allow_html=True
    )