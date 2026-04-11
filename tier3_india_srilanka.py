import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")

st.sidebar.title("Global Settings")
country = st.sidebar.selectbox("Select Country", ["India", "Sri Lanka"])

# -----------------------
# File Paths
# -----------------------



data_files = {
    "India":r"E:\SAICJS\india_srilanka_combined_data\ter_3\IND_T3.csv",
    "Sri Lanka": r"E:\SAICJS\india_srilanka_combined_data\ter_3\SL_T3.csv"
}


# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding="latin1")
    df.columns = df.columns.str.strip()
    print(df.columns)
    return df

df = load_data(data_files[country])

# -----------------------
# Reset Filters
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.State = []
    st.session_state.District = []
    st.session_state.metric = None
    st.session_state.prev_country = country

# -----------------------
# Dynamic Content (Header + Note)
# -----------------------
content = {
    "India": {
        "header": "Tier-3 : India : Social Vulnerability Index (2020-23)",
        "subheader": "Understanding Patterns of Social Risk and Institutional Strain Across Districts",
        "write": "Tier-3 assesses social vulnerability using district-level crime data across India. It analyses trends in reported offences against children, women, and marginalized communities, along with cybercrime, to identify areas where social protection systems may be under strain. Changes in reported cases are interpreted as signals of vulnerability, reflecting shifts in incidence, reporting practices, enforcement capacity, or public awareness.",
    },
    "Sri Lanka": {
        "header": "Tier-3 : Sri Lanka : Institutional & Exploitation Vulnerability Index (2020-24)",
        "subheader": "Understanding Where Protection Systems Show Signs of Strain During Climate and Economic Shocks",
        "write": "Tier-3 assesses vulnerability within child protection environments using district-level data. It analyses trends in reported child-related offences, including violence, exploitation, neglect, and abuse, to identify where protection systems may be under strain. Changes in reported cases are interpreted as signals of vulnerability, reflecting shifts in incidence, reporting practices, enforcement capacity, or public awareness."
        
    }
}

st.header(content[country]["header"])
st.subheader(content[country]["subheader"])
st.write(content[country]["write"]) 

# -----------------------
# Indicator Mapping
# -----------------------
if country == "India":
    indicators = {
        "Vulnerability Score": {
            "column": "Vulnerability Score",
            "chart_title": "Trend of Social Vulnerability Score",
            "chart_desc": "This composite score reflects overall social vulnerability across districts. It ranges from 0 (lower vulnerability) to 1 (higher vulnerability). Higher values indicate greater levels of reported crimes and potential strain on social protection systems."
        },
        "Crimes Against Children (Cases)": {
            "column": "Crimes Against Children (Cases)",
            "chart_title": "Trend of Crimes Against Children",
            "chart_desc": "Tracks reported cases involving crimes against children. Higher values may indicate increased risks to child safety or improved detection and reporting mechanisms."
        },
        "Crimes Against Women (Cases)": {
            "column": "Crimes Against Women (Cases)",
            "chart_title": "Trend of Crimes Against Women",
            "chart_desc": "Represents reported offences against women. Trends may reflect changes in gender-based violence, social conditions, or reporting practices."
        },
        "Crimes Against SC Communities (Cases)": {
            "column": "Crimes Against SC Communities (Cases)",
            "chart_title": "Crimes Against SC Communities (Cases)",
            "chart_desc": "Tracks reported crimes against Scheduled Caste communities. Higher values may indicate social inequality, discrimination, or increased reporting."
        },
        "Crimes Against ST Communities (Cases)": {
            "column": "Crimes Against ST Communities (Cases)",
            "chart_title": "Trend of Crimes Against ST Communities",
            "chart_desc": "Represents reported offences against Scheduled Tribe communities. Trends may highlight vulnerabilities linked to marginalization or geographic isolation."
        },
        "Cybercrime Cases": {
            "column": "Cybercrime Cases",
            "chart_title": "Trend of Cybercrime Cases",
            "chart_desc": " Tracks reported cybercrime incidents. Rising trends may indicate increasing digital risks, greater internet penetration, or improved reporting systems."
        },
        

        
        

        
    
    }
