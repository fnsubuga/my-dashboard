# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 10:12:30 2026

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
    page_title="QMS",
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
st.markdown('<div class="sticky-header">Quality Management Systems (QMS)<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load the data frames
# -----------------------------------------------------
# Load the RRH-Hub Spokes Data
# -----------------------------------------------------

# Summary of KPI indicators

file_path13 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/QMS/QMS_KPIs_RRH.xls"
qms = pd.read_excel(file_path13)

# QMS Detailed Table
file_path14 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/QMS/QMS_details_RRH.xls"
QMSDetail = pd.read_excel(file_path14)

# %age of sites with major tests enrolled onto EQA scheme
file_path15 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/QMS/MajorTests_onEQA.xls"
TestsEQA  =  pd.read_excel(file_path15)

# Tests without EQA Schemes
file_path15 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/QMS/testNotonEQA.xls"
NotestEQA  =  pd.read_excel(file_path15)

# Tests without EQA Schemes by RRH
file_path15 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/QMS/testNotonEQA_RRH.xls"
NotestEQArrh  =  pd.read_excel(file_path15)


# %% Further clean
TestsEQA  = TestsEQA[[
    "RRH", "Yr", "Qtr","Pct_EQASites"
    ]]

# rename columns
NotestEQArrh  =  NotestEQArrh.rename(columns = {
    "Tests Not enrolled onto an EQA Scheme": "NotEnrolled",
    "No.sites_withoutEQA":  "No_sites_withoutEQA"
    })


NotestEQA   =   NotestEQA.rename(columns  = {
    "No.sites_withoutEQA"  :  "No_sites_withoutEQA",
    "Tests Not enrolled onto an EQA Scheme": "NotEnrolled"
    })


# %% Common filter

# Sidebar Filter for all tables

# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(QMSDetail["RRH"].dropna().unique().tolist())
Yr_list  = sorted(QMSDetail["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(QMSDetail["Qtr"].dropna().unique().tolist())


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
     "QMSKPIs" :   qms,
    "QMS_DetailedTbl": QMSDetail,
    "RRH_EQAScheme":  NotestEQArrh,
    "rrh_EQAPerform" : TestsEQA,
    "NoEQA":  NotestEQA
        }

filtered_tables = {
    name: apply_filters(table, selected_RRH, selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_QMSKPIs = filtered_tables["QMSKPIs"]
filter_QMS_DetailedTbl = filtered_tables["QMS_DetailedTbl"]
filter_rrh_EQAPerform = filtered_tables["rrh_EQAPerform"]
filter_NoEQA = filtered_tables["NoEQA"]
filter_RRH_EQAScheme = filtered_tables["RRH_EQAScheme"]


# %% QMS status by RRH
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           QMS Status, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_QMSKPIs)

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
target_cols = ["Pct_enrolled", "Pct_QMSAudited", "Pct_ImproveScore"]


for col in target_cols:
    if col in filter_QMSKPIs.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Pct_enrolled",
    headerName="%age labs enrolled onto QMS",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Pct_QMSAudited",
    headerName="%age labs enrolled onto QMS, Audited in last 12 months",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Pct_ImproveScore",
    headerName="%age audited labs with improving QMS Scores",
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
       filter_QMSKPIs,
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
       "QMS.csv",
       "text/csv"
   )


# %% The detailed table
filtered_QMSDetail   =  filter_QMS_DetailedTbl

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with QMS Detail
    </h2>
    """, 
    unsafe_allow_html=True
)
gb = GridOptionsBuilder().from_dataframe(filtered_QMSDetail)

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

    let val = params.value.toString().trim().toUpperCase();

    if (val === "Y") {
        return {backgroundColor: '#28a745', color: 'white'};   // 🔴
    } else if (val === "Partial") {
        return {backgroundColor: '#ffc107', color: 'black'};   // 🟡
    } else if (val === "N") {
        return {backgroundColor: '#dc3545', color: 'white'};   // 🟢
    }

    return {};
}
""")

# Columns to color
target_cols = ["Lab is enrolled onto a QMS Program","Lab is audited at least one in the 12 months preceding this Supervision Visit",
               "Lab registered improving audit scores between succesive QMS Audits"
               ]

for col in target_cols:
    if col in filtered_QMSDetail.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)


