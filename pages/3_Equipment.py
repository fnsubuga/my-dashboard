# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 09:36:57 2026

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
    page_title="Equipment",
    page_icon="D:/CPHL-MOH/pics/MoH_logo.png",
    layout="wide"
)

# %% Functions
# extract value from mixed cell, e.g. 45% (2/5)

def extract_percent(x):
    if pd.isna(x) or x == "":
        return np.nan
    return float(x.split("%")[0])

# Color coding
def col_rag(val):
    if pd.isna(val):
        return ""
    elif val < 50:
        return "color:green; font-weight: bold;"
    elif val < 80:
        return "color:#BA8E23; font-weight: bold;"
    else:
        return "color: red; font-weight: bold;"

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
st.markdown('<div class="sticky-header">Equipment Functionality<b> </div>', unsafe_allow_html=True)

# Content spacing
st.markdown('<div class="content">', unsafe_allow_html=True)


# %% Load the data frames
# -----------------------------------------------------
# Load the RRH-Hub Spokes Data
# -----------------------------------------------------
# Health Facilties reached in support supervision
file_path3 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/visit/Linelist_sitesVisited.xls"
Fac_linelist  = pd.read_excel(file_path3)

# Summary of proportions of sites with non-functional equipt, with long donwntime TAT
file_path7 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/EquipNonFntl_LongDowntime.xls"
equip = pd.read_excel(file_path7)

# %age of sites with Equipment not serviced as scheduled
file_path8 = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/sites_Equip_nonServd_Scheduled.xls"
sche_ser = pd.read_excel(file_path8)

# list of equipment categories not serviced as scheduled
file_path9  =  "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/list_Equip_non_serviced.xls"
equipsche  = pd.read_excel(file_path9)

# List of equipment categories not sericed as scheduled by RRH
file_path10  = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/list_Equip_non_serviced_rrh.xls"
rrhEquipSer =  pd.read_excel(file_path10)

# equipment with prplonged downtime (all)
file_path13  = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/equipment_wc_long_downtime.xls"
EqpLng_Dtme =  pd.read_excel(file_path13)

# %age of sites reporting equipment with prplonged downtime
file_path14  = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/pctSites_longDtime_rrh.xls"
rrhlongdtime =  pd.read_excel(file_path14)

# list of equipment with prplonged downtime by RRH
file_path12  = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/equipment_wc_long_downtimeRRH.xls"
longdtime =  pd.read_excel(file_path12)


# Detailed equipment table
file_path11  = "D:/Python/dashboard/dashboard/SupportSupervisionRpt/Data/Jan_March/Equipt/equipment_detail.xls"
equip_detail =  pd.read_excel(file_path11)

# %% renaming and further cleaning
# RRH not services as scheduled
sche_ser  =  sche_ser.rename(columns = {
    "Proportion of sites with equipment not serviced as scheduled" : "Pct_Unsevcd"
    
        })

# select columns of interest
sche_ser = sche_ser[[
    "RRH", "Yr", "Qtr", "Pct_Unsevcd"
    ]]

# RRH Long downtime
rrhlongdtime  =  rrhlongdtime.rename(columns = {
    "%age of sites with long Equip. Downtime"  :  "Pct_LndDT"
        })
# select columns of interest
rrhlongdtime  =  rrhlongdtime[[
    "RRH", "Yr", "Qtr", "Pct_LndDT"
    ]]

# Equipment with Long downtime by RRH
longdtime   =  longdtime.rename(columns = {
    "No.sites_withLongDT"  :  "No_sites_withLongDT"
        })


# %% Common filter
# -----------------------------------------------------
# Sidebar Filter for all tables
# -----------------------------------------------------
# Apply the filter for all table

# Define Hub Name
RRH_list = sorted(Fac_linelist["RRH"].dropna().unique().tolist())
Yr_list  = sorted(Fac_linelist["Yr"].dropna().unique().tolist())
Qtr_list  = sorted(Fac_linelist["Qtr"].dropna().unique().tolist())

with st.sidebar:
    st.header("Filters", divider=True)
    
    selected_RRH = st.selectbox("RRH:", ["All"] + RRH_list, key="select_rrh")
    
    selected_Yr = st.selectbox("Yr:", ["All"] + Yr_list, key="select_yr")
    
    selected_Qtr = st.selectbox("Qtr:", ["All"] + Qtr_list, key="select_qtr")

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
    "rrh_Equipt_status": equip,
    "rrh_untimelySche": sche_ser,
    "rrh_eqpt_untimeSche" :rrhEquipSer,
    "Eqpt_lngDntime" :  EqpLng_Dtme,
    "Nat_equip_ser":equipsche,
    "rrh_longdtime" : longdtime,
    "rrh_PctLng_DT" : rrhlongdtime,
    "equip_Detail" :  equip_detail
     
        }

