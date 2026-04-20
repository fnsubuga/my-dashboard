# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 11:18:10 2026

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
    page_title="Radiology",
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
st.markdown('<div class="sticky-header">Radiology<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)



# %% Functions
# Function:  extract value from mixed cell, e.g. 45% (2/5)
def extract_percent(x):
    if pd.isna(x):
        return np.nan
    
    x = str(x).strip()
    
    # Handle common non-numeric cases
    if x in ["", "NA", "NA%", "N/A", "N/A%"]:
        return np.nan
    
    try:
        return float(x.replace("%", ""))
    except ValueError:
        return np.nan


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

# Radiology equipment in place
file_path40 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/radgy_kpis.xls"
radgy  =  pd.read_excel(file_path40)

# Microbiology Details
file_path41 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/radgy_QA.xls"
radgy_Details  =  pd.read_excel(file_path41)

# %% Common filters
# Sidebar Filter for all tables

# Define Hub Name
RRH_list = sorted(radgy["RRH"].dropna().unique().tolist())

Indicator_list  = sorted(radgy["Indicator"].dropna().unique().tolist())
Yr_list  = sorted(radgy["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(radgy["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH Region:", ["All"] + RRH_list, key="select_rrh")
    
    selected_Indicator = st.selectbox("Indicator:", ["All"] + Indicator_list, key="select_indicator")
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list, key="select_yr")
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")
  
# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, indicator, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH"] == rrh]
        
    # Filter by Indicator if column exists and not "All"
    if "Indicator" in df_filtered.columns and indicator != "All":
        df_filtered = df_filtered[df_filtered["Indicator"] == indicator]
        
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
    "RRH_radgy": radgy,
    "RRHradgy_Details":  radgy_Details
}

# Apply the filter to that dictionary
filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Indicator, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# Access the results
filter_RRH_radgy = filtered_tables["RRH_radgy"]
filter_RRHradgy_Details = filtered_tables["RRHradgy_Details"]

# %% Radiology KPIs

# apply the styling
col_name = ["All_inPlace"]


# create a helper columns
for col in col_name:
    filter_RRH_radgy[f"{col}_val"]  = filter_RRH_radgy[col].apply(extract_percent)

# Apply styling
styled_filter_RRH_radgy = filter_RRH_radgy.style

for col in col_name:
    styled_filter_RRH_radgy = styled_filter_RRH_radgy.apply(
        lambda x, c=col: [col_rag1(v) for v in filter_RRH_radgy[f"{c}_val"]],
        subset=[col],
        axis=0
    )
    
# Clean up: Hide all helper columns and display
helper_cols = [f"{col}_val" for col in col_name]
styled_filter_RRH_radgy = styled_filter_RRH_radgy.hide(helper_cols, axis="columns")

# Diplay the table

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Radiology Status by RRH Region
    </h2>
    """, 
    unsafe_allow_html=True
)


# Show all columns EXCEPT "percent_value"
visible_columns = ["RRH","Indicator", "Yr", "Qtr",  "All_inPlace", "None_inPlace", "Some_inPlace"]

st.dataframe(
    styled_filter_RRH_radgy,
    column_order=visible_columns, 
    use_container_width=True,
    hide_index=True
)


# %% MB Detail

filtered_radgydetails   =  filter_RRHradgy_Details

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with Radiolgy Detail
    </h2>
    """, 
    unsafe_allow_html=True
)

# Making a copy of the data frame
df_for_grid = filtered_radgydetails.copy()

# Define the JavaScript for color coding (Equivalent to the function)

color_jscode = JsCode("""
function(params) {
    if (params.value === 'Y') {
        return {'color': 'green', 'font-weight': 'bold', 'font-size': '12px'};
    } else if (params.value === 'Partial') {
        return {'color': '#BA8E23', 'font-weight': 'bold', 'font-size': '12px'};
    } else if (params.value === 'N') {
        return {'color': 'red', 'font-weight': 'bold', 'font-size': '12px'};
    } else if (params.value === 'Not All') {
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
target_cols = ["Radiology equipment in place, and functional", 
               "Radiation protection functional (Gadget signage, warning lights, lead glasses, lead screens, lead aprons etc in place",
               "Effective Radiology Quality assurance practices in place (Light beam collination test,x-ray beam alignment test, safe light test, lead apron integrity test, etc)"
               ]
for col in target_cols:
    gb.configure_column(col, cellStyle=color_jscode)

# Column Headers & Pining
gb.configure_column("RRH", pinned="left")
# Set manual widths for specific columns
gb.configure_column("Yr", width=80, suppressSizeToFit=True)
gb.configure_column("Qtr", width=80, suppressSizeToFit=True)
gb.configure_column("LEVEL", width=100, suppressSizeToFit=True)

gb.configure_column("Radiology equipment in place, and functional", headerName="Radiology equipment in place, and functional", wrapHeaderText=True, autoHeaderHeight=True)
gb.configure_column("Radiation protection functional (Gadget signage, warning lights, lead glasses, lead screens, lead aprons etc in place", headerName="The facility has functional Radiation protection equipment", wrapHeaderText=True, autoHeaderHeight=True)
gb.configure_column("Effective Radiology Quality assurance practices in place (Light beam collination test,x-ray beam alignment test, safe light test, lead apron integrity test, etc)", headerName="The facility practices effective Radiology Quality Assurance Practices", wrapHeaderText=True, autoHeaderHeight=True)




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
