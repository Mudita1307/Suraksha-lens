import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")

st.sidebar.title("Global Settings")
country = st.sidebar.selectbox("Select Country", ["India", "Sri Lanka"])

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
    df.columns = df.columns.str.strip()
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
content = {
    "India": {
        "header": "Tier-1 : India : Rainfall-Driven Climate Hazard Index (2010-25)",
        "subheader": "Measuring Rainfall Instability and Extreme Climate Signals Across States and Districts",
        "write": "Tier-1 evaluates rainfall-related climate hazard using district-level observations. It captures deviations from long-term rainfall patterns, extreme rainfall events, dry spells, wet spells, and peak daily intensity to assess overall hazard levels.",
    },
    "Sri Lanka": {
        "header": "Tier-1 : Sri Lanka : Rainfall-Driven Climate Hazard Index (2010-25)",
        "subheader": "Measuring Rainfall Instability and Extreme Climate Signals Across States and Districts",
        "write": " Tier-1 evaluates rainfall-related climate hazard using district-level observations. It captures deviations from long-term rainfall patterns, extreme rainfall events, dry spells, wet spells, and peak daily intensity to assess overall hazard levels",
        
    }
}

st.header(content[country]["header"])
st.subheader(content[country]["subheader"])
st.write(content[country]["write"]) 

# -----------------------
# Indicator Mapping
# -----------------------
if country == "India":
    indicators = {
        "Hazard Score": {
            "column": "Hazard Score",
            "chart_title": "Trend of Rainfall Hazard Score",
            "chart_desc": """The hazard score is a composite index that reflects the degree of rainfall variability and extremity within a district.
                             Higher values indicate greater climate hazard associated with irregular rainfall patterns, extreme events and prolonged 
                             dry or wet conditions."""
        },

        "Annual Total Rainfall (mm)": {
            "column": "Annual Total Rainfall (mm)",
            "chart_title": "Trend of Annual Total Rainfall (mm)",
            "chart_desc": "Total rainfall reflects overall precipitation levels. However, total rainfall alone does not capture climate instability or extreme patterns."
        },

        "Annual Rainfall Anomaly (mm)": {
            "column": "Annual Rainfall Anomaly (mm)",
            "chart_title": "Trend of Annual Rainfall Anomaly",
            "chart_desc": "Rainfall anomaly measures deviation from historical average rainfall. Larger deviations indicate increasing climate variability."
        },

        "Extreme Rainfall Days (90th Percentile)": {
            "column": "Extreme Rainfall Days (90th Percentile)",
            "chart_title": "Trend of Extreme Rainfall Days",
            "chart_desc": " Represents the number of days on which rainfall exceeds the 90th percentile threshold. An increase in such days indicates a higher frequency of extreme rainfall events."
        },
        "Very Heavy Rainfall Days (>50mm)": {
            "column": "Very Heavy Rainfall Days (>50mm)",
            "chart_title": "Trend of Very Heavy Rainfall Days",
            "chart_desc": " Counts the number of days with rainfall exceeding 50 mm.Higher values reflect an increased occurrence of intense rainfall events."
        },
        "Longest Consecutive Dry Spell (days)": {
            "column": "Longest Consecutive Dry Spell (days)",
            "chart_title": "Trend of Longest Consecutive Dry Spell",
            "chart_desc": "Indicates the longest continuous period with minimal or no rainfall. Extended dry spells may signal increasing drought-like conditions.."
        },


        "Longest Consecutive Wet Spell (days)": {
            "column": "Longest Consecutive Wet Spell (days)",
            "chart_title": "Trend of Longest Consecutive Wet Spell",
            "chart_desc": "Indicates the longest continuous period with minimal or no rainfall. Extended dry spells may signal increasing drought-like conditions.."
        },
        "Maximum Daily Rainfall (mm)": {
            "column": "Maximum Daily Rainfall (mm)",
            "chart_title": "Trend of Maximum Daily Rainfall",
            "chart_desc": "Represents the highest recorded daily rainfall within a year. Higher values indicate more intense single-day rainfall events"
        },

        
    
    }
else:
    indicators = {
        "Hazard Score": {
                "column": "Rainfall Hazard Index (Tier-1)", # Example of a different column name
                "chart_title": "Trend of Rainfall Hazard Score",
                "chart_desc": "The hazard score is a composite index that reflects the degree of rainfall variability and extremity within a district.Higher values indicate greater climate hazard associated with irregular rainfall patterns, extreme events and prolonged dry or wet conditions."
            },
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
            }

            
    }

# -----------------------
# Filters
# -----------------------
# -----------------------
# Reset Filters (FIXED)
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.states = []
    st.session_state.districts = []
    st.session_state.prev_country = country   # ❌ DO NOT reset metric

# -----------------------
# Filters
# -----------------------
st.sidebar.title("Filters")

filtered_df = df.copy()

state_label = "Select State" if country == "India" else "Select Province"

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
    "Select District",
    sorted(filtered_df[district_col].dropna().unique()),
    key="districts"
)

if districts:
    filtered_df = filtered_df[filtered_df[district_col].isin(districts)]

# -----------------------
# Indicator Selection (SAFE)
# -----------------------
indicator_options = list(indicators.keys())

# If session state is invalid → reset to first option
if "metric" not in st.session_state or st.session_state.metric not in indicator_options:
    st.session_state.metric = indicator_options[0]

metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=indicator_options,
    key="metric"
)

metric = indicators[metric_name]
# -----------------------
# Charting
# -----------------------
st.divider()
st.subheader(metric["chart_title"])

year_col = "year" if "year" in filtered_df.columns else "Year"

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    trend_df = (
        filtered_df.groupby([year_col, district_col])[metric["column"]]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x=year_col,
        y=metric["column"],
        color=district_col,
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])

if country == "India":
    st.markdown(
        """
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        <strong></strong>A value of 0 indicates no recorded rainfall, while missing values indicate absence of reliable data due to
        spatial mismatch between district boundaries and the rainfall grid. No artificial imputation has been applied.
        Data is unavailable for all years (2010–2025) in the following districts.  
          
        1.Andaman & Nicobar Islands (Nicobar Islands, North & Middle Andaman, South Andaman)  
        2.Lakshadweep  
        3.Chennai (Tamil Nadu)  

        </div>
        """,
        unsafe_allow_html=True
    )

