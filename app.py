import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import urllib.parse
import io
import datetime
import folium
from streamlit_folium import st_folium

# ===================================================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ===================================================================
st.set_page_config(
    page_title="Mirage AI Fleet & Wing Dispatch Command",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI cards, metric styling, and printable manifests
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .status-badge-ok {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .status-badge-warn {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .status-badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    @media print {
        .stApp > header, footer, .stSidebar, .stTabs {
            display: none !important;
        }
        .printable-sheet {
            page-break-after: always;
        }
    }
</style>
""", unsafe_allow_html=True)


# ===================================================================
# 2. COMPREHENSIVE DATABASE INITIALIZATION & MIGRATIONS
# ===================================================================
DB_FILE = "dispatch_system.db"

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes all database tables required for multi-wing logistics management."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 1. Company Wings Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS wings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 2. Technicians / Drivers Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            brand TEXT,
            skills TEXT,
            vehicle TEXT,
            capacity INTEGER,
            home_zone TEXT,
            shift_type TEXT DEFAULT 'Full Day',
            parts_inventory TEXT DEFAULT 'Standard Kit',
            status TEXT DEFAULT 'Active'
        )
    """)
    
    # 3. Spare Parts & Warehouse Inventory Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT UNIQUE,
            item_name TEXT,
            category TEXT,
            stock_quantity INTEGER,
            min_threshold INTEGER,
            unit_cost REAL
        )
    """)
    
    # 4. Fleet Vehicle Maintenance Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_name TEXT UNIQUE,
            vehicle_plate TEXT,
            vehicle_type TEXT,
            odometer_km INTEGER,
            last_service_date TEXT,
            health_status TEXT DEFAULT 'Good Condition',
            notes TEXT
        )
    """)
    
    # 5. Operations Audit Log Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            description TEXT,
            operator TEXT DEFAULT 'System Admin'
        )
    """)

    # Seed Default Wings
    c.execute("SELECT COUNT(*) FROM wings")
    if c.fetchone()[0] == 0:
        default_wings = [("Wing A",), ("Wing B",), ("Wing C",)]
        c.executemany("INSERT INTO wings (name) VALUES (?)", default_wings)
    
    # Seed Default Technicians
    c.execute("SELECT COUNT(*) FROM technicians")
    if c.fetchone()[0] == 0:
        default_techs = [
            ("أحمد عماد", "201000000001", "Wing A", "Installation,Maintenance", "Motorcycle", 8, "Shorouk", "Full Day", "Standard Kit", "Active"),
            ("شعبان", "201000000002", "Wing A", "Installation", "Car", 10, "Madinaty", "Full Day", "Heavy Kit, Replacement Parts", "Active"),
            ("كيمكو", "201000000003", "Wing B", "Installation,Maintenance", "Car", 12, "Maadi", "Full Day", "Heavy Kit, Replacement Parts", "Active"),
            ("محمد سامي", "201000000004", "Wing B", "Customer Service", "Motorcycle", 7, "Maadi", "Half Day", "Standard Kit", "Active"),
            ("تكنو", "201000000005", "Wing C", "Installation", "Car", 10, "Tagamoa", "Full Day", "Heavy Kit", "Active"),
            ("حسن", "201000000006", "Wing C", "Customer Service", "Motorcycle", 8, "Tagamoa", "Full Day", "Standard Kit", "Active"),
        ]
        c.executemany("""
            INSERT INTO technicians (name, phone, brand, skills, vehicle, capacity, home_zone, shift_type, parts_inventory, status)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, default_techs)

    # Seed Default Inventory
    c.execute("SELECT COUNT(*) FROM inventory")
    if c.fetchone()[0] == 0:
        default_parts = [
            ("PRT-001", "Standard Mounting Kit", "Hardware", 150, 30, 45.0),
            ("PRT-002", "Heavy Duty Motor Assembly", "Spare Parts", 40, 10, 850.0),
            ("PRT-003", "Universal Wiring Harness", "Electrical", 90, 20, 120.0),
            ("PRT-004", "Replacement Valves & Seals", "Spare Parts", 60, 15, 65.0),
        ]
        c.executemany("""
            INSERT INTO inventory (item_code, item_name, category, stock_quantity, min_threshold, unit_cost)
            VALUES (?,?,?,?,?,?)
        """, default_parts)

    # Seed Default Vehicle Health
    c.execute("SELECT COUNT(*) FROM vehicle_health")
    if c.fetchone()[0] == 0:
        default_fleet = [
            ("أحمد عماد", "م ط أ 123", "Motorcycle", 18500, "2026-05-10", "Good Condition", "Routine maintenance ok"),
            ("شعبان", "ق ب ج 456", "Car", 64000, "2026-06-01", "Good Condition", "Brake pads inspected"),
            ("كيمكو", "س ر د 789", "Car", 89000, "2026-04-15", "Needs Oil Change", "Oil service past due by 500km"),
            ("محمد سامي", "ن ف هـ 321", "Motorcycle", 12000, "2026-05-20", "Good Condition", "New front tire installed"),
            ("تكنو", "و ل م 654", "Car", 105000, "2026-05-02", "Under Repair", "Gearbox maintenance in progress"),
            ("حسن", "ي ص ط 987", "Motorcycle", 22100, "2026-05-18", "Good Condition", "Tuned up"),
        ]
        c.executemany("""
            INSERT INTO vehicle_health (driver_name, vehicle_plate, vehicle_type, odometer_km, last_service_date, health_status, notes)
            VALUES (?,?,?,?,?,?,?)
        """, default_fleet)

    conn.commit()
    conn.close()

