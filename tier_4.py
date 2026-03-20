import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv("SL_T4.csv", encoding="latin1")
df.columns = df.columns.str.strip()

# -----------------------
# Page Header
# -----------------------
st.header("Tier-4: Climate Exploitation Risk Index (CERI) (2020-21)")
st.subheader("Identifying Priority Areas Facing Combined Climate and Social Risk")
st.write(
    "Tier-4 integrates climate hazard, socio-economic exposure, and child protection vulnerability into a single composite index. "
    "It highlights areas where climate stress, population exposure, and protection risks overlap."
)

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.title("Filters")

states = st.sidebar.multiselect("Select State(s)", sorted(df["State"].dropna().unique()))
filtered_df = df.copy()

if states:
    filtered_df = filtered_df[filtered_df["State"].isin(states)]

districts = st.sidebar.multiselect("Select District(s)", sorted(filtered_df["District"].dropna().unique()))
if districts:
    filtered_df = filtered_df[filtered_df["District"].isin(districts)]

# -----------------------
# Metric Mapping
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
        "chart_desc": "Districts are classified into Low, Medium, or High Risk categories."
    }
}

metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=0
)

# ✅ FIX: define metric
metric = indicators[metric_name]

# -----------------------
# Visualization
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")

else:
    # -----------------------
    # Risk Category (Stacked Bar)
    # -----------------------
    if metric_name == "Risk Category":

        filtered_df = filtered_df.dropna(subset=["Year", metric["column"]])

        fig = px.histogram(
            filtered_df,
            x="Year",
            color=metric["column"],
            barmode="stack",
            color_discrete_map={
                "High": "red",
                "Medium": "orange",
                "Low": "green"
            },
            category_orders={metric["column"]: ["Low", "Medium", "High"]},
            text_auto=True
        )

        fig.update_layout(
            yaxis_title="Number of Districts",
            xaxis_title="Year"
        )

    # -----------------------
    # Risk Score (Line Chart)
    # -----------------------
    else:
        trend_df = (
            filtered_df.groupby(["Year", "District"])[metric["column"]]
            .mean()
            .reset_index()
        )

        # Clean data
        trend_df["Year"] = pd.to_numeric(trend_df["Year"], errors="coerce")
        trend_df[metric["column"]] = pd.to_numeric(trend_df[metric["column"]], errors="coerce")

        trend_df = trend_df.dropna()

        if trend_df.empty:
            st.warning("No data available after filtering.")
        else:
            fig = px.line(
                trend_df,
                x="Year",
                y=metric["column"],
                color="District",
                markers=True
            )

    # -----------------------
    # Plot
    # -----------------------
    if 'fig' in locals():
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------
    # Description (Colored text)
    # -----------------------
    if metric_name == "Risk Category":
        st.markdown(
            "Districts are classified into "
            "<span style='color:green; font-weight:bold;'>Low</span>, "
            "<span style='color:orange; font-weight:bold;'>Medium</span>, and "
            "<span style='color:red; font-weight:bold;'>High</span> risk categories. "
            "<span style='color:red; font-weight:bold;'>High-risk</span> districts represent priority areas.",
            unsafe_allow_html=True
        )
    else:
        st.write(metric["chart_desc"])
