
# st.line_chart(chart_data)
import streamlit as st
import pandas as pd
import plotly.express as pxpip
import plotly.express as px
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


Tier3_clean=pd.read_csv("E:\suraksha_lens\cleaned_data\Tier3_clean.csv")


states = st.sidebar.multiselect(
        "Select State(s)",
        options=Tier3_clean["state"].unique()
        
    )



metrics = [
        "human_val",
        "children_val",
        "cyber_val",
        "kidnapping_val",
        "vulnerability"
]

selected_metrics = st.sidebar.multiselect(
        "Select Metrics",
        metrics,

    )


filtered_df = Tier3_clean[
        Tier3_clean["state"].isin(states)
    ]

    # -----------------------
    # Charts
    # -----------------------
st.subheader("Trend Analysis")

for metric in selected_metrics:
    fig, ax = plt.subplots()

    for state in states:
        temp = filtered_df[filtered_df["state"] == state]
        ax.plot(temp["year"], temp[metric], marker="o", label=state)

    ax.set_xlabel("Year")
    ax.set_ylabel(metric)
    ax.set_title(f"{metric} Trend")
    ax.legend()
    st.pyplot(fig)



    # -----------------------
    # Summary stats
    # -----------------------
st.subheader("Summary Statistics")
# st.dataframe(filtered_df[selected_metrics].describe())









# add_selectbox_state = st.sidebar.selectbox(
#     'select the state',
#     Tier3_clean['state'].unique(),
# )

# # Add a selectbox to the sidebar:
# add_selectbox_year = st.sidebar.selectbox(
#     'select the district',
#     Tier3_clean['year'].unique(),
# )

# Tire3_state=Tier3_clean[Tier3_clean['state']==add_selectbox_state]
# Tire3_year=Tier3_clean[Tier3_clean['year']==add_selectbox_year]

# st.subheader(add_selectbox_state)

# st.subheader(add_selectbox_year)


# total_human_val=str(Tire3_year['human_val'].sum())
# st.subheader("total human_val")
# st.write(total_human_val)




# # #add_selectbox_district,' Data', df[df['district']==add_selectbox_district]
# # filtered_df=df[df['district']==add_selectbox_district]
# # # Line chart
# # #st.subheader(add_selectbox_district,"rainfall Trend")
# # st.line_chart(filtered_df.set_index("week_start")["rainfall_mm"])


# # # st.bar_chart(filtered_df.set_index("year")["rainfall_mm"])
# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt

# st.set_page_config(layout="wide")

# st.title("Human Trafficking & Vulnerability Dashboard")

# # -----------------------
# # File upload
# # -----------------------
# uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# if uploaded_file:
#     df = pd.read_csv(uploaded_file)

#     st.subheader("Raw Data")
#     st.dataframe(df)

#     # -----------------------
#     # Sidebar filters
#     # -----------------------
#     st.sidebar.header("Filters")

#     states = st.sidebar.multiselect(
#         "Select State(s)",
#         options=df["state"].unique(),
#         default=df["state"].unique()
#     )

#     years = st.sidebar.multiselect(
#         "Select Year(s)",
#         options=sorted(df["year"].unique()),
#         default=sorted(df["year"].unique())
#     )

#     metrics = [
#         "human_val",
#         "children_val",
#         "cyber_val",
#         "kidnapping_val",
#         "vulnerability"
#     ]

#     selected_metrics = st.sidebar.multiselect(
#         "Select Metrics",
#         metrics,
#         default=metrics
#     )

#     # -----------------------
#     # Filter data
#     # -----------------------
#     filtered_df = df[
#         (df["state"].isin(states)) &
#         (df["year"].isin(years))
#     ]

#     # -----------------------
#     # Charts
#     # -----------------------
#     st.subheader("Trend Analysis")

#     for metric in selected_metrics:
#         fig, ax = plt.subplots()

#         for state in states:
#             temp = filtered_df[filtered_df["state"] == state]
#             ax.plot(temp["year"], temp[metric], marker="o", label=state)

#         ax.set_xlabel("Year")
#         ax.set_ylabel(metric)
#         ax.set_title(f"{metric} Trend")
#         ax.legend()

#         st.pyplot(fig)

#     # -----------------------
#     # Summary stats
#     # -----------------------
#     st.subheader("Summary Statistics")
#     st.dataframe(filtered_df[selected_metrics].describe())

# else:
#     st.info("Upload a CSV file to begin.")
