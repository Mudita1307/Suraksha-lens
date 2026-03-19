import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Load data
# -----------------------
df = pd.read_csv(r"SL_T3.csv", encoding="latin1")
df.columns = df.columns.str.strip()  # Remove extra spaces

# -----------------------
# Page title and subtitle
# -----------------------
st.header("Tier-3: Institutional & Exploitation Vulnerability Index (2020-24)")
st.subheader("Understanding Where Protection Systems Show Signs of Strain During Climate and Economic Shocks")
st.write(
    "Tier-3 assesses vulnerability within child protection environments using district-level data. It analyses trends in reported child-related offences, including violence, exploitation, neglect, and abuse, to identify where protection systems may be under strain. Changes in reported cases are interpreted as signals of vulnerability, reflecting shifts in incidence, reporting practices, enforcement capacity, or public awareness."
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
    
    "Child Homicide": {
        "column": "Child Homicide Cases",
        "chart_title": "Trend of Child Homicide Cases",
        "chart_desc": "Tracks reported cases of homicide involving children. Such incidents represent severe breakdowns in protection and safety."
    },
    "Attempted Child Murder": {
        "column": "Attempted Child Murder Cases",
        "chart_title": "Trend of Attempted Child Murder Cases",
        "chart_desc": "Captures reported attempts of fatal violence against children. Trends may indicate serious threats to child safety and protection systems."
    },
    "Child Serious Injury": {
        "column": "Child Serious Injury Cases",
        "chart_title": "Trend of Child Serious Injury Cases",
        "chart_desc": "Represents cases involving significant physical harm to children. Higher values may indicate increased exposure to unsafe environments or violence."
    },
    "Child Assault": {
        "column": "Child Assault Cases",
        "chart_title": "Trend of Child Assault Cases",
        "chart_desc": "Tracks reported incidents of physical assault against children. Changes may reflect shifts in safety conditions or reporting."
    },
    "Child Sexual Exploitation": {
        "column": "Child Sexual Exploitation Cases",
        "chart_title": "Trend of Child Sexual Exploitation Cases",
        "chart_desc": "Captures cases involving exploitation of children for sexual purposes. Rising trends may indicate increased vulnerability or improved detection and reporting."
    },
    "Child Abduction": {
        "column": "Child Abduction Cases",
        "chart_title": "Trend of Child Abduction Cases",
        "chart_desc": "Represents reported cases of child abduction. Higher levels may signal increased risks related to safety and security."
    },
    "Child Kidnapping": {
        "column": "Child Kidnapping Cases",
        "chart_title": "Trend of Child Kid kidnapping Cases",
        "chart_desc": "Tracks reported kidnapping cases involving children. Increases may indicate heightened risks of coercion or exploitation."
    },
    "Child Rape": {
        "column": "Child Rape Cases",
        "chart_title": "Trend of Child Rape Cases",
        "chart_desc": "Captures reported rape cases involving children. Trends may indicate severe protection risks and vulnerabilities."
    },
    "Child Sexual Offence": {
        "column": "Child Sexual Offence Cases",
        "chart_title": "Trend of Child Sexual Offence Cases",
        "chart_desc": "Represents a broader category of sexual offences against children. Higher values may reflect increased vulnerability or improved reporting mechanisms."
    },
    "Child Trafficking": {
        "column": "Child Trafficking Cases",
        "chart_title": "Trend of Child Trafficking Cases",
        "chart_desc": "Tracks reported cases of trafficking involving children. Rising trends may indicate increased organised exploitation risks."
    },
    "Child Aggravated Sexual Abuse": {
        "column": "Child Aggravated Sexual Abuse Cases",
        "chart_title": "Trend of Child Aggravated Sexual Abuse Cases",
        "chart_desc": "Captures severe forms of sexual abuse involving children. Higher levels indicate significant protection concerns."
    },
    "Adultery Cases": {
        "column": "Adultery Cases",
        "chart_title": "Trend of Adultery Cases",
        "chart_desc": "Represents reported adultery-related cases. While not directly a child-specific offence, trends may reflect broader social conditions influencing household stability."
    },
    "Child Cruelty": {
        "column": "Child Cruelty Cases",
        "chart_title": "Trend of Child Cruelty Cases",
        "chart_desc": "Tracks cases involving cruelty or neglect towards children. Higher values may indicate stress within caregiving environments."
    },
    "Child Indecent Acts": {
        "column": "Child Indecent Acts Cases",
        "chart_title": "Trend of Child Indecent Acts Cases",
        "chart_desc": "Represents cases involving inappropriate or indecent acts affecting children. Trends may indicate risks related to exploitation or misconduct."
    },
    "Child Sexual Harassment": {
        "column": "Child Sexual Harassment Cases",
        "chart_title": "Trend of Child Sexual Harassment Cases",
        "chart_desc": "Tracks reported cases of sexual harassment involving children. Higher values may indicate increased exposure to unsafe environments."
    },
    "Child Assault & Injury": {
        "column": "Child Assault & Injury Cases",
        "chart_title": "Trend of Child Assault and Injury Cases",
        "chart_desc": "Captures combined incidents of assault and injury involving children. Trends may reflect broader patterns of violence affecting children."
    },
    "Child Obscene Content Exposure": {
        "column": "Child Exposure to Obscene Content Cases",
        "chart_title": "Trend of Child Exposure to Obscene Content Cases",
        "chart_desc": "Represents cases where children are exposed to inappropriate or explicit content. Increases may reflect growing digital or environmental risks."
    },
    "Child Exploitation & Assault": {
        "column": "Child Exploitation & Assault Cases",
        "chart_title": "Trend of Child Exploitation and Assault Cases",
        "chart_desc": "Captures combined cases of exploitation and physical harm. Higher values indicate overlapping vulnerabilities."
    },
    "Child Domestic Violence Exposure": {
        "column": "Child Domestic Violence Exposure Cases",
        "chart_title": "Trend of Child Exposure to Domestic Violence",
        "chart_desc": "Tracks cases where children are exposed to domestic violence. Such exposure may have long-term impacts on safety and well-being."
    },
    "Child Protection & Guardianship": {
        "column": "Child Protection & Guardianship Cases",
        "chart_title": "Trend of Child Protection and Guardianship Cases",
        "chart_desc": "Represents cases related to custody, protection, and guardianship. Trends may reflect pressures on formal protection systems."
    },
    "Child Media-Related Offence": {
        "column": "Child Media-Related Offence Cases",
        "chart_title": "Trend of Child Media-Related Offence Cases",
        "chart_desc": "Captures offences involving media or digital platforms affecting children. Increases may indicate emerging risks in digital environments."
    },
    "Child Education Neglect": {
        "column": "Child Education Neglect Cases",
        "chart_title": "Trend of Child Education Neglect Cases",
        "chart_desc": "Tracks cases where children are deprived of educational access or support. Higher values may signal broader socio-economic stress."
    },
    "Child Verbal Abuse": {
        "column": "Child Verbal Abuse Cases",
        "chart_title": "Trend of Child Verbal Abuse Cases",
        "chart_desc": "Represents reported cases of verbal abuse involving children. Trends may reflect underlying social and household stress factors."
    },

    # --- Labour Force Indicators ---
    "Labour Force Participation Rate – Male": {
        "column": "Labour Force Participation Rate – Male",
        "chart_title": "Trend of Male Labour Force Participation Rate",
        "chart_desc": "This indicator shows the proportion of the male population actively participating in the labour force. Variations may influence household income stability and resilience to climate-related disruptions."
    },
    "Labour Force Participation Rate – Female": {
        "column": "Labour Force Participation Rate – Female",
        "chart_title": "Trend of Female Labour Force Participation Rate",
        "chart_desc": "This indicator reflects the level of female participation in the labour force. Higher participation may indicate broader income sources, while lower participation may signal increased dependency."
    }
}
  
    


# Default = Exposure Score
metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=list(indicators.keys()),
    index=list(indicators.keys()).index("Child Homicide")
)

metric = indicators[metric_name]

# -----------------------
# Line chart
# -----------------------
st.subheader(metric["chart_title"])

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    # 1. Group by capitalized 'Year' and 'State'
    trend_df = (
        filtered_df.groupby(["Year", "State"])[metric["column"]]
        .mean()
        .reset_index()
    )

    # 2. Ensure px.line uses capitalized 'Year' and 'State'
    fig = px.line(
        trend_df,
        x="Year",
        y=metric["column"],
        color="State",  # Change 'state' to 'State'
        markers=True,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])
