import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Dynamic DataFrame App", page_icon="📊", layout="centered")

# Title of the app
st.title("Dynamic DataFrame with Editable Column")

# Slider to select the number of rows
num_rows = st.number_input('Set the number of rows', min_value=1, max_value=100, value=5, step=1)
api_key = st.text_input('Mapy.cz API klic:')
# Create an empty DataFrame with three columns and the number of rows selected
df = pd.DataFrame({
    'Adresa': [None] * num_rows
})

# Display editable DataFrame
editable_df = st.data_editor(df, num_rows="dynamic", key="editable_df",use_container_width =True)
result_df = pd.DataFrame({
    'Adresa': editable_df['Adresa'],
    'Kod Adresniho Mista RUIAN': editable_df['Adresa']+'bubub',
    'Mapy CZ Adresa': editable_df['Adresa']+'hahaha'
})

show_result = st.dataframe(result_df)
