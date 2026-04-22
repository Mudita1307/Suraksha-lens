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
    "India":"IND_T4_new.csv",
    "Sri Lanka": "SL_T4.csv"
}


# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding="latin1")
    #df.columns = df.columns.str.strip()
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
        "header": "Tier-4 : India : Climate Exploitation Risk Index (CERI) (2020-21) ",
        "subheader": "Identifying Priority Areas Facing Combined Climate and Social Risk",
        "write": "Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability into a single composite index. It highlights areas where climate stress, population exposure, and protection risks overlap. Higher scores indicate a greater likelihood that climate-related stress may translate into increased risks affecting vulnerable populations.",
    },
    "Sri Lanka": {
        "header": "Tier-4 : Sri Lanka : Climate Exploitation Risk Index (CERI) (2020-21)",
        "subheader": "Identifying Priority Areas Facing Combined Climate and Social Risk",
        "write": "Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability into a single composite index. It highlights areas where climate stress, population exposure, and protection risks overlap. Higher scores indicate a greater likelihood that climate-related stress may translate into increased risks affecting vulnerable populations."
        
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
        "Risk Score": {
            "column": "Risk Score",
            "chart_title": "Trend of Composite Socio-Economic Exposure Score",
            "chart_desc": "The risk score integrates hazard, exposure, and vulnerability into a single composite index (0–1). Higher values indicate greater overall climate-linked multi-risk."
        },
        "Risk Category": {
            "column": "Risk Category",
            "chart_title": "Risk Category Classification",
            "chart_desc": """Districts are classified into Low, Medium, or High Risk categories based on the composite index. 

High Risk: Districts with a risk score greater than or equal to 0.67 

Medium Risk: Districts with a risk score between 0.34 and 0.66 

Low Risk: Districts with a risk score below 0.34  

High-risk districts represent priority areas for targeted intervention.
"""
        },
           
    
    }
else:
    indicators = {
    "Risk Score": {
            "column": "Risk Score",
            "chart_title": "Trend of Composite Socio-Economic Exposure Score",
            "chart_desc": "The risk score integrates hazard, exposure, and vulnerability into a single composite index (0–1). Higher values indicate greater overall climate-linked multi-risk."
        },
    "Risk Category": {
            "column": "Risk Category",
            "chart_title": "Risk Category Classification",
            "chart_desc": """Districts are classified into Low, Medium, or High Risk categories based on the composite index. 

High Risk: Districts with a risk score greater than or equal to 0.67 

Medium Risk: Districts with a risk score between 0.34 and 0.66 

Low Risk: Districts with a risk score below 0.34  

High-risk districts represent priority areas for targeted intervention.
"""
},
           
    
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
    "Select District(s)",
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
    options=list(indicators.keys()),
    index=0
)

# ✅ Define metric
metric = indicators[metric_name]

# -----------------------
# Visualization
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")

else:
    # -----------------------
    # Risk Category (Stacked Bar)
    # -----------------------
    if metric_name == "Risk Category":

        filtered_df = filtered_df.dropna(subset=["Year", metric["column"]])

        fig = px.histogram(
            filtered_df,
            x="Year",
            color=metric["column"],
            barmode="stack",
            color_discrete_map={
                "High Risk": "#FF0000",     # Red
                "Medium Risk": "#FFC107",   # Yellow (better visibility)
                "Low Risk": "#008000"       # Green
            },
            category_orders={metric["column"]: ["Low Risk", "Medium Risk", "High Risk"]},
            text_auto=True
        )

        fig.update_layout(
            yaxis_title="Number of Districts",
            xaxis_title="Year"
        )

    # -----------------------
    # Risk Score (Line Chart)
    # -----------------------
    else:
        trend_df = (
            filtered_df.groupby(["Year", "District"])[metric["column"]]
            .mean()
            .reset_index()
        )

        # Clean data
        trend_df["Year"] = pd.to_numeric(trend_df["Year"], errors="coerce")
        trend_df[metric["column"]] = pd.to_numeric(trend_df[metric["column"]], errors="coerce")

        trend_df = trend_df.dropna()

        if trend_df.empty:
            st.warning("No data available after filtering.")
        else:
            fig = px.line(
                trend_df,
                x="Year",
                y=metric["column"],
                color="District",
                markers=True
            )

    # -----------------------
    # Plot
    # -----------------------
    if 'fig' in locals():
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------
    # Description (Plain Text)
    # -----------------------
    st.write(metric["chart_desc"])
if country == "India":
    st.markdown(
        """
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        <strong></strong>Risk Scores are calculated by combining Hazard (Tier 1), Exposure (Tier 2), Vulnerability (Tier 3) scores at the district level for the common
        time period (2020–2021). Scores are computed using all available data. Where one or more scores are unavailable for a district, the Risk Score is calculated 
        using the remaining available scores. No assumptions or artificial imputation have been applied. Districts with no available scores across all three components 
        are excluded from the analysis.

        </div>
        """,
        unsafe_allow_html=True
    )
