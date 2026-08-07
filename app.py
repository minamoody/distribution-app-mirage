import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import urllib.parse
import io
import math
from datetime import datetime
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------------
# 1. PAGE CONFIG & CUSTOM CSS STYLING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Dispatch Command & Live Fleet Tracker",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom Styling for operational UI
st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .stMetric { background-color: #f8f9fa; border-radius: 8px; padding: 10px; border-left: 4px solid #1E88E5; }
    .alert-card { background-color: #ffebee; border-left: 6px solid #d32f2f; padding: 15px; border-radius: 6px; margin-bottom: 10px; }
    .success-card { background-color: #e8f5e9; border-left: 6px solid #388e3c; padding: 15px; border-radius: 6px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

MIRAGE_CENTER_COORDS = (30.0074, 31.4312)

@st.cache_data
def get_city_coords_dict():
    return {
        "MADINATY": (30.0917, 31.6295),
        "TAGAMOA": (30.0074, 31.4312),
        "SHOROUK": (30.1458, 31.6067),
        "MAADI": (29.9602, 31.2569),
        "HELIOPOLIS": (30.0889, 31.3262),
        "NASR CITY": (30.0561, 31.3301),
        "MOKKATAM": (30.0167, 31.3000),
        "OCTOBER": (29.9722, 30.9439),
        "BADR": (30.1408, 31.7454),
        "NEW CAIRO": (30.0074, 31.4312),
        "ZAMALEK": (30.0609, 31.2196),
        "KATAMEYA": (29.9911, 31.4092)
    }

CITY_COORDS = get_city_coords_dict()

SERVICE_DURATIONS_MIN = {
    "installation": 90,
    "repair": 60,
    "maintenance": 45,
    "inspection": 30
}

TECH_ROUTE_COLORS = [
    "red", "blue", "green", "purple", "orange", "darkred", 
    "lightred", "beige", "darkblue", "darkgreen", "cadetblue", 
    "darkpurple", "white", "pink", "lightblue", "lightgreen"
]

# -------------------------------------------------------------------
# 2. DATABASE INITIALIZATION & ROBUST SCHEMA MIGRATION
# -------------------------------------------------------------------
REQUIRED_COLUMNS = [
    ("id", "INTEGER PRIMARY KEY AUTOINCREMENT"),
    ("name", "TEXT UNIQUE"),
    ("phone", "TEXT"),
    ("brand", "TEXT"),
    ("appliance_specialty", "TEXT"),
    ("skills", "TEXT"),
    ("vehicle", "TEXT"),
    ("capacity", "INTEGER"),
    ("start_type", "TEXT"),
    ("home_zone", "TEXT"),
    ("max_radius_km", "INTEGER"),
    ("experience", "TEXT"),
    ("status", "TEXT"),
    ("last_lat", "REAL"),
    ("last_lng", "REAL"),
    ("last_ping", "TEXT"),
    ("active_status", "TEXT")
]

def init_db():
    with sqlite3.connect("dispatch_system.db") as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS technicians (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                phone TEXT,
                brand TEXT,
                appliance_specialty TEXT,
                skills TEXT,
                vehicle TEXT,
                capacity INTEGER,
                start_type TEXT,
                home_zone TEXT,
                max_radius_km INTEGER,
                experience TEXT,
                status TEXT,
                last_lat REAL,
                last_lng REAL,
                last_ping TEXT,
                active_status TEXT
            )
        """)
        
        # Auto-Schema Migration: Adds any missing columns to existing database
        c.execute("PRAGMA table_info(technicians)")
        existing_cols = [col[1] for col in c.fetchall()]
        for col_name, col_type in REQUIRED_COLUMNS:
            if col_name not in existing_cols and col_name != "id":
                c.execute(f"ALTER TABLE technicians ADD COLUMN {col_name} {col_type}")

        c.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tech_name TEXT,
                message TEXT,
                sent_time TEXT,
                status TEXT,
                tech_reply TEXT,
                reply_time TEXT
            )
        """)
        
        c.execute("SELECT COUNT(*) FROM technicians")
        if c.fetchone()[0] == 0:
            default_techs = [
                ("أحمد عماد", "201000000001", "Brand A, Brand B", "AC, Refrigerator", "Installation, Maintenance", "Motorcycle", 8, "Mirage Service Center", "Shorouk", 35, "Senior", "Active", 30.1458, 31.6067, "Just Now", "In Transit"),
                ("شعبان", "201000000002", "Brand A", "Refrigerator, AC", "Installation, Repair", "Car", 10, "Mirage Service Center", "Madinaty", 40, "Senior", "Active", 30.0917, 31.6295, "Just Now", "On-Site"),
                ("كيمكو", "201000000003", "Brand B, Brand C", "Washing Machine, Oven", "Installation, Maintenance, Repair", "Car", 12, "Home / Outside", "Maadi", 35, "Mid", "Active", 29.9602, 31.2569, "Just Now", "In Transit"),
                ("محمد سامي", "201000000004", "Brand A, Brand B, Brand C", "AC, Refrigerator", "Maintenance, Repair", "Motorcycle", 7, "Home / Outside", "Maadi", 20, "Junior", "Active", 29.9911, 31.4092, "Just Now", "Idle"),
                ("تكنو", "201000000005", "All Brands", "Oven, Washing Machine, Other Appliances", "Installation, Repair", "Car", 10, "Mirage Service Center", "Tagamoa", 35, "Senior", "Active", 30.0074, 31.4312, "Just Now", "In Transit"),
            ]
            c.executemany("""
                INSERT INTO technicians 
                (name, phone, brand, appliance_specialty, skills, vehicle, capacity, start_type, home_zone, max_radius_km, experience, status, last_lat, last_lng, last_ping, active_status) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, default_techs)
        conn.commit()

init_db()

def get_tech_df():
    with sqlite3.connect("dispatch_system.db") as conn:
        df = pd.read_sql_query("SELECT * FROM technicians", conn)
        defaults = {
            "name": "Unknown", "phone": "000", "brand": "All", "appliance_specialty": "All",
            "skills": "General", "vehicle": "Car", "capacity": 8, "start_type": "Mirage Service Center",
            "home_zone": "Tagamoa", "max_radius_km": 35, "experience": "Mid", "status": "Active",
            "last_lat": 30.0074, "last_lng": 31.4312, "last_ping": "N/A", "active_status": "Idle"
        }
        for col, default_val in defaults.items():
            if col not in df.columns:
                df[col] = default_val
            else:
                df[col] = df[col].fillna(default_val)
        return df

def save_tech_df(df):
    with sqlite3.connect("dispatch_system.db") as conn:
        df.to_sql("technicians", conn, if_exists="replace", index=False)

def send_alert(tech_name, message):
    with sqlite3.connect("dispatch_system.db") as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO alerts (tech_name, message, sent_time, status, tech_reply, reply_time)
            VALUES (?, ?, ?, 'PENDING', '', '')
        """, (tech_name, message, datetime.now().strftime("%I:%M %p")))
        conn.commit()

def get_alerts():
    with sqlite3.connect("dispatch_system.db") as conn:
        return pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC", conn)

def reply_alert(alert_id, reply_text):
    with sqlite3.connect("dispatch_system.db") as conn:
        c = conn.cursor()
        c.execute("""
            UPDATE alerts 
            SET status = 'ACKNOWLEDGED', tech_reply = ?, reply_time = ?
            WHERE id = ?
        """, (reply_text, datetime.now().strftime("%I:%M %p"), alert_id))
        conn.commit()

# -------------------------------------------------------------------
# 3. GEOGRAPHIC MATH & COORDINATE RESOLUTION
# -------------------------------------------------------------------
@st.cache_data
def fast_haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_effective_coords(row):
    if str(row.get('start_type', '')) == "Mirage Service Center":
        return MIRAGE_CENTER_COORDS
    zone_raw = str(row.get('home_zone', '')).upper().strip()
    return next((coords for k, coords in CITY_COORDS.items() if k in zone_raw or zone_raw in k), MIRAGE_CENTER_COORDS)

# -------------------------------------------------------------------
# 4. DISPATCH ENGINE & TSP ROUTE OPTIMIZATION
# -------------------------------------------------------------------
def run_optimized_dispatch(df_raw, tech_df, allow_overflow=True, traffic_factor=1.2, emergency_priority_weight=30.0):
    orders = df_raw.copy()
    col_map = {c: c.strip().title().replace(" ", "_") for c in orders.columns}
    orders.rename(columns=col_map, inplace=True)
    
    if 'City' not in orders.columns and 'Area' in orders.columns:
        orders.rename(columns={'Area': 'City'}, inplace=True)
    if 'Status' not in orders.columns:
        orders['Status'] = 'Pending'

    cancelled_or_postponed = orders[orders['Status'].astype(str).str.upper().isin(['CANCELLED', 'CANCELED', 'POSTPONED', 'DELAYED'])].copy()
    active_orders = orders[~orders['Status'].astype(str).str.upper().isin(['CANCELLED', 'CANCELED', 'POSTPONED', 'DELAYED'])].copy()

    def calc_duration(row):
        service = str(row.get('Service_Type', '')).lower()
        for k, v in SERVICE_DURATIONS_MIN.items():
            if k in service:
                return v
        return 60

    active_orders['Est_Duration_Min'] = active_orders.apply(calc_duration, axis=1)
    active_orders['Is_Emergency'] = active_orders['Is_Emergency'].astype(str).str.lower().isin(['true', '1', 'yes']) if 'Is_Emergency' in active_orders.columns else False
    active_orders['Assigned_Tech'] = "Unassigned"
    active_orders['Stop_Sequence'] = 0
    active_orders['Est_Travel_KM'] = 0.0

    active_techs = tech_df[tech_df['status'] == 'Active'].copy()
    
    tracker = {}
    for _, row in active_techs.iterrows():
        eff_lat, eff_lng = get_effective_coords(row)
        tracker[row['name']] = {
            'brands': [b.strip().lower() for b in str(row.get('brand', 'General')).split(',')],
            'raw_brand_str': str(row.get('brand', 'General')),
            'specialties': [s.strip().lower() for s in str(row.get('appliance_specialty', 'AC')).split(',')],
            'capacity': int(row.get('capacity', 8)),
            'phone': str(row.get('phone', '201000000000')),
            'home_zone': str(row.get('home_zone', 'Tagamoa')),
            'base_lat': eff_lat,
            'base_lng': eff_lng,
            'max_radius_km': float(row.get('max_radius_km', 35)),
            'assigned_jobs': [],
            'total_dist_km': 0.0,
            'total_work_min': 0,
            'projected_revenue': 0.0,
            'vehicle': str(row.get('vehicle', 'Motorcycle'))
        }

    active_orders.sort_values(by=['Is_Emergency', 'Time_Slot'], ascending=[False, True], inplace=True)

    for idx, row in active_orders.iterrows():
        order_brand = str(row.get('Brand', '')).strip().lower()
        order_appliance = str(row.get('Appliance', row.get('Appliance_Type', ''))).strip().lower()
        city_raw = str(row.get('City', '')).upper().strip()
        revenue = float(row.get('Estimated_Revenue', 350.0))
        is_emergency = row['Is_Emergency']
        
        order_coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))

        candidates = []
        for name, info in tracker.items():
            if len(info['assigned_jobs']) >= info['capacity']: continue
            dist_km = fast_haversine_km(info['base_lat'], info['base_lng'], order_coords[0], order_coords[1]) * traffic_factor
            if dist_km > info['max_radius_km']: continue

            score = dist_km
            if not order_brand or any(order_brand in b or b in order_brand or 'all' in b for b in info['brands']):
                score -= 12.0
            elif not allow_overflow:
                continue
            else:
                score += 20.0

            if any(order_appliance in s or s in order_appliance or 'all' in s for s in info['specialties']):
                score -= 10.0
            if is_emergency:
                score -= emergency_priority_weight

            candidates.append((name, score, dist_km))

        if candidates:
            best_tech, _, dist_km = min(candidates, key=lambda x: x[1])
            active_orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned_jobs'].append(idx)
            tracker[best_tech]['projected_revenue'] += revenue
            tracker[best_tech]['total_work_min'] += row['Est_Duration_Min']

    # TSP Route Sequencing (Nearest Neighbor with Base Return)
    for name, info in tracker.items():
        job_indices = info['assigned_jobs']
        if not job_indices: continue
            
        current_lat, current_lng = info['base_lat'], info['base_lng']
        unvisited = job_indices.copy()
        sequence = 1
        home_coords = next((c for k, c in CITY_COORDS.items() if k in info['home_zone'].upper()), MIRAGE_CENTER_COORDS)

        while unvisited:
            next_job, best_dist = None, float('inf')
            for idx in unvisited:
                row = active_orders.loc[idx]
                city_raw = str(row.get('City', '')).upper().strip()
                coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
                dist = fast_haversine_km(current_lat, current_lng, coords[0], coords[1])
                
                if len(unvisited) == 1:
                    home_dist = fast_haversine_km(coords[0], coords[1], home_coords[0], home_coords[1])
                    dist = (dist * 0.5) + (home_dist * 0.5)

                if dist < best_dist:
                    best_dist = dist
                    next_job = idx

            active_orders.at[next_job, 'Stop_Sequence'] = sequence
            active_orders.at[next_job, 'Est_Travel_KM'] = round(best_dist, 2)
            info['total_dist_km'] += best_dist
            
            city_raw = str(active_orders.loc[next_job].get('City', '')).upper().strip()
            curr_coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
            current_lat, current_lng = curr_coords[0], curr_coords[1]
            unvisited.remove(next_job)
            sequence += 1

    active_orders.sort_values(by=['Assigned_Tech', 'Stop_Sequence'], inplace=True)
    return active_orders, cancelled_or_postponed, tracker

