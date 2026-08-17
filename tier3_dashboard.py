import streamlit as st
import pandas as pd
import plotly.express as px

from i18n import inject_sidebar_layout_fix, t, inject_font_css

# -----------------------
# Config
# -----------------------
st.set_page_config(page_title="Climate Hazard Index", layout="wide")
inject_font_css()
inject_sidebar_layout_fix()

st.session_state["tier"] = "T3"
st.session_state["_current_page"] = "tier3"
st.session_state["dashboard_chart_data"] = None

COUNTRY_CODES = ["India", "Sri Lanka"]

if "country" not in st.session_state or st.session_state.country not in COUNTRY_CODES:
    st.session_state.country = COUNTRY_CODES[0]

country = st.sidebar.selectbox(
    t("common.select_country"),
    COUNTRY_CODES,
    format_func=lambda c: t("common.india") if c == "India" else t("common.sri_lanka"),
    key="country",
)

# -----------------------
# File Paths
# -----------------------
data_files = {
    "India": "IND_T3.csv",
    "Sri Lanka": "SL_T3.csv"
}

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding="latin1")
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
st.header(t(f"tier3.content.{country}.header"))
st.subheader(t(f"tier3.content.{country}.subheader"))
st.write(t(f"tier3.content.{country}.write"))

# -----------------------
# Indicator Column Mapping (technical - CSV column names, not translated)
# -----------------------
INDICATOR_COLUMNS = {
    "India": {
        "vulnerability_score": "Vulnerability Score",
        "crimes_against_children": "Crimes Against Children (Cases)",
        "crimes_against_women": "Crimes Against Women (Cases)",
        "crimes_against_sc": "Crimes Against SC Communities (Cases)",
        "crimes_against_st": "Crimes Against ST Communities (Cases)",
        "cybercrime_cases": "Cybercrime Cases",
    },
    "Sri Lanka": {
        "vulnerability_score": "Vulnerability Score",
        "child_homicide": "Child Homicide Cases",
        "attempted_child_murder": "Attempted Child Murder Cases",
        "child_serious_injury": "Child Serious Injury Cases",
        "child_assault": "Child Assault Cases",
        "child_sexual_exploitation": "Child Sexual Exploitation Cases",
        "child_abduction": "Child Abduction Cases",
        "child_kidnapping": "Child Kidnapping Cases",
        "child_rape": "Child Rape Cases",
        "child_sexual_offence": "Child Sexual Offence Cases",
        "child_trafficking": "Child Trafficking Cases",
        "child_aggravated_sexual_abuse": "Child Aggravated Sexual Abuse Cases",
        "adultery_cases": "Adultery Cases",
        "child_cruelty": "Child Cruelty Cases",
        "child_indecent_acts": "Child Indecent Acts Cases",
        "child_sexual_harassment": "Child Sexual Harassment Cases",
        "child_assault_injury": "Child Assault & Injury Cases",
        "child_obscene_content": "Child Exposure to Obscene Content Cases",
        "child_exploitation_assault": "Child Exploitation & Assault Cases",
        "child_domestic_violence": "Child Domestic Violence Exposure Cases",
        "child_protection_guardianship": "Child Protection & Guardianship Cases",
        "child_media_offence": "Child Media-Related Offence Cases",
        "child_education_neglect": "Child Education Neglect Cases",
        "child_verbal_abuse": "Child Verbal Abuse Cases",
    },
}

indicator_ids = list(INDICATOR_COLUMNS[country].keys())

def indicator_label(ind_id):
    return t(f"tier3.indicators.{country}.{ind_id}.label")

# -----------------------
# Filters
# -----------------------
if "prev_country" not in st.session_state:
    st.session_state.prev_country = country

if st.session_state.prev_country != country:
    st.session_state.states = []
    st.session_state.districts = []
    st.session_state.prev_country = country   # ❌ DO NOT reset metric

st.sidebar.title(t("common.filters"))

filtered_df = df.copy()

state_label = t("common.select_state") if country == "India" else t("common.select_province")

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
    t("common.select_districts"),
    sorted(filtered_df[district_col].dropna().unique()),
    key="districts"
)

if districts:
    filtered_df = filtered_df[filtered_df[district_col].isin(districts)]

# -----------------------
# Indicator Selection (SAFE)
# -----------------------
if "metric" not in st.session_state or st.session_state.metric not in indicator_ids:
    st.session_state.metric = indicator_ids[0]

