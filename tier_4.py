import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
# Ensure the file is in the same directory as your script
df = pd.read_csv("SL_T4.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Remove extra spaces

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-4: Climate Exploitation Risk Index (CERI) (2020-21)")
st.subheader("Identifying Priority Areas Facing Combined Climate and Social Risk")
st.write(
    "Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability into a single composite index."
)

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
# Metric mapping
# -----------------------
indicators = {
    "Risk Score": {
        "column": "Risk Score",
        "chart_title": "Trend of Composite Socio-Economic Exposure Score",
        "chart_desc": "The risk score integrates hazard, exposure, and vulnerability into a single composite index (0–1)."
    },
    "Risk Category": {
        "column": "Risk Category", 
        "chart_title": "Distribution of Risk Categories",
        "chart_desc": "Districts are classified into Low, Medium, or High Risk categories."
    }
}

# Select Indicator
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=0
)

# --- FIX: Define the metric variable here ---
metric = indicators[metric_name]

st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data! Available columns: {list(filtered_df.columns)}")
else:
    # --- LOGIC FOR RISK CATEGORY (Bar Chart) ---
    if metric_name == "Risk Category":
        # A stacked bar chart is best for visualizing categorical shifts over time
        fig = px.histogram(
            filtered_df,
            x="Year",
            color=metric["column"],
            barmode="stack",
            # This ensures the colors match the risk level naturally
            color_discrete_map={"High": "#e74c3c", "Medium": "#f1c40f", "Low": "#2ecc71"},
            category_orders={metric["column"]: ["Low", "Medium", "High"]},
            text_auto=True
        )
        fig.update_layout(yaxis_title="Number of Districts", xaxis_title="Year")

    # --- LOGIC FOR RISK SCORE (Line Chart) ---
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