filtered_tables = {
    name: apply_filters (table, selected_RRH,selected_Yr, selected_Qtr)
    for name, table in tables.items()
}

# -----------------------------------------------------
# Access filtered tables
# -----------------------------------------------------
filter_rrh_Equipt_status = filtered_tables["rrh_Equipt_status"]
filter_rrh_untimelySche = filtered_tables["rrh_untimelySche"]
filter_rrh_eqpt_untimeSche = filtered_tables["rrh_eqpt_untimeSche"]
filter_Eqpt_lngDntime = filtered_tables["Eqpt_lngDntime"]
filter_Nat_equip_ser = filtered_tables["Nat_equip_ser"]
filter_rrh_longdtime = filtered_tables["rrh_longdtime"]
filter_rrh_PctLng_DT = filtered_tables["rrh_PctLng_DT"]
filter_equip_Detail = filtered_tables["equip_Detail"]

# %% List of equipment categories not serviced as scheduled
# rename columns
equipsche = equipsche.rename(columns = {
    "No.sites_withunserviced": "No_sites_unserviced"
    })   


# %% List of equipment with prolonged downtime
# rename columns
longdtime = longdtime.rename(columns = {
    "No.sites_withLongDT": "No_sites_withLongDT",
    "Equipment Category with >30 Day downtime": "Equipment Category"
    })   

# %% Combine the graphs, side by side
graph1, graph2 = st.columns(2)

with graph1: # No. of sites with equipment not serviced as scheduled
    st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Most Common Equipment Categories unserviced as scheduled (National)
    </h2>
    """, 
    unsafe_allow_html=True
)

 # -----------------------------
    # Apply filters (Yr and Qtr)
    # -----------------------------
    filter_Nat_equip_ser = apply_filters(
        equipsche,
        rrh="All",              # force National (ignore RRH filter)
        yr=selected_Yr,
        qtr=selected_Qtr
    )

    # -----------------------------
    # Aggregate AFTER filtering
    # -----------------------------
    filter_Nat_equip_ser = filter_Nat_equip_ser.groupby(
        "Equipment",
        as_index=False
    )["No_sites_unserviced"].sum()

    # -----------------------------
    # Sort values
    # -----------------------------
    filter_Nat_equip_ser = filter_Nat_equip_ser.sort_values(
        by="No_sites_unserviced",
        ascending=False
    )

    # -----------------------------
    # Create the graph
    # -----------------------------
    chart = alt.Chart(filter_Nat_equip_ser).mark_bar().encode(
        y=alt.Y(
            "Equipment:N",
            sort="-x",
            axis=alt.Axis(
                labelLimit=300,
                labelFontSize=11
            )
        ),
        x=alt.X(
            "No_sites_unserviced:Q",
            axis=alt.Axis(format="d"),
            title="Number of Sites with Unserviced Equipment"
        ),
        tooltip=["Equipment", "No_sites_unserviced"]
    )

    # -----------------------------
    # Display
    # -----------------------------
    st.altair_chart(chart, use_container_width=True)
    
with graph2: # No. of sites with Equipment with long downtime
 st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Most Common Equipment Categories with long (>30day) equipment downtime (National)
    </h2>
    """, 
    unsafe_allow_html=True
)

# -----------------------------
   # Apply filters (Yr and Qtr)
   # -----------------------------
 filter_Eqpt_lngDntime = apply_filters(
       longdtime,
       rrh="All",              # force National (ignore RRH filter)
       yr=selected_Yr,
       qtr=selected_Qtr
   )

   # -----------------------------
   # Aggregate AFTER filtering
   # -----------------------------
 filter_Eqpt_lngDntime = filter_Eqpt_lngDntime.groupby(
       "Equipment",
       as_index=False
   )["No_sites_withLongDT"].sum()

   # -----------------------------
   # Sort values
   # -----------------------------
 filter_Eqpt_lngDntime = filter_Eqpt_lngDntime.sort_values(
       by="No_sites_withLongDT",
       ascending=False
   )

   # -----------------------------
   # Create the graph
   # -----------------------------
 chart = alt.Chart(filter_Eqpt_lngDntime).mark_bar().encode(
       y=alt.Y(
           "Equipment:N",
           sort="-x",
           axis=alt.Axis(
               labelLimit=300,
               labelFontSize=11
           )
       ),
       x=alt.X(
           "No_sites_withLongDT:Q",
           axis=alt.Axis(format="d"),
           title="Number of Sites with Equipment with long (>30 Day) TAT"
       ),
       tooltip=["Equipment", "No_sites_withLongDT"]
   )

   # -----------------------------
   # Display
   # -----------------------------
 st.altair_chart(chart, use_container_width=True)