# Run database setup
init_db()


# ===================================================================
# 3. DATABASE HELPER FUNCTIONS & OPERATIONAL SERVICES
# ===================================================================
def log_audit_event(event_type, description, operator="System Admin"):
    """Logs system events into the SQLite audit table."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO audit_logs (event_type, description, operator) VALUES (?,?,?)", (event_type, description, operator))
    conn.commit()
    conn.close()

def get_wings():
    """Retrieves list of active company wings."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM wings ORDER BY name ASC")
    rows = c.fetchall()
    conn.close()
    return [r['name'] for r in rows]

def add_wing(wing_name):
    """Adds a new wing to the database."""
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO wings (name) VALUES (?)", (wing_name,))
        conn.commit()
        log_audit_event("ADD_WING", f"Added new wing: {wing_name}")
    except sqlite3.IntegrityError:
        pass
    conn.close()

def rename_wing(old_name, new_name):
    """Renames an existing wing and updates all associated drivers."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE wings SET name = ? WHERE name = ?", (new_name, old_name))
    c.execute("UPDATE technicians SET brand = ? WHERE brand = ?", (new_name, old_name))
    conn.commit()
    conn.close()
    log_audit_event("RENAME_WING", f"Renamed wing '{old_name}' to '{new_name}'")

def delete_wing(wing_name):
    """Deletes a wing from the database."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM wings WHERE name = ?", (wing_name,))
    conn.commit()
    conn.close()
    log_audit_event("DELETE_WING", f"Deleted wing: {wing_name}")

def get_tech_df():
    """Fetches technician table as a Pandas DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM technicians", conn)
    conn.close()
    return df

def save_tech_df(df):
    """Saves updated technician DataFrame back to SQLite."""
    conn = get_db_connection()
    df.to_sql("technicians", conn, if_exists="replace", index=False)
    conn.close()
    log_audit_event("UPDATE_TECH_DB", "Updated technicians master configuration table.")

def get_inventory_df():
    """Fetches inventory table."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()
    return df

def save_inventory_df(df):
    """Saves inventory updates."""
    conn = get_db_connection()
    df.to_sql("inventory", conn, if_exists="replace", index=False)
    conn.close()
    log_audit_event("UPDATE_INVENTORY", "Updated warehouse inventory stock levels.")

def get_fleet_health_df():
    """Fetches vehicle health data."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM vehicle_health", conn)
    conn.close()
    return df

def save_fleet_health_df(df):
    """Saves vehicle health data."""
    conn = get_db_connection()
    df.to_sql("vehicle_health", conn, if_exists="replace", index=False)
    conn.close()

def get_audit_logs_df():
    """Fetches system audit logs."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 200", conn)
    conn.close()
    return df


# ===================================================================
# 4. EGYPT REGIONAL GEOGRAPHY & ROUTING ENGINE
# ===================================================================
FAR_AREAS = [
    "MADINATY", "MOSTAKBAL", "TAGAMOA", "OCTOBER", "ISMAILIA", 
    "KATAMEYA", "ZAMALEK", "QALYUB", "OBOUR", "BADR", "SHERATON", "ALEXANDRIA"
]

CITY_COORDS = {
    "MADINATY CITY ( مدينتى )": (30.0917, 31.6295),
    "TAGAMOA 5 (التجمع الخامس)": (30.0074, 31.4312),
    "TAGAMOA 1 (التجمع الأول)": (30.0511, 31.4486),
    "SHOROUK (الشروق)": (30.1458, 31.6067),
    "AL MAADI ( المعادى )": (29.9602, 31.2569),
    "HELIOPOLIS (مصر الجديدة)": (30.0889, 31.3262),
    "NASR CITY (مدينة نصر)": (30.0561, 31.3301),
    "MOKKATAM ( المقطم )": (30.0167, 31.3000),
    "6TH OF OCTOBER CITY ( 6 أكتوبر )": (29.9722, 30.9439),
    "BADR CITY (مدينه بدر)": (30.1408, 31.7454),
    "EL OBOUR CITY (العبور)": (30.2415, 31.4820),
    "ZAMALEK (الزمالك)": (30.0609, 31.2197),
    "SHEIKH ZAYED (الشيخ زايد)": (30.0463, 30.9997),
}

