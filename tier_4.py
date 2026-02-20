
# st.line_chart(chart_data)
import streamlit as st
import pandas as pd
import plotly.express as pxpip
import plotly.express as px
import pandas as pd
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


Tier3_clean=pd.read_csv("E:\suraksha_lens\cleaned_data\Tier4_clean.csv")


states = st.sidebar.multiselect(
        "Select State(s)",
        options=Tier3_clean["state_clean"].unique()
        
    )



metrics = [
        "CERI_norm",
        "Risk_Category",

]

selected_metrics = st.sidebar.multiselect(
        "Select Metrics",
        metrics,

    )


filtered_df = Tier3_clean[
        Tier3_clean["state_clean"].isin(states)
    ]

    # -----------------------
    # Charts
    # -----------------------
st.subheader("Trend Analysis")

for metric in selected_metrics:
    fig, ax = plt.subplots()

    for state in states:
        temp = filtered_df[filtered_df["state_clean"] == state]
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