metric_id = st.sidebar.selectbox(
    t("common.select_indicator"),
    options=indicator_ids,
    format_func=indicator_label,
    key="metric"
)

st.sidebar.markdown("<div style='height: 400px;'></div>", unsafe_allow_html=True)

metric_column = INDICATOR_COLUMNS[country][metric_id]
chart_title = t(f"tier3.indicators.{country}.{metric_id}.chart_title")
chart_desc = t(f"tier3.indicators.{country}.{metric_id}.chart_desc")
# Sri Lanka indicators carry an extra "note" field (missing-data footnote).
# Place names are kept in English by design - see translation notes.
chart_note = t(f"tier3.indicators.{country}.{metric_id}.note") if country == "Sri Lanka" else ""

# -----------------------
# Charting
# -----------------------
st.divider()
st.subheader(chart_title)

year_col = "year" if "year" in filtered_df.columns else "Year"

if metric_column not in filtered_df.columns:
    st.error(t("common.column_not_found", column=metric_column))
else:
    trend_df = (
    filtered_df.groupby([year_col, district_col])[metric_column]
    .mean()
    .reset_index()
    )

# Give the chatbot the exact data being plotted
    st.session_state["chat_chart_data"] = trend_df.to_dict(orient="records")
    st.session_state["chat_chart_context"] = {
    "country": country,
    "tier": "T3",
    "metric": metric_id,
    "metric_column": metric_column,
    "year_column": year_col,
    "district_column": district_col,
    "chart_title": chart_title,
    }

    fig = px.line(
        trend_df,
        x=year_col,
        y=metric_column,
        color=district_col,
        markers=True
    )

    st.plotly_chart(fig, width="stretch")
    st.write(chart_desc)
    if chart_note:
        st.caption(f"ℹ️ {chart_note}")

# -----------------------
# Large data-availability appendix notes.
# District / police-station names are proper nouns and are kept in
# English throughout, even in the Hindi UI - only the surrounding
# sentences are translated. See translation notes for rationale.
# -----------------------
TIER3_INDIA_MISSING_2020 = (
    "Andhra Pradesh (Alluri Sitharama Raju, Anakapalli, Anantapuramu, Annamayya, "
    "Bapatla, Dr BR Ambedkar Konaseema, Eluru, Kakinada, NTR, Nandyal, Palnadu, Parvathipuram Manyam, Prakasam, Sri Potti Sriramulu Nellore, "
    "Sri Sathya Sai, Tirupati, Vijayawada Railway, YSR), Assam (Bajali, Tamulpur), Bihar (Kaimur (Bhabhua)), Chhattisgarh (Khairagarh–Chhuikhadan–Gandai, "
    "Manendragarh–Chirmiri–Bharatpur, Mohla–Manpur–Ambagarh Chouki, Sakti, Sarangarh–Bilaigarh), Gujarat (W Rly Ahmedabad, W Rly Vadodara), "
    "Himachal Pradesh (Nurpur), Jammu & Kashmir (Anti Narcotic Task Force Jammu, Anti Narcotic Task Force Kashmir, CICE Jammu, CICE Kashmir, "
    "Cyber Crime Jammu, Cyber Crime Kashmir, EOW Jammu, EOW Kashmir, Special Crime Wing Jammu, Special Crime Wing Kashmir), Karnataka "
    "(KGF, KRailways, Vijayanagara), Kerala (All Districts, Ernakulam Commr, Kannur City, Kannur Rural, Kollam Commr, Kozhikode Commr, Thrissur Commr, "
    "Trivandrum Commr), Madhya Pradesh (Bhopal Commissionarate, Bhopal Rural, Indore Commissionarate, Indore Rural, Narmadapuram), Maharashtra "
    "(Amravati Commr, Chhatrapati Sambhajinagar Commr, Chhatrapati Sambhajinagar Railway, Chhatrapati Sambhajinagar Rural, Dharashiv, Mira Bhayandar Vasai Virar Commr, "
    "Mumbai Commr, Nagpur Commr, Nasik Commr, Pune Commr, Solapur Commr, Thane Commr), Meghalaya (Khasi Hills Eastern West), Mizoram (Crime and EOU), Nagaland "
    "(Crime, Cyber Security, Narcotics, Noklak, Shamator, Tseminyu, Dimapur, Kiphire, Kohima, Longleng, Mokokchung, Mon, Peren, Phek, Tuensang, Wokha, Zunheboto), "
    "Puducherry (Puducherry), Punjab (Cyber Crime Wing, Malerkotla), Rajasthan (ATS & SOG, Anupgarh, Balotra, Beawar, Deeg, Didwana-Kuchaman, Dudu, Gangapur City, "
    "Jodhpur Crime, Kekri, Khairtal-Tijara, Kotputli-Behror, Neem Ka Thana, Phalodi, Salumbar, Sanchore, Shahpura), Sikkim (CID, Gangtok (East), Gyalshing (West), "
    "Mangan (North), Namchi (South), Pakyong (East), Soreng (West)), Tamil Nadu (Avadi, Mayiladuthurai, Tambaram), Uttar Pradesh (Kanpur Commissionarate, Kanpur Outer, "
    "Varanasi Commissionarate, Varanasi Dehat), Uttarakhand (Cyber Cell)"
)