def classify_distance(city_name):
    """Categorizes trip into Near vs Far zone based on Cairo geography."""
    city_str = str(city_name).upper().strip()
    return "Far" if any(area in city_str for area in FAR_AREAS) else "Near"

def get_coordinates(city_name):
    """Matches city string against spatial coordinates dictionary."""
    city_str = str(city_name).strip()
    return next((v for k, v in CITY_COORDS.items() if k in city_str or city_str in k), (30.0444, 31.2357))

def build_gmaps_route_link(orders_df):
    """Generates a multi-stop Google Maps navigation link for driver handsets."""
    locations = []
    for _, r in orders_df.iterrows():
        c_str = str(r['City']).strip()
        coords = get_coordinates(c_str)
        locations.append(f"{coords[0]},{coords[1]}")
    
    if not locations:
        return "#"
    origin = locations[0]
    destination = locations[-1]
    waypoints = "|".join(locations[1:-1]) if len(locations) > 2 else ""
    
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    if waypoints:
        url += f"&waypoints={waypoints}"
    return url

def generate_driver_whatsapp(phone, tech_name, orders):
    """Builds pre-formatted WhatsApp route notification for technicians."""
    gmaps_url = build_gmaps_route_link(orders)
    msg = f"📱 *Daily Route & Work Orders for {tech_name}*\n"
    msg += f"Total Jobs Assigned: {len(orders)}\n"
    msg += f"🗺️ *Google Maps Multi-Stop Route:* {gmaps_url}\n\n"
    
    for i, (_, row) in enumerate(orders.iterrows(), 1):
        prio = "🚨 VIP" if str(row.get('Priority', '')).lower() in ['high', 'vip', 'emergency'] else "Standard"
        slot = row.get('Time_Slot', 'Morning (9 AM - 1 PM)')
        wing = row.get('Brand', 'General')
        msg += f"*{i}. WO:* {row.get('Work_Order', 'N/A')} [{wing}] [{prio}]\n"
        msg += f"⏰ *Time Slot:* {slot}\n"
        msg += f"📍 *Area:* {row.get('City', 'N/A')}\n"
        msg += f"🛠️ *Service:* {row.get('Service_Type', 'Standard Service')}\n"
        msg += f"------------------\n"
    
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "")
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

def generate_customer_whatsapp(phone, customer_name, wo_number, tech_name, slot, wing_name):
    """Builds WhatsApp customer alert link with arrival window."""
    msg = f"Dear {customer_name},\n"
    msg += f"Your Service Request *#{wo_number}* with *{wing_name}* has been scheduled for today!\n"
    msg += f"👨‍🔧 *Assigned Specialist:* {tech_name}\n"
    msg += f"⏰ *Arrival Window:* {slot}\n\n"
    msg += "Our specialist will contact you 30 minutes prior to arrival. Thank you for choosing us!"
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "")
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"


# ===================================================================
# 5. ADVANCED DISPATCH ENGINE & RISK ANALYSIS
# ===================================================================
def calculate_job_risk(row):
    """Scores operational delay risk for work orders."""
    risk_score = 0
    if str(row.get('Priority', '')).lower() in ['high', 'vip', 'emergency']:
        risk_score += 40
    if classify_distance(row.get('City', '')) == "Far":
        risk_score += 35
    if "Evening" in str(row.get('Time_Slot', '')):
        risk_score += 15
    return min(100, risk_score)

