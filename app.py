import streamlit as st
import pandas as pd
import datetime
import random

# ==============================================================================
# 1. SYSTEM CONFIGURATION & GLOBAL STYLES
# ==============================================================================
st.set_page_config(
    page_title="Mirage Field Service & Parts Distribution ERP",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS safely wrapped inside st.markdown string to avoid Python SyntaxErrors
st.markdown("""
    <style>
    /* Global Layout & Theme */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Executive Metric Cards */
    .kpi-card {
        background-color: #1e293b;
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
        padding: 1.2rem;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-title {
        font-size: 0.85rem;
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

    /* Status Badges */
    .badge-urgent {
        background-color: #ef4444;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.75rem;
    }
    .badge-active {
        background-color: #3b82f6;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    /* Section Headers */
    .section-header {
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
        color: #0f172a;
    }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. SESSION STATE INITIALIZATION (DATA STORE)
# ==============================================================================
def init_session_state():
    # 2.1 Spare Parts Inventory Database
    if "inventory_df" not in st.session_state:
        st.session_state.inventory_df = pd.DataFrame([
            {
                "SKU": "PRT-WASH-101", 
                "Part Name": "Direct Drive Drain Pump Motor", 
                "Category": "Washing Machines", 
                "Target Machine": "Residential Front-Load Washers",
                "Bin Location": "Aisle 3 - Shelf B", 
                "Stock Qty": 42, 
                "Min Threshold": 15, 
                "Unit Cost ($)": 34.50, 
                "Selling Price ($)": 89.99
            },
            {
                "SKU": "PRT-FRIG-204", 
                "Part Name": "Inverter Compressor Start Relay", 
                "Category": "Refrigeration", 
                "Target Machine": "Commercial & Residential Fridges",
                "Bin Location": "Aisle 1 - Shelf D", 
                "Stock Qty": 8, 
                "Min Threshold": 20, 
                "Unit Cost ($)": 18.00, 
                "Selling Price ($)": 55.00
            },
            {
                "SKU": "PRT-HVAC-502", 
                "Part Name": "Dual Run Capacitor 45/5 MFD", 
                "Category": "HVAC & Air Cooling", 
                "Target Machine": "Split Unit ACs & Heat Pumps",
                "Bin Location": "Aisle 5 - Shelf A", 
                "Stock Qty": 115, 
                "Min Threshold": 30, 
                "Unit Cost ($)": 6.20, 
                "Selling Price ($)": 28.00
            },
            {
                "SKU": "PRT-OVN-901", 
                "Part Name": "Commercial Igniter Assembly", 
                "Category": "Commercial Cooking", 
                "Target Machine": "Restaurant Gas Ranges & Ovens",
                "Bin Location": "Aisle 8 - Shelf C", 
                "Stock Qty": 14, 
                "Min Threshold": 10, 
                "Unit Cost ($)": 45.00, 
                "Selling Price ($)": 135.00
            },
            {
                "SKU": "PRT-DSH-305", 
                "Part Name": "High-Pressure Water Circulation Pump", 
                "Category": "Dishwashers", 
                "Target Machine": "Built-in Dishwashers",
                "Bin Location": "Aisle 2 - Shelf C", 
                "Stock Qty": 5, 
                "Min Threshold": 12, 
                "Unit Cost ($)": 62.00, 
                "Selling Price ($)": 160.00
            }
        ])

    # 2.2 Technicians & Area Zones Roster
    if "technicians_df" not in st.session_state:
        st.session_state.technicians_df = pd.DataFrame([
            {
                "Tech ID": "TECH-101", 
                "Name": "Marcus Vance", 
                "Assigned Area/Zone": "North District (Zone 1)", 
                "Primary Skill": "Commercial Refrigeration & HVAC", 
                "Van ID": "VAN-N01", 
                "Active Jobs": 3, 
                "Max Capacity": 5, 
                "Status": "On Field Duty",
                "Line Efficiency (%)": 94.2
            },
            {
                "Tech ID": "TECH-102", 
                "Name": "Ahmed Hassan", 
                "Assigned Area/Zone": "Central Metropolitan (Zone 2)", 
                "Primary Skill": "Residential Laundry & Cooking", 
                "Van ID": "VAN-C04", 
                "Active Jobs": 4, 
                "Max Capacity": 6, 
                "Status": "On Field Duty",
                "Line Efficiency (%)": 91.5
            },
            {
                "Tech ID": "TECH-103", 
                "Name": "David Miller", 
                "Assigned Area/Zone": "East Industrial Sector (Zone 3)", 
                "Primary Skill": "Heavy Commercial Equipment", 
                "Van ID": "VAN-E02", 
                "Active Jobs": 1, 
                "Max Capacity": 4, 
                "Status": "Available",
                "Line Efficiency (%)": 98.0
            },
            {
                "Tech ID": "TECH-104", 
                "Name": "Sami Rahim", 
                "Assigned Area/Zone": "South District (Zone 4)", 
                "Primary Skill": "General Home Appliances", 
                "Van ID": "VAN-S03", 
                "Active Jobs": 5, 
                "Max Capacity": 5, 
                "Status": "Fully Booked",
                "Line Efficiency (%)": 88.7
            }
        ])

    # 2.3 Work Orders & Service Tickets
    if "work_orders_df" not in st.session_state:
        st.session_state.work_orders_df = pd.DataFrame([
            {
                "Ticket ID": "WO-8801",
                "Date": "2026-08-05",
                "Client Type": "Commercial",
                "Client Name": "Grand Plaza Hotel & Suites",
                "Appliance Issue": "Walk-in Cooler not maintaining freezing temp",
                "Area Zone": "North District (Zone 1)",
                "Assigned Tech": "Marcus Vance",
                "Parts Allocated": "PRT-FRIG-204 (x1)",
                "Priority": "CRITICAL",
                "Status": "In Progress",
                "Est. Revenue ($)": 380.00
            },
            {
                "Ticket ID": "WO-8802",
                "Date": "2026-08-06",
                "Client Type": "Residential",
                "Client Name": "Johnathan Myers",
                "Appliance Issue": "Washer displaying E4 error code during drain cycle",
                "Area Zone": "Central Metropolitan (Zone 2)",
                "Assigned Tech": "Ahmed Hassan",
                "Parts Allocated": "PRT-WASH-101 (x1)",
                "Priority": "Medium",
                "Status": "Dispatched",
                "Est. Revenue ($)": 175.00
            },
            {
                "Ticket ID": "WO-8803",
                "Date": "2026-08-06",
                "Client Type": "Commercial",
                "Client Name": "Bistro Deluxe Restaurant",
                "Appliance Issue": "Main conveyer oven burner igniter failed",
                "Area Zone": "East Industrial Sector (Zone 3)",
                "Assigned Tech": "David Miller",
                "Parts Allocated": "PRT-OVN-901 (x1)",
                "Priority": "High",
                "Status": "Pending Parts",
                "Est. Revenue ($)": 290.00
            }
        ])

    # 2.4 Area Zones Master List
    if "zones_list" not in st.session_state:
        st.session_state.zones_list = [
            "North District (Zone 1)",
            "Central Metropolitan (Zone 2)",
            "East Industrial Sector (Zone 3)",
            "South District (Zone 4)",
            "West Suburban Corridor (Zone 5)"
        ]

init_session_state()


# ==============================================================================
# 3. SIDEBAR NAVIGATION & SYSTEM SETTINGS
# ==============================================================================
st.sidebar.title("⚙️ Mirage ERP Hub")
st.sidebar.caption("Service Parts Distribution & Field Technician Dispatch")

nav_choice = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Executive Operations Dashboard",
        "📦 Appliance Parts Inventory",
        "🚛 Area Technicians & Route Dispatch",
        "📝 Service Work Orders & Tickets",
        "🚐 Fleet Van Stock & Requisition",
        "💰 Service Financials & Labor Rates",
        "⚙️ System Rules & Customization"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

if st.sidebar.button("➕ Log New Emergency Service Ticket"):
    st.session_state.show_ticket_modal = True

if st.sidebar.button("🔄 Reset System to Default Baseline"):
    st.session_state.clear()
    init_session_state()
    st.sidebar.success("Database baseline restored!")


# ==============================================================================
# MODULE 1: EXECUTIVE OPERATIONS DASHBOARD
# ==============================================================================
if nav_choice == "📊 Executive Operations Dashboard":
    st.title("📊 Executive Operations & Dispatch Command")
    st.markdown("Real-time monitoring of technician area lines, emergency tickets, and parts inventory stock integrity.")

    # KPI Summary Row
    c1, c2, c3, c4 = st.columns(4)
    
    total_parts = st.session_state.inventory_df["Stock Qty"].sum()
    low_stock_count = len(st.session_state.inventory_df[st.session_state.inventory_df["Stock Qty"] <= st.session_state.inventory_df["Min Threshold"]])
    active_techs = len(st.session_state.technicians_df[st.session_state.technicians_df["Status"] == "On Field Duty"])
    avg_efficiency = st.session_state.technicians_df["Line Efficiency (%)"].mean()

    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Warehouse Inventory</div>
                <div class="kpi-value">{total_parts:,} Units</div>
                <div class="kpi-subtext">Across {len(st.session_state.inventory_df)} Active SKUs</div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #ef4444;">
                <div class="kpi-title">Critical Stock Alerts</div>
                <div class="kpi-value">{low_stock_count} SKUs</div>
                <div class="kpi-subtext" style="color: #ef4444;">Needs Warehouse Reorder</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #10b981;">
                <div class="kpi-title">Deployed Field Techs</div>
                <div class="kpi-value">{active_techs} / {len(st.session_state.technicians_df)}</div>
                <div class="kpi-subtext" style="color:#10b981;">Active in Service Zones</div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #8b5cf6;">
                <div class="kpi-title">Avg Line Efficiency</div>
                <div class="kpi-value">{avg_efficiency:.1f}%</div>
                <div class="kpi-subtext" style="color:#8b5cf6;">Route & First-Time Fix Score</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.subheader("🚛 Live Technician Lines by Geographic Area Zone")
        tech_df = st.session_state.technicians_df.copy()
        
        # Add a visual progress indicator for capacity
        tech_df["Capacity Utilization"] = (tech_df["Active Jobs"] / tech_df["Max Capacity"]) * 100
        
        st.dataframe(
            tech_df[["Tech ID", "Name", "Assigned Area/Zone", "Primary Skill", "Active Jobs", "Max Capacity", "Line Efficiency (%)", "Status"]],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### 📈 Dispatch & Line Performance Analysis")
        chart_data = tech_df.set_index("Name")[["Line Efficiency (%)", "Active Jobs"]]
        st.bar_chart(chart_data)

    with col_right:
        st.subheader("⚠️ Parts Requiring Immediate Reorder")
        inv_df = st.session_state.inventory_df
        low_stock = inv_df[inv_df["Stock Qty"] <= inv_df["Min Threshold"]]
        
        if len(low_stock) > 0:
            for _, row in low_stock.iterrows():
                st.error(f"**{row['SKU']}** - {row['Part Name']}\n\nCurrent: **{row['Stock Qty']}** | Min Threshold: **{row['Min Threshold']}** | Bin: {row['Bin Location']}")
        else:
            st.success("All parts stock levels are above minimum thresholds!")

        st.markdown("---")
        st.subheader("📋 Urgent Work Tickets")
        urgent_tickets = st.session_state.work_orders_df[st.session_state.work_orders_df["Priority"].isin(["CRITICAL", "High"])]
        st.table(urgent_tickets[["Ticket ID", "Client Name", "Area Zone", "Priority", "Status"]])


# ==============================================================================
# MODULE 2: APPLIANCE PARTS INVENTORY HUB
# ==============================================================================
elif nav_choice == "📦 Appliance Parts Inventory":
    st.title("📦 Appliance Parts & Commercial Components Master")
    st.markdown("Full catalog management for residential appliance replacement parts and commercial equipment items.")

    tab1, tab2 = st.tabs(["📋 View & Edit Inventory Catalog", "➕ Add New Spare Part SKU"])

    with tab1:
        st.subheader("Inventory Stock Table")
        
        # Filters
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            category_filter = st.selectbox("Filter by Appliance Category", ["All Categories"] + list(st.session_state.inventory_df["Category"].unique()))
        with f_col2:
            search_query = st.text_input("Search SKU, Part Name, or Target Machine", "")

        df_display = st.session_state.inventory_df.copy()

        if category_filter != "All Categories":
            df_display = df_display[df_display["Category"] == category_filter]

        if search_query:
            df_display = df_display[
                df_display["Part Name"].str.contains(search_query, case=False) |
                df_display["SKU"].str.contains(search_query, case=False) |
                df_display["Target Machine"].str.contains(search_query, case=False)
            ]

        # Editable Dataframe
        edited_df = st.data_editor(
            df_display,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="inventory_editor"
        )

        if st.button("💾 Save Inventory Modifications"):
            st.session_state.inventory_df = edited_df
            st.success("Inventory changes committed successfully!")

    with tab2:
        st.subheader("Add New Appliance Part SKU")
        with st.form("new_part_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_sku = st.text_input("SKU Code", f"PRT-NEW-{random.randint(100,999)}")
                new_name = st.text_input("Part Name", "e.g., Compressor Thermostat")
                new_cat = st.selectbox("Category", ["Washing Machines", "Refrigeration", "HVAC & Air Cooling", "Commercial Cooking", "Dishwashers", "Microwaves & Small Appliances"])
            with c2:
                new_target = st.text_input("Target Machine / Model Compatibility", "e.g., Heavy-Duty Commercial Fryers")
                new_bin = st.text_input("Bin / Shelf Location", "Aisle 4 - Shelf A")
                new_qty = st.number_input("Initial Stock Quantity", min_value=0, value=25)
            with c3:
                new_threshold = st.number_input("Reorder Minimum Threshold", min_value=1, value=10)
                new_cost = st.number_input("Unit Cost ($)", min_value=0.0, value=20.0, step=0.5)
                new_price = st.number_input("Selling Price ($)", min_value=0.0, value=65.0, step=0.5)

            submit_part = st.form_submit_button("➕ Save Part to Catalog")

            if submit_part:
                new_row = {
                    "SKU": new_sku,
                    "Part Name": new_name,
                    "Category": new_cat,
                    "Target Machine": new_target,
                    "Bin Location": new_bin,
                    "Stock Qty": new_qty,
                    "Min Threshold": new_threshold,
                    "Unit Cost ($)": new_cost,
                    "Selling Price ($)": new_price
                }
                st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Part {new_sku} - '{new_name}' added to inventory!")


# ==============================================================================
# MODULE 3: AREA TECHNICIANS & ROUTE DISPATCH
# ==============================================================================
elif nav_choice == "🚛 Area Technicians & Route Dispatch":
    st.title("🚛 Technician Dispatch Lines & Zone Efficiency")
    st.markdown("Organize field service technicians by geographic sector to minimize transit time and maximize repair yield.")

    t_col1, t_col2 = st.columns([2, 1])

    with t_col1:
        st.subheader("Field Technician Roster & Assignment")
        edited_techs = st.data_editor(
            st.session_state.technicians_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Assigned Area/Zone": st.column_config.SelectboxColumn(
                    "Assigned Area/Zone",
                    options=st.session_state.zones_list,
                    required=True
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Available", "On Field Duty", "Fully Booked", "Off Duty"],
                    required=True
                )
            }
        )

        if st.button("💾 Update Technician Lines"):
            st.session_state.technicians_df = edited_techs
            st.success("Technician zone lines updated successfully!")

    with t_col2:
        st.subheader("➕ Register New Technician")
        with st.form("add_tech_form"):
            t_name = st.text_input("Full Name")
            t_zone = st.selectbox("Assigned Area / Zone Line", st.session_state.zones_list)
            t_skill = st.text_input("Primary Skill Specialty", "e.g., Commercial Dishwashers")
            t_van = st.text_input("Assigned Van ID", f"VAN-Z0{random.randint(1,9)}")
            t_cap = st.number_input("Max Daily Jobs", min_value=1, max_value=10, value=5)

            submit_tech = st.form_submit_button("Register Tech")
            if submit_tech and t_name:
                new_tech = {
                    "Tech ID": f"TECH-{random.randint(105, 999)}",
                    "Name": t_name,
                    "Assigned Area/Zone": t_zone,
                    "Primary Skill": t_skill,
                    "Van ID": t_van,
                    "Active Jobs": 0,
                    "Max Capacity": t_cap,
                    "Status": "Available",
                    "Line Efficiency (%)": 95.0
                }
                st.session_state.technicians_df = pd.concat([st.session_state.technicians_df, pd.DataFrame([new_tech])], ignore_index=True)
                st.success(f"Technician {t_name} assigned to {t_zone}!")


# ==============================================================================
# MODULE 4: SERVICE WORK ORDERS & TICKETS
# ==============================================================================
elif nav_choice == "📝 Service Work Orders & Tickets":
    st.title("📝 Service Tickets & Work Order Dispatch")
    st.markdown("Manage repair requests for residential homeowners and corporate/commercial accounts.")

    st.subheader("Current Active Work Orders")
    st.dataframe(
        st.session_state.work_orders_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("➕ Generate New Work Order Ticket")

    with st.form("work_order_form"):
        wo_c1, wo_c2, wo_c3 = st.columns(3)

        with wo_c1:
            client_type = st.radio("Client Classification", ["Residential", "Commercial"])
            client_name = st.text_input("Client / Company Name")
            priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "CRITICAL"])

        with wo_c2:
            target_zone = st.selectbox("Job Location Area / Zone", st.session_state.zones_list)
            
            # Filter available techs for this zone
            available_techs = st.session_state.technicians_df["Name"].tolist()
            assigned_tech = st.selectbox("Assign Field Technician", available_techs)
            
            appliance_issue = st.text_area("Appliance Type & Reported Breakdown Issue")

        with wo_c3:
            # Parts Selector
            parts_list = st.session_state.inventory_df["Part Name"].tolist()
            selected_part = st.selectbox("Allocate Required Repair Part", ["None Required"] + parts_list)
            est_revenue = st.number_input("Estimated Total Job Quote ($)", min_value=0.0, value=150.0, step=10.0)

        submit_ticket = st.form_submit_button("🚀 Create & Dispatch Service Ticket")

        if submit_ticket and client_name:
            new_ticket = {
                "Ticket ID": f"WO-{random.randint(8804, 9999)}",
                "Date": str(datetime.date.today()),
                "Client Type": client_type,
                "Client Name": client_name,
                "Appliance Issue": appliance_issue,
                "Area Zone": target_zone,
                "Assigned Tech": assigned_tech,
                "Parts Allocated": selected_part,
                "Priority": priority,
                "Status": "Dispatched",
                "Est. Revenue ($)": est_revenue
            }
            
            # Append ticket
            st.session_state.work_orders_df = pd.concat([st.session_state.work_orders_df, pd.DataFrame([new_ticket])], ignore_index=True)
            
            # Deduct part from stock if allocated
            if selected_part != "None Required":
                idx = st.session_state.inventory_df[st.session_state.inventory_df["Part Name"] == selected_part].index
                if len(idx) > 0:
                    st.session_state.inventory_df.loc[idx[0], "Stock Qty"] = max(0, st.session_state.inventory_df.loc[idx[0], "Stock Qty"] - 1)
            
            st.success(f"Work Order generated and assigned to {assigned_tech} in {target_zone}!")


# ==============================================================================
# MODULE 5: FLEET VAN STOCK & REQUISITION
# ==============================================================================
elif nav_choice == "🚐 Fleet Van Stock & Requisition":
    st.title("🚐 Mobile Fleet Van Stock & Parts Requisition")
    st.markdown("Track parts loaded directly into technician service vans to ensure high first-time fix rates.")

    v_tech = st.selectbox("Select Technician Fleet Van", st.session_state.technicians_df["Name"].unique())
    selected_tech_info = st.session_state.technicians_df[st.session_state.technicians_df["Name"] == v_tech].iloc[0]

    st.info(f"**Van ID:** {selected_tech_info['Van ID']} | **Assigned Area:** {selected_tech_info['Assigned Area/Zone']} | **Tech Skill:** {selected_tech_info['Primary Skill']}")

    c_left, c_right = st.columns(2)

    with c_left:
        st.subheader("📦 Simulated Parts Currently Loaded in Van")
        van_stock_sample = pd.DataFrame([
            {"Part SKU": "PRT-WASH-101", "Item Description": "Direct Drive Drain Pump Motor", "Qty Carried": 2},
            {"Part SKU": "PRT-HVAC-502", "Item Description": "Dual Run Capacitor 45/5 MFD", "Qty Carried": 5},
            {"Part SKU": "PRT-FRIG-204", "Item Description": "Inverter Compressor Start Relay", "Qty Carried": 1}
        ])
        st.table(van_stock_sample)

    with c_right:
        st.subheader("🔄 Warehouse-to-Van Transfer Requisition")
        with st.form("transfer_form"):
            req_part = st.selectbox("Select Warehouse SKU to Transfer", st.session_state.inventory_df["SKU"] + " - " + st.session_state.inventory_df["Part Name"])
            req_qty = st.number_input("Quantity to Load into Van", min_value=1, max_value=10, value=1)
            
            submit_transfer = st.form_submit_button("Transfer Items to Van")
            if submit_transfer:
                st.success(f"Requisition order confirmed! {req_qty} units of '{req_part.split(' - ')[1]}' loaded into {selected_tech_info['Van ID']}.")


# ==============================================================================
# MODULE 6: SERVICE FINANCIALS & LABOR RATES
# ==============================================================================
elif nav_choice == "💰 Service Financials & Labor Rates":
    st.title("💰 Service Financials, Billing & Labor Analytics")
    st.markdown("Monitor service ticket revenue, parts profit margins, and technician labor rate calculations.")

    wo_df = st.session_state.work_orders_df.copy()
    
    rev_col1, rev_col2, rev_col3 = st.columns(3)
    
    total_pipeline_rev = wo_df["Est. Revenue ($)"].sum()
    comm_rev = wo_df[wo_df["Client Type"] == "Commercial"]["Est. Revenue ($)"].sum()
    res_rev = wo_df[wo_df["Client Type"] == "Residential"]["Est. Revenue ($)"].sum()

    with rev_col1:
        st.metric("Total Service Pipeline Revenue", f"${total_pipeline_rev:,.2f}")
    with rev_col2:
        st.metric("Commercial B2B Service Revenue", f"${comm_rev:,.2f}")
    with rev_col3:
        st.metric("Residential Home Appliance Revenue", f"${res_rev:,.2f}")

    st.markdown("---")
    st.subheader("📊 Revenue Breakdown by Area Zone")
    zone_rev = wo_df.groupby("Area Zone")["Est. Revenue ($)"].sum().reset_index()
    st.bar_chart(zone_rev.set_index("Area Zone"))


# ==============================================================================
# MODULE 7: SYSTEM RULES & CUSTOMIZATION
# ==============================================================================
elif nav_choice == "⚙️ System Rules & Customization":
    st.title("⚙️ System Customization & Operational Rules")
    st.markdown("Customize service rules, add new geographic lines/zones, and set standard diagnostic billing rates.")

    st.subheader("📍 Manage Geographic Area Lines & Zones")
    
    col_zone_list, col_zone_add = st.columns(2)

    with col_zone_list:
        st.write("**Active Operational Area Zones:**")
        for z in st.session_state.zones_list:
            st.markdown(f"- 🟢 {z}")

    with col_zone_add:
        new_zone_name = st.text_input("New Geographic Zone Name", "")
        if st.button("➕ Add Area Zone"):
            if new_zone_name and new_zone_name not in st.session_state.zones_list:
                st.session_state.zones_list.append(new_zone_name)
                st.success(f"Zone '{new_zone_name}' added to global system options!")
                st.rerun()

    st.markdown("---")
    st.subheader("⏱️ Standard Rates & Diagnostics Settings")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.number_input("Standard Appliance Diagnostic Fee ($)", value=75.0, step=5.0)
        st.number_input("Commercial Emergency Call-Out Rate ($)", value=150.0, step=10.0)
    with col_r2:
        st.number_input("Hourly Technician Field Labor Rate ($)", value=95.0, step=5.0)
        st.number_input("Default Parts Markup Rate (%)", value=35.0, step=5.0)

    if st.button("💾 Save System Parameters"):
        st.success("Configuration updated successfully!")
