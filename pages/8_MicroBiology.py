# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 09:39:32 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, ColumnsAutoSizeMode 

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="MicroBiology",
    page_icon="D:/CPHL-MOH/pics/MoH_logo.png",
    layout="wide"
)

# %% Fix the heading 
st.markdown("""
    <style>
    .sticky-header {
        position: fixed;
        top: 3.5rem;   /* pushes below Streamlit top bar */
        left: 0;
        right: 0;
        width: 100%;
        background-color: #f9f9f9;
        padding: 12px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        z-index: 9999;
        border-bottom: 2px solid #ccc;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
   .content {
        margin-top: 90px;  /* prevents overlap */
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="sticky-header">MicroBiology<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)



# %% Functions
# Function:  extract value from mixed cell, e.g. 45% (2/5)
def extract_percent(x):
    if pd.isna(x) or x == "":
        return np.nan
    return float(x.split("%")[0])


# Fucntion:  Color coding - lowest to highest
def col_rag(val):
    if pd.isna(val):
        return ""
    elif val < 50:
        return "color:green; font-weight: bold;"
    elif val < 80:
        return "color:#BA8E23; font-weight: bold;"
    else:
        return "color: red; font-weight: bold;"
    
# Fucntion:  Color coding for normal highest to lowest
def col_rag1(val):
    if pd.isna(val):
        return ""
    elif val < 50:
        return "color:red; font-weight: bold;"
    elif val < 80:
        return "color:#BA8E23; font-weight: bold;"
    else:
        return "color: green; font-weight: bold;"
    

# Fucntion:  Color coding for Y or n
def col_rag2(val):
    if pd.isna(val):
        return ""
    elif val == "Y": # Use == for comparison
        return "color: green; font-weight: bold;"
    elif val == "Partial": # Use == for comparison
        return "color: #BA8E23; font-weight: bold;"
    else:
        return "color: red; font-weight: bold;"

# %% Load the data frames

# Microbiology KPIs
file_path40 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/MB_tech_capacity.xls"
MBTA  =  pd.read_excel(file_path40)

# Microbiology Details
file_path41 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/MB_details.xls"
MB_Details  =  pd.read_excel(file_path41)

# %% Cleaning the dataset
MBTA   =  MBTA.rename(columns = {
    "%age labs with all MB staff trained": "Pct_MBStaff_Trained",
    "%age labs with No MB staff trained" :"Pct_NoStaff_Trained",
    "%age labs with some staff trained" :"Pct_SomeStaff_Trained"
        })


# %% Common filter (RRH)
# Sidebar Filter for all tables

# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(MBTA["RRH"].dropna().unique().tolist())

Yr_list  = sorted(MB_Details["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(MB_Details["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH Region:", ["All"] + RRH_list, key="select_rrh")
    
    selected_Indicator = st.selectbox("Yr:", ["All"] + Yr_list, key="select_ind")
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")
  
# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH"] == rrh]
        
    # Filter by Yr if column exists and not "All"
    if "Yr" in df_filtered.columns and yr != "All":
        df_filtered = df_filtered[df_filtered["Yr"] == yr]
        
    # Filter by Qtr if column exists and not "All"
    if "Qtr" in df_filtered.columns and qtr != "All":
        df_filtered = df_filtered[df_filtered["Qtr"] == qtr]
        
        
    return df_filtered

# -----------------------------------------------------
# Apply filter to ALL tables
# -----------------------------------------------------
# 1. Define the dictionary of original tables FIRST
tables = {
    "RRH_MBTA": MBTA,
    "MB_Details":  MB_Details
}

# Apply the filter to that dictionary
filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Indicator, selected_Qtr)
    for name, table in tables.items()
}

# 3. Access the results
filter_RRH_MBTA = filtered_tables["RRH_MBTA"]
filter_MB_Details = filtered_tables["MB_Details"]

# %% Microbiology KPIs
# apply the styling
target_cols = ["Pct_MBStaff_Trained"]

# create a helper columns
for col in target_cols:
    filter_RRH_MBTA[f"{col}_val"]  = filter_RRH_MBTA[col].apply(extract_percent)

# Apply styling
styled_filter_RRH_MBTA = filter_RRH_MBTA.style

for col in target_cols:
    styled_filter_RRH_MBTA = styled_filter_RRH_MBTA.apply(
        lambda x, c=col: [col_rag1(v) for v in filter_RRH_MBTA[f"{c}_val"]],
        subset=[col],
        axis=0
    )
    
# Clean up: Hide all helper columns and display
helper_cols = [f"{col}_val" for col in target_cols]
styled_filter_RRH_MBTA = styled_filter_RRH_MBTA.hide(helper_cols, axis="columns")

# Diplay the table

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Microbiology Staff Technical Capacity Status by RRH Region
    </h2>
    """, 
    unsafe_allow_html=True
)


