# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 17:22:28 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="HR",
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
st.markdown('<div class="sticky-header">Human Resources<b> </div>', unsafe_allow_html=True)

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
# -----------------------------------------------------
# Load the RRH-Hub Spokes Data
# -----------------------------------------------------

# HR Available by Health Level
file_path2 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/HR/PctHRAvail_by_Level.xls"
HRLevel = pd.read_excel(file_path2)

# HR avaible by RRH Region
file_path3  =  "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/HR/PctHRAvail_by_RRH.xls"
HRRgns  =  pd.read_excel(file_path3)

# Prop cadres unavailable by health level
file_path4  =  "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/HR/Prop_cadres_unavailable.xls"
CadreAvail  =  pd.read_excel(file_path4)

# prop unvailable by RRH and health level
file_path5  =  "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/HR/Prop_cadres_unavailable_RRH_lvl.xls"
CadreRRH_Lvl  =  pd.read_excel(file_path5)

# prop unvailable by RRH and health level
file_path6  =  "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/HR/Detailed_HR.xls"
HRDetail  =  pd.read_excel(file_path6)


# %% rename columns
HRLevel  =    HRLevel.rename(columns = {
    "RRH"  : "RRH_Region",
    "%age labs with all the required lab cadres" : "PctLabs_NoCadre"
    })

HRRgns   =  HRRgns.rename(columns  = {
    "HC III"   :  "HCIII",
    "HC IV"    :  "HCIV"
        })


# Re-order data frame columns
CadreRRH_Lvl  =  CadreRRH_Lvl[
    [
    "RRH_Region",
    "List of cadre categories unavailable in the facility",
        "Yr",
        "Qtr",
        "HC III",
        "HC IV",
        "HOSPITAL",
        "RRH"
        ]]
# rename
CadreRRH_Lvl  =   CadreRRH_Lvl.rename(columns = {
    "HC III"   :  "HCIII",
    "HC IV"    :  "HCIV",
    "List of cadre categories unavailable in the facility" : "Cadre"
        })

# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(HRLevel["RRH_Region"].dropna().unique().tolist())

Yr_list  = sorted(HRLevel["Yr"].dropna().unique().tolist())

Qtr_list  = sorted(HRLevel["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH_Region:", ["All"] + RRH_list, key="select_rrh")
    
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list, key="select_yr")
    
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")

# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH_Region" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH_Region"] == rrh]
        
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
    "Prop_HRLevel": HRLevel,
    "Prop_HRRgns": HRRgns,
    "Prop_CadreRRH_Lvl": CadreRRH_Lvl,
    "HRdetail" : HRDetail
    }


filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_Prop_HRLevel = filtered_tables["Prop_HRLevel"]
filter_Prop_HRRgns = filtered_tables["Prop_HRRgns"]
filter_Prop_CadreRRH_Lvl = filtered_tables["Prop_CadreRRH_Lvl"]
filter_HRdetail = filtered_tables["HRdetail"]


# %% The HR Available

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Proportion of health facilities with Recommended HR Available, by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_Prop_HRLevel)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH_Region", pinned="left")

# Wrap long column headers
# RRH
gb.configure_column(
    "RRH_Region",
    headerName="RRH",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "PctLabs_NoCadre",
    headerName="%age labs with all the required lab cadres",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode2 = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let valueStr = params.value.toString().trim();

    if (valueStr === "" || valueStr.toLowerCase() === "nan") return {};

    // Extract number (e.g. 33 from "33% (1/3)")
    let match = valueStr.match(/\\d+/);
    if (!match) return {};

    let val = parseInt(match[0]);

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
target_cols = ["PctLabs_NoCadre"]


for col in target_cols:
    if col in filter_Prop_HRLevel.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode2)

# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '12px',
        'line-height': '14px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)
gb.configure_grid_options(domLayout='autoHeight') 
grid_options = gb.build()

# Display the grid and capture the response
grid_response = AgGrid(
    filter_Prop_HRLevel,
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
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='hr_byrrh.csv',
    mime='text/csv'
)



# %% Proportion of cadres unavailable by health level

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Proportion of health facilities with Recommended HR Available, by RRH and Health Level
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_Prop_HRRgns)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH_Region", pinned="left")

