import streamlit as st
import pandas as pd
import streamlit as st



main_page = st.Page("main.py", title="Main Page", icon="🎈")

# Define the pages
main_page = st.Page(r"main.py", title="Main Page", icon="🎈")
page_1 = st.Page(r"Suraksha_Lens.py", title="Discover Suraksha Lens with us", icon="❄️")
page_2 = st.Page(r"tier_2.py", title="Tier 2", icon="❄️")
page_3 = st.Page(r"tier_3.py", title="Tier 3", icon="❄️")


# Set up navigation
pg = st.navigation([page_1,page_2,page_3])

# Run the selected page
pg.run()



