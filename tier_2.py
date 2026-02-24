import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("Tier2_clean.csv")

st.header("Tier-2: Socio-Economic Exposure Index (1981–2025)"

 st.subheader("Understanding Who Is Most Exposed to Rainfall-Related Climate Hazards")

st.write("""
    Tier-2 measures how socially and economically exposed each state or district is to rainfall-related climate hazards. 
    It combines population size, demographic structure and livelihood vulnerability to identify where climate shocks would have the greatest human impact.""")
# -----------------------
# Sidebar filters
# -----------------------

# State
states = st.sidebar.multiselect(
    "Select State(s)",
    sorted(df["state"].unique())
)

filtered_df = df.copy()

if states:
    filtered_df = filtered_df[filtered_df["state"].isin(states)]

# District (depends on state)
districts = st.sidebar.multiselect(
    "Select District(s)",
    sorted(filtered_df["district"].unique())
)

if districts:
    filtered_df = filtered_df[filtered_df["district"].isin(districts)]

# Metric
metrics = [
    "population",
    "children_pct",
    "scst_pct",
    "agri_pct",
    "marginal_pct",
    "nonwork_pct",
    "pop_density",
    "Tier2_Exposure"
]

metric = st.sidebar.selectbox("Select Metric", metrics)

# -----------------------
# Line chart
# -----------------------
st.subheader(f"{metric} Trend Over Years")

trend_df = (
    filtered_df
    .groupby(["year", "district"])[metric]
    .mean()
    .reset_index()
)

fig = px.line(
    trend_df,
    x="year",
    y=metric,
    color="district",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)




