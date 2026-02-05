
# st.line_chart(chart_data)
import streamlit as st
import pandas as pd
import plotly.express as pxpip
import plotly.express as px
import pandas as pd


Tier2_clean=pd.read_csv("E:\suraksha_lens\cleaned_data\Tier2_clean.csv")
Tier3_clean=pd.read_csv("E:\suraksha_lens\cleaned_data\Tier3_clean.csv")

df = pd.read_csv("E:\suraksha_lens\data\TIER1_weekly_all_districts_1981_2025.csv")
df=df[:80000]
df


add_selectbox_state = st.sidebar.selectbox(
    'select the state',
    Tier3_clean['state'].unique(),
)

# Add a selectbox to the sidebar:
add_selectbox_district = st.sidebar.selectbox(
    'select the district',
    df['district'].unique(),
)
add_selectbox_week_start = st.sidebar.selectbox(
    'year', 
    df['year'].unique())

selected_date = st.sidebar.slider("Select rainfall",
df['rainfall_mm'].min(),
df['rainfall_mm'].max()
)
st.subheader(add_selectbox_district)

rainfall=df[df['district']==add_selectbox_district]
total_rainfall=str(rainfall['rainfall_mm'].sum())
st.subheader("Rainfall in MM")
st.write(total_rainfall)


Tire3=Tier3_clean[Tier3_clean['state']==add_selectbox_state]
total_human_val=str(Tire3['human_val'].sum())
st.subheader("total human_val")
st.write(total_human_val)




# #add_selectbox_district,' Data', df[df['district']==add_selectbox_district]
# filtered_df=df[df['district']==add_selectbox_district]
# # Line chart
# #st.subheader(add_selectbox_district,"rainfall Trend")
# st.line_chart(filtered_df.set_index("week_start")["rainfall_mm"])


# st.bar_chart(filtered_df.set_index("year")["rainfall_mm"])
