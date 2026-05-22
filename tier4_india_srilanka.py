import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
# Config
# -----------------------
st.set_page_config(
    page_title="Climate Hazard Index",
    layout="wide"
)

# -----------------------
# Country Selection
# -----------------------
country = st.sidebar.selectbox(
    "Select Country",
    ["India", "Sri Lanka"]
)

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
    return df

df = load_data(data_files[country])

# -----------------------
# Session State Reset
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.states = []
    st.session_state.districts = []
    st.session_state.prev_country = country

# -----------------------
# Dynamic Content
# -----------------------
content = {
    "India": {
        "header": "tier-4 : India : Climate Exploitation Risk Index (CERI) (2020-21)",
        "subheader": "Identifying Priority Areas Facing Combined Climate and Social Risk",
        "write": """
Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability into a single composite index. 
It highlights areas where climate stress, population exposure, and protection risks overlap. 
Higher scores indicate a greater likelihood that climate-related stress may translate into increased risks affecting vulnerable populations.
"""
    },

    "Sri Lanka": {
        "header": "Tier-4 : Sri Lanka : Climate Exploitation Risk Index (CERI) (2020-21)",
        "subheader": "Identifying Priority Areas Facing Combined Climate and Social Risk",
        "write": """
Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability into a single composite index. 
It highlights areas where climate stress, population exposure, and protection risks overlap. 
Higher scores indicate a greater likelihood that climate-related stress may translate into increased risks affecting vulnerable populations.
"""
    }
}

# -----------------------
# Page Content
# -----------------------
st.header(content[country]["header"])
st.subheader(content[country]["subheader"])
st.write(content[country]["write"])

# -----------------------
# Indicator Mapping
# -----------------------
indicators = {

    "Risk Score": {
        "column": "Risk Score",

        "chart_title": "Trend of Composite Socio-Economic Exposure Score",

        "chart_desc": """
The risk score integrates hazard, exposure, and vulnerability into a single composite index (0–1). 
Higher values indicate greater overall climate-linked multi-risk.
"""
    },

    "Risk Category": {
        "column": "Risk Category",

        "chart_title": "Risk Category Classification",

        "chart_desc": """
Districts are classified into Low, Medium, or High Risk categories based on the composite index.

High Risk: Districts with a risk score greater than or equal to 0.67

Medium Risk: Districts with a risk score between 0.34 and 0.66

Low Risk: Districts with a risk score below 0.34

High-risk districts represent priority areas for targeted intervention.
"""
    }
}

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.title("Filters")

filtered_df = df.copy()

# -----------------------
# State Filter
# -----------------------
state_label = (
    "Select State"
    if country == "India"
    else "Select Province"
)

if "State" in df.columns:

    states = st.sidebar.multiselect(
        state_label,
        sorted(df["State"].dropna().unique()),
        key="states"
    )

    if states:
        filtered_df = filtered_df[
            filtered_df["State"].isin(states)
        ]

else:
    states = []

# -----------------------
# District Filter
# -----------------------
districts = st.sidebar.multiselect(
    "Select District(s)",
    sorted(filtered_df["District"].dropna().unique()),
    key="districts"
)

if districts:
    filtered_df = filtered_df[
        filtered_df["District"].isin(districts)
    ]

# -----------------------
# Indicator Selection
# -----------------------
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys())
)

metric = indicators[metric_name]

# =========================================================
# RISK CATEGORY → BAR CHART
# =========================================================
# =========================================================
# RISK CATEGORY
# INDIA  -> BAR CHART
# SRI LANKA -> MAP
# =========================================================
# =========================================================
# VISUALIZATION
# =========================================================

# =========================================================
# RISK CATEGORY
# INDIA  -> BAR CHART
# SRI LANKA -> MAP
# =========================================================
# =========================================================
if metric_name == "Risk Category":

    # =====================================================
    # INDIA → BAR CHART
    # =====================================================
    if country == "India":

        st.subheader("Risk Category Distribution")

        filtered_df = filtered_df.dropna(
            subset=["Year", metric["column"]]
        )

        fig = px.histogram(
            filtered_df,
            x="Year",
            color=metric["column"],
            barmode="stack",

            color_discrete_map={
                "High Risk": "#FF0000",
                "Medium Risk": "#FFC107",
                "Low Risk": "#008000"
            },

            category_orders={
                metric["column"]: [
                    "Low Risk",
                    "Medium Risk",
                    "High Risk"
                ]
            },

            text_auto=True
        )

        fig.update_layout(
            yaxis_title="Number of Districts",
            xaxis_title="Year"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.write(metric["chart_desc"])

    # =====================================================
    # SRI LANKA → MAP
    # =====================================================
    else:

        st.subheader("Risk Category Map")

        # -----------------------------------
        # Load shapefile + CSV
        # -----------------------------------
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
        # Year Filter
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
            zoom_control=False,
            scrollWheelZoom=False,
            dragging=False,
            doubleClickZoom=False,
            touchZoom=False
        )

         # Transparent background
        transparent_css = """
                     <style>
                    .leaflet-container {
                    background: transparent !important;
                        }
                    </style>
                    """

        m.get_root().header.add_child(
                   folium.Element(transparent_css))


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
        # Legend
        # -----------------------------------
        legend_html = """
        <div style="
            position: fixed;
            bottom: 50px;
            left: 50px;
            width: 140px;
            height: 120px;
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

        m.get_root().html.add_child(
            folium.Element(legend_html)
        )

        # -----------------------------------
        # Add Layer
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

        st_folium(
            m,
            width=550,
            height=600
        )

# =========================================================
# RISK SCORE → LINE GRAPH
# =========================================================
else:

    st.subheader(metric["chart_title"])

    trend_df = (
        filtered_df.groupby(
            ["Year", "District"]
        )[metric["column"]]
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

    # -----------------------------------
    # Line Chart
    # -----------------------------------
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