else:
    indicators = {
    "Vulnerability Score": {
    "column": "Vulnerability Score",
    "chart_title": "Trend of Child Protection Vulnerability Score",
    "chart_desc": """This composite score reflects the overall level of vulnerability within child protection systems. The score ranges from 0 (lower vulnerability) to 1 (higher vulnerability). 

 Note :The vulnerability score is unavailable for Hambantota for all years 
 from 2020 to 2024 due to missing underlying indicator data.
"""
},
    "Child Homicide": {
        "column": "Child Homicide Cases",
        "chart_title": "Trend of Child Homicide Cases",
        "chart_desc": """Tracks reported cases of homicide involving children. Such incidents represent severe breakdowns in protection and safety.
        
Note : Data is missing for the year 2023 in Badulla, Galle, Kandy, Kegalle, Kurunegala, Mannar,
Matale, Moneragala, Mullaitivu, Polonnaruwa, Puttalam, Ratnapura, Trincomalee, and Vavuniya
"""
        
    },
    "Attempted Child Murder": {
        "column": "Attempted Child Murder Cases",
        "chart_title": "Trend of Attempted Child Murder Cases",
        "chart_desc": """Captures reported attempts of fatal violence against children. Trends may indicate serious threats to child safety and protection systems.

Note : Data is missing for the year 2023 in Ampara, Batticaloa, Colombo, Galle, Gampaha, Jaffna,
Kalutara, Kandy, Kegalle, Kilinochchi, Mannar, Matale, Matara, Moneragala, Mullaitivu,
Polonnaruwa, Ratnapura, Trincomalee, and Vavuniya.Hambantota has no data available for 2020 to 2024.
"""

    },
    "Child Serious Injury": {
        "column": "Child Serious Injury Cases",
        "chart_title": "Trend of Child Serious Injury Cases",
        "chart_desc": """Represents cases involving significant physical harm to children. Higher values may indicate increased exposure to unsafe environments or violence.

Note :  Data is missing for 2023 in Badulla, Gampaha, Kalutara, and Vavuniya.
Hambantota has no data for 2020–2024.
"""

    },
    "Child Assault": {
        "column": "Child Assault Cases",
        "chart_title": "Trend of Child Assault Cases",
        "chart_desc": """Tracks reported incidents of physical assault against children. Changes may reflect shifts in safety conditions or reporting.
        
Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Gampaha,
Jaffna, Kalutara, Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, 
Mullaitivu, Nuwara Eliya, Polonnaruwa, Puttalam, Ratnapura, and Trincomalee.
Hambantota has no data for 2020–2024.
"""

    },
    "Child Sexual Exploitation": {
        "column": "Child Sexual Exploitation Cases",
        "chart_title": "Trend of Child Sexual Exploitation Cases",
        "chart_desc": """Captures cases involving exploitation of children for sexual purposes. Rising trends may indicate increased vulnerability or improved detection and reporting.

Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Galle, Kalutara, Kegalle,
Kilinochchi, Kurunegala, Mannar, Matale, Mullaitivu, Nuwara Eliya, Polonnaruwa, Puttalam, Trincomalee, and Vavuniya.
Hambantota has no data for 2020–2024.
"""

    },
    "Child Abduction": {
        "column": "Child Abduction Cases",
        "chart_title": "Trend of Child Abduction Cases",
        "chart_desc": """Represents reported cases of child abduction. Higher levels may signal increased risks related to safety and security.
        
Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Jaffna, Kilinochchi, Kurunegala, Mannar, Moneragala, Mullaitivu, Puttalam, and Vavuniya.
Hambantota has no data for 2020–2024.
"""


    },
    "Child Kidnapping": {
        "column": "Child Kidnapping Cases",
        "chart_title": "Trend of Child Kid kidnapping Cases",
        "chart_desc": """Tracks reported kidnapping cases involving children. Increases may indicate heightened risks of coercion or exploitation.
        
Note : Data is missing for 2023 in Vavuniya.
Hambantota has no data for 2020–2024.
"""

        
    },
    "Child Rape": {
        "column": "Child Rape Cases",
        "chart_title": "Trend of Child Rape Cases",
        "chart_desc": """Captures reported rape cases involving children. Trends may indicate severe protection risks and vulnerabilities.
        
Note : No data is available for Hambantota for the period 2020 to 2024.
"""

        
    },
    "Child Sexual Offence": {
        "column": "Child Sexual Offence Cases",
        "chart_title": "Trend of Child Sexual Offence Cases",
        "chart_desc": """Represents a broader category of sexual offences against children. Higher values may reflect increased vulnerability or improved reporting mechanisms.
        
Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Gampaha, Jaffna, Kalutara, 
Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matale, Moneragala, Mullaitivu, Nuwara Eliya, Polonnaruwa,
Puttalam, Ratnapura, Trincomalee, and Vavuniya.Hambantota has no data for 2020–2024.
"""
        
    },
    "Child Trafficking": {
        "column": "Child Trafficking Cases",
        "chart_title": "Trend of Child Trafficking Cases",
        "chart_desc": """Tracks reported cases of trafficking involving children. Rising trends may indicate increased organised exploitation risks.
        
Note :  Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Gampaha, 
Jaffna, Kalutara, Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, Mullaitivu,
Nuwara Eliya, Polonnaruwa, Puttalam, Ratnapura, Trincomalee, and Vavuniya.Hambantota has no data for 2020–2024.
"""


        
    },
    "Child Aggravated Sexual Abuse": {
        "column": "Child Aggravated Sexual Abuse Cases",
        "chart_title": "Trend of Child Aggravated Sexual Abuse Cases",
        "chart_desc": """Captures severe forms of sexual abuse involving children. Higher levels indicate significant protection concerns.

Note:  No data is available for Hambantota for the period 2020 to 2024.
"""

        
    },
    "Adultery Cases": {
        "column": "Adultery Cases",
        "chart_title": "Trend of Adultery Cases",
        "chart_desc": """Represents reported adultery-related cases. While not directly a child-specific offence, trends may reflect broader social conditions influencing household stability.
        
Note : Data is missing for 2023 in Batticaloa, Colombo, Gampaha, Jaffna, Kalutara, Kegalle, Kilinochchi, Mullaitivu, Trincomalee, and Vavuniya.
Hambantota has no data for 2020–2024.
"""

        
    },
    "Child Cruelty": {
        "column": "Child Cruelty Cases",
        "chart_title": "Trend of Child Cruelty Cases",
        "chart_desc": """Tracks cases involving cruelty or neglect towards children. Higher values may indicate stress within caregiving environments.
        
Note :  Data is missing for 2023 in Badulla, Gampaha, Mannar, and Moneragala.
"""
        
    },
    "Child Indecent Acts": {
        "column": "Child Indecent Acts Cases",
        "chart_title": "Trend of Child Indecent Acts Cases",
        "chart_desc": """Represents cases involving inappropriate or indecent acts affecting children. Trends may indicate risks related to exploitation or misconduct.
        
Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Gampaha, Jaffna, Kalutara,
Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matara, Moneragala, Mullaitivu, Nuwara Eliya, Polonnaruwa, Puttalam, Trincomalee, and Vavuniya.
Hambantota has no data for 2020–2024.
"""

        
    },
    "Child Sexual Harassment": {
        "column": "Child Sexual Harassment Cases",
        "chart_title": "Trend of Child Sexual Harassment Cases",
        "chart_desc": """Tracks reported cases of sexual harassment involving children. Higher values may indicate increased exposure to unsafe environments.

Note :  Data is missing for 2023 in Mannar.Hambantota has no data for 2020–2024.
"""

    },
    "Child Assault & Injury": {
        "column": "Child Assault & Injury Cases",
        "chart_title": "Trend of Child Assault and Injury Cases",
        "chart_desc": """Captures combined incidents of assault and injury involving children. Trends may reflect broader patterns of violence affecting children.

Note : No data is available for Hambantota for the period 2020 to 2024.
"""


        
    },
    "Child Obscene Content Exposure": {
        "column": "Child Exposure to Obscene Content Cases",
        "chart_title": "Trend of Child Exposure to Obscene Content Cases",
        "chart_desc": """Represents cases where children are exposed to inappropriate or explicit content. Increases may reflect growing digital or environmental risks.
        
 Note : Data is missing for 2023 in Ampara, Batticaloa, Colombo, Galle, Gampaha, Jaffna, Kalutara, Kegalle, Kilinochchi, Mannar, Matara, Moneragala, Mullaitivu, Nuwara Eliya, Puttalam, Ratnapura, Trincomalee, and Vavuniya.
 Hambantota has no data for 2020–2024.
 """


        
    },
    "Child Exploitation & Assault": {
        "column": "Child Exploitation & Assault Cases",
        "chart_title": "Trend of Child Exploitation and Assault Cases",
        "chart_desc": """Captures combined cases of exploitation and physical harm. Higher values indicate overlapping vulnerabilities.
Note : Data is missing for 2023 in Ampara, Badulla, Batticaloa, Colombo, Galle, Gampaha, Jaffna, Kalutara, Kegalle,
Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, Mullaitivu, Polonnaruwa, Puttalam, Ratnapura, Trincomalee,
and Vavuniya.Hambantota has no data for 2020–2024.
"""

    },
    "Child Domestic Violence Exposure": {
        "column": "Child Domestic Violence Exposure Cases",
        "chart_title": "Trend of Child Exposure to Domestic Violence",
        "chart_desc": """Tracks cases where children are exposed to domestic violence. Such exposure may have long-term impacts on safety and well-being.

Note : : Data is missing for 2023 in Ampara, Badulla, Batticaloa, Colombo, Galle, Gampaha, Jaffna, 
Kalutara, Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, Mullaitivu,
Nuwara Eliya, Polonnaruwa, Puttalam, Ratnapura, Trincomalee, and Vavuniya.Hambantota has no data for 2020–2024.
"""

    },
    "Child Protection & Guardianship": {
        "column": "Child Protection & Guardianship Cases",
        "chart_title": "Trend of Child Protection and Guardianship Cases",
        "chart_desc": """Represents cases related to custody, protection, and guardianship. Trends may reflect pressures on formal protection systems.

Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Gampaha, Jaffna, 
Kalutara, Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, Mullaitivu,
Nuwara Eliya, Polonnaruwa, Puttalam, Ratnapura, Trincomalee, and Vavuniya.Hambantota has no data for 2020–2024.
"""

    },
    "Child Media-Related Offence": {
        "column": "Child Media-Related Offence Cases",
        "chart_title": "Trend of Child Media-Related Offence Cases",
        "chart_desc": """Captures offences involving media or digital platforms affecting children. Increases may indicate emerging risks in digital environments.
        
Note :  Data is missing for 2023 in Anuradhapura, Batticaloa, Gampaha, Kalutara, Kegalle,
Kilinochchi, Kurunegala, and Mullaitivu.Hambantota has no data for 2020–2024.
"""

    },
    "Child Education Neglect": {
        "column": "Child Education Neglect Cases",
        "chart_title": "Trend of Child Education Neglect Cases",
        "chart_desc": """Tracks cases where children are deprived of educational access or support. Higher values may signal broader socio-economic stress.
        
Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Colombo, Galle, Gampaha, Jaffna, Kalutara,
Kandy, Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, Mullaitivu, Nuwara Eliya, Polonnaruwa, Puttalam, Ratnapura, Trincomalee, and Vavuniya.
Hambantota has no data for 2020–2024.
"""



        
    },
    "Child Verbal Abuse": {
        "column": "Child Verbal Abuse Cases",
        "chart_title": "Trend of Child Verbal Abuse Cases",
        "chart_desc": """Represents reported cases of verbal abuse involving children. Trends may reflect underlying social and household stress factors.

Note : Data is missing for 2023 in Ampara, Anuradhapura, Badulla, Batticaloa, Colombo, Galle, Gampaha, Jaffna, Kalutara, 
Kandy, Kegalle, Kilinochchi, Kurunegala, Mannar, Matale, Matara, Moneragala, Mullaitivu, Nuwara Eliya, 
Polonnaruwa, Puttalam, Ratnapura, Trincomalee, and Vavuniya.Hambantota has no data for 2020–2024.
"""
        
    },
}