def run_smart_dispatch(orders_df, tech_df, fleet_health_df, allow_overflow=True):
    """
    Main Multi-Wing Heuristic Optimization Dispatch Engine:
    1. Filters out disabled drivers or vehicles under repair.
    2. Matches order wings, parts requirements, and distance vehicle suitability (Cars vs Motorcycles).
    3. Respects daily driver capacity limits and calculates stop order.
    """
    orders = orders_df.copy()
    orders['Distance_Type'] = orders['City'].apply(classify_distance)
    orders['Risk_Score'] = orders.apply(calculate_job_risk, axis=1)
    orders['Priority_Rank'] = orders['Priority'].apply(lambda x: 0 if str(x).lower() in ['vip', 'high', 'emergency'] else 1) if 'Priority' in orders.columns else 1
    
    if 'Time_Slot' not in orders.columns:
        orders['Time_Slot'] = np.where(np.random.rand(len(orders)) > 0.5, "Morning (9 AM - 1 PM)", "Evening (2 PM - 6 PM)")
    
    orders['Assigned_Tech'] = "Unassigned"
    orders['Stop_Sequence'] = 0
    
    # Filter out drivers whose vehicles are 'Under Repair'
    disabled_drivers = fleet_health_df[fleet_health_df['health_status'] == 'Under Repair']['driver_name'].tolist()
    active_techs = tech_df[(tech_df.get('status', 'Active') == 'Active') & (~tech_df['name'].isin(disabled_drivers))]
    
    tracker = {}
    for _, row in active_techs.iterrows():
        cap = row['capacity'] if row.get('shift_type', 'Full Day') == 'Full Day' else int(row['capacity'] * 0.5)
        tracker[row['name']] = {
            'brand': str(row['brand']).strip(),
            'vehicle': row['vehicle'],
            'capacity': max(1, cap),
            'phone': row['phone'],
            'home_zone': str(row.get('home_zone', '')).lower(),
            'parts': str(row.get('parts_inventory', '')).lower(),
            'assigned': 0
        }
    
    orders = orders.sort_values(by=['Priority_Rank', 'Time_Slot', 'Distance_Type'], ascending=[True, True, True])
    
    for idx, row in orders.iterrows():
        order_brand = str(row.get('Brand', '')).strip() if pd.notna(row.get('Brand')) else None
        req_part = str(row.get('Required_Part', '')).lower() if pd.notna(row.get('Required_Part')) else ""
        city_str = str(row['City']).lower()
        dist_type = row['Distance_Type']
        
        target_vehicle = "Car" if (dist_type == "Far" or "heavy" in req_part or "replacement" in req_part) else "Motorcycle"
        
        # Priority Candidate Search: Exact Wing + Capacity + Vehicle Fit + Inventory Fit
        candidates = [
            name for name, info in tracker.items()
            if (not order_brand or info['brand'].lower() == order_brand.lower())
            and info['assigned'] < info['capacity']
            and info['vehicle'] == target_vehicle
            and (not req_part or req_part in info['parts'])
        ]
        
        # Fallback Candidate Search 1: Wing match regardless of vehicle type
        if not candidates:
            candidates = [
                name for name, info in tracker.items()
                if (not order_brand or info['brand'].lower() == order_brand.lower())
                and info['assigned'] < info['capacity']
            ]
            
        # Fallback Candidate Search 2: Cross-wing overflow if permitted
        if not candidates and allow_overflow:
            candidates = [
                name for name, info in tracker.items()
                if info['assigned'] < info['capacity']
            ]
            
        if candidates:
            # Home Zone Geographic Preference
            home_matches = [c for c in candidates if tracker[c]['home_zone'] and tracker[c]['home_zone'] in city_str]
            selected_pool = home_matches if home_matches else candidates
            
            # Select driver with lowest load
            best_tech = min(selected_pool, key=lambda t: tracker[t]['assigned'])
            orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned'] += 1

    # Calculate stop sequencing
    for tech in orders['Assigned_Tech'].unique():
        if tech == "Unassigned": continue
        t_mask = orders['Assigned_Tech'] == tech
        orders.loc[t_mask, 'Stop_Sequence'] = range(1, t_mask.sum() + 1)

    log_audit_event("RUN_DISPATCH", f"Successfully ran AI dispatch engine for {len(orders)} orders.")
    return orders, tracker


# ===================================================================
# 6. APPLICATION HEADER & MAIN NAVIGATION TABS
# ===================================================================
st.markdown("<div class='main-header'>⚡ Mirage AI Fleet & Wing Dispatch Command</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Enterprise Multi-Wing Logistics, Fleet Maintenance & Workforce Operations System</div>", unsafe_allow_html=True)

nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5, nav_tab6, nav_tab7, nav_tab8, nav_tab9, nav_tab10 = st.tabs([
    "🚀 Dispatch Hub", 
    "🗺️ Live Route Map", 
    "📱 Driver & Client Portals", 
    "🖨️ Printable Manifests",
    "📦 Parts Inventory",
    "🛠️ Fleet Health",
    "📊 Analytics & Payroll", 
    "🚨 SLA Risk Sentinel",
    "⚙️ Master Wing Manager",
    "📜 System Audit Trail"
])

# Load state dataframes
tech_df = get_tech_df()
active_wings = get_wings()
inventory_df = get_inventory_df()
fleet_health_df = get_fleet_health_df()


