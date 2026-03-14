import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("Tier2_clean3.csv", encoding="latin1")
df.columns = df.columns.str.strip()

# If state and district columns are swapped in the CSV


# -----------------------
# Page title
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

# State filter
states = st.sidebar.multiselect(
    "Select State(s)",
    sorted(df["state"].dropna().unique())
)

filtered_df = df.copy()

if states:
    filtered_df = filtered_df[filtered_df["state"].isin(states)]

# District filter (based on selected states)
districts = st.sidebar.multiselect(
    "Select District(s)",
    sorted(filtered_df["district"].dropna().unique())
)

if districts:
    filtered_df = filtered_df[filtered_df["district"].isin(districts)]

# -----------------------
# Indicator dictionary
# -----------------------
indicators = {

    "Population Density": {
        "column": "pop_density",
        "chart_title": "Trend of Population Density",
        "chart_desc": "Population density indicates the concentration of people per square kilometre. Higher density implies greater exposure intensity during rainfall-related climate shocks."
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
        .groupby(["year", "district"])[metric["column"]]
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