# -----------------------
# Filters
# -----------------------
# -----------------------
# Reset Filters (FIXED)
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.states = []
    st.session_state.districts = []
    st.session_state.prev_country = country   # ❌ DO NOT reset metric

# -----------------------
# Filters
# -----------------------
st.sidebar.title("Filters")

filtered_df = df.copy()

state_label = "Select State" if country == "India" else "Select Province"

# State filter (safe)
if "State" in df.columns:
    states = st.sidebar.multiselect(
        state_label,
        sorted(df["State"].dropna().unique()),
        key="states"
    )

    if states:
        filtered_df = filtered_df[filtered_df["State"].isin(states)]

# District filter
district_col = "District" if "District" in df.columns else "District"

districts = st.sidebar.multiselect(
    "Select District(s)",
    sorted(filtered_df[district_col].dropna().unique()),
    key="districts"
)

if districts:
    filtered_df = filtered_df[filtered_df[district_col].isin(districts)]

# -----------------------
# Indicator Selection (SAFE)
# -----------------------
indicator_options = list(indicators.keys())

# If session state is invalid → reset to first option
if "metric" not in st.session_state or st.session_state.metric not in indicator_options:
    st.session_state.metric = indicator_options[0]

metric_name = st.sidebar.selectbox(
    "Select Indicator",
    options=indicator_options,
    key="metric"
)