# -------------------------------------------------------------------
# 5. NAVIGATION & VIEW ROUTING
# -------------------------------------------------------------------
st.sidebar.title("⚡ System View Mode")
app_mode = st.sidebar.radio("Select Interface:", ["🏢 Dispatch Command Center", "📱 Technician Mobile Portal"])

tech_df = get_tech_df()

# ===================================================================
# MODE 1: ADMIN DISPATCH COMMAND CENTER
# ===================================================================
if app_mode == "🏢 Dispatch Command Center":
    st.title("🏢 Field Technician Dispatch & GPS Command Center")

    nav1, nav2, nav3, nav4, nav5, nav6 = st.tabs([
        "🚀 AI Dispatch Engine", 
        "🗺️ TSP Route Map", 
        "🛰️ Live Tracker & 2-Way Alerts", 
        "📊 Fleet Performance", 
        "🚫 Cancellations Ledger", 
        "⚙️ Technicians DB"
    ])

    # TAB 1: DISPATCH ENGINE
    with nav1:
        st.header("📂 Order File Upload & TSP Dispatch Optimization")
        c1, c2 = st.columns([2, 1])
        with c1:
            uploaded_file = st.file_uploader("Upload Today's Work Orders (.xlsx or .csv)", type=["xlsx", "csv"])
        with c2:
            st.subheader("⚙️ Dispatch Tuning Parameters")
            allow_overflow = st.checkbox("Allow Cross-Brand Overflow", value=True)
            traffic_factor = st.slider("Traffic Congestion Multiplier", 1.0, 2.0, 1.2, 0.1)
            emergency_weight = st.slider("Emergency Prioritization Factor", 10.0, 50.0, 30.0, 5.0)
            fuel_rate = st.number_input("Fuel Cost / KM (EGP)", value=4.5, step=0.5)

        if uploaded_file:
            df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded {len(df_raw)} work orders!")
            
            with st.expander("👀 Raw Work Orders Preview", expanded=False):
                st.dataframe(df_raw.head(10), use_container_width=True)

            if st.button("⚡ Execute AI Routing & Dispatch Optimization", type="primary"):
                active_orders, cancelled_postponed, tracker = run_optimized_dispatch(
                    df_raw, tech_df, allow_overflow, traffic_factor, emergency_weight
                )
                st.session_state['active_orders'] = active_orders
                st.session_state['cancelled_postponed'] = cancelled_postponed
                st.session_state['tracker'] = tracker
                st.session_state['fuel_rate'] = fuel_rate

                st.subheader("📋 Dispatched Work Orders (Sequenced by Technician)")
                
                # Summary Metrics
                m1, m2, m3, m4 = st.columns(4)
                assigned_cnt = len(active_orders[active_orders['Assigned_Tech'] != 'Unassigned'])
                unassigned_cnt = len(active_orders[active_orders['Assigned_Tech'] == 'Unassigned'])
                total_rev = sum(t['projected_revenue'] for t in tracker.values())
                total_dist = sum(t['total_dist_km'] for t in tracker.values())

                m1.metric("Assigned Orders", assigned_cnt)
                m2.metric("Unassigned Orders", unassigned_cnt)
                m3.metric("Est. Total Revenue", f"{total_rev:,.0f} EGP")
                m4.metric("Est. Total Distance", f"{total_dist:,.1f} KM")

                st.dataframe(
                    active_orders[['Stop_Sequence', 'Assigned_Tech', 'Work_Order', 'Brand', 'Customer_Name', 'City', 'Time_Slot', 'Est_Duration_Min', 'Est_Travel_KM', 'Is_Emergency']], 
                    use_container_width=True
                )

                # Export Multi-Sheet Report
                multi_excel = io.BytesIO()
                with pd.ExcelWriter(multi_excel, engine='openpyxl') as writer:
                    active_orders.to_excel(writer, index=False, sheet_name='Dispatched_Orders_TSP')
                    perf_rows = []
                    for name, info in tracker.items():
                        perf_rows.append({
                            "Technician": name,
                            "Jobs Assigned": len(info['assigned_jobs']),
                            "Capacity": info['capacity'],
                            "Travel KM": round(info['total_dist_km'], 1),
                            "Work Hours": round(info['total_work_min']/60.0, 1),
                            "Revenue (EGP)": info['projected_revenue'],
                            "Fuel Cost (EGP)": round(info['total_dist_km'] * fuel_rate, 1)
                        })
                    pd.DataFrame(perf_rows).to_excel(writer, index=False, sheet_name='Tech_Performance')
                    cancelled_postponed.to_excel(writer, index=False, sheet_name='Cancelled_Postponed')

                st.download_button(
                    "📥 Download Master Multi-Sheet Dispatch Report (.xlsx)", 
                    multi_excel.getvalue(), 
                    f"Master_Dispatch_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"
                )

    # TAB 2: ROUTE MAP
    with nav2:
        st.header("🗺️ Sequenced Technician TSP Route Map")
        if 'active_orders' in st.session_state:
            orders = st.session_state['active_orders']
            m = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11)
            folium.Marker(MIRAGE_CENTER_COORDS, popup="🏭 Mirage Base Center", tooltip="Mirage Base Center", icon=folium.Icon(color="darkred", icon="building", prefix="fa")).add_to(m)

            unique_techs = [t for t in orders['Assigned_Tech'].unique() if t != 'Unassigned']
            tech_color_map = {tech: TECH_ROUTE_COLORS[i % len(TECH_ROUTE_COLORS)] for i, tech in enumerate(unique_techs)}

            for tech_name in unique_techs:
                tech_orders = orders[orders['Assigned_Tech'] == tech_name].sort_values(by='Stop_Sequence')
                route_coords = []
                
                tech_row = tech_df[tech_df['name'] == tech_name]
                if not tech_row.empty:
                    base_coords = get_effective_coords(tech_row.iloc[0])
                    route_coords.append(base_coords)

                for _, row in tech_orders.iterrows():
                    city_raw = str(row.get('City', '')).upper().strip()
                    coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
                    route_coords.append(coords)
                    
                    folium.Marker(
                        coords,
                        popup=f"<b>Stop #{row['Stop_Sequence']}</b><br>Tech: {row['Assigned_Tech']}<br>WO: {row.get('Work_Order')}<br>Customer: {row.get('Customer_Name')}",
                        tooltip=f"Stop #{row['Stop_Sequence']} ({row['Assigned_Tech']})",
                        icon=folium.Icon(color=tech_color_map[tech_name], icon="wrench", prefix="fa")
                    ).add_to(m)

                if len(route_coords) > 1:
                    folium.PolyLine(route_coords, color=tech_color_map[tech_name], weight=4, opacity=0.8, tooltip=f"Route for {tech_name}").add_to(m)

            st_folium(m, width=1200, height=550)
        else:
            st.info("Please upload orders and run the AI Dispatch Engine in Tab 1 first.")

    # TAB 3: LIVE TRACKER & 2-WAY ALERTS
    with nav3:
        st.header("🛰️ Dedicated Live GPS Tracker & 2-Way Command Center")
        
        c_map, c_alerts = st.columns([2, 1])
        
        with c_map:
            st.subheader("📍 Live Fleet Locations")
            m_live = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11)
            
            # SAFE DEFENSIVE RETRIEVAL WITH .get()
            for _, tech in tech_df.iterrows():
                if str(tech.get('status', 'Active')) != 'Active': continue
                
                active_status = str(tech.get('active_status', 'Idle'))
                status_color = "green" if active_status == 'On-Site' else ("blue" if active_status == 'In Transit' else "gray")
                lat = float(tech.get('last_lat', 30.0074))
                lng = float(tech.get('last_lng', 31.4312))
                ping = str(tech.get('last_ping', 'Just Now'))
                name = str(tech.get('name', 'Technician'))
                
                folium.Marker(
                    [lat, lng],
                    popup=f"<b>{name}</b><br>Status: {active_status}<br>Last Ping: {ping}",
                    tooltip=f"{name} ({active_status})",
                    icon=folium.Icon(color=status_color, icon="user", prefix="fa")
                ).add_to(m_live)
            st_folium(m_live, width=700, height=480)

        with c_alerts:
            st.subheader("🚨 Send Forced Alert or Ping")
            target_tech = st.selectbox("Select Technician:", tech_df['name'].tolist())
            alert_msg = st.text_area("Urgent Forced Message:", placeholder="e.g. Work order #104 cancelled. Go directly to Tagamoa emergency WO-902.")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🚨 Send Forced Alert", type="primary"):
                    if alert_msg:
                        send_alert(target_tech, alert_msg)
                        st.success(f"Alert transmitted to {target_tech}!")
                    else:
                        st.warning("Please enter a message.")
            with col_b2:
                if st.button("⚡ Ping GPS Location"):
                    st.info(f"High-accuracy location ping sent to {target_tech}!")

            st.markdown("---")
            st.subheader("📥 Live Tech Replies & Acknowledgments")
            alerts_df = get_alerts()
            if not alerts_df.empty:
                for _, a in alerts_df.iterrows():
                    status_badge = "🟢 ACKNOWLEDGED" if a['status'] == 'ACKNOWLEDGED' else "🔴 PENDING READ"
                    with st.expander(f"{status_badge} - {a['tech_name']} ({a['sent_time']})"):
                        st.write(f"**Dispatch Message:** {a['message']}")
                        if a['status'] == 'ACKNOWLEDGED':
                            st.success(f"**Tech Reply:** {a['tech_reply']} (at {a['reply_time']})")
                        else:
                            st.warning("Awaiting technician interaction on mobile screen...")
            else:
                st.caption("No alerts logged today.")

    # TAB 4: FLEET PERFORMANCE & COSTING
    with nav4:
        st.header("📊 Master Fleet Analytics & Net Margins")
        if 'tracker' in st.session_state:
            tr = st.session_state['tracker']
            fr = st.session_state.get('fuel_rate', 4.5)
            rows = []
            for name, info in tr.items():
                fuel_cost = info['total_dist_km'] * fr
                net_margin = info['projected_revenue'] - fuel_cost
                rows.append({
                    "Technician": name,
                    "Jobs Assigned": len(info['assigned_jobs']),
                    "Capacity": info['capacity'],
                    "Travel (KM)": round(info['total_dist_km'], 1),
                    "Work Time (Hrs)": round(info['total_work_min'] / 60.0, 1),
                    "Revenue (EGP)": info['projected_revenue'],
                    "Est. Fuel Cost": round(fuel_cost, 1),
                    "Net Margin (EGP)": round(net_margin, 1)
                })
            df_perf = pd.DataFrame(rows)
            st.dataframe(df_perf, use_container_width=True)

            c_a1, c_a2 = st.columns(2)
            with c_a1:
                st.subheader("💰 Projected Revenue by Technician")
                st.bar_chart(df_perf.set_index("Technician")["Revenue (EGP)"])
            with c_a2:
                st.subheader("🚗 Total Distance Traveled (KM)")
                st.bar_chart(df_perf.set_index("Technician")["Travel (KM)"])
        else:
            st.info("Run the AI Dispatch Engine in Tab 1 to calculate real-time fleet analytics.")

    # TAB 5: CANCELLATIONS & POSTPONEMENTS LEDGER
    with nav5:
        st.header("🚫 Cancelled & Postponed Work Orders Ledger")
        if 'cancelled_postponed' in st.session_state:
            df_canc = st.session_state['cancelled_postponed']
            if not df_canc.empty:
                st.warning(f"Found {len(df_canc)} cancelled or postponed orders.")
                st.dataframe(df_canc, use_container_width=True)
            else:
                st.success("No cancelled or postponed orders found in the uploaded batch!")
        else:
            st.info("Upload orders in Tab 1 to view cancellations.")

    # TAB 6: TECHNICIAN DATABASE MANAGER
    with nav6:
        st.header("⚙️ Technician Master Database Manager")
        st.caption("Add, edit, or modify technician profiles, home bases, capacities, and active statuses.")
        
        edited = st.data_editor(tech_df, use_container_width=True, num_rows="dynamic")
        
        c_db1, c_db2 = st.columns(2)
        with c_db1:
            if st.button("💾 Save Database Changes", type="primary"):
                save_tech_df(edited)
                st.success("Technician database successfully saved to disk!")
                st.rerun()
        with c_db2:
            if st.button("🔄 Reset to Default Technicians"):
                with sqlite3.connect("dispatch_system.db") as conn:
                    conn.execute("DROP TABLE IF EXISTS technicians")
                init_db()
                st.success("Database reset to defaults!")
                st.rerun()

