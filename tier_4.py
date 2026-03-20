import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
# Using a raw string for the path to handle Windows backslashes
df = pd.read_csv("SL_T4.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Clean up column names

# -----------------------
# Page Header
# -----------------------
st.header("Tier-4: Climate Exploitation Risk Index (CERI) (2020-21)")
st.subheader("Identifying Priority Areas Facing Combined Climate and Social Risk")
st.write(
    "Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability. "
    "Higher scores indicate a greater likelihood of climate-related stress affecting populations."
)

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.title("Filters")

states = st.sidebar.multiselect("Select State(s)", sorted(df["State"].unique()))
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["State"].isin(states)]

districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["District"].unique()))
if districts:
    filtered_df = filtered_df[filtered_df["District"].isin(districts)]

# -----------------------
# Metric Configuration
# -----------------------
indicators = {
    "Risk Score": {
        "column": "Risk Score",
        "chart_title": "Trend of Composite Socio-Economic Exposure Score",
        "chart_desc": "The risk score integrates hazard, exposure, and vulnerability into a single composite index (0–1). Higher values indicate greater overall climate-linked multi-risk."
    },
    "Risk Category": {
        "column": "Risk Category", 
        "chart_title": "Distribution of Risk Categories",
        "chart_desc": "Districts are classified into Low, Medium, or High Risk categories based on the composite index. High-risk districts represent priority areas for targeted intervention."
    }
}

# User Selection
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=0
)

# CRITICAL FIX: Define 'metric' variable before using it below
metric = indicators[metric_name]

# -----------------------
# Visualization Logic
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    # --- BAR CHART for Risk Category ---
    if metric_name == "Risk Category":
        fig = px.histogram(
            filtered_df,
            x="Year",
            color=metric["column"],
            barmode="stack",
            # Red for High, Yellow for Medium, Green for Low
            color_discrete_map={"High": "#FF0000", "Medium": "#FFEFD5", "Low": "#008000"},
            category_orders={metric["column"]: ["Low", "Medium", "High"]},
            text_auto=True
        )
        fig.update_layout(yaxis_title="Number of Districts", xaxis_title="Year")

    # --- LINE CHART for Risk Score ---
    else:
        trend_df = (
            filtered_df.groupby(["Year", "District"])[metric["column"]]
            .mean()
            .reset_index()
        )

        fig = px.line(
            trend_df,
            x="Year",
            y=metric["column"],
            color="District",
            markers=True
        )

    st.plotly_chart(fig, use_container_width=True)
    st.info(metric["chart_desc"])
