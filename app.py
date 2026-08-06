import streamlit as st
import pandas as pd
import numpy as np
import random

# ==============================================================================
# 1. APP CONFIGURATION & STYLES
# ==============================================================================
st.set_page_config(
    page_title="Mirage AI Distribution & Logistics Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean, modern UI styling
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    .kpi-card {
        background-color: #0f172a;
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        color: white;
    }
    .kpi-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. SESSION STATE DATASTORE
# ==============================================================================
def init_session_state():
    if "zones_dict" not in st.session_state:
        st.session_state.zones_dict = {
            "North District (Zone 1)": {"lat": 30.0800, "lon": 31.2800},
            "Central Metropolitan (Zone 2)": {"lat": 30.0444, "lon": 31.2357},
            "East Industrial Sector (Zone 3)": {"lat": 30.0100, "lon": 31.4000},
            "South District (Zone 4)": {"lat": 29.9600, "lon": 31.2500},
            "West Suburban Corridor (Zone 5)": {"lat": 30.0200, "lon": 31.1200}
        }

    if "inventory_df" not in st.session_state:
        st.session_state.inventory_df = pd.DataFrame([
            {"SKU": "PRT-WASH-101", "Part Name": "Direct Drive Drain Pump Motor", "Category": "Washing Machines", "Bin Location": "Aisle 3 - Shelf B", "Stock Qty": 42, "Min Threshold": 15},
            {"SKU": "PRT-FRIG-204", "Part Name": "Inverter Compressor Start Relay", "Category": "Refrigeration", "Bin Location": "Aisle 1 - Shelf D", "Stock Qty": 8, "Min Threshold": 20},
            {"SKU": "PRT-HVAC-502", "Part Name": "Dual Run Capacitor 45/5 MFD", "Category": "HVAC", "Bin Location": "Aisle 5 - Shelf A", "Stock Qty": 115, "Min Threshold": 30},
            {"SKU": "PRT-OVN-901", "Part Name": "Commercial Igniter Assembly", "Category": "Commercial Cooking", "Bin Location": "Aisle 8 - Shelf C", "Stock Qty": 14, "Min Threshold": 10}
        ])

    if "technicians_df" not in st.session_state:
        st.session_state.technicians_df = pd.DataFrame([
            {"Tech ID": "TECH-101", "Name": "Marcus Vance", "Assigned Zone": "North District (Zone 1)", "Primary Skill": "Refrigeration", "Active Jobs": 3, "Max Capacity": 5, "lat": 30.0820, "lon": 31.2850},
            {"Tech ID": "TECH-102", "Name": "Ahmed Hassan", "Assigned Zone": "Central Metropolitan (Zone 2)", "Primary Skill": "Washing Machines", "Active Jobs": 4, "Max Capacity": 6, "lat": 30.0460, "lon": 31.2380},
            {"Tech ID": "TECH-103", "Name": "David Miller", "Assigned Zone": "East Industrial Sector (Zone 3)", "Primary Skill": "Commercial Cooking", "Active Jobs": 1, "Max Capacity": 4, "lat": 30.0120, "lon": 31.4050}
        ])

    if "work_orders_df" not in st.session_state:
        st.session_state.work_orders_df = pd.DataFrame([
            {"Ticket ID": "WO-8801", "Client Name": "Grand Plaza Hotel", "Appliance Issue": "Walk-in Cooler down", "Zone": "North District (Zone 1)", "Assigned Tech": "Marcus Vance", "Priority": "CRITICAL", "Status": "In Progress", "lat": 30.0780, "lon": 31.2750},
            {"Ticket ID": "WO-8802", "Client Name": "Johnathan Myers", "Appliance Issue": "Washer displaying E4 error", "Zone": "Central Metropolitan (Zone 2)", "Assigned Tech": "Ahmed Hassan", "Priority": "Medium", "Status": "Dispatched", "lat": 30.0410, "lon": 31.2310}
        ])

init_session_state()


# ==============================================================================
# 3. AI MATCHING ENGINE
# ==============================================================================
def smart_ai_dispatch(zone, skill):
    techs = st.session_state.technicians_df.copy()
    if techs.empty:
        return "No Techs Available", "N/A", 0
    
    scores = []
    for _, tech in techs.iterrows():
        score = 50.0
        if tech["Assigned Zone"] == zone:
            score += 30.0
        if skill.lower() in str(tech["Primary Skill"]).lower():
            score += 20.0
        
        # Capacity availability bonus
        if tech["Active Jobs"] < tech["Max Capacity"]:
            score += 15.0
        else:
            score -= 20.0
            
        scores.append((tech["Name"], tech["Tech ID"], score))

    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[0]


# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.title("⚡ AI Distributor Hub")
st.sidebar.caption("Logistics & Dispatch Management")

nav_choice = st.sidebar.radio(
    "Select Module",
    [
        "🗺️ Interactive Map",
        "🤖 AI-Powered Distributor",
        "📦 Logistics Center",
        "ℹ️ Central Info Hub"
    ]
)

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Reset Application Data"):
    st.session_state.clear()
    init_session_state()
    st.rerun()


# ==============================================================================
# MODULE 1: INTERACTIVE MAP
# ==============================================================================
if nav_choice == "🗺️ Interactive Map":
    st.title("🗺️ Geographic Dispatch & Ticket Map")
    st.markdown("Visual map tracking technician lines and active work orders.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Active Orders Mapped</div><div class="kpi-value">{len(st.session_state.work_orders_df)}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #10b981;"><div class="kpi-title">Technicians in Field</div><div class="kpi-value">{len(st.session_state.technicians_df)}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #8b5cf6;"><div class="kpi-title">Active Zones</div><div class="kpi-value">{len(st.session_state.zones_dict)}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Compile map coordinates
    map_points = []
    for _, t in st.session_state.technicians_df.iterrows():
        if "lat" in t and "lon" in t:
            map_points.append({"lat": t["lat"], "lon": t["lon"]})

    for _, w in st.session_state.work_orders_df.iterrows():
        if "lat" in w and "lon" in w:
            map_points.append({"lat": w["lat"], "lon": w["lon"]})

    if map_points:
        st.map(pd.DataFrame(map_points), latitude="lat", longitude="lon", size=20)
    else:
        st.info("No location points uploaded yet.")


# ==============================================================================
# MODULE 2: AI-POWERED DISTRIBUTOR
# ==============================================================================
elif nav_choice == "🤖 AI-Powered Distributor":
    st.title("🤖 AI-Powered Smart Dispatch Engine")
    st.markdown("Instantly distribute incoming work orders to the optimal technician line.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🎯 Dispatch Matcher")
        sel_zone = st.selectbox("Select Delivery/Service Zone", list(st.session_state.zones_dict.keys()))
        sel_skill = st.selectbox("Required Machine Skill", ["Refrigeration", "Washing Machines", "HVAC", "Commercial Cooking"])
        
        if st.button("⚡ Run AI Dispatch Match"):
            best_tech, tech_id, score = smart_ai_dispatch(sel_zone, sel_skill)
            st.success(f"**Recommended Technician:** {best_tech} ({tech_id})")
            st.info(f"**AI Match Score:** {score:.0f}/100")

    with col2:
        st.subheader("📋 Technician Capacity Lines")
        st.dataframe(
            st.session_state.technicians_df[["Tech ID", "Name", "Assigned Zone", "Primary Skill", "Active Jobs", "Max Capacity"]],
            use_container_width=True,
            hide_index=True
        )


# ==============================================================================
# MODULE 3: LOGISTICS CENTER
# ==============================================================================
elif nav_choice == "📦 Logistics Center":
    st.title("📦 Logistics & Inventory Center")
    st.markdown("Manage spare parts, stock levels, and bin locations.")

    # Low Stock Alerts
    low_stock = st.session_state.inventory_df[st.session_state.inventory_df["Stock Qty"] <= st.session_state.inventory_df["Min Threshold"]]
    if not low_stock.empty:
        st.warning(f"⚠️ **Logistics Alert:** {len(low_stock)} items are at or below minimum reorder thresholds!")

    st.subheader("Inventory Master List")
    edited_inv = st.data_editor(st.session_state.inventory_df, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Stock Changes"):
        st.session_state.inventory_df = edited_inv
        st.success("Logistics inventory updated!")


# ==============================================================================
# MODULE 4: CENTRAL INFO HUB
# ==============================================================================
elif nav_choice == "ℹ️ Central Info Hub":
    st.title("ℹ️ Central Info Hub & Bulk Import Gateway")
    st.markdown("Upload bulk files or manage and edit active work order records in an Excel-like grid.")

    tab1, tab2 = st.tabs(["📤 Bulk File Uploads", "📝 Active Work Tickets (Excel Editor)"])

    with tab1:
        st.subheader("Upload CSV / Excel Data Files")
        upload_type = st.selectbox("Select Target Dataset", ["Technicians", "Work Orders", "Inventory"])
        uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.write("Uploaded Data Preview:", df_up.head())
                
                if st.button("Confirm Data Import"):
                    if upload_type == "Technicians":
                        st.session_state.technicians_df = pd.concat([st.session_state.technicians_df, df_up], ignore_index=True)
                    elif upload_type == "Work Orders":
                        st.session_state.work_orders_df = pd.concat([st.session_state.work_orders_df, df_up], ignore_index=True)
                    elif upload_type == "Inventory":
                        st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, df_up], ignore_index=True)
                    st.success(f"Successfully imported {len(df_up)} records into {upload_type}!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with tab2:
        st.subheader("Interactive Work Order Grid")
        st.markdown("Edit ticket status, client info, or assign technicians directly in the cells below.")
        
        edited_orders = st.data_editor(
            st.session_state.work_orders_df,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        if st.button("💾 Save Work Order Changes"):
            st.session_state.work_orders_df = edited_orders
            st.success("Work orders updated successfully!")
