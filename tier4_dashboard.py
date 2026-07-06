import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import folium
from streamlit_folium import st_folium

from i18n import t, inject_font_css

# -----------------------
# Config
# -----------------------
st.set_page_config(
    page_title="Climate Hazard Index",
    layout="wide"
)
inject_font_css()

# -----------------------
# Country Selection
# -----------------------
COUNTRY_CODES = ["India", "Sri Lanka"]

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
    "India": "IND_T4.csv",
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
# Page Content
# -----------------------
st.header(t(f"tier4.content.{country}.header"))
st.subheader(t(f"tier4.content.{country}.subheader"))
st.write(t(f"tier4.content.{country}.write"))

# -----------------------
# Indicator Mapping (single set, shared across both countries)
# -----------------------
INDICATOR_COLUMNS = {
    "risk_score": "Risk Score",
    "risk_category": "Risk Category",
}

indicator_ids = list(INDICATOR_COLUMNS.keys())

def indicator_label(ind_id):
    return t(f"tier4.indicators.{ind_id}.label")

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.title(t("common.filters"))

filtered_df = df.copy()

# -----------------------
# State Filter
# -----------------------
state_label = t("common.select_state") if country == "India" else t("common.select_province")

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
    t("common.select_districts"),
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
metric_id = st.sidebar.selectbox(
    t("common.select_indicator"),
    options=indicator_ids,
    format_func=indicator_label,
)

metric_column = INDICATOR_COLUMNS[metric_id]
chart_title = t(f"tier4.indicators.{metric_id}.chart_title")
chart_desc = t(f"tier4.indicators.{metric_id}.chart_desc")

# =========================================================
# RISK CATEGORY
# INDIA  -> BAR CHART
# SRI LANKA -> MAP
# =========================================================
if metric_id == "risk_category":

    # =====================================================
    # INDIA → BAR CHART
    # =====================================================
    if country == "India":

        st.subheader(t("tier4.risk_distribution"))

        filtered_df = filtered_df.dropna(
            subset=["Year", metric_column]
        )

        fig = px.histogram(
            filtered_df,
            x="Year",
            color=metric_column,
            barmode="stack",

            color_discrete_map={
                "High Risk": "#FF0000",
                "Medium Risk": "#FFC107",
                "Low Risk": "#008000"
            },

            category_orders={
                metric_column: [
                    "Low Risk",
                    "Medium Risk",
                    "High Risk"
                ]
            },

            text_auto=True
        )

        fig.update_layout(
            yaxis_title=t("tier4.risk_axis"),
            xaxis_title=t("tier4.year_axis")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.write(chart_desc)

    # =====================================================
    # SRI LANKA → MAP
    # =====================================================
    else:

        st.subheader(t("tier4.risk_map"))

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
            t("common.select_year"),
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
        legend_html = f"""
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

        <b>{t("tier4.legend_title")}</b><br><br>

        <div>
            <span style="
                background:red;
                width:15px;
                height:15px;
                display:inline-block;
                margin-right:8px;">
            </span>
            {t("tier4.legend_high")}
        </div>

        <div>
            <span style="
                background:yellow;
                width:15px;
                height:15px;
                display:inline-block;
                margin-right:8px;">
            </span>
            {t("tier4.legend_medium")}
        </div>

        <div>
            <span style="
                background:green;
                width:15px;
                height:15px;
                display:inline-block;
                margin-right:8px;">
            </span>
            {t("tier4.legend_low")}
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

    st.subheader(chart_title)

    trend_df = (
        filtered_df.groupby(
            ["Year", "District"]
        )[metric_column]
        .mean()
        .reset_index()
    )

    trend_df["Year"] = pd.to_numeric(
        trend_df["Year"],
        errors="coerce"
    )

    trend_df[metric_column] = pd.to_numeric(
        trend_df[metric_column],
        errors="coerce"
    )

    trend_df = trend_df.dropna()

    # -----------------------------------
    # Line Chart
    # -----------------------------------
    fig = px.line(
        trend_df,
        x="Year",
        y=metric_column,
        color="District",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.write(chart_desc)