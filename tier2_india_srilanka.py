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
    "India": "IND_T2.csv",
    
    "Sri Lanka": "SL_T2.csv"
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
        "header": "Tier-2 : India : Socio-Demographic Exposure Index (2015-21)",
        "subheader": " Understanding Population Vulnerability and Development Conditions Across Districts",
        "write": "Tier-2 evaluates socio-demographic exposure across districts using indicators from NFHS surveys. It captures population structure, health, nutrition, education, and access to basic services to assess where populations may be more exposed to climate and socio-economic risks. These indicators reflect underlying vulnerabilities that influence the ability of communities to withstand and recover from shocks.",
    },
    "Sri Lanka": {
        "header": "Tier-2 : Sri Lanka : Socio-Economic Exposure Index (2006-21)",
        "subheader": "Understanding Who Is Most Exposed to Rainfall-Related Climate Hazards",
        "write": "Tier-2 evaluates socio-economic exposure to climate-related hazards using district-level indicators. It captures population concentration, labour force participation, economic activity, and education levels to assess where climate shocks may have the greatest human impact."
        
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
        "Exposure Score": {
            "column": "Exposure Score",
            "chart_title": "Trend of Composite Socio-Demographic Exposure Score ",
            "chart_desc": "The composite exposure score ranges from 0 (lower exposure) to 1 (higher exposure). Higher values indicate districts where populations face greater socio-demographic vulnerabilities due to weaker health, education, and living conditions."
        },
        "ANC 4+ visits %": {
            "column": "ANC 4+ visits %",
            "chart_title": "Trend of Antenatal Care Coverage",
            "chart_desc": "Represents the percentage of mothers receiving at least four antenatal care visits. Higher values indicate better maternal healthcare access."
        },
        
        "Adequate child diet %": {
            "column": "Adequate child diet %",
            "chart_title": " Trend of Adequate Child Nutrition",
            "chart_desc": "Shows the proportion of children receiving an adequate diet. Lower values indicate higher nutritional vulnerability."
        },
        "Child anaemia %": {
            "column": "Child anaemia %",
            "chart_title": "Trend of Child Anaemia",
            "chart_desc": "Represents the percentage of children with anaemia. Higher values indicate poorer health conditions and increased vulnerability."
        },
        "Child stunting %": {
            "column": "Child stunting %",
            "chart_title": " Trend of Child Underweight",
            "chart_desc": "Indicates the proportion of underweight children, reflecting both acute and chronic malnutrition."
        },
        "Clean fuel %": {
            "column": "Clean fuel %",
            "chart_title": "Trend of Clean Cooking Fuel Usage",
            "chart_desc": "Shows household access to clean cooking fuel. Lower values indicate higher exposure to indoor pollution and health risks."
        },
        "Drinking water access %": {
            "column": "Drinking water access %",
            "chart_title": "Drinking water access %",
            "chart_desc": " Represents access to improved drinking water sources. Higher values indicate better basic infrastructure."
        },
        "Early marriage %": {
            "column": "Early marriage %",
            "chart_title": "Trend of Early Marriage",
            "chart_desc": "Indicates the proportion of women married before age 18. Higher values reflect social vulnerability and gender inequality."
        },
        "Electricity access %": {
            "column": "Electricity access %",
            "chart_title": "Trend of Electricity Access",
            "chart_desc": "Measures household access to electricity. Higher values indicate better living conditions and development."
        },
        "Institutional births %": {
            "column": "Institutional births %",
            "chart_title": "Trend of Institutional Births",
            "chart_desc": "Represents births occurring in healthcare facilities. Higher values indicate improved maternal healthcare systems."
        },
        "Population below 15 %": {
            "column": "Population below 15 %",
            "chart_title":"Trend of Young Population Share",
            "chart_desc": "Shows the proportion of population below age 15. Higher values indicate higher dependency ratios."
        },
        "Sanitation %": {
            "column": "Sanitation %",
            "chart_title": "Trend of Sanitation Access",
            "chart_desc": "Represents access to improved sanitation facilities. Higher values indicate better hygiene conditions."
        },
        "Sex ratio": {
            "column": "Sex ratio",
            "chart_title": "Trend of Sex Ratio",
            "chart_desc": "Shows the number of females per 1,000 males. Variations may reflect demographic imbalances."
        },
        "Teen pregnancy %": {
            "column": "Teen pregnancy %",
            "chart_title": "Trend of Teen Pregnancy",
            "chart_desc": "Indicates early motherhood among adolescents. Higher values suggest increased social and health risks."
        },
         "Women 10+ schooling %": {
            "column": "Women 10+ schooling %",
            "chart_title": "Trend of Female Education (10+ Years)",
            "chart_desc": "Represents women with at least 10 years of schooling. Higher values indicate better educational attainment."
        },
        "Women anaemia %": {
            "column": "Women anaemia %",
            "chart_title": "Trend of Women Anaemia",
            "chart_desc": "Indicates prevalence of anaemia among women. Higher values reflect poor nutritional and health status."
        },
        "Women literacy %": {
            "column": "Women literacy %",
            "chart_title": "Trend of Women Literacy",
            "chart_desc": "Represents literacy levels among women. Higher literacy supports awareness and resilience."
        },
        

        
        

        
    
    }
