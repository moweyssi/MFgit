import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Dynamic DataFrame App", page_icon="📊", layout="centered")

# Title of the app
st.title("Dynamic DataFrame with Editable Column")

# Slider to select the number of rows
num_rows = st.number_input('Set the number of rows', min_value=1, max_value=100, value=5, step=1)

# Create an empty DataFrame with three columns and the number of rows selected
df = pd.DataFrame({
    'Input Numbers': [None] * num_rows,
    'Column 1': [None] * num_rows,
    'Column 2': [None] * num_rows
})

# Display editable DataFrame
edited_df = st.data_editor(df, num_rows="dynamic", key="editable_df")

# If any number is entered in the first column, fill the other two columns
if 'Input Numbers' in edited_df.columns:
    for i in range(len(edited_df)):
        if pd.notna(edited_df.at[i, 'Input Numbers']):
            # Example operations to fill the other columns based on the first column's input
            edited_df.at[i, 'Column 1'] = edited_df.at[i, 'Input Numbers'] ** 2  # Square the number
            edited_df.at[i, 'Column 2'] = edited_df.at[i, 'Input Numbers'] * 2   # Multiply by 2

# Display the updated DataFrame
st.write("Updated DataFrame:")
st.write(edited_df)
