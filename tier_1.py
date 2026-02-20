import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
# -----------------------
# Load data
# -----------------------
df = pd.read_csv(r"Tier1_clean.csv")

st.title("District Trend Dashboard")

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
    "rainfall_mm",
    "Tier1_Hazard"
    
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