else:
    indicators = {
        "Exposure Score": {
                "column": "Exposure Score", # Example of a different column name
                "chart_title": "Trend of Composite Socio-Economic Exposure Score",
                "chart_desc": "The composite exposure score ranges from 0 (lowest exposure) to 1 (highest exposure). Higher values indicate districts where rainfall shocks would affect larger and more socio-economically vulnerable populations."
            },
        "Population Density": {
                "column": "Population_Density", # Example of a different column name
                "chart_title": "Trend of Population Density",
                "chart_desc": "Population density reflects the concentration of people within a given area. Higher density may increase the number of people exposed to climate hazards and amplify potential impacts."
            },
        "Labour Force Participation Rate – Male": {
                "column": "Labour Force Participation rate_M", # Example of a different column name
                "chart_title": "Trend of Male Labour Force Participation Rate",
                "chart_desc": "This indicator shows the proportion of the male population actively participating in the labour force. Variations may influence household income stability and resilience to climate-related disruptions."
            },
        "Labour Force Participation Rate – Female": {
                "column": "Labour Force Participation rate_F", # Example of a different column name
                "chart_title": "Trend of Female Labour Force Participation Rate",
                "chart_desc": "This indicator reflects the level of female participation in the labour force. Higher participation may indicate broader income sources, while lower participation may signal increased dependency."
            },
        "Economically Active Population – Male (%)": {
                "column": "Economically Active Population_M (%)", # Example of a different column name
                "chart_title": "Trend of Economically Active Male Population",
                "chart_desc": "Represents the share of the male population engaged in economic activities. Higher values indicate greater economic engagement, which may influence adaptive capacity."
            },
        "Economically Active Population – Female (%)": {
                "column": "Economically Active Population_F (%)", # Example of a different column name
                "chart_title": "Trend of Economically Active Female Population",
                "chart_desc": "This indicator reflects the proportion of the workforce dependent on agriculture. Districts with higher agricultural dependence are more sensitive to rainfall variability and extreme weather events."
            },
        "Literacy Rate – Female": {
                "column": "Literacy Rate_F", # Example of a different column name
                "chart_title": "Trend of Female Literacy Rate",
                "chart_desc": " Indicates the proportion of literate females within the population. Higher literacy supports informed decision-making and enhances resilience to climate risks."
            },
        "Literacy Rate – Male": {
                "column": "Literacy Rate_M", # Example of a different column name
                "chart_title": "Trend of Male Literacy Rate",
                "chart_desc": "Indicates the proportion of literate males within the population. Higher literacy levels are associated with improved access to information and adaptive capacity."
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
        <strong></strong>Values are derived from National Family Health Survey (NFHS) rounds NFHS-4 (2015–16) and NFHS-5 (2019–21). 
        NFHS-4 data was collected during 2015–2016 (report released in 2017), while NFHS-5 data was collected in two phases: June 2019–January 2020 and 
        January 2020–April 2021, with the second phase delayed due to COVID-19.To enable consistent temporal comparison, NFHS-4 values 
        are represented for the years 2015 and 2016, while NFHS-5 values are extended across 2019, 2020, and 2021.At present, 
        data integration is complete for the majority of states. Data for the following states is currently being processed and will be 
        incorporated in subsequent updates: Jharkhand, Uttar Pradesh, Punjab, Delhi, Odisha, Maharashtra, Madhya Pradesh. Exposure scores 
        are calculated using available data only.

        </div>
        """,
        unsafe_allow_html=True
    )

