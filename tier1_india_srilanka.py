import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Configuration & Country Switcher
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")

st.sidebar.title("Global Settings")
country = st.sidebar.selectbox("Select Country", ["India", "Sri Lanka"])

# Map countries to their respective files
data_files = {
    "India": "Tier1_clean.csv",
    "Sri Lanka": r"E:\SAICJS\python\SL_T1.csv"
}

# -----------------------
# Load Data (Cached)
# -----------------------
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding="latin1")
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"File '{file_path}' not found. Please ensure it is in the correct directory.")
        return None

df = load_data(data_files[country])

if df is not None:
    # -----------------------
    # Dynamic Metric Mapping
    # -----------------------
    # Define descriptions and column names for both countries
    if country == "India":
        indicators = {
    "Hazard Score": {
        "column": "Hazard Score",
        "chart_title": "Trend of Rainfall Hazard Score",
        "chart_desc": "The hazard score combines rainfall instability, extreme events, dry spells, wet spells, and intensity spikes into a single index (0–1).Higher values indicate increasing rainfall-related climate stress."

    },
    "Total Rainfall": {
        "column": "Total Rainfall",
        "chart_title":  "Trend of Total Rainfall",
        "chart_desc": "Total rainfall reflects overall precipitation levels. However, total rainfall alone does not capture climate instability or extreme patterns."
    },

    "Rainfall Anomaly": {
        "column": "Rainfall Anomaly",
        "chart_title": "Trend of Rainfall Anomaly Percentile ",
        "chart_desc": "This indicator shows how unusual rainfall levels are compared to historical records. Higher percentiles indicate rarer and more extreme rainfall conditions."

    },
    "Rainfall Anomaly Percentile": {
        "column": "Rainfall Anomaly Percentile",
        "chart_title": "Trend of Rainfall Anomaly Percentile ",
        "chart_desc": "Chart Description: This indicator shows how unusual rainfall levels are compared to historical records. Higher percentiles indicate rarer and more extreme rainfall conditions."

    },
  
    "Rainfall Z-Score Percentile": {
        "column": "Rainfall Z-Score Percentile",
        "chart_title":"Trend of Rainfall Z-Score Percentile",
        "chart_desc": "The Z-score percentile captures statistical extremeness of rainfall events. Higher values indicate more statistically extreme conditions."
    },



    "Extreme Rainfall Days": {
        "column": "Extreme Rainfall Days",
        "chart_title": "Trend of Extreme Rainfall Days",
        "chart_desc": "Counts the number of days exceeding the district-specific extreme rainfall threshold. More extreme days increase flood and landslide risk."

    },
    "Very Heavy Rainfall Days": {
        "column": "Very Heavy Rainfall Days",
        "chart_title": "Trend of Very Heavy Rainfall Days",
        "chart_desc": "Measures the frequency of very heavy rainfall events. Higher values indicate greater short-term flood risk."

    },
    "Longest Dry Spell": {
        "column": "Longest Dry Spell",
        "chart_title":"Trend of Longest Dry Spell",
        "chart_desc": "Indicates the longest stretch of minimal rainfall within a period. Longer dry spells signal drought-like stress conditions."
    },

    "Longest Wet Spell": {
        "column": "Longest Wet Spell",
        "chart_title": "Trend of Longest Wet Spell",
        "chart_desc": "Measures consecutive days of sustained rainfall. Extended wet spells increase flood and landslide vulnerability."

    },

    "Peak Daily Rainfall Intensity": {
        "column": "Peak Daily Rainfall Intensity",
        "chart_title": "Trend of Peak Daily Rainfall Intensity",
        "chart_desc": "Captures the highest single-day rainfall event within a period. High peak intensity reflects sudden shock-type rainfall events."


    },




            
            # Add other India-specific indicators here...
        }
    else:  # Sri Lanka
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






            # Add other Sri Lanka-specific indicators here...
        }

    # -----------------------
    # Page Header
    # -----------------------
    st.header(f"Tier-1 : {country} Rainfall-Driven Climate Hazard Index (1981–2025)")
    st.subheader("Measuring Rainfall Instability and Extreme Climate Signals")
    st.write(f"Currently viewing data for **{country}**. Tier-1 evaluates climate stress by comparing patterns to long-term historical norms.")

    # -----------------------
    # Sidebar Filters
    # -----------------------
    st.sidebar.title("Filters")
    
    # Dynamic labels based on country
    state_label = "Select Province" if country == "Sri Lanka" else "Select State"
    
    states = st.sidebar.multiselect(state_label, sorted(df["State"].unique()))
    filtered_df = df.copy()
    if states:
        filtered_df = filtered_df[filtered_df["State"].isin(states)]

    districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["District"].unique()))
    if districts:
        filtered_df = filtered_df[filtered_df["District"].isin(districts)]

    metric_name = st.sidebar.selectbox("Select Indicator", options=list(indicators.keys()))
    metric = indicators[metric_name]

    # -----------------------
    # Charting
    # -----------------------
    st.divider()
    st.subheader(metric["chart_title"])

    if metric["column"] not in filtered_df.columns:
        st.error(f"Column '{metric['column']}' not found in the {country} dataset!")
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
            markers=True,
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
        st.info(f"**Description:** {metric['chart_desc']}")

    