# ===================================================================
# TAB 1: DISPATCH HUB & FILE UPLOADER
# ===================================================================
with nav_tab1:
    st.header("📂 Daily Order Ingestion & AI Routing")
    
    col_files, col_opts = st.columns([2, 1])
    all_uploaded_orders = []
    
    with col_files:
        st.subheader("📤 Dynamic Dedicated Upload Slots per Wing")
        st.caption("Each registered wing has its dedicated upload box. Orders are auto-tagged upon file upload.")
        
        # Create an upload box for every registered company wing
        for wing in active_wings:
            with st.expander(f"🏢 Wing Upload Slot: **{wing}**", expanded=True):
                wing_file = st.file_uploader(
                    f"Select Excel/CSV orders file for {wing}", 
                    type=["xlsx", "csv"], 
                    key=f"uploader_{wing}"
                )
                if wing_file:
                    df_w = pd.read_csv(wing_file) if wing_file.name.endswith('.csv') else pd.read_excel(wing_file)
                    df_w['Brand'] = wing
                    all_uploaded_orders.append(df_w)
                    st.success(f"✓ Loaded {len(df_w)} orders assigned to {wing}")
        
        # Ad-hoc wing upload slot
        with st.expander("➕ Upload Orders for Temporary / Unlisted Wing", expanded=False):
            custom_wing_name = st.text_input("Enter Ad-hoc Wing Name", placeholder="e.g. Mirage Commercial Project")
            custom_file = st.file_uploader("Upload ad-hoc order file", type=["xlsx", "csv"], key="uploader_custom")
            if custom_file and custom_wing_name:
                df_c = pd.read_csv(custom_file) if custom_file.name.endswith('.csv') else pd.read_excel(custom_file)
                df_c['Brand'] = custom_wing_name.strip()
                all_uploaded_orders.append(df_c)
                st.success(f"✓ Loaded {len(df_c)} orders for custom wing '{custom_wing_name}'")
                
    with col_opts:
        st.markdown("### ⚙️ Dispatch Parameters")
        allow_overflow = st.checkbox("Allow Cross-Wing Overflow", value=True, help="Allow under-capacity drivers from Wing B to take overflow jobs from Wing A.")
        fuel_cost_per_km = st.number_input("Fuel Expense Rate (EGP / KM)", value=4.5, step=0.5)
        base_bonus_rate = st.number_input("Driver Bonus Rate per Job > 5 (EGP)", value=50, step=10)
        co2_emission_factor = st.number_input("CO2 Rate (kg/km)", value=0.19, step=0.01)

    if all_uploaded_orders:
        df_raw = pd.concat(all_uploaded_orders, ignore_index=True)
        st.session_state['df_raw'] = df_raw
        
        st.markdown("---")
        st.markdown("### 📊 Ingested Orders Summary Across Wings")
        wing_summary = df_raw['Brand'].value_counts().reset_index()
        wing_summary.columns = ['Wing Name', 'Loaded Orders Count']
        st.dataframe(wing_summary, use_container_width=True)
        
        if st.button("⚡ Execute AI Sequence & Route Dispatch Engine", type="primary"):
            processed_orders, tracker = run_smart_dispatch(df_raw, tech_df, fleet_health_df, allow_overflow)
            st.session_state['processed_orders'] = processed_orders
            st.session_state['tracker'] = tracker
            
            st.subheader("📋 Final Optimized Dispatch Plan")
            display_cols = [c for c in ['Work_Order', 'Brand', 'City', 'Time_Slot', 'Priority', 'Assigned_Tech', 'Stop_Sequence', 'Risk_Score'] if c in processed_orders.columns]
            st.dataframe(processed_orders[display_cols], use_container_width=True)
            
            # Master Excel Download Button
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                processed_orders.to_excel(writer, sheet_name='Master Dispatch Plan', index=False)
            st.download_button(
                label="📥 Download Consolidated Master Excel Report",
                data=buffer.getvalue(),
                file_name="Master_Daily_Dispatch_Plan.xlsx",
                mime="application/vnd.ms-excel",
                type="secondary"
            )


# ===================================================================
# TAB 2: LIVE INTERACTIVE ROUTE MAP
# ===================================================================
with nav_tab2:
    st.header("MAP: GIS Cluster & Route Visualization")
    st.caption("Interactive map depicting customer stops, driver clusters, and risk zones across Cairo.")
    
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        m = folium.Map(location=[30.0444, 31.2357], zoom_start=11)
        
        for idx, row in orders.iterrows():
            coords = get_coordinates(row['City'])
            tech = row['Assigned_Tech']
            dist = row['Distance_Type']
            seq = row.get('Stop_Sequence', 1)
            risk = row.get('Risk_Score', 0)
            
            color = "red" if risk > 60 else ("orange" if dist == "Far" else "blue")
            
            folium.Marker(
                location=coords,
                popup=f"<b>Stop #{seq}</b><br>WO: {row.get('Work_Order', 'N/A')}<br>Wing: {row.get('Brand', 'N/A')}<br>Driver: {tech}<br>Area: {row['City']}<br>Risk Score: {risk}%",
                tooltip=f"Stop {seq}: {tech} ({row['City']})",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)
            
        st_folium(m, width=1200, height=550)
    else:
        st.info("💡 Upload wing orders and execute dispatch in Tab 1 to activate spatial map views.")


