import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
import io

# ==============================================================================
# 1. SYSTEM CONFIGURATION & GLOBAL STYLES
# ==============================================================================
st.set_page_config(
    page_title="Mirage Field Logistics & Parts Distribution ERP Hub",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS safely wrapped in python multiline strings
st.markdown("""
    <style>
    /* Main Layout Customization */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Executive Metric Cards */
    .kpi-card {
        background-color: #0f172a;
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
        padding: 1.2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-title {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 0.2rem;
    }
    .kpi-subtext {
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 0.3rem;
    }

    /* Operational Cards */
    .dispatch-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        color: white;
    }

    /* Status Badges */
    .badge-critical { background-color: #ef4444; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: bold; font-size: 0.75rem; }
    .badge-high { background-color: #f97316; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-weight: bold; font-size: 0.75rem; }
    .badge-normal { background-color: #3b82f6; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; }
    .badge-success { background-color: #10b981; color: white; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. SESSION STATE INITIALIZATION (CENTRAL DATASTORE)
# ==============================================================================
def init_session_state():
    # 2.1 Default Operational Zones with Coordinates for Mapping
    if "zones_dict" not in st.session_state:
        st.session_state.zones_dict = {
            "North District (Zone 1)": {"lat": 30.0800, "lon": 31.2800},
            "Central Metropolitan (Zone 2)": {"lat": 30.0444, "lon": 31.2357},
            "East Industrial Sector (Zone 3)": {"lat": 30.0100, "lon": 31.4000},
            "South District (Zone 4)": {"lat": 29.9600, "lon": 31.2500},
            "West Suburban Corridor (Zone 5)": {"lat": 30.0200, "lon": 31.1200}
        }

    # 2.2 Spare Parts Inventory Database
    if "inventory_df" not in st.session_state:
        st.session_state.inventory_df = pd.DataFrame([
            {
                "SKU": "PRT-WASH-101", "Part Name": "Direct Drive Drain Pump Motor", 
                "Category": "Washing Machines", "Target Machine": "Front-Load Washers",
                "Bin Location": "Aisle 3 - Shelf B", "Stock Qty": 42, "Min Threshold": 15, 
                "Unit Cost ($)": 34.50, "Selling Price ($)": 89.99, "Supplier": "Global OEM Parts Co"
            },
            {
                "SKU": "PRT-FRIG-204", "Part Name": "Inverter Compressor Start Relay", 
                "Category": "Refrigeration", "Target Machine": "Commercial & Residential Fridges",
                "Bin Location": "Aisle 1 - Shelf D", "Stock Qty": 8, "Min Threshold": 20, 
                "Unit Cost ($)": 18.00, "Selling Price ($)": 55.00, "Supplier": "ColdTech Logistics"
            },
            {
                "SKU": "PRT-HVAC-502", "Part Name": "Dual Run Capacitor 45/5 MFD", 
                "Category": "HVAC & Air Cooling", "Target Machine": "Split Unit ACs & Heat Pumps",
                "Bin Location": "Aisle 5 - Shelf A", "Stock Qty": 115, "Min Threshold": 30, 
                "Unit Cost ($)": 6.20, "Selling Price ($)": 28.00, "Supplier": "HVAC Component Corp"
            },
            {
                "SKU": "PRT-OVN-901", "Part Name": "Commercial Igniter Assembly", 
                "Category": "Commercial Cooking", "Target Machine": "Restaurant Gas Ranges & Ovens",
                "Bin Location": "Aisle 8 - Shelf C", "Stock Qty": 14, "Min Threshold": 10, 
                "Unit Cost ($)": 45.00, "Selling Price ($)": 135.00, "Supplier": "PyroMaster Equipment"
            }
        ])

    # 2.3 Field Technicians Roster
    if "technicians_df" not in st.session_state:
        st.session_state.technicians_df = pd.DataFrame([
            {
                "Tech ID": "TECH-101", "Name": "Marcus Vance", 
                "Assigned Area/Zone": "North District (Zone 1)", 
                "Primary Skill": "Refrigeration", "Van ID": "VAN-N01", 
                "Active Jobs": 3, "Max Capacity": 5, "Status": "On Field Duty",
                "Line Efficiency (%)": 94.2, "lat": 30.0820, "lon": 31.2850
            },
            {
                "Tech ID": "TECH-102", "Name": "Ahmed Hassan", 
                "Assigned Area/Zone": "Central Metropolitan (Zone 2)", 
                "Primary Skill": "Washing Machines", "Van ID": "VAN-C04", 
                "Active Jobs": 4, "Max Capacity": 6, "Status": "On Field Duty",
                "Line Efficiency (%)": 91.5, "lat": 30.0460, "lon": 31.2380
            },
            {
                "Tech ID": "TECH-103", "Name": "David Miller", 
                "Assigned Area/Zone": "East Industrial Sector (Zone 3)", 
                "Primary Skill": "Commercial Cooking", "Van ID": "VAN-E02", 
                "Active Jobs": 1, "Max Capacity": 4, "Status": "Available",
                "Line Efficiency (%)": 98.0, "lat": 30.0120, "lon": 31.4050
            }
        ])

    # 2.4 Work Orders & Service Tickets
    if "work_orders_df" not in st.session_state:
        st.session_state.work_orders_df = pd.DataFrame([
            {
                "Ticket ID": "WO-8801", "Date": "2026-08-05", "Client Type": "Commercial",
                "Client Name": "Grand Plaza Hotel", "Serial Number": "SN-REF-99201",
                "Appliance Issue": "Walk-in Cooler not maintaining temp",
                "Area Zone": "North District (Zone 1)", "Assigned Tech": "Marcus Vance",
                "Parts Allocated": "PRT-FRIG-204 (x1)", "Priority": "CRITICAL",
                "SLA Remaining (Hrs)": 1.5, "Status": "In Progress", "Est. Revenue ($)": 380.00,
                "lat": 30.0780, "lon": 31.2750
            },
            {
                "Ticket ID": "WO-8802", "Date": "2026-08-06", "Client Type": "Residential",
                "Client Name": "Johnathan Myers", "Serial Number": "SN-WASH-4410",
                "Appliance Issue": "Washer displaying E4 error code",
                "Area Zone": "Central Metropolitan (Zone 2)", "Assigned Tech": "Ahmed Hassan",
                "Parts Allocated": "PRT-WASH-101 (x1)", "Priority": "Medium",
                "SLA Remaining (Hrs)": 6.0, "Status": "Dispatched", "Est. Revenue ($)": 175.00,
                "lat": 30.0410, "lon": 31.2310
            }
        ])

    # 2.5 Reverse Logistics Faulty Parts Returns (Vault)
    if "faulty_returns_df" not in st.session_state:
        st.session_state.faulty_returns_df = pd.DataFrame([
            {
                "Return ID": "RMA-501", "Ticket ID": "WO-8790", "Tech ID": "TECH-101",
                "Tech Name": "Marcus Vance", "Faulty Part SKU": "PRT-FRIG-204",
                "Part Description": "Burnt Compressor Relay", "Van Location": "VAN-N01",
                "Return Status": "In Tech Van (Pending Return)", "Date Collected": "2026-08-04"
            }
        ])

    # 2.6 Appliance Asset History Log (Optional)
    if "asset_history_df" not in st.session_state:
        st.session_state.asset_history_df = pd.DataFrame([
            {
                "Serial Number": "SN-REF-99201", "Owner Name": "Grand Plaza Hotel",
                "Client Type": "Commercial", "Appliance Type": "Walk-In Commercial Cooler",
                "Installation Date": "2022-03-15", "Total Repairs": 2,
                "Last Service Date": "2026-08-05", "Warranty Active": "Yes"
            },
            {
                "Serial Number": "SN-WASH-4410", "Owner Name": "Johnathan Myers",
                "Client Type": "Residential", "Appliance Type": "LG Front-Load Washer",
                "Installation Date": "2023-11-10", "Total Repairs": 1,
                "Last Service Date": "2026-08-06", "Warranty Active": "No"
            }
        ])

init_session_state()


# ==============================================================================
# 3. HELPER ENGINES (AI DISPATCH & UTILITIES)
# ==============================================================================
def run_ai_smart_dispatch(zone, issue_category, required_part_sku):
    """AI Matching Engine to find the best technician line based on Zone, Skill, & Van Capacity."""
    techs = st.session_state.technicians_df.copy()
    
    # 1. Filter by Zone Line
    zone_techs = techs[techs["Assigned Area/Zone"] == zone]
    if zone_techs.empty:
        zone_techs = techs  # Fallback to all if zone line has no techs

    # 2. Filter by Available Capacity
    available_techs = zone_techs[zone_techs["Active Jobs"] < zone_techs["Max Capacity"]]
    if available_techs.empty:
        available_techs = zone_techs

    # 3. Calculate AI Match Score
    scores = []
    for _, tech in available_techs.iterrows():
        score = 50.0  # Base Score
        if tech["Assigned Area/Zone"] == zone:
            score += 25.0
        if issue_category.lower() in str(tech["Primary Skill"]).lower():
            score += 20.0
        score += (100 - tech["Active Jobs"] * 15)  # Capacity bonus
        score += (tech["Line Efficiency (%)"] * 0.1)  # Efficiency bonus
        scores.append((tech["Name"], tech["Tech ID"], score, tech["Assigned Area/Zone"]))

    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[0] if scores else ("Unassigned", "N/A", 0.0, zone)


# ==============================================================================
# 4. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.title("⚙️ Mirage Logistics Hub")
st.sidebar.caption("Service Parts Distribution & Field Dispatch")

nav_choice = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Executive Command & GIS Map",
        "📥 Central Data Import Gateway",
        "🚛 Technician Lines & AI Dispatch Engine",
        "📈 Logistics, SLA & Performance Analytics",
        "📝 Service Tickets & Appliance History",
        "📦 Appliance Parts Catalog & Auto PO",
        "🚐 Fleet Van Stock & Faulty Part Returns",
        "💰 Financial Rates & Custom Rules"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Control Panel")

if st.sidebar.button("🗑️ Wipe All Data (Factory Reset)"):
    st.session_state.clear()
    init_session_state()
    st.sidebar.success("Database wiped clean!")
    st.rerun()


# ==============================================================================
# MODULE 1: EXECUTIVE COMMAND & INTERACTIVE GIS MAP
# ==============================================================================
if nav_choice == "📊 Executive Command & GIS Map":
    st.title("📊 Executive Command & GIS Interactive Dispatch Map")
    st.markdown("Real-time geographic distribution of field technicians, emergency tickets, and warehouse stocking points.")

    # KPI Top Bar
    c1, c2, c3, c4 = st.columns(4)
    
    total_parts = st.session_state.inventory_df["Stock Qty"].sum() if not st.session_state.inventory_df.empty else 0
    active_orders = len(st.session_state.work_orders_df) if not st.session_state.work_orders_df.empty else 0
    active_techs = len(st.session_state.technicians_df[st.session_state.technicians_df["Status"] == "On Field Duty"]) if not st.session_state.technicians_df.empty else 0
    pending_returns = len(st.session_state.faulty_returns_df[st.session_state.faulty_returns_df["Return Status"].str.contains("Pending", case=False)]) if not st.session_state.faulty_returns_df.empty else 0

    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Warehouse Stock</div><div class="kpi-value">{total_parts:,} Units</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #ef4444;"><div class="kpi-title">Active Work Tickets</div><div class="kpi-value">{active_orders}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #10b981;"><div class="kpi-title">Field Techs Deployed</div><div class="kpi-value">{active_techs}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #8b5cf6;"><div class="kpi-title">Faulty Parts Pending Return</div><div class="kpi-value">{pending_returns} Cores</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Interactive Map Section
    st.subheader("🗺️ Live Regional Field Dispatch & Order Map")
    
    # Combine Tech and Order Lat/Lon points for Map rendering
    map_points = []
    
    # Add Tech locations
    if not st.session_state.technicians_df.empty:
        for _, t in st.session_state.technicians_df.iterrows():
            if "lat" in t and "lon" in t:
                map_points.append({"lat": t["lat"], "lon": t["lon"], "Type": "Technician Line", "Name": t["Name"]})

    # Add Order locations
    if not st.session_state.work_orders_df.empty:
        for _, w in st.session_state.work_orders_df.iterrows():
            if "lat" in w and "lon" in w:
                map_points.append({"lat": w["lat"], "lon": w["lon"], "Type": "Service Ticket", "Name": w["Ticket ID"] + " (" + w["Client Name"] + ")"})

    if map_points:
        map_df = pd.DataFrame(map_points)
        st.map(map_df, latitude="lat", longitude="lon", size=20)
    else:
        st.info("No geographic data points currently uploaded for map rendering.")

    col_left, col_right = st.columns([1.5, 1])
    with col_left:
        st.subheader("📋 Active Field Lines Overview")
        st.dataframe(st.session_state.technicians_df, use_container_width=True, hide_index=True)
    with col_right:
        st.subheader("⚠️ Critical Emergency Tickets")
        if not st.session_state.work_orders_df.empty:
            crit_df = st.session_state.work_orders_df[st.session_state.work_orders_df["Priority"].isin(["CRITICAL", "High"])]
            st.dataframe(crit_df[["Ticket ID", "Client Name", "Area Zone", "Priority", "Status"]], use_container_width=True, hide_index=True)


# ==============================================================================
# MODULE 2: CENTRAL DATA IMPORT GATEWAY
# ==============================================================================
elif nav_choice == "📥 Central Data Import Gateway":
    st.title("📥 Central Gateway for Bulk Data Uploads")
    st.markdown("Upload your custom CSV or Excel files here to populate Technicians, Orders, Inventory, or Asset History.")

    up_tab1, up_tab2, up_tab3, up_tab4 = st.tabs([
        "🚛 Upload Technicians", 
        "📝 Upload Service Orders", 
        "📦 Upload Parts Catalog", 
        "🏠 Upload Appliance Asset History"
    ])

    # 1. Upload Technicians
    with up_tab1:
        st.subheader("Bulk Upload Field Technicians")
        st.caption("Required / Recommended Columns: Tech ID, Name, Assigned Area/Zone, Primary Skill, Van ID, Max Capacity")
        file_tech = st.file_uploader("Upload Technician CSV / Excel", type=["csv", "xlsx"], key="up_tech")
        if file_tech:
            try:
                df_up = pd.read_csv(file_tech) if file_tech.name.endswith('.csv') else pd.read_excel(file_tech)
                st.write("Preview of Uploaded Data:", df_up.head())
                if st.button("Confirm Import Technicians"):
                    st.session_state.technicians_df = pd.concat([st.session_state.technicians_df, df_up], ignore_index=True)
                    st.success(f"Successfully imported {len(df_up)} technicians!")
            except Exception as e:
                st.error(f"Failed to read file: {e}")

    # 2. Upload Service Orders
    with up_tab2:
        st.subheader("Bulk Upload Work Orders & Breakdown Tickets")
        st.caption("Recommended Columns: Ticket ID, Date, Client Type, Client Name, Serial Number, Appliance Issue, Area Zone, Priority, Est. Revenue ($)")
        file_order = st.file_uploader("Upload Work Orders CSV / Excel", type=["csv", "xlsx"], key="up_order")
        if file_order:
            try:
                df_up = pd.read_csv(file_order) if file_order.name.endswith('.csv') else pd.read_excel(file_order)
                st.write("Preview of Uploaded Data:", df_up.head())
                if st.button("Confirm Import Work Orders"):
                    st.session_state.work_orders_df = pd.concat([st.session_state.work_orders_df, df_up], ignore_index=True)
                    st.success(f"Successfully imported {len(df_up)} service orders!")
            except Exception as e:
                st.error(f"Failed to read file: {e}")

    # 3. Upload Parts Catalog
    with up_tab3:
        st.subheader("Bulk Upload Spare Parts Catalog")
        st.caption("Recommended Columns: SKU, Part Name, Category, Target Machine, Bin Location, Stock Qty, Min Threshold, Unit Cost ($), Selling Price ($)")
        file_parts = st.file_uploader("Upload Parts CSV / Excel", type=["csv", "xlsx"], key="up_parts")
        if file_parts:
            try:
                df_up = pd.read_csv(file_parts) if file_parts.name.endswith('.csv') else pd.read_excel(file_parts)
                st.write("Preview of Uploaded Data:", df_up.head())
                if st.button("Confirm Import Parts Catalog"):
                    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, df_up], ignore_index=True)
                    st.success(f"Successfully imported {len(df_up)} parts SKUs!")
            except Exception as e:
                st.error(f"Failed to read file: {e}")

    # 4. Upload Appliance Asset History
    with up_tab4:
        st.subheader("Bulk Upload Appliance Asset Records")
        st.caption("Optional File. Recommended Columns: Serial Number, Owner Name, Client Type, Appliance Type, Installation Date")
        file_asset = st.file_uploader("Upload Asset History CSV / Excel", type=["csv", "xlsx"], key="up_asset")
        if file_asset:
            try:
                df_up = pd.read_csv(file_asset) if file_asset.name.endswith('.csv') else pd.read_excel(file_asset)
                st.write("Preview of Uploaded Data:", df_up.head())
                if st.button("Confirm Import Asset History"):
                    st.session_state.asset_history_df = pd.concat([st.session_state.asset_history_df, df_up], ignore_index=True)
                    st.success(f"Successfully imported {len(df_up)} asset records!")
            except Exception as e:
                st.error(f"Failed to read file: {e}")


# ==============================================================================
# MODULE 3: TECHNICIAN LINES & AI DISPATCH ENGINE
# ==============================================================================
elif nav_choice == "🚛 Technician Lines & AI Dispatch Engine":
    st.title("🚛 Technician Area Distribution Lines & AI Dispatcher")
    st.markdown("Distribute technicians by geographic area line for max efficiency and match incoming jobs using AI logic.")

    tab1, tab2 = st.tabs(["🤖 AI Smart Dispatch Matcher", "📋 Technician Roster & Area Lines"])

    with tab1:
        st.subheader("🤖 AI Automated Technician Match Engine")
        st.markdown("Select job parameters to run the AI matching algorithm against active technician lines.")

        c_a, c_b, c_c = st.columns(3)
        with c_a:
            target_zone = st.selectbox("Target Area Zone Line", list(st.session_state.zones_dict.keys()))
        with c_b:
            target_skill = st.selectbox("Required Skill Specialty", ["Refrigeration", "Washing Machines", "HVAC & Air Cooling", "Commercial Cooking", "Dishwashers"])
        with c_c:
            part_skus = ["None Required"] + st.session_state.inventory_df["SKU"].tolist() if not st.session_state.inventory_df.empty else ["None Required"]
            target_part = st.selectbox("Required Replacement Part SKU", part_skus)

        if st.button("⚡ Run AI Dispatch Optimization"):
            best_tech, tech_id, score, match_zone = run_ai_smart_dispatch(target_zone, target_skill, target_part)
            
            st.success(f"**AI Recommendation:** Assign to **{best_tech}** ({tech_id})")
            st.info(f"**Match Confidence Score:** {score:.1f}/100 | **Line Zone:** {match_zone}")

    with tab2:
        st.subheader("Active Technician Roster")
        edited_techs = st.data_editor(st.session_state.technicians_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Technician Roster Updates"):
            st.session_state.technicians_df = edited_techs
            st.success("Technician lines updated!")


# ==============================================================================
# MODULE 4: LOGISTICS, SLA & PERFORMANCE ANALYTICS
# ==============================================================================
elif nav_choice == "📈 Logistics, SLA & Performance Analytics":
    st.title("📈 Dedicated Logistics & SLA Performance Analytics")
    st.markdown("Monitor First-Time Fix Rates (FTFR), Service Level Agreement countdown timers, and regional bottlenecks.")

    an_c1, an_c2, an_c3 = st.columns(3)
    with an_c1:
        st.metric("First-Time Fix Rate (FTFR)", "92.4%", "+2.1% this month")
    with an_c2:
        st.metric("Avg Response SLA Time", "3.4 Hours", "-45 mins faster")
    with an_c3:
        st.metric("Parts Availability Index", "96.8%", "High fulfillment")

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("⏱️ Service SLA Timers by Priority")
        if not st.session_state.work_orders_df.empty and "SLA Remaining (Hrs)" in st.session_state.work_orders_df.columns:
            sla_df = st.session_state.work_orders_df[["Ticket ID", "Client Name", "Priority", "SLA Remaining (Hrs)"]]
            st.dataframe(sla_df, use_container_width=True, hide_index=True)
        else:
            st.info("No active tickets with SLA timers.")

    with col_g2:
        st.subheader("🏆 Line Efficiency Leadboard")
        if not st.session_state.technicians_df.empty and "Line Efficiency (%)" in st.session_state.technicians_df.columns:
            st.bar_chart(st.session_state.technicians_df.set_index("Name")["Line Efficiency (%)"])


# ==============================================================================
# MODULE 5: SERVICE TICKETS & APPLIANCE ASSET HISTORY
# ==============================================================================
elif nav_choice == "📝 Service Tickets & Appliance History":
    st.title("📝 Service Work Orders & Optional Appliance Asset History")

    tab1, tab2 = st.tabs(["📋 Active Service Tickets", "🏠 Appliance Asset History Vault (Optional)"])

    with tab1:
        st.subheader("Manage Active Work Orders")
        edited_orders = st.data_editor(st.session_state.work_orders_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Order Pipeline Changes"):
            st.session_state.work_orders_df = edited_orders
            st.success("Work orders saved successfully!")

    with tab2:
        st.subheader("🏠 Appliance Asset Serial Number Lookup")
        st.markdown("Search a specific serial number to view repair history, or add a new home/commercial asset.")

        search_sn = st.text_input("Enter Appliance Serial Number (Optional)", "")
        if search_sn and not st.session_state.asset_history_df.empty:
            res = st.session_state.asset_history_df[st.session_state.asset_history_df["Serial Number"].str.contains(search_sn, case=False)]
            if not res.empty:
                st.dataframe(res, use_container_width=True, hide_index=True)
            else:
                st.warning(f"No asset record found for '{search_sn}'. The system safely logs this as an Unregistered Appliance.")
        else:
            st.dataframe(st.session_state.asset_history_df, use_container_width=True, hide_index=True)


# ==============================================================================
# MODULE 6: APPLIANCE PARTS CATALOG & AUTO PO
# ==============================================================================
elif nav_choice == "📦 Appliance Parts Catalog & Auto PO":
    st.title("📦 Appliance Spare Parts Catalog & Supplier PO Generator")

    tab1, tab2 = st.tabs(["📋 Parts Inventory Catalog", "📑 Auto Supplier Purchase Order (PO) Drafts"])

    with tab1:
        st.subheader("Central Warehouse Inventory")
        edited_inv = st.data_editor(st.session_state.inventory_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Catalog Changes"):
            st.session_state.inventory_df = edited_inv
            st.success("Inventory catalog updated!")

    with tab2:
        st.subheader("📑 Automated Supplier Purchase Order Generator")
        st.markdown("The system detects items at or below minimum reorder thresholds and auto-drafts POs.")

        if not st.session_state.inventory_df.empty:
            low_stock = st.session_state.inventory_df[st.session_state.inventory_df["Stock Qty"] <= st.session_state.inventory_df["Min Threshold"]]
            if not low_stock.empty:
                st.error(f"Found {len(low_stock)} SKUs requiring stock replenishment!")
                st.dataframe(low_stock[["SKU", "Part Name", "Stock Qty", "Min Threshold", "Supplier"]], use_container_width=True, hide_index=True)
                
                if st.button("📄 Generate Draft Purchase Orders"):
                    st.success("Draft Supplier Purchase Orders (PO-2026-08) generated and sent to Purchasing Queue!")
            else:
                st.success("All spare parts stock levels are above minimum reorder thresholds!")


# ==============================================================================
# MODULE 7: FLEET VAN STOCK & FAULTY PART RETURNS
# ==============================================================================
elif nav_choice == "🚐 Fleet Van Stock & Faulty Part Returns":
    st.title("🚐 Fleet Van Stock & Reverse Logistics Faulty Core Returns")
    st.markdown("Track parts inside mobile field vans and process defective components returned from field jobs.")

    tab1, tab2 = st.tabs(["🔄 Faulty Part Return Vault (Reverse Logistics)", "🚐 Mobile Van Requisition"])

    with tab1:
        st.subheader("🔄 Defective Core Returns (Tech Van -> Central Warehouse)")
        st.markdown("When field techs replace a faulty motor/relay, broken components are tracked here until returned to the company.")

        st.dataframe(st.session_state.faulty_returns_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Log New Returned Faulty Part")
        with st.form("faulty_return_form"):
            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                r_ticket = st.text_input("Work Ticket ID", "WO-8805")
                r_tech = st.text_input("Tech Name", "Marcus Vance")
            with rc2:
                r_sku = st.text_input("Faulty Part SKU", "PRT-FRIG-204")
                r_desc = st.text_input("Defect Description", "Burnt motor windings")
            with rc3:
                r_van = st.text_input("Van ID", "VAN-N01")
                r_status = st.selectbox("Status", ["In Tech Van (Pending Return)", "Received at Central Hub", "Credit Claimed"])

            submit_faulty = st.form_submit_button("📥 Log Returned Core")
            if submit_faulty:
                new_rma = {
                    "Return ID": f"RMA-{random.randint(502, 999)}",
                    "Ticket ID": r_ticket,
                    "Tech ID": "TECH-101",
                    "Tech Name": r_tech,
                    "Faulty Part SKU": r_sku,
                    "Part Description": r_desc,
                    "Van Location": r_van,
                    "Return Status": r_status,
                    "Date Collected": str(datetime.date.today())
                }
                st.session_state.faulty_returns_df = pd.concat([st.session_state.faulty_returns_df, pd.DataFrame([new_rma])], ignore_index=True)
                st.success(f"Faulty part core logged successfully into Reverse Logistics Vault!")
                st.rerun()

    with tab2:
        st.subheader("🚐 Van Requisition & Stock Transfers")
        st.info("Warehouse-to-van parts loading interface.")


# ==============================================================================
# MODULE 8: FINANCIAL RATES & CUSTOM RULES
# ==============================================================================
elif nav_choice == "💰 Financial Rates & Custom Rules":
    st.title("💰 Service Financials, Billing Rates & Zone Customization")

    st.subheader("Operational Area Zones Manager")
    st.write("Current Configured Zones:", list(st.session_state.zones_dict.keys()))

    new_z_name = st.text_input("Add New Geographic Area Zone")
    if st.button("➕ Register New Zone") and new_z_name:
        st.session_state.zones_dict[new_z_name] = {"lat": 30.0000, "lon": 31.2000}
        st.success(f"Zone '{new_z_name}' added to global line system!")
        st.rerun()

    st.markdown("---")
    st.subheader("Financial Revenue Analytics")
    if not st.session_state.work_orders_df.empty and "Est. Revenue ($)" in st.session_state.work_orders_df.columns:
        zone_rev = st.session_state.work_orders_df.groupby("Area Zone")["Est. Revenue ($)"].sum().reset_index()
        st.bar_chart(zone_rev.set_index("Area Zone"))
    else:
        st.info("Upload work orders with revenue data to render financial charts.")
