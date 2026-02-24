import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load Data
# -----------------------
df = pd.read_csv("Tier1_clean.csv")  # Replace with your CSV path

# -----------------------
# Page Title and Description
# -----------------------
st.title("Rainfall-Driven Climate Hazard Index (1981–2025)")
st.subheader("Measuring Rainfall Instability and Extreme Climate Signals Across States and Districts")
st.write(
    "Tier-1 evaluates rainfall-related climate stress by comparing current rainfall patterns "
    "to long-term historical norms. It captures anomalies, extreme events, dry spells, wet spells, "
    "and intensity spikes to assess climate hazard levels."
)

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.title("Filters")

# State
states = st.sidebar.multiselect("Select State(s)", sorted(df["state"].unique()))

filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["state"].isin(states)]

# District
districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["district"].unique()))
if districts:
    filtered_df = filtered_df[filtered_df["district"].isin(districts)]

# Metric (grouping could be used later if needed)
metrics = ["Rainfall Metrics", "Extreme Event Indicators", "Core Hazard Indicator"]

# Indicator options
indicators = {
    "Hazard Score": {
        "column": "tier1_hazard",
        "chart_title": "Trend of Rainfall Hazard Score",
        "chart_desc": "The hazard score combines rainfall instability, extreme events, dry spells, wet spells, and intensity spikes into a single index (0–1). Higher values indicate increasing rainfall-related climate stress."
    },
    "Total Rainfall": {
        "column": "rainfall_mm",
        "chart_title": "Trend of Total Rainfall",
        "chart_desc": "Total rainfall reflects overall precipitation levels. However, total rainfall alone does not capture climate instability or extreme patterns."
    },
    "Rainfall Anomaly": {
        "column": "anomaly",
        "chart_title": "Trend of Rainfall Anomaly",
        "chart_desc": "Rainfall anomaly measures deviation from historical average rainfall. Larger deviations indicate increasing climate variability."
    },
    "Rainfall Anomaly Percentile": {
        "column": "H1",
        "chart_title": "Trend of Rainfall Anomaly Percentile",
        "chart_desc": "This indicator shows how unusual rainfall levels are compared to historical records. Higher percentiles indicate rarer and more extreme rainfall conditions."
    },
    "Rainfall Z-Score Percentile": {
        "column": "H2",
        "chart_title": "Trend of Rainfall Z-Score Percentile",
        "chart_desc": "The Z-score percentile captures statistical extremeness of rainfall events. Higher values indicate more statistically extreme conditions."
    },
    "Extreme Rainfall Days": {
        "column": "H3",
        "chart_title": "Trend of Extreme Rainfall Days",
        "chart_desc": "Counts the number of days exceeding the district-specific extreme rainfall threshold. More extreme days increase flood and landslide risk."
    },
    "Very Heavy Rainfall Days": {
        "column": "H4",
        "chart_title": "Trend of Very Heavy Rainfall Days",
        "chart_desc": "Measures the frequency of very heavy rainfall events. Higher values indicate greater short-term flood risk."
    },
    "Longest Dry Spell": {
        "column": "H5",
        "chart_title": "Trend of Longest Dry Spell",
        "chart_desc": "Indicates the longest stretch of minimal rainfall within a period. Longer dry spells signal drought-like stress conditions."
    },
    "Longest Wet Spell": {
        "column": "H6",
        "chart_title": "Trend of Longest Wet Spell",
        "chart_desc": "Measures consecutive days of sustained rainfall. Extended wet spells increase flood and landslide vulnerability."
    },
    "Peak Daily Rainfall Intensity": {
        "column": "H7",
        "chart_title": "Trend of Peak Daily Rainfall Intensity",
        "chart_desc": "Captures the highest single-day rainfall event within a period. High peak intensity reflects sudden shock-type rainfall events."
    }
}

# Indicator selection (default = Hazard Score)
indicator_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=list(indicators.keys()).index("Hazard Score")
)

indicator = indicators[indicator_name]

# -----------------------
# Line Chart
# -----------------------
st.subheader(indicator["chart_title"])

# Prepare trend data
trend_df = (
    filtered_df.groupby(["year", "district"])[indicator["column"]]
    .mean()
    .reset_index()
)

fig = px.line(
    trend_df,
    x="year",
    y=indicator["column"],
    color="district",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# Chart description
st.write(indicator["chart_desc"])