# %% %age of facilities with equipment with long (>30 Days) Downtime RRH

# apply the styling

gb1 = GridOptionsBuilder().from_dataframe(filter_rrh_PctLng_DT)

# Enable filtering
gb1.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb1.configure_column("RRH", pinned="left")



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
        return {backgroundColor: '#dc3545', color: 'white'};
    } else if (val >= 50) {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else {
        return {backgroundColor: '#28a745', color: 'white'};
    }
}
""")

# Columns to color
target_cols = ["Pct_LndDT"]


for col in target_cols:
    if col in filter_rrh_PctLng_DT.columns:
        gb1.configure_column(col, cellStyle=cellstyle_jscode)
        
# Wrap long column headers

# column: %age labs with all the required lab cadres
gb1.configure_column(
    "Pct_LndDT",
    headerName="%age labs",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# Configure default column behavior
gb1.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'line-height': '12px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)
gb1.configure_grid_options(domLayout='normal') 
grid_options1 = gb1.build()


# %% %age of facilities with equipment not serviced as scheduled RRH

# apply the styling

gb2 = GridOptionsBuilder().from_dataframe(filter_rrh_untimelySche)

# Enable filtering
gb2.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb2.configure_column("RRH", pinned="left")

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
        return {backgroundColor: '#dc3545', color: 'white'};
    } else if (val >= 50) {
        return {backgroundColor: '#ffc107', color: 'black'};
    } else {
        return {backgroundColor: '#28a745', color: 'white'};
    }
}
""")

# Columns to color
target_cols = ["Pct_Unsevcd"]


for col in target_cols:
    if col in filter_rrh_untimelySche.columns:
        gb2.configure_column(col, cellStyle=cellstyle_jscode)
        
# column: %age labs with all the required lab cadres
gb2.configure_column(
    "Pct_Unsevcd",
    headerName="%age labs",
    wrapHeaderText=True,
    autoHeaderHeight=True
)


# Configure default column behavior
gb2.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'line-height': '12px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)
gb2.configure_grid_options(domLayout='normal') 
grid_options2 = gb2.build()


# %% Side by Side Table, Equip Ser and Downtime report

col1, col2 = st.columns(2)
# Table 1: long downtime

with col1:
    st.markdown(
        """
        <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
            %age of labs with equipment with long (>30 Days) Downtime, by RRH
        </h2>
        """, 
        unsafe_allow_html=True
    )
    
 # Display the grid and capture the response
    grid_response1 = AgGrid(
        filter_rrh_PctLng_DT,
        gridOptions=grid_options1,
        # for downloading
        data_return_mode="FILTERED_AND_SORTED", 
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        theme='alpine',
        allow_unsafe_jscode=True
    )

    # Add the Download Button
    # Extract the data currently shown in the grid (post-filter/sort)
    df_download1 = grid_response1['data']

    st.download_button(
        "📥 Download Table",
        df_download1.to_csv(index=False).encode('utf-8'),
        "rrh_lngDtime.csv",
        "text/csv"
    )
    
# Table 2: unserviced
with col2:
    
 st.markdown(
        """
        <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
            %age of labs with equipment not serviced as scheduled, by RRH
        </h2>
        """, 
        unsafe_allow_html=True
    )
# Display the grid and capture the response
 grid_response2 = AgGrid(
    filter_rrh_untimelySche,
    gridOptions=grid_options2,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    theme='alpine',
    allow_unsafe_jscode=True
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)

 df_download2 = grid_response2['data']

 st.download_button(
     "📥 Download Table",
     df_download2.to_csv(index=False).encode('utf-8'),
     "rrh_unserd.csv",
     "text/csv"
)
   
# %% List of equipment with long downtime by RRH

gb4 = GridOptionsBuilder().from_dataframe(filter_rrh_longdtime)

