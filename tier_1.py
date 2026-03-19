import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("SL_T1.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Remove extra spaces

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-1 :Rainfall-Driven Climate Hazard Index (2010-26)")
st.subheader("Measuring Rainfall Instability and Extreme Climate Signals Across States and Districts")
st.write(
    "Tier-1 evaluates rainfall-related climate hazard using district-level observations. It captures deviations from long-term rainfall patterns, extreme rainfall events, dry spells, wet spells, and peak daily intensity to assess overall hazard levels.")


# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.title("Filters")

# State
states = st.sidebar.multiselect("Select State(s)", sorted(df["State"].unique()))
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["State"].isin(states)]

# District
districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["District"].unique()))
if districts:
    filtered_df = filtered_df[filtered_df["District"].isin(districts)]

# -----------------------
# Metric mapping
# -----------------------
indicators = {
    "Annual Total Rainfall (mm)": {
                "column": "Annual Total Rainfall (mm)", # Example of a different column name
                "chart_title": "Trend of Annual Total Rainfall (mm)",
                "chart_desc": "Total rainfall reflects overall precipitation levels. However, total rainfall alone does not capture climate instability or extreme patterns."
            },
            "Annual Rainfall Anomaly (mm)": {
                "column": "Annual Rainfall Anomaly (mm)", # Example of a different column name
                "chart_title": "Trend of Annual Rainfall Anomaly",
                "chart_desc": "Rainfall anomaly measures deviation from historical average rainfall. Larger deviations indicate increasing climate variability."
            },

            "Extreme Rainfall Days (90th Percentile)": {
                "column": "Extreme Rainfall Days (90th Percentile)", # Example of a different column name
                "chart_title": "Trend of Extreme Rainfall Days",
                "chart_desc": "Represents the number of days on which rainfall exceeds the 90th percentile threshold. An increase in such days indicates a higher frequency of extreme rainfall events."
            },

            "Very Heavy Rainfall Days (>50mm)": {
                "column": "Very Heavy Rainfall Days (>50mm)", # Example of a different column name
                "chart_title": "Trend of Very Heavy Rainfall Days",
                "chart_desc": "Counts the number of days with rainfall exceeding 50 mm.Higher values reflect an increased occurrence of intense rainfall events."
            },

            "Longest Consecutive Dry Spell (days)": {
                "column": "Longest Consecutive Dry Spell (days)", # Example of a different column name
                "chart_title": "Trend of Longest Consecutive Dry Spell",
                "chart_desc": "Indicates the longest continuous period with minimal or no rainfall. Extended dry spells may signal increasing drought-like conditions.."
            },

            "Longest Consecutive Wet Spell (days)": {
                "column": "Longest Consecutive Wet Spell (days)", # Example of a different column name
                "chart_title": "Trend of Longest Consecutive Dry Spell",
                "chart_desc": "Measures the longest sequence of consecutive rainfall days. Prolonged wet periods may contribute to flooding and soil saturation."
            },

            
            "Maximum Daily Rainfall (mm)": {
                "column": "Maximum Daily Rainfall (mm)", # Example of a different column name
                "chart_title": "Trend of Maximum Daily Rainfall",
                "chart_desc": " Represents the highest recorded daily rainfall within a year. Higher values indicate more intense single-day rainfall events."
            },

            "Hazard Score": {
                "column": "Rainfall Hazard Index (Tier-1)", # Example of a different column name
                "chart_title": "Trend of Rainfall Hazard Score",
                "chart_desc": "The hazard score is a composite index that reflects the degree of rainfall variability and extremity within a district.Higher values indicate greater climate hazard associated with irregular rainfall patterns, extreme events and prolonged dry or wet conditions."
            }

    



    

    
}

# Default = Exposure Score
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=list(indicators.keys()).index("Hazard Score")
)

metric = indicators[metric_name]

# -----------------------
# Line chart
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    trend_df = (
        filtered_df.groupby(["Year", "District"])[metric["column"]]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x="Year",
        y=metric["column"],
        color="District",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])