TIER3_INDIA_MISSING_2021 = (
    "Andhra Pradesh (Alluri Sitharama Raju, Anakapalli, Anantapuramu, Annamayya, "
    "Bapatla, Dr BR Ambedkar Konaseema, Eluru, Kakinada, NTR, Nandyal, Palnadu, Parvathipuram Manyam, Prakasam, Sri Potti Sriramulu Nellore, "
    "Sri Sathya Sai, Tirupati, Vijayawada Railway, YSR), Assam (Bajali, Tamulpur), Bihar (Bhabhua), Chhattisgarh (Khairagarh–Chhuikhadan–Gandai, "
    "Manendragarh–Chirmiri–Bharatpur, Mohla–Manpur–Ambagarh Chouki, Sakti, Sarangarh–Bilaigarh), Gujarat (W Rly Ahmedabad, W Rly Vadodara), "
    "Himachal Pradesh (Nurpur), Jammu & Kashmir (Anti Narcotic Task Force Kashmir, CICE Jammu, CICE Kashmir, EOW Jammu, EOW Kashmir, Special Crime Wing Jammu, "
    "Special Crime Wing Kashmir), Karnataka (KGF, KRailways, Vijayanagara), Kerala (All Districts, Ernakulam Commr, Kannur, Kollam Commr, Kozhikode Commr, Thrissur Commr, "
    "Trivandrum Commr), Madhya Pradesh (Bhopal Commissionarate, Bhopal Rural, Indore Commissionarate, Indore Rural, Narmadapuram), Maharashtra (Amravati Commr, Chhatrapati "
    "Sambhajinagar Commr, Chhatrapati Sambhajinagar Railway, Chhatrapati Sambhajinagar Rural, Dharashiv, Mira Bhayandar Vasai Virar Commr, Mumbai Commr, Nagpur Commr, "
    "Nasik Commr, Pune Commr, Solapur Commr, Thane Commr), Meghalaya (Khasi Hills Eastern West), Mizoram (Crime and EOU), Nagaland (Crime, Cyber Security, Narcotics, "
    "Noklak, Shamator, Tseminyu, Dimapur, Kiphire, Kohima, Longleng, Mokokchung, Mon, Peren, Phek, Tuensang, Wokha, Zunheboto), Puducherry (All Districts), "
    "Punjab (Cyber Crime Wing), Rajasthan (ATS & SOG, Anupgarh, Balotra, Beawar, Deeg, Didwana-Kuchaman, Dudu, Gangapur City, Jodhpur Crime, Kekri, Khairtal-Tijara, "
    "Kotputli-Behror, Neem Ka Thana, Phalodi, Salumbar, Sanchore, Shahpura), Sikkim (Gangtok (East), Gyalshing (West), Mangan (North), Namchi (South), Pakyong (East), "
    "Soreng (West)), Tamil Nadu (Avadi, Mayiladuthurai, Tambaram), Uttar Pradesh (Kanpur Nagar, Varanasi)"
)