# Enable filtering
gb4.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb4.configure_column("RRH", pinned="left")



# Wrap long column headers
# column: No_sites_withLongDT
gb4.configure_column(
    "No_sites_withLongDT",
    headerName="No. of labs",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: No_sites_withLongDT
gb4.configure_column(
    "Equipment",
    headerName="Equipment",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# Configure default column behavior
gb4.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'line-height': '14px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)

grid_options4 = gb4.build()


# %% List of equipment with unserviced equipment by RRH

gb3 = GridOptionsBuilder().from_dataframe(filter_rrh_eqpt_untimeSche)

# Enable filtering
gb3.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb3.configure_column("RRH", pinned="left")



# Wrap long column headers
# column: No_sites_withLongDT
gb3.configure_column(
    "No.sites_withunserviced",
    headerName="No. of labs",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

# column: No_sites_withLongDT
gb3.configure_column(
    "Equipment",
    headerName="Equipment",
    wrapHeaderText=True,
    autoHeaderHeight=True
)



# Configure default column behavior
gb3.configure_default_column(
    wrapText=True,              # Enable text wrapping
    autoHeight=True,            # Adjust row height to fit wrapped text
    cellStyle={
        'font-size': '10px',
        'line-height': '14px',  # Forces lines closer together (try 1.0 or 1.2 as well)
        'padding-top': '2px',   # Optional: reduces space at the top of the cell
        'padding-bottom': '2px' # Optional: reduces space at the bottom of the cell
          } 
)

grid_options3 = gb3.build()



# %% Side by Side table: RRH equipment cats. not serviced, long downtime
col1, col2 = st.columns(2)

# Table 1: long downtime

with col1:
 st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        No. of sites with equipment with long downtime by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)


# Display the grid and capture the response
 grid_response4 = AgGrid(
    filter_rrh_longdtime,
    gridOptions=grid_options4,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine'
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
 df_to_download4 = grid_response4['data']

 st.download_button(
    label="📥 Download Table",
    data=df_to_download4.to_csv(index=False).encode('utf-8'),
    file_name='equip_catRRH.csv',
    mime='text/csv'
)


# Table not serviced

with col2:
 st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        No. of sites with equipment not services as scheduled, by RRH
    </h2>
    """, 
    unsafe_allow_html=True
)

# Display the grid and capture the response
 grid_response3 = AgGrid(
    filter_rrh_eqpt_untimeSche,
    gridOptions=grid_options3,
    # for downloading
    data_return_mode="FILTERED_AND_SORTED", 
    fit_columns_on_grid_load=True,
    theme='alpine'
)

# Add the Download Button
# Extract the data currently shown in the grid (post-filter/sort)
 df_to_download3 = grid_response3['data']

 st.download_button(
    label="📥 Download Table",
    data=df_to_download3.to_csv(index=False).encode('utf-8'),
    file_name='equip_unservdRRH.csv',
    mime='text/csv'
)

# %% Detailed equipment report

filtered_equip_detail   =  filter_equip_Detail

st.markdown(
    """
    <h2 style='font-size: 14px; font-family: sans-serif; font-weight: bold;'>
        Health Facility Line list with Equipment Detail
    </h2>
    """, 
    unsafe_allow_html=True
)


gb = GridOptionsBuilder().from_dataframe(filtered_equip_detail)

# Enable filtering
gb.configure_default_column(filter = True, sortable=True)

# Freeze RRH column
gb.configure_column("RRH", pinned="left")

# Wrap long column headers properly
gb.configure_column(
    "HFacility",
    headerName="Facility Name",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "VDate",
    headerName="Visit Date",
    wrapHeaderText=True,
    autoHeaderHeight=True
)
gb.configure_column(
       "District",
       headerName="District",
       wrapHeaderText=True,
       autoHeaderHeight=True
   ) 

gb.configure_column(
       "Equipment",
       headerName="Equipment Category",
       wrapHeaderText=True,
       autoHeaderHeight=True
   ) 
    

gb.configure_column(
    "No. of equipment not serviced as scheduled",
    headerName="Untimely Service",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "No. of equipment not functional",
    headerName="Non-Functional",
    wrapHeaderText=True,
    autoHeaderHeight=True
)

gb.configure_column(
    "No. of equipment with equipment downtime > 30 days",
    headerName=">30 Day Downtime",
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
    filtered_equip_detail,
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
    file_name='equipment_report.csv',
    mime='text/csv'
)

