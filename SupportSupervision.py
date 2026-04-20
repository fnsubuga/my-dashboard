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
st.subheader("Number of health labs visited")

st.dataframe(TlVisit)  # should show

gb = GridOptionsBuilder.from_dataframe(TlVisit)
gb.configure_default_column(filter=True, sortable=True)

grid_options = gb.build()

AgGrid(
    TlVisit,
    gridOptions=grid_options,
    height=100,
    theme="streamlit"
)

#######################################################################################################
#######################################################################################################
# %% Total sites visited, and by RRH

st.subheader("Number of health labs visited")

st.dataframe(filter_RRH_Vslvl)  # should show

gb = GridOptionsBuilder.from_dataframe(filter_RRH_Vslvl)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

grid_options = gb.build()

# ✅ Capture response
grid_response = AgGrid(
    filter_RRH_Vslvl,
    gridOptions=grid_options,
    height=400,
    theme="streamlit"
)

# ✅ Extract displayed data
df_to_download = pd.DataFrame(grid_response['data'])

# ✅ Download button
st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='rrh_sites1.csv',
    mime='text/csv'
)

####################################################################################################
#####################################################################################################
#### %% Line list of health facilities visited ####

st.subheader("Line list of health facilities visited")

st.dataframe(filter_Fac_linelist)  # should show

gb = GridOptionsBuilder.from_dataframe(filter_Fac_linelist)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

grid_options = gb.build()

# ✅ Capture response
grid_response = AgGrid(
    filter_Fac_linelist,
    gridOptions=grid_options,
    height=400,
    theme="streamlit"
)

# ✅ Extract displayed data
df_to_download = pd.DataFrame(grid_response['data'])

# ✅ Download button
st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='rrh_sites1ist.csv',
    mime='text/csv'
)
#######################################################################################################

