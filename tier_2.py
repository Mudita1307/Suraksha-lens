import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("Tier2_clean1.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Remove extra spaces

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-2: Socio-Economic Exposure Index (1981–2025)")
st.subheader("Understanding Who Is Most Exposed to Rainfall-Related Climate Hazards")
st.write(
    "Tier-2 measures how socially and economically exposed each state or district is "
    "to rainfall-related climate hazards. It combines population size, demographic structure "
    "and livelihood vulnerability to identify where climate shocks would have the greatest human impact."
)

# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.title("Filters")

# State
states = st.sidebar.multiselect("Select State(s)", sorted(df["state"].unique()))
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["state"].isin(states)]

# District
districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["district"].unique()))
if districts:
    filtered_df = filtered_df[filtered_df["district"].isin(districts)]

# -----------------------
# Metric mapping
# -----------------------
indicators = {
    "Exposure Score": {
        "column": "Exposure Score",
        "chart_title": "Trend of Composite Socio-Economic Exposure Score",
        "chart_desc": "The composite exposure score ranges from 0 (lowest exposure) to 1 (highest exposure). Higher values indicate districts where rainfall shocks would affect larger and more socio-economically vulnerable populations."
    },

    "Total Population": {
        "column": "Total Population",
        "chart_title": "Trend of Total Population",
        "chart_desc": "Total population reflects the scale of potential human impact. Districts with larger populations may experience greater absolute impact during climate hazards."
    },
    "Population Density": {
        "column": "Population Density",
        "chart_title": "Trend of Population Density",
        "chart_desc": "Population density indicates the concentration of people per square kilometre. Higher density implies greater exposure intensity during rainfall-related climate shocks."
    },
  
    "SC/ST Population (%)": {
        "column": "SC/ST Population (%)",
        "chart_title": "Trend of SC/ST Population",
        "chart_desc": "This indicator captures the share of historically marginalised communities. Higher values indicate greater social vulnerability and unequal recovery capacity during climate hazards."
    },
    "Agricultural Workforce (%)": {
        "column": "Agricultural Workforce (%)",
        "chart_title": "Trend of Agricultural Workforce Share",
        "chart_desc": "This indicator reflects the proportion of the workforce dependent on agriculture. Districts with higher agricultural dependence are more sensitive to rainfall variability and extreme weather events."
    },
    "Marginal Workers (%)": {
        "column": "Marginal Workers (%)",
        "chart_title": "Trend of Marginal Workers",
        "chart_desc": "Marginal workers typically engage in unstable or seasonal employment. Higher values indicate greater livelihood insecurity, increasing susceptibility to climate-related economic shocks."
    },
    "Non-Workers (%)": {
        "column": "Non-Workers (%)",
        "chart_title": "Trend of Non-Workers Share (1981–2025)",
        "chart_desc": "This indicator reflects the proportion of the dependent population not engaged in formal work. Higher dependency burdens may reduce household coping capacity during climate shocks."
    }
}

# Default = Exposure Score
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=list(indicators.keys()).index("Total Population")
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
        filtered_df.groupby(["year", "district"])[metric["column"]]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x="year",
        y=metric["column"],
        color="district",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])
