# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:36:25 2026

@author: HP
"""

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# -----------------------------------------------------
# Streamlit Page Config
# -----------------------------------------------------
st.set_page_config(
    page_title="Support Supervision Report",
    page_icon="D:/CPHL-MOH/pics/MoH_logo.png",
    layout="wide"
)

st.title("Support Supervision Report")



st.markdown("""
            The suppport supervision report 
    
            """
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
st.markdown('<div class="sticky-header">The suppport supervision report<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load data 

# Total sites visited
file_path = "Data/visit/TotalSites_Visited.xlsx"
TlVisit  =  pd.read_excel(file_path)

# Total sites visited, and by RRH
file_path1 = "Data/visit/RRH_SitesVisited_level.xlsx"
visits  = pd.read_excel(file_path1)

# Total visited by level
file_path2 = "Data/visit/TotalSites_level.xlsx"
VLevel  = pd.read_excel(file_path2)

# Line list of visited facilities
file_path3 = "Data/visit/Linelist_sitesVisited.xlsx"
Fac_linelist  = pd.read_excel(file_path3)

# KPI summary table
file_path4 = "KPI_Summary.xlsx"
KPIs  = pd.read_excel(file_path4)

# %% Filters
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(visits["RRH"].dropna().unique().tolist())

indicator_list  = sorted(KPIs["Indicator"].dropna().unique().tolist())

Yr_list  = sorted(Fac_linelist["Yr"].dropna().unique().tolist())

Qtr_list  = sorted(Fac_linelist["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH Region:", ["All"] + RRH_list, key="select_rrh")
    
    selected_Indicator = st.selectbox("Indicator:", ["All"] + indicator_list, key="select_ind")
    
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list, key="select_yr")
    
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")

  
# -----------------------------------------------------
# Reusable filter function
# -----------------------------------------------------
def apply_filters(df, indicator, rrh, yr, qtr):
    df_filtered = df.copy()
    
    # Filter by RRH if column exists and not "All"
    if "RRH" in df_filtered.columns and rrh != "All":
        df_filtered = df_filtered[df_filtered["RRH"] == rrh]
          
    # Filter by Indicator if column exists and not "All"
    if "Indicator" in df_filtered.columns and indicator != "All":
        df_filtered = df_filtered[df_filtered["Indicator"] == indicator]
        
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
# 1. Define the dictionary of original tables FIRST
tables = {
    "RRH_visits": visits,
    "RRH_linelist":  Fac_linelist,
    "kpi_sumry":    KPIs,
    "RRH_Vslvl":    VLevel 
    
}

# Now apply the filter
filtered_tables = {
    name: apply_filters(table, selected_Indicator, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# 3. Access the results
filter_RRH_visits = filtered_tables["RRH_visits"]
filter_Fac_linelist = filtered_tables["RRH_linelist"]
filter_kpi_sumry = filtered_tables["kpi_sumry"]
filter_RRH_Vslvl = filtered_tables["RRH_Vslvl"]

##################################################################################################
##################################################################################################
# %% No. sites visited (National)
st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Number of health labs visited
    </h2>
    """, 
    unsafe_allow_html=True
)
# change Yr type to String
TlVisit["Yr"]  = TlVisit["Yr"].astype(str)

# The table
gb = GridOptionsBuilder().from_dataframe(TlVisit)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("Yr", pinned="left")


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
    TlVisit,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine'
)

#######################################################################################################
#######################################################################################################
# %% Total sites visited, and by RRH

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Number of health labs visited by RRH, and health level
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_RRH_Vslvl)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")


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
    filter_RRH_Vslvl,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine',
    height=300 
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='rrh_sites1.csv',
    mime='text/csv'
)

# %% Line list of health facilities visited

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Linelist of health facilities visited by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filter_Fac_linelist)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")


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
    filter_Fac_linelist,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine',
    height=300 
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='sites_visited.csv',
    mime='text/csv'
)
