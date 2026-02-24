import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("Tier4_clean1.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Remove extra spaces

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-4: Climate Exploitation Risk Index (CERI) (2017–2025)")
st.subheader("Identifying Priority Areas Facing Combined Climate and Social Risk")
st.write(
    "Tier-4 integrates climate hazard, socio-economic exposure, and institutional vulnerability into a single composite risk index.",
    "It highlights districts and states where climate stress, human exposure, and exploitation risks overlap.",
    "Higher scores indicate a greater likelihood that climate-related stress may translate into exploitation risks."
)

# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.title("Filters")

# State filter
states = st.sidebar.multiselect("Select State(s)", sorted(df["state_clean"].unique()))
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["state_clean"].isin(states)]

# District filter
districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["district_clean"].unique()))
if districts:
    filtered_df = filtered_df[filtered_df["district_clean"].isin(districts)]

# -----------------------
# Metric mapping
# -----------------------
indicators = {
    "Risk Score": {
        "column": "CERI_norm",
        "chart_title": "Trend of Composite Socio-Economic Exposure Score",
        "chart_desc": "The risk score integrates hazard, exposure, and vulnerability into a single composite index (0–1). Higher values indicate greater overall climate-linked multi-risk."
    },
    "Risk Category": {
        "column": "Risk_Category",
        "chart_title": "Risk Category Classification",
        "chart_desc": "Districts are classified into Low, Medium, or High Risk categories based on the composite index. High-risk districts represent priority areas for targeted intervention."
    },
}

# Select metric
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=list(indicators.keys()).index("Risk Score")
)
metric = indicators[metric_name]

# -----------------------
# Line chart
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    # Numeric metric
    if pd.api.types.is_numeric_dtype(filtered_df[metric["column"]]):
        trend_df = (
            filtered_df.groupby(["year", "district_clean"])[metric["column"]]
            .mean()
            .reset_index()
        )
        fig = px.line(
            trend_df,
            x="year",
            y=metric["column"],
            color="district_clean",
            markers=True,
            title=f"{metric['column'].capitalize()} Trend by District"
        )

    # Categorical metric
    else:
        trend_df = (
            filtered_df.groupby(["year", metric["column"]])
            .size()
            .reset_index(name="count")
        )
        fig = px.line(
            trend_df,
            x="year",
            y="count",
            color=metric["column"],
            markers=True,
            title=f"{metric['column'].capitalize()} Trend by Year"
        )
        # Remove counts labels from markers
        fig.update_traces(text=None)

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])
