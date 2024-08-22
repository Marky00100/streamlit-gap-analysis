import streamlit as st
import pandas as pd

# URLs to the raw data files on GitHub
lmi_url = 'https://raw.githubusercontent.com/marky00100/suppdmndprgmtool/main/lmi_oews.csv'
graduates_url = 'https://raw.githubusercontent.com/marky00100/suppdmndprgmtool/main/state_region_graduates.csv'
crosswalk_url = 'https://raw.githubusercontent.com/marky00100/suppdmndprgmtool/main/CIP2020_SOC2018_Crosswalk.xlsx'

# Load the data directly from GitHub
lmi_df = pd.read_csv(lmi_url)
graduates_df = pd.read_csv(graduates_url)
crosswalk_df = pd.read_excel(crosswalk_url)

# Filter graduates data for 2022
graduates_2022_df = graduates_df[graduates_df['year'] == 2022]

# Function to get matching SOCs for a given CIP
def get_matching_socs(cip_code):
    return crosswalk_df[crosswalk_df['CIP2020Code'] == cip_code]['SOC2018Code'].unique()

# Function to calculate gap ratio based on selected CIP and degree type
def calculate_gap_ratio(cip_code, degree_type):
    total_graduates = graduates_2022_df[graduates_2022_df['cip_code'] == cip_code]['graduates'].sum()
    matching_socs = get_matching_socs(cip_code)
    
    # Filter LMI data for these SOCs
    lmi_filtered_df = lmi_df[lmi_df['soc_code'].isin(matching_socs)]
    
    # Adjust demand based on degree type and matching SOCs
    if degree_type == 'Doctoral':
        degree_column = 'ONET % Doctoral'
    elif degree_type == 'Master':
        degree_column = 'ONET % Master'
    else:
        degree_column = 'ONET % Bachelor'
    
    # Example of calculating adjusted demand (simplified)
    adjusted_demand = sum(
        lmi_filtered_df['annual_openings_growth'] * (lmi_filtered_df[degree_column] / 100)
    )
    
    gap_ratio = total_graduates / adjusted_demand if adjusted_demand else 0
    return gap_ratio, total_graduates, adjusted_demand

# Streamlit App
st.title('Program Supply-Demand Gap Analysis Tool')

# Sidebar Inputs
st.sidebar.header('Select CIP and Parameters')
selected_cip = st.sidebar.selectbox('Select a CIP:', graduates_2022_df['cip_code'].unique())
selected_degree_type = st.sidebar.selectbox('Select Degree Type:', ['Doctoral', 'Master', 'Bachelor'])

# Calculate Gap Ratio
gap_ratio, total_graduates, adjusted_demand = calculate_gap_ratio(selected_cip, selected_degree_type)

# Display Results
st.write(f"### Selected CIP: {selected_cip}")
st.write(f"### Calculated Gap Ratio: {gap_ratio:.2f}")
st.write(f"### Total Graduates (2022): {total_graduates}")
st.write(f"### Total Adjusted Demand: {adjusted_demand}")

# Detailed Calculations
if st.button("Show Detailed Calculations"):
    st.write("### Detailed Calculation Breakdown")
    st.write(f"Total Graduates: {total_graduates}")
    st.write(f"Adjusted Demand: {adjusted_demand}")