# ===================================================================
# TAB 3: DRIVER & CUSTOMER WHATSAPP PORTALS
# ===================================================================
with nav_tab3:
    st.header("📱 Automated WhatsApp Communications Hub")
    
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        techs = orders['Assigned_Tech'].unique()
        
        col_dr, col_cl = st.columns(2)
        
        with col_dr:
            st.subheader("👨‍🔧 Technician Multi-Stop Routes")
            st.caption("1-Click WhatsApp links containing optimized stop order & Google Maps links.")
            for tech in techs:
                if tech == "Unassigned": continue
                t_orders = orders[orders['Assigned_Tech'] == tech].sort_values(by='Stop_Sequence')
                tech_info = tech_df[tech_df['name'] == tech].iloc[0] if not tech_df[tech_df['name'] == tech].empty else None
                phone = tech_info['phone'] if tech_info is not None else "201000000000"
                wa_url = generate_driver_whatsapp(phone, tech, t_orders)
                
                with st.expander(f"📲 Send Route to {tech} ({len(t_orders)} Jobs assigned)"):
                    st.markdown(f"[🚀 **Dispatch Multi-Stop Route to WhatsApp**]({wa_url})", unsafe_allow_html=True)
                    st.dataframe(t_orders[['Stop_Sequence', 'Work_Order', 'Brand', 'City', 'Time_Slot']], use_container_width=True)
                    
        with col_cl:
            st.subheader("📲 Customer Arrival Alerts")
            st.caption("Send instant arrival notifications directly to clients.")
            for idx, r in orders.iterrows():
                if r['Assigned_Tech'] == "Unassigned": continue
                cust_phone = str(r.get('Customer_Phone', '201000000000'))
                cust_name = str(r.get('Customer_Name', 'Valued Client'))
                wo = str(r.get('Work_Order', 'N/A'))
                tech = r['Assigned_Tech']
                slot = r.get('Time_Slot', 'Morning (9 AM - 1 PM)')
                wing = r.get('Brand', 'Mirage Wing')
                
                cust_wa_url = generate_customer_whatsapp(cust_phone, cust_name, wo, tech, slot, wing)
                st.markdown(f"**WO #{wo}** ({cust_name}) ➔ [{tech}] | [📩 Send Customer SMS Alert]({cust_wa_url})")
    else:
        st.info("💡 Run the dispatch engine to populate communication channels.")