# Wrap long column headers properly
gb.configure_column(
    "Lab is enrolled onto a QMS Program",
    headerName="Lab is enrolled onto a QMS Program",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Lab is audited at least one in the 12 months preceding this Supervision Visit",
    headerName="Lab is audited at least one in the last 12 months",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "Lab registered improving audit scores between succesive QMS Audits",
    headerName="Lab registered improving audit scores between succesive QMS Audits",
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
    filtered_QMSDetail,
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
    file_name='QMSDetail_report.csv',
    mime='text/csv'
)


# %% %age of sites with major tests enrolled onto EQA scheme
st.markdown(
       """
       <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
           External Quality Assessment, by RRH
       </h2>
       """, 
       unsafe_allow_html=True
   )

st.header("", divider="rainbow")
          
# apply the styling

gb = GridOptionsBuilder().from_dataframe(filter_rrh_EQAPerform)

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
target_cols = ["Pct_EQASites"]


for col in target_cols:
    if col in filter_rrh_EQAPerform.columns:
        gb.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb.configure_column(
    "Pct_EQASites",
    headerName="%age labs with all major tests enrolled onto an EQA Scheme",
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
       filter_rrh_EQAPerform,
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
       "eqa.csv",
       "text/csv"
   )



# %% National: Tests not on EQA schemes

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Tests not enrolled onto National EQA Schemes
    </h2>
    """, 
    unsafe_allow_html=True
)

 # -----------------------------
    # Apply filters (Yr and Qtr)
    # -----------------------------
filter_NoEQA = apply_filters(
        NotestEQA,
        rrh="All",              # force National (ignore RRH filter)
        yr=selected_Yr,
        qtr=selected_Qtr
    )

# -----------------------------
# Aggregate AFTER filtering
# -----------------------------
filter_NoEQA = filter_NoEQA.groupby(
        "NotEnrolled",
        as_index=False
    )["No_sites_withoutEQA"].sum()

 # -----------------------------
 # Sort values
 # -----------------------------
filter_NoEQA = filter_NoEQA.sort_values(
        by="No_sites_withoutEQA",
        ascending=False
    )

# -----------------------------
# Create the graph
# -----------------------------
chart = alt.Chart(filter_NoEQA).mark_bar().encode(
        y=alt.Y(
            "NotEnrolled:N",
            sort="-x",
            axis=alt.Axis(
                labelLimit=300,
                labelFontSize=11
            )
        ),
        x=alt.X(
            "No_sites_withoutEQA:Q",
            axis=alt.Axis(format="d"),
            title="Number of Sites with major tests not enrolled"
        ),
        tooltip=["NotEnrolled", "No_sites_withoutEQA"]
    )

    # -----------------------------
    # Display
    # -----------------------------
st.altair_chart(chart, use_container_width=True)


# %% Tests not enrolled onto EQA by RRH

filtered_NotestEQArrh   =  filter_RRH_EQAScheme

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list whose major tests are not enrolled onto an EQA Scheme
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filtered_NotestEQArrh)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# Wrap long column headers properly
gb.configure_column(
    "NotEnrolled",
    headerName="Major Test Without EQA Scheme",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "No_sites_withoutEQA",
    headerName="No.of labs without the EQA scheme",
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

grid_options = gb.build()

# Display the grid and capture the response
grid_response = AgGrid(
    filtered_NotestEQArrh,
    gridOptions=grid_options,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='alpine'
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
df_to_download = grid_response['data']

st.download_button(
    label="📥 Download Table",
    data=df_to_download.to_csv(index=False).encode('utf-8'),
    file_name='EQA_report.csv',
    mime='text/csv'
)