metric = indicators[metric_name]
# -----------------------
# Charting
# -----------------------
st.divider()
st.subheader(metric["chart_title"])

year_col = "year" if "year" in filtered_df.columns else "Year"

if metric["column"] not in filtered_df.columns:
    st.error(f"Column '{metric['column']}' not found in data!")
else:
    trend_df = (
        filtered_df.groupby([year_col, district_col])[metric["column"]]
        .mean()
        .reset_index()
    )

    fig = px.line(
        trend_df,
        x=year_col,
        y=metric["column"],
        color=district_col,
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)
    st.write(metric["chart_desc"])

if country == "India":
    st.markdown(
        """
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        <strong></strong>Values represent reported cases. A value of 0 indicates no reported cases, not absence of risk. 
        Trends may be influenced by changes in reporting practices, enforcement capacity, or public awareness. Indicators should be interpreted alongside contextual factors.
        No missing values have been artificially filled, scores are computed using available data only.
        </div>
        """,
        unsafe_allow_html=True
    )

else: 
    st.markdown(
        """
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        <strong></strong>Trends reflect reported cases and may be influenced by changes in reporting practices, enforcement capacity, 
        or public awareness.Indicators are interpreted alongside other contextual data.
        </div>
        """,
        unsafe_allow_html=True
    )