# ===================================================================
# MODE 2: TECHNICIAN MOBILE PORTAL
# ===================================================================
else:
    st.title("📱 Technician Mobile Web Portal")
    
    tech_names = tech_df['name'].tolist() if not tech_df.empty else ["Default Tech"]
    active_tech = st.selectbox("Simulate Active Technician Mobile App:", tech_names)
    
    st.info("📍 Live GPS Signal Active: Transmitting coordinates to Command Center every 2 minutes.")
    
    alerts_df = get_alerts()
    pending = pd.DataFrame()
    if not alerts_df.empty and 'tech_name' in alerts_df.columns and 'status' in alerts_df.columns:
        pending = alerts_df[(alerts_df['tech_name'] == active_tech) & (alerts_df['status'] == 'PENDING')]

    if not pending.empty:
        current_alert = pending.iloc[0]
        st.error("🚨 **URGENT DISPATCH NOTICE (SCREEN LOCKED)**")
        st.warning("Message from Dispatch: " + str(current_alert.get('message', '')))
        
        st.markdown("---")
        st.subheader("💬 Reply to Dispatch")
        
        quick_reply = st.radio("Quick Options:", [
            "🟢 Accepted & Moving Now", 
            "🟡 Delayed by Traffic (15-20 mins)", 
            "🔴 Need Call Back / Emergency", 
            "Custom Typed Response"
        ])
        
        custom_txt = ""
        if quick_reply == "Custom Typed Response":
            custom_txt = st.text_input("Type your reply message:")
            
        final_reply = custom_txt if quick_reply == "Custom Typed Response" else quick_reply
        
        if st.button("🚀 Send Response & Unlock Screen", type="primary"):
            reply_alert(current_alert['id'], final_reply if final_reply else "Acknowledged")
            st.success("Reply transmitted to Command Center! Screen Unlocked.")
            st.rerun()
    else:
        st.success("✅ All clear. No pending forced alerts.")
        st.subheader("📋 Your Assigned Route Today")
        if 'active_orders' in st.session_state:
            my_jobs = st.session_state['active_orders'][st.session_state['active_orders']['Assigned_Tech'] == active_tech]
            if not my_jobs.empty:
                st.dataframe(my_jobs[['Stop_Sequence', 'Work_Order', 'Brand', 'Customer_Name', 'Customer_Phone', 'Address', 'Time_Slot', 'Est_Duration_Min', 'Est_Travel_KM']], use_container_width=True)
            else:
                st.info("You have no work orders assigned in the current schedule.")
        else:
            st.info("No active dispatch schedule published for today yet.")
