# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 19:13:23 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import altair as alt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="ICT",
    page_icon="D:/CPHL-MOH/pics/MoH_logo.png",
    layout="wide"
)

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
st.markdown('<div class="sticky-header">ICT<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load the data frames

# ICT RRH KPIs
file_path30 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/ict/all_ict_status.xls"
ictkpis  =  pd.read_excel(file_path30)

# ICT Health Facility Detail
file_path31 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/ict/ict_detail.xls"
ictDetails  =  pd.read_excel(file_path31)

# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

RRH_list = sorted(ictkpis["RRH"].dropna().unique().tolist())
Yr_list  = sorted(ictkpis["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(ictkpis["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters")
    selected_RRH = st.selectbox("RRH:", ["All"] + RRH_list)
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list)
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list)

# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH"] == rrh]
        
    # Filter by Year if column exists and not "All"
    if "Yr" in df_filtered.columns and yr != "All":
        df_filtered = df_filtered[df_filtered["Yr"] == yr]
        
    # Filter by Quarter if column exists and not "All"
    if "Qtr" in df_filtered.columns and qtr != "All":
        df_filtered = df_filtered[df_filtered["Qtr"] == qtr]
        
    return df_filtered

# -----------------------------------------------------
# Apply filter to ALL tables
# -----------------------------------------------------
tables = {
    "ict_KPIs": ictkpis,
    "ictdetails": ictDetails
        }

filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_ict_KPIs = filtered_tables["ict_KPIs"]
filter_ictdetails = filtered_tables["ictdetails"]

# %% ICT RRH KPIs

# apply the styling
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           ICT KPI Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_ict_KPIs)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")



# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let valueStr = params.value.toString().trim();

    // Extract ONLY the first number (handles "40% (2/5)")
    let match = valueStr.match(/^\\d+(\\.\\d+)?/);
    if (!match) return {};

    let val = parseFloat(match[0]);

    // 🔴 High downtime = BAD
    if (val >= 80) {
        return {backgroundColor: '#28a745', color: 'white'};
    } else if (val >= 50) {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else {
        return {backgroundColor: '#dc3545', color: 'white'};
    }
}
""")  

# Columns to color
target_cols = ["%age labs with functional e-LIMS", 
               "%age labs transferred to e-data management", 
               "%age labs with functinal EMRs"]


for col in target_cols:
    if col in filter_ict_KPIs.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age labs with functional e-LIMS",
    headerName="%age labs with functional e-LIMS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age labs transferred to e-data management",
    headerName="%age labs transferred to 100% e-data mgt",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age labs with functinal EMRs",
    headerName="%age labs with functinal EMRs",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'line-height': '12px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)
gb.configure_grid_options(domLayout='normal') 
grid_options = gb.build()

# display
  
# Display the grid and capture the response
grid_response = AgGrid(
       filter_ict_KPIs,
       gridOptions=grid_options,
       # for downloading
       data_return_mode="FILTERED_AND_SORTED", 
       update_mode=GridUpdateMode.MODEL_CHANGED,
       fit_columns_on_grid_load=True,
       theme='alpine',
       allow_unsafe_jscode=True
   )

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_download = grid_response['data']

st.download_button(
       "📥 Download Table",
       df_download.to_csv(index=False).encode('utf-8'),
       "ict_kpis.csv",
       "text/csv"
   )

# %% The detailed table
filtered_ictdetails   =  filter_ictdetails

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with ICT Detail
    </h2>
    """, 
    unsafe_allow_html=True
)

# Making a copy of the data frame
df_for_grid = filtered_ictdetails.copy()

# Define the JavaScript for color coding (Equivalent to the function)

color_jscode = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) {
        return {fontSize: '8px'};
    }

    let val = params.value.toString().trim();

    if (val === "Y") {
        return {backgroundColor: '#28a745', color: 'white', fontSize: '8px'};
    } else if (val === "Partial") {
        return {backgroundColor: '#ffc107', color: 'black', fontSize: '8px'};
    } else if (val === "N") {
        return {backgroundColor: '#dc3545', color: 'white', fontSize: '8px'};
    }

    return {fontSize: '8px'};
}
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
target_cols = ["The facility possesses a functional lab e-LIMS (ALIS) - with the required infrastructure, computer, internet bundles, Power Back up", 
               "The facility has fully transferred to electronic data management, using e-LIMS for among others, monthly, and quarterly HMIS reporting", 
               "If the facility is an EMR site, the facility is implementing Health Information Exchange (HIE) - VL request and results made and returned to EMR sites, respectively", 
               "Timely (at least once a week if not automated), automated data connectivity implemented" 
               ]
for col in target_cols:
    gb.configure_column(col, cellStyle=color_jscode)

# Column Headers & Pining
gb.configure_column("RRH", pinned="left")

gb.configure_column("The facility possesses a functional lab e-LIMS (ALIS) - with the required infrastructure, computer, internet bundles, Power Back up", headerName="The facility possesses a functional lab e-LIMS (ALIS)", wrapHeaderText=True, autoHeaderHeight=True)
gb.configure_column("The facility has fully transferred to electronic data management, using e-LIMS for among others, monthly, and quarterly HMIS reporting", headerName="The facility has fully transferred to electronic data management", wrapHeaderText=True, autoHeaderHeight=True)
gb.configure_column("If the facility is an EMR site, the facility is implementing Health Information Exchange (HIE) - VL request and results made and returned to EMR sites, respectively", headerName="The facility has functional EMRs", wrapHeaderText=True, autoHeaderHeight=True)
gb.configure_column("Timely (at least once a week if not automated), automated data connectivity implemented", headerName="The facility has automated connectivity", wrapHeaderText=True, autoHeaderHeight=True)

grid_options = gb.build()

# Display the grid using the DATAFRAME 
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
    file_name='ict_report.csv',
    mime='text/csv'
)