# Show all columns EXCEPT "percent_value"
visible_columns = ["RRH", "Pct_MBStaff_Trained", "Pct_NoStaff_Trained", "Pct_SomeStaff_Trained"]

st.dataframe(
    styled_filter_RRH_MBTA,
    column_order=visible_columns, 
    use_container_width=True,
    hide_index=True
)


# %% MB Detail

filtered_mbdetails   =  filter_MB_Details

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with MicroBiology Detail
    </h2>
    """, 
    unsafe_allow_html=True
)

# Making a copy of the data frame
df_for_grid = filtered_mbdetails.copy()

# Define the JavaScript for color coding (Equivalent to the function)

color_jscode = JsCode("""
function(params) {
    if (params.value === 'Y') {
        return {'color': 'green', 'font-weight': 'bold', 'font-size': '12px'};
    } else if (params.value === 'Partial') {
        return {'color': '#BA8E23', 'font-weight': 'bold', 'font-size': '12px'};
    } else if (params.value === 'N') {
        return {'color': 'red', 'font-weight': 'bold', 'font-size': '12px'};
    } else if (params.value === 'Not all') {
        return {'color': '#BA8E23', 'font-weight': 'bold', 'font-size': '12px'};
    } else {
        return {'font-size': '12px'};
    }
};
""")

# Build Grid Options from the data frame
gb = GridOptionsBuilder.from_dataframe(df_for_grid)

# Default column behavior
gb.configure_default_column(
    filter=True, 
    sortable=True,
    wrapText=True,
    autoHeight=True,
    cellStyle={'font-size': '12px', 'line-height': '14px', 'padding-top': '2px'}
)

# Apply the color logic to the target columns
target_cols = ["Staff performing microbiology lab tests, and AMR surveillance are trained, and are subjected to competence assessments", 
               ]
for col in target_cols:
    gb.configure_column(col, cellStyle=color_jscode)

# Column Headers & Pining
gb.configure_column("RRH", pinned="left")
# Set manual widths for specific columns
gb.configure_column("Yr", width=80, suppressSizeToFit=True)
gb.configure_column("Qtr", width=80, suppressSizeToFit=True)
gb.configure_column("LEVEL", width=100, suppressSizeToFit=True)

gb.configure_column("Staff performing microbiology lab tests, and AMR surveillance are trained, and are subjected to competence assessments", headerName="The facility staff performing MicroBgy and Surveillance testing is trained and periodically have Technical capacity assessed", wrapHeaderText=True, autoHeaderHeight=True)

grid_options = gb.build()

# Display the grid  
grid_response = AgGrid(
    df_for_grid,
    gridOptions=grid_options,
    allow_unsafe_jscode=True,  # REQUIRED to use JsCode for colors
    data_return_mode="FILTERED_AND_SORTED", 
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='alpine'
)

# Download Button
df_to_download = grid_response['data']
st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='mb_report.csv',
    mime='text/csv'
)



