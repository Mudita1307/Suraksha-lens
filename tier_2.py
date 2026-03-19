import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("SL_T2_new.csv",  encoding="latin1")
df.columns = df.columns.str.strip()


# If state and district columns are swapped in the CSV


# -----------------------
# Page title
# -----------------------
st.header("Tier-2: Socio-Economic Exposure Index (2006-21)")
st.subheader("Understanding Who Is Most Exposed to Rainfall-Related Climate Hazards")

st.write(
    "Tier-2 evaluates socio-economic exposure to climate-related hazards using district-level indicators."
    "It captures population concentration, labour force participation, economic activity, and education levels to assess where climate shocks may have the greatest human impact.")

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
# Indicator dictionary
# -----------------------
indicators = {

    "Exposure Score": {
        "column": "T",
        "chart_title": "rend of Composite Socio-Economic Exposure Score",
        "chart_desc": "The composite exposure score ranges from 0 (lowest exposure) to 1 (highest exposure). Higher values indicate districts where rainfall shocks would affect larger and more socio-economically vulnerable populations."

    },
    
    "Population Density": {
        "column": "Population_Density",
        "chart_title": "Trend of Population Density",
        "chart_desc": " Population density reflects the concentration of people within a given area. Higher density may increase the number of people exposed to climate hazards and amplify potential impacts."

    },

    "Labour Force Participation Rate – Male": {
        "column": "Labour Force Participation rate_M",
        "chart_title": "Trend of Male Labour Force Participation Rate",
        "chart_desc": "This indicator shows the proportion of the male population actively participating in the labour force. Variations may influence household income stability and resilience to climate-related disruptions."

    },
    "Labour Force Participation Rate – Female": {
        "column": "Labour Force Participation rate_F",
        "chart_title": "Trend of Female Labour Force Participation Rate",
        "chart_desc": "This indicator reflects the level of female participation in the labour force. Higher participation may indicate broader income sources, while lower participation may signal increased dependency."

    },

    "Economically Active Population – Male (%)": {
        "column": "Economically Active Population_M (%)",
        "chart_title": "Trend of Economically Active Male Population",
        "chart_desc": " Represents the share of the male population engaged in economic activities. Higher values indicate greater economic engagement, which may influence adaptive capacity."

    },

    "Economically Active Population – Female (%)": {
        "column": "Economically Active Population_F (%)",
        "chart_title": "Trend of Economically Active Female Population",
        "chart_desc": "This indicator reflects the proportion of the workforce dependent on agriculture. Districts with higher agricultural dependence are more sensitive to rainfall variability and extreme weather events."

    },

    "Literacy Rate – Female": {
        "column": "Literacy Rate_F",
        "chart_title": "Trend of Female Literacy Rate",
        "chart_desc": "Indicates the proportion of literate females within the population. Higher literacy supports informed decision-making and enhances resilience to climate risks."

    },

    "Literacy Rate – Male": {
        "column": "Literacy Rate_M",
        "chart_title": "Trend of Male Literacy Rate",
        "chart_desc": "Indicates the proportion of literate males within the population. Higher literacy levels are associated with improved access to information and adaptive capacity."

    },
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