# Wrap long column headers properly
gb.configure_column(
    "RRH_Region",
    headerName="RRH",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let valueStr = params.value.toString().trim();

    if (valueStr === "" || valueStr.toLowerCase() === "nan") return {};

    // Extract number (e.g. 33 from "33% (1/3)")
    let match = valueStr.match(/\\d+/);
    if (!match) return {};

    let val = parseInt(match[0]);

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
target_cols = ["HCIII", "HCIV", "HOSPITAL", "RRH"]

for col in target_cols:
    if col in filter_Prop_HRRgns.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)

# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=False,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '12px',
        'line-height': '8px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'display': 'flex',
        'align-items': 'center',
        'padding-top': '0px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '0px', # Optional: reduces space at the bottom of the cell
        'margin-bottom': '0px'
          } 
)
gb.configure_grid_options(domLayout='autoHeight') 
grid_options = gb.build()

# Display the grid and capture the response
grid_response = AgGrid(
    filter_Prop_HRRgns,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='alpine',
    rowHeight=10,
    height=400,
    allow_unsafe_jscode=True 
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='hr_byLvl.csv',
    mime='text/csv'
)

# %% The cadres not available by RRH and cadre

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Proportion of cadres not available by RRH and cadre
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_Prop_CadreRRH_Lvl)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH_Region", pinned="left")

# Wrap long column headers properly
gb.configure_column(
    "RRH_Region",
    headerName="RRH",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode1 = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let valueStr = params.value.toString().trim();

    if (valueStr === "" || valueStr.toLowerCase() === "nan") return {};

    // Extract number (e.g. 33 from "33% (1/3)")
    let match = valueStr.match(/\\d+/);
    if (!match) return {};

    let val = parseInt(match[0]);

    if (val >= 80) {
        return {backgroundColor: '#dc3545', color: 'white'};
    } else if (val >= 50) {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else {
        return {backgroundColor: '#28a745', color: 'white'};
    }
}
""")       

# Columns to color
target_cols = ["HCIII", "HCIV", "HOSPITAL", "RRH"]

for col in target_cols:
    if col in filter_Prop_CadreRRH_Lvl.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode1)

# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=False,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '12px',
        'line-height': '8px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'display': 'flex',
        'align-items': 'center',
        'padding-top': '0px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '0px', # Optional: reduces space at the bottom of the cell
        'margin-bottom': '0px'
          } 
)

gb.configure_grid_options(domLayout='autoHeight') 
grid_options = gb.build()

# Display the grid and capture the response
grid_response = AgGrid(
    filter_Prop_CadreRRH_Lvl,
    gridOptions=grid_options,
     # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='alpine',
    rowHeight=10,
    height=400,
    allow_unsafe_jscode=True 
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='hr_cdreLvl.csv',
    mime='text/csv'
)

# %% Detailed HR

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with Human Resources Detail
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_HRdetail)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")



# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode3 = JsCode("""
function(params) {
    if (params.value === null || params.value === undefined) return {};

    let val = params.value.toString().trim();

    if (val === "Y") {
        return {backgroundColor: '#28a745', color: 'white'};
    } else if (val === "Partial") {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else if (val === "N") {
        return {backgroundColor: '#dc3545', color: 'white'};
    }

    return {};
}
""")

# Columns to color
target_cols = ["The facility possesses all the required cadre categories (See attachment)", 
               "The facility has required cadres, but, in inadequate numbers in the health facility", 
               "The staff receive targeted capacity-building"]

for col in target_cols:
    if col in filter_HRdetail.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode3)

# Wrap long column headers properly
gb.configure_column(
    "The facility possesses all the required cadre categories (See attachment)",
    headerName="All the required cadre categories",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "List of cadre categories unavailable in the facility",
    headerName="Cadres not available",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    cellStyle={
        'fontSize': '8px',     
        'lineHeight': '13px'  
    }
)

gb.configure_column(
    "The facility has required cadres, but, in inadequate numbers in the health facility",
    headerName="Inadequate Cadre numbers in the facility",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


gb.configure_column(
    "List of HR cadres with inadequate numbers",
    headerName="TList of HR cadres with inadequate numbers",
    wrapHeaderText=True,
    autoHeaderHeight=True,
    cellStyle={
        'fontSize': '8px',     
        'lineHeight': '13px'  
    }
)

gb.configure_column(
    "The staff receive targeted capacity-building",
    headerName="Staff receive capacity-building",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '12px',
        'line-height': '14px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)

grid_options = gb.build()

# Display the grid and capture the response
grid_response = AgGrid(
    filter_HRdetail,
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
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='hr_detail_report.csv',
    mime='text/csv'
)