TIER3_INDIA_MISSING_2022 = (
    "Andhra Pradesh (Anantapur, Cuddapah, Guntur Urban, Nellore, Prakasham, Rajahmundry, "
    "Tirupathi Urban, Vijayawada City, Vijayawada Railway, Visakha Rural), Bihar (Bhabhua), Gujarat (W Rly Ahmedabad, W Rly Vadodara), Himachal Pradesh (Nurpur), "
    "Jammu & Kashmir (Crime Jammu, Crime Srinagar), Karnataka (KGF, KRailways), Kerala (Ernakulam Commr, Kannur, Kollam Commr, Kozhikode Commr, Thrissur Commr, Trivandrum Commr), "
    "Madhya Pradesh (Bhopal, Hoshangabad, Indore), Maharashtra (Amravati Commr, Chhatrapati Sambhajinagar Commr, Chhatrapati Sambhajinagar Railway, Chhatrapati Sambhajinagar Rural, "
    "Dharashiv, Mira Bhayandar Vasai Virar Commr, Mumbai Commr, Nagpur Commr, Nasik Commr, Pune Commr, Solapur Commr, Thane Commr), Mizoram (Crime and EOU), "
    "Nagaland (Crime, Cyber Security, Narcotics, Noklak, Shamator, Tseminyu, Dimapur, Kiphire, Kohima, Longleng, Mokokchung, Mon, Peren, Phek, Tuensang, Wokha, Zunheboto), "
    "Puducherry (All Districts), Punjab (Cyber Crime Wing), Rajasthan (ATS & SOG, Anupgarh, Balotra, Beawar, Deeg, Didwana-Kuchaman, Dudu, Gangapur City, Jodhpur Crime, Kekri, "
    "Khairtal-Tijara, Kotputli-Behror, Neem Ka Thana, Phalodi, Salumbar, Sanchore, Shahpura), Sikkim (CID, East, North, South, West), Tamil Nadu (Mayiladuthurai), "
    "Uttar Pradesh (Amroha, Kanpur Nagar, Varanasi)"
)

TIER3_INDIA_MISSING_2023 = (
    "Andhra Pradesh (Anantapur, Cuddapah, Guntur Urban, Nellore, Prakasham, Rajahmundry, Tirupathi Urban, "
    "Vijayawada City, Vijayawada Railway, Visakha Rural), Bihar (Bhabhua), Gujarat (W.Rly Ahmedabad, W.Rly Vadodara), Jammu & Kashmir (Crime Jammu, Crime Srinagar), "
    "Karnataka (K.G.F., K.Railways), Kerala (All Districts, Ernakulam Commr, Kannur, Kollam Commr, Kozhikode Commr, Thrissur Commr, Trivandrum Commr), "
    "Madhya Pradesh (Bhopal, Hoshangabad, Indore), Maharashtra (Amravati Commr, Aurangabad Commr, Aurangabad Railway, Aurangabad Rural, Mira Bhayandar Vasai Virar Commr, "
    "Mumbai Commr, Nagpur Commr, Nasik Commr, Osmanabad, Pune Commr, Solapur Commr, Thane Commr), Nagaland (Dimapur, Kiphire, Kohima, Longleng, Mokokchung, Mon, Peren, "
    "Phek, Tuensang, Wokha, Zunheboto), Puducherry (All Districts), Rajasthan (SOG), Sikkim (East, North, South, West), Uttar Pradesh (Kanpur Nagar, Kanpur Outer, "
    "Lucknow Grameen, Varanasi, Varanasi Dehat)"
)

if country == "India":
    st.markdown(
        f"""
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        {t("tier3.notes.india_intro")}
        </div>

        <div style="background-color: #FFDE21;; padding: 15px; border-radius: 5px; border: 1px solid #FFDE21;">
        <strong>{t("tier3.notes.india_2020_label")}</strong> {TIER3_INDIA_MISSING_2020}
        </div>

        <div style="background-color: #FFDE21;; padding: 15px; border-radius: 5px; border: 1px solid #FFDE21;">
        <strong>{t("tier3.notes.india_2021_label")}</strong> {TIER3_INDIA_MISSING_2021}
        </div>

        <div style="background-color: #FFDE21;; padding: 15px; border-radius: 5px; border: 1px solid #FFDE21;">
        <strong>{t("tier3.notes.india_2022_label")}</strong> {TIER3_INDIA_MISSING_2022}
        </div>

        <div style="background-color: #FFDE21;; padding: 15px; border-radius: 5px; border: 1px solid #FFDE21;">
        <strong>{t("tier3.notes.india_2023_label")}</strong> {TIER3_INDIA_MISSING_2023}
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.markdown(
        f"""
        <div style="background-color: #ffcccc; padding: 15px; border-radius: 5px; border: 1px solid #ff0000;">
        {t("tier3.notes.sri_lanka")}
        </div>
        """,
        unsafe_allow_html=True
    )