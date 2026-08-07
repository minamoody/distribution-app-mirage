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
# 1. PAGE CONFIG & STYLING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Dispatch Command & Field Tech GPS Tracker",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

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

# -------------------------------------------------------------------
# 2. DATABASE INITIALIZATION & HELPER FUNCTIONS
# -------------------------------------------------------------------
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
        return pd.read_sql_query("SELECT * FROM technicians", conn)

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
# 3. FAST GEOGRAPHIC MATH & COORDINATE RESOLUTION
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
    if str(row.get('start_type')) == "Mirage Service Center":
        return MIRAGE_CENTER_COORDS
    zone_raw = str(row.get('home_zone', '')).upper().strip()
    return next((coords for k, coords in CITY_COORDS.items() if k in zone_raw or zone_raw in k), MIRAGE_CENTER_COORDS)

# -------------------------------------------------------------------
# 4. DISPATCH ENGINE (TSP SEQUENCING)
# -------------------------------------------------------------------
def run_optimized_dispatch(df_raw, tech_df, allow_overflow=True, traffic_factor=1.2):
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
                score -= 30.0

            candidates.append((name, score, dist_km))

        if candidates:
            best_tech, _, dist_km = min(candidates, key=lambda x: x[1])
            active_orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned_jobs'].append(idx)
            tracker[best_tech]['projected_revenue'] += revenue
            tracker[best_tech]['total_work_min'] += row['Est_Duration_Min']

    # TSP Route Sequencing
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
            allow_overflow = st.checkbox("Allow Cross-Brand Overflow", value=True)
            traffic_factor = st.slider("Traffic Congestion Multiplier", 1.0, 2.0, 1.2)
            fuel_rate = st.number_input("Fuel Cost / KM (EGP)", value=4.5)

        if uploaded_file:
            df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            st.success(f"Successfully loaded {len(df_raw)} work orders!")
            
            if st.button("⚡ Execute AI Routing & Dispatch", type="primary"):
                active_orders, cancelled_postponed, tracker = run_optimized_dispatch(df_raw, tech_df, allow_overflow, traffic_factor)
                st.session_state['active_orders'] = active_orders
                st.session_state['cancelled_postponed'] = cancelled_postponed
                st.session_state['tracker'] = tracker
                st.session_state['fuel_rate'] = fuel_rate

                st.dataframe(active_orders[['Stop_Sequence', 'Assigned_Tech', 'Work_Order', 'Brand', 'Customer_Name', 'City', 'Time_Slot', 'Est_Duration_Min', 'Est_Travel_KM', 'Is_Emergency']], use_container_width=True)

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
                            "Revenue (EGP)": info['projected_revenue']
                        })
                    pd.DataFrame(perf_rows).to_excel(writer, index=False, sheet_name='Tech_Performance')
                    cancelled_postponed.to_excel(writer, index=False, sheet_name='Cancelled_Postponed')

                st.download_button("📥 Download Master Multi-Sheet Dispatch Report", multi_excel.getvalue(), "Master_Dispatch_Report.xlsx")

    # TAB 2: ROUTE MAP
    with nav2:
        st.header("🗺️ Sequenced Technician TSP Route Map")
        if 'active_orders' in st.session_state:
            orders = st.session_state['active_orders']
            m = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11)
            folium.Marker(MIRAGE_CENTER_COORDS, popup="🏭 Mirage Base Center", icon=folium.Icon(color="red", icon="building", prefix="fa")).add_to(m)

            for _, row in orders.iterrows():
                if row['Assigned_Tech'] == 'Unassigned': continue
                city_raw = str(row.get('City', '')).upper().strip()
                coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
                folium.Marker(
                    coords,
                    popup=f"Stop #{row['Stop_Sequence']} | {row['Assigned_Tech']}<br>WO: {row.get('Work_Order')}",
                    icon=folium.Icon(color="red" if row.get('Is_Emergency') else "blue", icon="wrench", prefix="fa")
                ).add_to(m)
            st_folium(m, width=1200, height=500)
        else:
            st.info("Please upload orders and run the AI Dispatch Engine in Tab 1 first.")

    # TAB 3: LIVE TRACKER & 2-WAY ALERTS
    with nav3:
        st.header("🛰️ Dedicated Live GPS Tracker & 2-Way Command Center")
        
        c_map, c_alerts = st.columns([2, 1])
        
        with c_map:
            st.subheader("📍 Live Fleet Locations")
            m_live = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11)
            
            for _, tech in tech_df.iterrows():
                if tech['status'] != 'Active': continue
                status_color = "green" if tech['active_status'] == 'On-Site' else ("blue" if tech['active_status'] == 'In Transit' else "gray")
                folium.Marker(
                    [tech['last_lat'], tech['last_lng']],
                    popup=f"<b>{tech['name']}</b><br>Status: {tech['active_status']}<br>Last Ping: {tech['last_ping']}",
                    tooltip=f"{tech['name']} ({tech['active_status']})",
                    icon=folium.Icon(color=status_color, icon="user", prefix="fa")
                ).add_to(m_live)
            st_folium(m_live, width=700, height=450)

        with c_alerts:
            st.subheader("🚨 Send Forced Alert or Ping")
            target_tech = st.selectbox("Select Technician:", tech_df['name'].tolist())
            alert_msg = st.text_area("Urgent Forced Message:", placeholder="e.g. Work order #104 cancelled. Go directly to Tagamoa emergency WO-902.")
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("🚨 Send Forced Alert"):
                    if alert_msg:
                        send_alert(target_tech, alert_msg)
                        st.success(f"Alert transmitted to {target_tech}!")
            with col_b2:
                if st.button("⚡ Ping GPS Location"):
                    st.info(f"High-accuracy location request sent to {target_tech}!")

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

    # TAB 4: ANALYTICS
    with nav4:
        st.header("📊 Master Fleet Analytics & Net Margins")
        if 'tracker' in st.session_state:
            tr = st.session_state['tracker']
            fr = st.session_state.get('fuel_rate', 4.5)
            rows = []
            for name, info in tr.items():
                fuel_cost = info['total_dist_km'] * fr
                rows.append({
                    "Technician": name,
                    "Jobs": len(info['assigned_jobs']),
                    "Capacity": info['capacity'],
                    "Travel (KM)": round(info['total_dist_km'], 1),
                    "Revenue (EGP)": info['projected_revenue'],
                    "Est. Fuel Cost": round(fuel_cost, 1),
                    "Net Margin": round(info['projected_revenue'] - fuel_cost, 1)
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

    # TAB 5: CANCELLATIONS
    with nav5:
        st.header("🚫 Cancelled & Postponed Work Orders")
        if 'cancelled_postponed' in st.session_state:
            st.dataframe(st.session_state['cancelled_postponed'], use_container_width=True)

    # TAB 6: DB EDITING
    with nav6:
        st.header("⚙️ Technician Master Database Editor")
        edited = st.data_editor(tech_df, use_container_width=True)
        if st.button("💾 Save Database Changes"):
            save_tech_df(edited)
            st.success("Technician database successfully updated!")

# ===================================================================
# MODE 2: TECHNICIAN MOBILE PORTAL (SIMULATOR & BROWSER INTERFACE)
# ===================================================================
else:
    st.title("📱 Technician Mobile Web Portal")
    active_tech = st.selectbox("Simulate / Active Technician:", tech_df['name'].tolist())
    
    st.info("📍 Live GPS Signal Active: Transmitting coordinates to Command Center every 2 minutes.")
    
    # Check for active pending alerts
    alerts_df = get_alerts()
    pending = alerts_df[(alerts_df['tech_name'] == active_tech) & (alerts_df['status'] == 'PENDING')]

    if not pending.empty:
        current_alert = pending.iloc[0]
        st.error("🚨 **URGENT DISPATCH NOTICE (SCREEN LOCKED)**")
        st.warning(f"**Message from Dispatch:**\n\n{current_alert['message']}")
        
        st.markdown("---")
        st.subheader("💬 Reply to Dispatch")
        
        quick_reply = st.radio("Quick Options:", ["🟢 Accepted & Moving Now", "🟡 Delayed by Traffic (15-20 mins)", "🔴 Need Call Back / Emergency", "Custom Typed Response"])
        
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
            st.dataframe(my_jobs[['Stop_Sequence', 'Work_Order', 'Brand', 'Customer_Name', 'Customer_Phone', 'Address', 'Time_Slot']], use_container_width=True)
        else:
            st.info("No active dispatch schedule published for today yet.")
