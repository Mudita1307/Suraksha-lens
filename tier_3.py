
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






