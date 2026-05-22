import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")

#st.sidebar.title("Global Settings")
country = st.sidebar.selectbox("Select Country", ["India", "Sri Lanka"])

# -----------------------
# File Paths
# -----------------------



data_files = {
    "India":"IND_T4.csv",
    "Sri Lanka": "SL_T4.csv"
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

# =========================================================
# RISK CATEGORY → MAP
# =========================================================
if metric_name == "Risk Category":

    st.subheader("Risk Category Map")

    # -----------------------------------
    # Load shapefile + CSV
    # -----------------------------------
    if country == "Sri Lanka":

        gdf = gpd.read_file(
            "gadm41_LKA_1.geojson"
        )

        gdf = gdf.rename(columns={
            "NAME_1": "District"
        })

        map_df = pd.read_csv(
            "SL_T4.csv"
        )

        map_location = [7.8, 80.7]
        zoom_level = 7

    else:

        gdf = gpd.read_file(
            "gadm41_IND_1.geojson"
        )

        gdf = gdf.rename(columns={
            "NAME_2": "District"
        })

        map_df = pd.read_csv(
            "IND_T4.csv"
        )

        map_location = [23.5937, 80.9629]
        zoom_level = 5

    # -----------------------------------
    # Clean names
    # -----------------------------------
    gdf["District"] = (
        gdf["District"]
        .str.upper()
        .str.strip()
    )

    map_df["District"] = (
        map_df["District"]
        .str.upper()
        .str.strip()
    )

    # -----------------------------------
    # Year filter
    # -----------------------------------
    year = st.sidebar.selectbox(
        "Select Year",
        sorted(map_df["Year"].unique())
    )

    df_year = map_df[
        map_df["Year"] == year
    ]

    # -----------------------------------
    # Merge
    # -----------------------------------
    gdf_year = gdf.merge(
        df_year,
        on="District",
        how="left"
    )

    # -----------------------------------
    # Create map
    # -----------------------------------
    m = folium.Map(
        location=map_location,
    zoom_start=zoom_level,
    tiles=None,
    zoom_control=False,      # removes + / - buttons
    scrollWheelZoom=False,   # disable mouse wheel zoom
    dragging=False,          # disable map dragging
    doubleClickZoom=False,   # disable double click zoom
    touchZoom=False          # disable touch zoom

    )
    transparent_css = """
<style>
.leaflet-container {
    background: transparent !important;
}
</style>
"""

m.get_root().header.add_child(
    folium.Element(transparent_css)
)

    # -----------------------------------
    # Color function
    # -----------------------------------
    def get_color(value):

        if pd.isna(value):
            return "gray"

        elif value == "High Risk":
            return "red"

        elif value == "Medium Risk":
            return "yellow"

        elif value == "Low Risk":
            return "green"

        else:
            return "gray"

    # -----------------------------------

    legend_html = """
<div style="
    position: fixed;
    bottom: 50px;
    left: 50px;
    width: 180px;
    height: 140px;
    z-index:9999;
    background-color: white;
    border:2px solid grey;
    border-radius:6px;
    padding: 10px;
    font-size:14px;">

<b>Risk Category</b><br><br>

<div>
    <span style="
        background:red;
        width:15px;
        height:15px;
        display:inline-block;
        margin-right:8px;">
    </span>
    High Risk
</div>

<div>
    <span style="
        background:yellow;
        width:15px;
        height:15px;
        display:inline-block;
        margin-right:8px;">
    </span>
    Medium Risk
</div>

<div>
    <span style="
        background:green;
        width:15px;
        height:15px;
        display:inline-block;
        margin-right:8px;">
    </span>
    Low Risk
</div>



</div>
"""

# Add legend to map
    m.get_root().html.add_child(folium.Element(legend_html))

    # Add layer
    # -----------------------------------
    folium.GeoJson(

        gdf_year,

        style_function=lambda feature: {
            "fillColor": get_color(
                feature["properties"]["Risk Category"]
            ),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7,
        },

        tooltip=folium.GeoJsonTooltip(
            fields=["District", "Risk Category"],
            aliases=["District:", "Risk Category:"]
        )

    ).add_to(m)
    

    st_folium(m, width=800, height=900)

# =========================================================
# RISK SCORE → LINE GRAPH
# =========================================================
else:

    st.subheader(metric["chart_title"])

    trend_df = (
        filtered_df.groupby(["Year", "District"])[metric["column"]]
        .mean()
        .reset_index()
    )

    trend_df["Year"] = pd.to_numeric(
        trend_df["Year"],
        errors="coerce"
    )

    trend_df[metric["column"]] = pd.to_numeric(
        trend_df[metric["column"]],
        errors="coerce"
    )

    trend_df = trend_df.dropna()

    fig = px.line(
        trend_df,
        x="Year",
        y=metric["column"],
        color="District",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

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

st.write("")