# ===================================================================
# TAB 4: PRINTABLE MANIFESTS & WORK ORDERS
# ===================================================================
with nav_tab4:
    st.header("🖨️ Daily Printable Driver Work Sheets")
    st.caption("Generate paper-ready job manifests for field specialists.")
    
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        selected_tech = st.selectbox("Select Technician Manifest to Print", [t for t in orders['Assigned_Tech'].unique() if t != "Unassigned"])
        
        if selected_tech:
            t_orders = orders[orders['Assigned_Tech'] == selected_tech].sort_values(by='Stop_Sequence')
            tech_info = tech_df[tech_df['name'] == selected_tech].iloc[0] if not tech_df[tech_df['name'] == selected_tech].empty else None
            
            st.markdown(f"""
            <div class='printable-sheet' style='border: 2px solid #333; padding: 25px; background: #fff; color: #000;'>
                <h2>MIRAGE FIELD OPERATIONS - DAILY MANIFEST</h2>
                <hr>
                <p><b>Technician Name:</b> {selected_tech} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Primary Wing:</b> {tech_info['brand'] if tech_info is not None else 'N/A'}</p>
                <p><b>Vehicle Type:</b> {tech_info['vehicle'] if tech_info is not None else 'N/A'} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Assigned Jobs:</b> {len(t_orders)}</p>
                <p><b>Date:</b> {datetime.date.today().strftime('%Y-%m-%d')}</p>
                <br>
            </div>
            """, unsafe_allow_html=True)
            
            for idx, r in t_orders.iterrows():
                st.markdown(f"""
                <div style='border-bottom: 1px dashed #666; padding: 10px 0;'>
                    <h4>Stop #{r.get('Stop_Sequence', 1)} | Work Order: #{r.get('Work_Order', 'N/A')} [{r.get('Brand', 'N/A')}]</h4>
                    <p><b>City/Area:</b> {r.get('City', 'N/A')} | <b>Time Slot:</b> {r.get('Time_Slot', 'N/A')} | <b>Priority:</b> {r.get('Priority', 'Standard')}</p>
                    <p><b>Customer Signature:</b> ___________________________ &nbsp;&nbsp;&nbsp;&nbsp; <b>Completion Status:</b> [  ] Done  [  ] Rescheduled</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.caption("Press Ctrl+P (or Cmd+P) in your browser to print this sheet.")
    else:
        st.info("💡 Run dispatch engine to generate driver work sheets.")


# ===================================================================
# TAB 5: SPARE PARTS & WAREHOUSE INVENTORY
# ===================================================================
with nav_tab5:
    st.header("📦 Warehouse & Technician Parts Inventory")
    st.caption("Manage spare parts, kits, and warehouse stock levels.")
    
    st.subheader("📊 Current Warehouse Stock Levels")
    edited_inv = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "stock_quantity": st.column_config.NumberColumn("Quantity in Stock", min_value=0),
            "unit_cost": st.column_config.NumberColumn("Unit Cost (EGP)", format="%.2f EGP")
        }
    )
    
    if st.button("💾 Save Inventory Changes", type="primary"):
        save_inventory_df(edited_inv)
        st.success("Inventory records updated successfully!")
        st.rerun()

    st.markdown("---")
    st.subheader("⚠️ Low Stock Sentinel Alerts")
    low_stock = edited_inv[edited_inv['stock_quantity'] <= edited_inv['min_threshold']]
    if not low_stock.empty:
        for idx, r in low_stock.iterrows():
            st.warning(f"🚨 **Low Stock Alert:** Item `{r['item_code']}` ({r['item_name']}) has only **{r['stock_quantity']} units** remaining (Threshold: {r['min_threshold']}).")
    else:
        st.success("✓ All warehouse items are sufficiently stocked above minimum thresholds.")


# ===================================================================
# TAB 6: FLEET HEALTH & MAINTENANCE TRACKER
# ===================================================================
with nav_tab6:
    st.header("🛠️ Vehicle Maintenance & Fleet Health Engine")
    st.caption("Monitor motorcycle and car health, service history, and repair statuses.")
    
    edited_fleet = st.data_editor(
        fleet_health_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "health_status": st.column_config.SelectboxColumn(
                "Vehicle Status",
                options=["Good Condition", "Needs Oil Change", "Under Repair", "Inspection Due"],
                required=True
            ),
            "odometer_km": st.column_config.NumberColumn("Odometer Reading (KM)")
        }
    )
    
    if st.button("💾 Save Fleet Health Updates", type="primary"):
        save_fleet_health_df(edited_fleet)
        st.success("Vehicle health database saved successfully!")
        st.rerun()
        
    st.markdown("---")
    st.subheader("🚜 Vehicle Operational Status Summary")
    repair_vehicles = edited_fleet[edited_fleet['health_status'] == 'Under Repair']
    if not repair_vehicles.empty:
        st.error(f"⛔ **Dispatch Lockout Warning:** {len(repair_vehicles)} drivers are currently linked to vehicles marked 'Under Repair' and will be excluded from dispatch runs.")
        st.dataframe(repair_vehicles[['driver_name', 'vehicle_plate', 'vehicle_type', 'notes']], use_container_width=True)


# ===================================================================
# TAB 7: FINANCIAL ANALYTICS, CO2 & PAYROLL
# ===================================================================
with nav_tab7:
    st.header("📊 Fleet Performance, Financials & Payroll")
    
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        tracker = st.session_state['tracker']
        
        total_orders = len(orders)
        assigned_count = len(orders[orders['Assigned_Tech'] != 'Unassigned'])
        far_count = len(orders[orders['Distance_Type'] == 'Far'])
        
        est_distance = (far_count * 35) + ((total_orders - far_count) * 12)
        total_fuel_cost = est_distance * fuel_cost_per_km
        total_co2_emissions = est_distance * co2_emission_factor
        
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
        m_col1.metric("Total Ingested Jobs", total_orders)
        m_col2.metric("Successful Allocation", f"{(assigned_count/total_orders)*100:.1f}%")
        m_col3.metric("Est. Total Distance", f"{est_distance:,} KM")
        m_col4.metric("Est. Fuel Cost", f"{total_fuel_cost:,.0f} EGP")
        m_col5.metric("Est. CO2 Carbon Footprint", f"{total_co2_emissions:,.1f} kg")
        
        st.markdown("---")
        st.subheader("👨‍🔧 Driver Payroll & Performance Summary")
        payroll_rows = []
        for k, v in tracker.items():
            bonus = max(0, (v['assigned'] - 5) * base_bonus_rate)
            fuel = (v['assigned'] * 15) * fuel_cost_per_km
            payroll_rows.append({
                "Technician Name": k,
                "Assigned Wing": v['brand'],
                "Vehicle": v['vehicle'],
                "Jobs Completed": v['assigned'],
                "Capacity Limit": v['capacity'],
                "Fuel Reimbursement (EGP)": f"{fuel:,.0f}",
                "Productivity Bonus (EGP)": f"{bonus:,.0f}",
                "Total Daily Payout (EGP)": f"{(fuel + bonus):,.0f}"
            })
        st.dataframe(pd.DataFrame(payroll_rows), use_container_width=True)
    else:
        st.info("💡 Run the dispatch engine in Tab 1 to generate operational financial metrics.")


# ===================================================================
# TAB 8: SLA RISK SENTINEL
# ===================================================================
with nav_tab8:
    st.header("🚨 SLA Delay Sentinel & Emergency Matrix")
    st.caption("Identify work orders at risk of breaching customer delivery SLAs.")
    
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        high_risk_jobs = orders[orders['Risk_Score'] >= 50].sort_values(by='Risk_Score', ascending=False)
        
        st.subheader(f"⚠️ High-Risk Work Orders ({len(high_risk_jobs)} Jobs Flagged)")
        if not high_risk_jobs.empty:
            display_cols = [c for c in ['Work_Order', 'Brand', 'City', 'Priority', 'Risk_Score', 'Assigned_Tech'] if c in high_risk_jobs.columns]
            st.dataframe(high_risk_jobs[display_cols], use_container_width=True)
            
            st.markdown("---")
            st.subheader("🚨 Emergency Driver Override")
            col_swap1, col_swap2, col_swap3 = st.columns(3)
            with col_swap1:
                target_wo = st.selectbox("Select Work Order to Re-assign", high_risk_jobs['Work_Order'].tolist())
            with col_swap2:
                available_techs = [t for t in tech_df['name'].tolist() if t != 'Unassigned']
                new_assigned_tech = st.selectbox("Assign to Specialist", available_techs)
            with col_swap3:
                st.write("")
                st.write("")
                if st.button("Re-assign Job Now"):
                    st.session_state['processed_orders'].loc[
                        st.session_state['processed_orders']['Work_Order'] == target_wo, 'Assigned_Tech'
                    ] = new_assigned_tech
                    log_audit_event("EMERGENCY_REASSIGN", f"Reassigned WO #{target_wo} to {new_assigned_tech}")
                    st.success(f"Work Order #{target_wo} successfully reassigned to {new_assigned_tech}!")
                    st.rerun()
        else:
            st.success("✓ No high-risk delay warnings detected in current dispatch schedule.")
    else:
        st.info("💡 Run dispatch to calculate SLA risk matrix.")


# ===================================================================
# TAB 9: MASTER WING MANAGER & DRIVER CONFIGURATION
# ===================================================================
with nav_tab9:
    st.header("⚙️ Master Wing & Technician Setup")
    
    st.subheader("🏢 Dedicated Wing Manager Control Panel")
    w_col1, w_col2, w_col3 = st.columns(3)
    
    with w_col1:
        st.markdown("#### ✏️ Rename Existing Wing")
        target_wing = st.selectbox("Select Target Wing", active_wings if active_wings else ["None"])
        new_wing_name = st.text_input("New Name String", key="rename_wing_input")
        if st.button("Update Wing Name", type="primary"):
            if target_wing and new_wing_name:
                rename_wing(target_wing, new_wing_name.strip())
                st.success(f"Renamed '{target_wing}' to '{new_wing_name.strip()}' system-wide!")
                st.rerun()
                
    with w_col2:
        st.markdown("#### ➕ Add New Wing")
        wing_to_add = st.text_input("New Wing Name", key="add_wing_input")
        if st.button("Add Wing"):
            if wing_to_add:
                add_wing(wing_to_add.strip())
                st.success(f"Added wing '{wing_to_add.strip()}'!")
                st.rerun()
                
    with w_col3:
        st.markdown("#### 🗑️ Remove Wing")
        wing_to_del = st.selectbox("Select Wing to Remove", active_wings if active_wings else ["None"], key="del_wing_select")
        if st.button("Delete Wing"):
            if wing_to_del:
                delete_wing(wing_to_del)
                st.warning(f"Deleted wing '{wing_to_del}'")
                st.rerun()

    st.markdown("---")
    st.subheader("✏️ Master Technician & Driver Registry")
    
    edited_df = st.data_editor(
        tech_df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "brand": st.column_config.SelectboxColumn(
                "Wing Name", 
                options=active_wings, 
                required=True,
                help="Select the company wing this specialist belongs to."
            ),
            "vehicle": st.column_config.SelectboxColumn(
                "Vehicle Type",
                options=["Motorcycle", "Car"],
                required=True
            ),
            "shift_type": st.column_config.SelectboxColumn(
                "Shift Duration",
                options=["Full Day", "Half Day"],
                required=True
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Active", "Inactive", "On Leave"],
                required=True
            )
        }
    )
    
    if st.button("💾 Save Driver Table Changes"):
        save_tech_df(edited_df)
        st.success("Technician table updated successfully!")
        st.rerun()


# ===================================================================
# TAB 10: SYSTEM AUDIT TRAIL & LOGS
# ===================================================================
with nav_tab10:
    st.header("📜 System Operations Audit Trail")
    st.caption("Immutable log of dispatch runs, manual driver reassignments, and database modifications.")
    
    audit_df = get_audit_logs_df()
    st.dataframe(audit_df, use_container_width=True)
