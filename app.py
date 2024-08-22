import streamlit as st
import pandas as pd
import numpy as np

# URLs to the raw data files on GitHub
lmi_url = 'https://raw.githubusercontent.com/Marky00100/streamlit-gap-analysis/main/lmi_oews.csv'
graduates_url = 'https://raw.githubusercontent.com/Marky00100/streamlit-gap-analysis/main/state_region_graduates.csv'
cip_soc_url = 'https://raw.githubusercontent.com/Marky00100/streamlit-gap-analysis/main/cip_soc.csv'
soc_cip_url = 'https://raw.githubusercontent.com/Marky00100/streamlit-gap-analysis/main/soc_cip.csv'

@st.cache_data
def load_data():
    try:
        lmi_df = pd.read_csv(lmi_url)
        graduates_df = pd.read_csv(graduates_url)
        cip_soc_df = pd.read_csv(cip_soc_url)
        soc_cip_df = pd.read_csv(soc_cip_url)
        return lmi_df, graduates_df, cip_soc_df, soc_cip_df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None, None

# Load the data
lmi_df, graduates_df, cip_soc_df, soc_cip_df = load_data()

if lmi_df is None or graduates_df is None or cip_soc_df is None or soc_cip_df is None:
    st.stop()

# Filter graduates data for the latest year
graduates_2022_df = graduates_df[graduates_df['academic_year'] == 2022]

# Assign random education category percentages
np.random.seed(42)  # For reproducibility
lmi_df['ONET % Doctoral'] = np.random.uniform(0.1, 0.5, size=len(lmi_df))
lmi_df['ONET % Master'] = np.random.uniform(0.2, 0.6, size=len(lmi_df))
lmi_df['ONET % Bachelor'] = np.random.uniform(0.3, 0.7, size=len(lmi_df))

# Map degree_group_logord to educational categories
degree_mapping = {
    1: 'Doctoral',
    2: 'Master',
    3: 'Bachelor'
}

graduates_2022_df['degree_category'] = graduates_2022_df['degree_group_logord'].map(degree_mapping)

# Function to get matching SOCs for a given CIP
def get_matching_socs(cip_code):
    return cip_soc_df[cip_soc_df['CIP2020Code'] == cip_code]['SOC2018Code'].unique()

# Function to calculate gap ratio based on selected CIP, degree type, and region
def calculate_gap_ratio(cip_code, degree_type, region):
    # Filter graduates by CIP, degree type, and region
    total_graduates = graduates_2022_df[
        (graduates_2022_df['cip_code'] == cip_code) &
        (graduates_2022_df['degree_category'] == degree_type) &
        ((graduates_2022_df['jobsohioregion'] == region) | (region == 'Statewide'))
    ]['graduates'].sum()
    
    matching_socs = get_matching_socs(cip_code)
    
    # Filter LMI data for these SOCs and region
    lmi_filtered_df = lmi_df[
        (lmi_df['soc_code'].isin(matching_socs)) & 
        ((lmi_df['jobsohioregion'] == region) | (region == 'Statewide'))
    ]
    
    # Adjust demand based on degree type and matching SOCs
    if degree_type == 'Doctoral':
        degree_column = 'ONET % Doctoral'
    elif degree_type == 'Master':
        degree_column = 'ONET % Master'
    else:
        degree_column = 'ONET % Bachelor'
    
    # Calculate adjusted demand
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
selected_region = st.sidebar.selectbox('Select Region:', ['Statewide'] + list(lmi_df['jobsohioregion'].unique()))

# Calculate Gap Ratio
gap_ratio, total_graduates, adjusted_demand = calculate_gap_ratio(selected_cip, selected_degree_type, selected_region)

# Display Results
st.write(f"### Selected CIP: {selected_cip}")
st.write(f"### Selected Degree Type: {selected_degree_type}")
st.write(f"### Selected Region: {selected_region}")
st.write(f"### Calculated Gap Ratio: {gap_ratio:.2f}")
st.write(f"### Total Graduates (2022): {total_graduates}")
st.write(f"### Total Adjusted Demand: {adjusted_demand}")

# Detailed Calculations
if st.button("Show Detailed Calculations"):
    st.write("### Detailed Calculation Breakdown")
    st.write(f"Total Graduates: {total_graduates}")
    st.write(f"Adjusted Demand: {adjusted_demand}")
