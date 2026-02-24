import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv(r"Tier3_clean1.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Remove extra spaces

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-3: Institutional & Exploitation Vulnerability Index (2017–2023)")
st.subheader(" Understanding Where Protection Systems Show Signs of Strain During Climate and Economic Shocks")
st.write(
    "Tier-3 assesses the vulnerability of state-level protection environments."
    "It analyses trends in reported exploitation-related crimes to identify where institutional strain may increase vulnerability during climate or economic shocks."
     " Changes in reported cases are interpreted as signals of system stress, reflecting shifts in incidence, reporting practices, enforcement capacity, or public awareness."
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


# -----------------------
# Metric mapping
# -----------------------
indicators = {
    "Protection Vulnerability Score": {
        "column": "vulnerability",
        "chart_title": "Trend of Protection Vulnerability Score",
        "chart_desc": "This composite score reflects the overall strength of a state’s protection environment. The score ranges from 0 (stronger protection systems) to 1 (weaker protection systems). Higher values suggest that institutions may be under strain and less able to prevent or respond to exploitation during periods of climate, economic, or social stress."

    },
    "Human Trafficking Cases": {
        "column": "human_val",
        "chart_title":  "Trend of Reported Human Trafficking Cases",
        "chart_desc": "This indicator tracks officially reported human trafficking cases. Rising trends may reflect increasing exploitation risks, weakened preventive systems, or greater stress within vulnerable communities, particularly during or after climate and economic shocks."
    },

    "Crimes Against Children": {
        "column": "children_val",
        "chart_title": "Trend of Crimes Against Children",
        "chart_desc": "This indicator captures reported crimes against children, including abuse, exploitation, and neglect. Increases may signal growing pressure on child protection systems and heightened vulnerability during periods of displacement, livelihood loss, or social instability."

    },
    "Kidnapping Cases": {
        "column": "kidnapping_val",
        "chart_title": "Trend of Reported Cybercrime Cases",
        "chart_desc": "This indicator tracks reported kidnapping cases. Higher levels may point to serious security stress and increased vulnerability to coercion, trafficking, or organised exploitation networks."

    },
  
    
    

    



    

    
}

# Default = Exposure Score
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=list(indicators.keys()).index("Protection Vulnerability Score")
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
        filtered_df.groupby(["year", "state"])[metric["column"]]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x="year",
        y=metric["column"],
        color="state",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])

