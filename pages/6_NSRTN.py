# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 15:13:54 2026

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
    page_title="NSRTN",
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
st.markdown('<div class="sticky-header">National Sample and Results Transport Network (NSRTN)<b> </div>', unsafe_allow_html=True)

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

# NSRTN KPIs
file_path21 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/nsrtn/nsrtn_kpis.xls"
NSRTN_KPIs  =  pd.read_excel(file_path21)

# NSRTN Details
file_path20 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/nsrtn/nsrtn_details.xls"
NSRTN_Details  =  pd.read_excel(file_path20)



# %% Common filter (RRH)
# Sidebar Filter for all tables

# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(NSRTN_KPIs["RRH"].dropna().unique().tolist())
Yr_list  = sorted(NSRTN_KPIs["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(NSRTN_KPIs["Qtr"].dropna().unique().tolist())

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
# 1. Define the dictionary of original tables FIRST
tables = {
    "RRH_NSRTNKpis": NSRTN_KPIs,
    "NSRTN_Detail":  NSRTN_Details
}

# apply the filter to that dictionary
filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# 3. Access the results
filter_NSRTN_KPIs = filtered_tables["RRH_NSRTNKpis"]
filter_NSRTN_Detail = filtered_tables["NSRTN_Detail"]


# %% NSRTN KPI list, by RRH Region
# apply the styling

st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           NSRTN KPI Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_NSRTN_KPIs)

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
target_cols = ["%age of labs visited by sample transporter as scheduled", 
               "%age of hubs with bikes timely serviced and fueled", 
               "%age of labs indicating to attain the targeted Results receipt TAT",
               "%age of labs indicating to refer samples within targeted TAT",
               "%age of labs with acceptable rejection rates"
               ]


for col in target_cols:
    if col in filter_NSRTN_KPIs.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs visited by sample transporter as scheduled",
    headerName="%age of labs visited by sample transporter as scheduled",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of hubs with bikes timely serviced and fueled",
    headerName="%age of hubs with bikes timely serviced and fueled",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs indicating to attain the targeted Results receipt TAT",
    headerName="%age of labs achieving targeted Results receipt TAT",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs indicating to refer samples within targeted TAT",
    headerName="%age of labs indicating to refer samples within targeted TAT",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "%age of labs with acceptable rejection rates",
    headerName="%age of labs with acceptable rejection rates",
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
       filter_NSRTN_KPIs,
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
       "nsrtn.csv",
       "text/csv"
   )

# %% NSRTN Detailed table

st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           NSRTN Health Facility Line List, NSRTN Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_NSRTN_Detail)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")



# -----------------------------
# Conditional Coloring 
# -----------------------------
cellstyle_jscode = JsCode("""
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

# Columns to color
target_cols = ["scheduledVst", "bike_service_fueled", "TAT_withinTarget", "Refer_timely", "RejtRate"]


for col in target_cols:
    if col in filter_NSRTN_Detail.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers
# column: scheduledVst
gb.configure_column(
    "District",
    headerName="District",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: bike_service_fueled
gb.configure_column(
    "HFacility",
    headerName="Health Facility",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: bike_service_fueled
gb.configure_column(
    "VDate",
    headerName="Visit Date",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: scheduledVst
gb.configure_column(
    "scheduledVst",
    headerName="Scheduled Sample Transporter Visit",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: bike_service_fueled
gb.configure_column(
    "bike_service_fueled",
    headerName="Bikes fueled as serviced as required (Where Applicable)",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: TAT_withinTarget
gb.configure_column(
    "TAT_withinTarget",
    headerName="Timely sample receipt TAT",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: Refer_timely
gb.configure_column(
    "Refer_timely",
    headerName="Timely Sample Referral TAT",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# column: RejtRate
gb.configure_column(
    "RejtRate",
    headerName="%Acceptable sample rejection rate",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# Configure default column behavior
gb.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    
    headerClass="small-header",
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
       filter_NSRTN_Detail,
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
       "nsrtn_detail.csv",
       "text/csv"
   )

