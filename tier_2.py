import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("SL_T2_new.csv", encoding="latin1")
df.columns = df.columns.str.strip()

# If state and district columns are swapped in the CSV


# -----------------------
# Page title
# -----------------------
st.header("Tier-4: Climate Exploitation Risk Index (CERI) (2020-21)")
st.subheader("Understanding Who Is Most Exposed to Rainfall-Related Climate Hazards")

st.write(
    "Tier-2 evaluates socio-economic exposure to climate-related hazards using district-level indicators."
    "It captures population concentration, labour force participation, economic activity, and education levels to assess where climate shocks may have the greatest human impact.")

# -----------------------
# Sidebar filters
# -----------------------
countries = st.sidebar.multiselect(
    "Select Country",
    sorted(df["Country"].dropna().unique())
)

filtered_df = df.copy()

if countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(countries)]

# -----------------------
# State filter
# -----------------------
states = st.sidebar.multiselect(
    "Select State(s)",
    sorted(filtered_df["State"].dropna().unique())
)

if states:
    filtered_df = filtered_df[filtered_df["state"].isin(states)]

# -----------------------
# District filter
# -----------------------
districts = st.sidebar.multiselect(
    "Select District(s)",
    sorted(filtered_df["District"].dropna().unique())
)

if districts:
    filtered_df = filtered_df[filtered_df["District"].isin(districts)]

# -----------------------
# Indicator dictionary
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

# -----------------------
# Indicator selection
# -----------------------
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=0
)

metric = indicators[metric_name]

# -----------------------
# Chart
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:

    st.error(f"Column '{metric['column']}' not found in data!")

else:

    trend_df = (
        filtered_df
        .groupby(["Year", "District"])[metric["column"]]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x="Year",
        y=metric["column"],
        color="district",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.write(metric["chart_desc"])


