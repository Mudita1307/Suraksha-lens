import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
try:
    df = pd.read_csv("SL_T4.csv", encoding="latin1")
    df.columns = df.columns.str.strip()  # Remove extra spaces
except FileNotFoundError:
    st.error("CSV file 'SL_T4.csv' not found. Please ensure it is in the same folder.")
    st.stop()

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-4: Climate Exploitation Risk Index (CERI) (2020-21)")
st.subheader("Identifying Priority Areas Facing Combined Climate and Social Risk")
st.write(
    "Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability. "
    "Higher scores indicate a greater likelihood that climate-related stress affects vulnerable populations.")

# -----------------------
# Sidebar filters
# -----------------------
st.sidebar.title("Filters")

# State Filter
states = st.sidebar.multiselect("Select State(s)", sorted(df["State"].unique()))
filtered_df = df.copy()
if states:
    filtered_df = filtered_df[filtered_df["State"].isin(states)]

# District Filter
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
        "column": "Risk Category Classification",
        "chart_title": "Heatmap of Risk Category Classification by District",
        "chart_desc": "Districts are classified into Low, Medium, or High Risk categories. Darker colors represent priority areas."
    }
}

# User Selection
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=0
)

# Assign 'metric' variable AFTER the selection to avoid NameError
metric = indicators[metric_name]

# -----------------------
# Visualization Logic
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    # --- LOGIC FOR CATEGORICAL HEATMAP (Risk Category) ---
    if metric_name == "Risk Category":
        # 1. Convert text to numbers for Plotly scaling
        # (Using a numeric scale ensures the order: Low < Medium < High)
        cat_map = {"Low": 1, "Medium": 2, "High": 3}
        heatmap_df = filtered_df.copy()
        heatmap_df['Risk_Rank'] = heatmap_df[metric["column"]].map(cat_map)

        # 2. Pivot data for Heatmap
        # We use 'max' to handle cases where there might be duplicate rows for a Year/District
        pivot_df = heatmap_df.pivot_table(
            index="District", 
            columns="Year", 
            values="Risk_Rank", 
            aggfunc='max'
        )

        fig = px.imshow(
            pivot_df,
            labels=dict(x="Year", y="District", color="Risk Level"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']],
            aspect="auto"
        )
        
        # Update colorbar to show Low/Medium/High instead of 1/2/3
        fig.update_coloraxes(
            colorbar=dict(
                tickvals=[1, 2, 3],
                ticktext=["Low", "Medium", "High"]
            )
        )

    # --- LOGIC FOR LINE CHART (Risk Score) ---
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
            markers=True,
            template="plotly_white"
        )

    # Render Chart
    st.plotly_chart(fig, use_container_width=True)
    st.info(metric["chart_desc"])
