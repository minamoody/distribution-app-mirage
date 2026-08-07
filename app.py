import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import urllib.parse
import io
import math
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------------
# 1. PAGE CONFIG & STYLING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="High-Speed AI Dynamic Dispatch & Fleet Command Center",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

MIRAGE_CENTER_COORDS = (30.0074, 31.4312)

# Cached Coordinate Mapping for Maximum Performance
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

# Dynamic Duration Estimator per Appliance & Service (Feature 20)
SERVICE_DURATIONS_MIN = {
    "installation": 90,
    "repair": 60,
    "maintenance": 45,
    "inspection": 30
}

T = {
    "English": {
        "title": "⚡ High-Speed Dynamic AI Dispatch Command Center",
        "tab1": "🚀 High-Speed Dispatch Engine",
        "tab2": "🗺️ TSP Sequenced Route Map",
        "tab3": "📱 Driver WhatsApp Portal",
        "tab4": "📊 Technician & Fleet Analytics",
        "tab5": "🚫 Cancelled & Postponed Orders",
        "tab6": "⚙️ Tech Profiles & Multi-Brand DB",
        "upload_header": "📂 Upload Daily Work Orders Sheet",
        "upload_label": "Upload Excel or CSV Order Sheet",
        "dispatch_opts": "Optimization & SLA Settings",
        "allow_overflow": "Allow Dynamic Cross-Brand Dispatch",
        "traffic_factor": "Traffic Congestion Delay Multiplier",
        "fuel_cost_label": "Est. Fuel Cost per KM (EGP)",
        "run_dispatch": "⚡ Run High-Speed AI Dispatch & TSP Sequencing",
        "results_header": "📋 Sequenced Dispatch Results",
        "download_excel": "📥 Download Complete Multi-Sheet Report (Excel)",
        "orders_loaded": "Loaded {count} orders successfully!",
        "map_header": "🗺️ Geographic TSP Route Map",
        "wa_header": "📱 Technician Mobile Dispatch Messages",
        "wa_send": "📲 Send via WhatsApp",
        "wa_jobs": "Jobs assigned",
        "no_data": "No active dispatch data available yet. Please run dispatch first.",
        "analytics_header": "📊 Fleet Performance & Capacity Summary",
        "db_header": "⚙️ Master Technician Database",
        "save_db": "💾 Save Database Changes",
        "db_updated": "Technician database updated successfully!",
        "lang_select": "🌐 Language / اللغة",
    },
    "العربية": {
        "title": "⚡ مركز التوجيه والتحكم الذكي السريع للأسطول",
        "tab1": "🚀 المحرك الذكي التفاعلي",
        "tab2": "🗺️ خريطة مسارات التسلسل الزمني (TSP)",
        "tab3": "📱 بوابة وتفاصيل الفنيين (واتساب)",
        "tab4": "📊 تحليلات تقارير الأداء والفنيين",
        "tab5": "🚫 الأوامر الملغاة والمؤجلة",
        "tab6": "⚙️ قاعدة بيانات البروفايل والفنيين",
        "upload_header": "📂 رفع جدول أوامر العمل اليومية",
        "upload_label": "رفع ملف أوامر العمل (Excel أو CSV)",
        "dispatch_opts": "إعدادات الحركة والأولويات السريعة",
        "allow_overflow": "السماح بالتوزيع التبادلي بين العلامات",
        "traffic_factor": "معامل التأخير والازدحام المروري",
        "fuel_cost_label": "متوسط تكلفة الوقود لكل كم (جنيه)",
        "run_dispatch": "⚡ تشغيل التوزيع السريع وتسلسل المسارات (TSP)",
        "results_header": "📋 نتائج التوزيع وتسلسل خطوط السير",
        "download_excel": "📥 تحميل التقرير الشامل التفاعلي (Excel متعدد الصفحات)",
        "orders_loaded": "تم تحميل {count} أمر عمل بنجاح!",
        "map_header": "🗺️ خريطة المسارات المبتكرة للتوزيع الذكي",
        "wa_header": "📱 رسائل أوامر العمل اليومية للفنيين",
        "wa_send": "📲 إرسال عبر واتساب",
        "wa_jobs": "مهام مُسندة",
        "no_data": "لا توجد بيانات توزيع نشطة حالياً. يرجى تشغيل التوزيع أولاً.",
        "analytics_header": "📊 تحليلات سعة وأداء الأسطول والفنيين",
        "db_header": "⚙️ قاعدة البيانات الرئيسية للفنيين",
        "save_db": "💾 حفظ التغييرات",
        "db_updated": "تم تحديث البيانات بنجاح!",
        "lang_select": "🌐 اختر اللغة / Language",
    }
}

# -------------------------------------------------------------------
# 2. SIDEBAR & DATABASE
# -------------------------------------------------------------------
st.sidebar.title("⚙️ Settings / الإعدادات")
selected_lang = st.sidebar.selectbox("🌐 Language / اللغة", options=["English", "العربية"], index=0)
txt = T[selected_lang]

def init_db():
    conn = sqlite3.connect("dispatch_system.db")
    c = conn.cursor()
    c.execute("PRAGMA table_info(technicians)")
    existing_cols = [col[1] for col in c.fetchall()]
    
    if existing_cols and ("base_lat" in existing_cols or "appliance_specialty" not in existing_cols):
        c.execute("DROP TABLE technicians")
        conn.commit()
        
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
            status TEXT
        )
    """)
    
    c.execute("SELECT COUNT(*) FROM technicians")
    if c.fetchone()[0] == 0:
        default_data = [
            ("أحمد عماد", "201000000001", "Brand A, Brand B", "AC, Refrigerator", "Installation, Maintenance", "Motorcycle", 8, "Mirage Service Center", "Shorouk", 35, "Senior", "Active"),
            ("شعبان", "201000000002", "Brand A", "Refrigerator, AC", "Installation, Repair", "Car", 10, "Mirage Service Center", "Madinaty", 40, "Senior", "Active"),
            ("كيمكو", "201000000003", "Brand B, Brand C", "Washing Machine, Oven", "Installation, Maintenance, Repair", "Car", 12, "Home / Outside", "Maadi", 35, "Mid", "Active"),
            ("محمد سامي", "201000000004", "Brand A, Brand B, Brand C", "AC, Refrigerator", "Maintenance, Repair", "Motorcycle", 7, "Home / Outside", "Maadi", 20, "Junior", "Active"),
            ("تكنو", "201000000005", "All Brands", "Oven, Washing Machine, Other Appliances", "Installation, Repair", "Car", 10, "Mirage Service Center", "Tagamoa", 35, "Senior", "Active"),
            ("حسن", "201000000006", "Brand C", "Other Appliances", "Maintenance", "Motorcycle", 8, "Home / Outside", "Tagamoa", 20, "Mid", "On Leave"),
        ]
        c.executemany("""
            INSERT INTO technicians 
            (name, phone, brand, appliance_specialty, skills, vehicle, capacity, start_type, home_zone, max_radius_km, experience, status) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, default_data)
        conn.commit()
    conn.close()

init_db()

def get_tech_df():
    conn = sqlite3.connect("dispatch_system.db")
    df = pd.read_sql_query("SELECT * FROM technicians", conn)
    conn.close()
    return df

def save_tech_df(df):
    conn = sqlite3.connect("dispatch_system.db")
    df_clean = df.drop(columns=['base_lat', 'base_lng'], errors='ignore')
    df_clean.to_sql("technicians", conn, if_exists="replace", index=False)
    conn.close()

# -------------------------------------------------------------------
# 3. HIGH-SPEED GEOGRAPHIC MATH & FAST CACHING
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

def generate_google_maps_url(address, city):
    full_loc = f"{address}, {city}, Egypt" if address else f"{city}, Egypt"
    return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(full_loc)}"

def generate_whatsapp_link(phone, tech_name, orders, lang="English"):
    if lang == "العربية":
        msg = f"📱 *جدول أسلوب الحركة والمواعيد المتسلسلة لـ {tech_name}*\n"
        msg += f"إجمالي المهام المؤكدة: {len(orders)}\n\n"
        for _, row in orders.iterrows():
            seq = row.get('Stop_Sequence', 1)
            msg += f"🛑 *المحطة #{seq}* | WO #{row.get('Work_Order', 'N/A')}\n"
            msg += f"🏢 *العلامة التجارية:* {row.get('Brand', 'N/A')}\n"
            msg += f"👤 *العميل:* {row.get('Customer_Name', 'N/A')} ({row.get('Customer_Phone', 'N/A')})\n"
            msg += f"⏰ *النافذة المحددة:* {row.get('Time_Slot', 'N/A')} (التقدير: {row.get('Est_Duration_Min', 60)} دقيقة)\n"
            msg += f"📍 *العنوان:* {row.get('Address', 'N/A')}, {row.get('City', 'N/A')}\n"
            msg += f"🗺️ *الخريطة:* {generate_google_maps_url(row.get('Address', ''), row.get('City', ''))}\n"
            if str(row.get('Is_Emergency', '')).lower() in ['true', '1', 'yes']:
                msg += f"🚨 *تنبيه: حالة طارئة / أولوية قصوى*\n"
            msg += f"----------------------------------\n"
    else:
        msg = f"📱 *TSP Route & Scheduled Orders for {tech_name}*\n"
        msg += f"Total Assigned Jobs: {len(orders)}\n\n"
        for _, row in orders.iterrows():
            seq = row.get('Stop_Sequence', 1)
            msg += f"🛑 *Stop #{seq}* | WO #{row.get('Work_Order', 'N/A')}\n"
            msg += f"🏢 *Brand:* {row.get('Brand', 'N/A')}\n"
            msg += f"👤 *Client:* {row.get('Customer_Name', 'N/A')} ({row.get('Customer_Phone', 'N/A')})\n"
            msg += f"⏰ *Time Slot:* {row.get('Time_Slot', 'N/A')} (Est. Duration: {row.get('Est_Duration_Min', 60)} mins)\n"
            msg += f"📍 *Address:* {row.get('Address', 'N/A')}, {row.get('City', 'N/A')}\n"
            msg += f"🗺️ *Map:* {generate_google_maps_url(row.get('Address', ''), row.get('City', ''))}\n"
            if str(row.get('Is_Emergency', '')).lower() in ['true', '1', 'yes']:
                msg += f"🚨 *HIGH PRIORITY / EMERGENCY JOB*\n"
            msg += f"----------------------------------\n"
            
    clean_phone = str(phone).replace("+", "").replace(" ", "").split(".")[0]
    return f"https://wa.me/{clean_phone}?text={urllib.parse.quote(msg)}"

# -------------------------------------------------------------------
# 4. OPTIMIZED ENGINE: TSP ROUTING, EMERGENCY SLA & TRAFFIC
# -------------------------------------------------------------------
def run_optimized_dispatch(df_raw, tech_df, allow_overflow=True, traffic_factor=1.2):
    orders = df_raw.copy()
    
    # Normalize Column Names efficiently
    col_map = {c: c.strip().title().replace(" ", "_") for c in orders.columns}
    orders.rename(columns=col_map, inplace=True)
    if 'City' not in orders.columns and 'Area' in orders.columns:
        orders.rename(columns={'Area': 'City'}, inplace=True)
    if 'Status' not in orders.columns:
        orders['Status'] = 'Pending'

    # Filter Cancelled and Postponed Orders into separate tracker (Feature 18)
    cancelled_or_postponed = orders[orders['Status'].astype(str).str.upper().isin(['CANCELLED', 'CANCELED', 'POSTPONED', 'DELAYED'])].copy()
    active_orders = orders[~orders['Status'].astype(str).str.upper().isin(['CANCELLED', 'CANCELED', 'POSTPONED', 'DELAYED'])].copy()

    # Pre-calculate Durations (Feature 20)
    def calc_duration(row):
        service = str(row.get('Service_Type', '')).lower()
        for k, v in SERVICE_DURATIONS_MIN.items():
            if k in service:
                return v
        return 60

    active_orders['Est_Duration_Min'] = active_orders.apply(calc_duration, axis=1)
    
    # Handle High SLA / Emergency Flags (Feature 17)
    if 'Is_Emergency' not in active_orders.columns:
        active_orders['Is_Emergency'] = False
    else:
        active_orders['Is_Emergency'] = active_orders['Is_Emergency'].astype(str).str.lower().isin(['true', '1', 'yes'])

    active_orders['Assigned_Tech'] = "Unassigned"
    active_orders['Stop_Sequence'] = 0
    active_orders['Est_Travel_KM'] = 0.0

    active_techs = tech_df[tech_df['status'] == 'Active'].copy()
    
    # Setup Tech Tracker
    tracker = {}
    for _, row in active_techs.iterrows():
        eff_lat, eff_lng = get_effective_coords(row)
        tracker[row['name']] = {
            'brands': [b.strip().lower() for b in str(row.get('brand', 'General')).split(',')],
            'raw_brand_str': str(row.get('brand', 'General')),
            'specialties': [s.strip().lower() for s in str(row.get('appliance_specialty', 'AC')).split(',')],
            'skills': [sk.strip().lower() for sk in str(row.get('skills', '')).split(',')],
            'vehicle': str(row.get('vehicle', 'Motorcycle')),
            'capacity': int(row.get('capacity', 8)),
            'phone': str(row.get('phone', '201000000000')),
            'start_type': str(row.get('start_type', 'Mirage Service Center')),
            'home_zone': str(row.get('home_zone', 'Tagamoa')),
            'base_lat': eff_lat,
            'base_lng': eff_lng,
            'max_radius_km': float(row.get('max_radius_km', 25)),
            'assigned_jobs': [],
            'total_dist_km': 0.0,
            'total_work_min': 0,
            'projected_revenue': 0.0
        }

    # Order Sorting Strategy: Emergency Jobs First, then Time Slot
    active_orders.sort_values(by=['Is_Emergency', 'Time_Slot'], ascending=[False, True], inplace=True)

    # 1. MATCHING ENGINE
    for idx, row in active_orders.iterrows():
        order_brand = str(row.get('Brand', '')).strip().lower()
        order_appliance = str(row.get('Appliance', row.get('Appliance_Type', ''))).strip().lower()
        city_raw = str(row.get('City', '')).upper().strip()
        revenue = float(row.get('Estimated_Revenue', 350.0))
        is_emergency = row['Is_Emergency']
        
        order_coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))

        candidates = []
        for name, info in tracker.items():
            if len(info['assigned_jobs']) >= info['capacity']:
                continue
                
            dist_km = fast_haversine_km(info['base_lat'], info['base_lng'], order_coords[0], order_coords[1]) * traffic_factor
            if dist_km > info['max_radius_km']:
                continue

            score = dist_km
            
            # Brand & Specialty Discounts
            is_brand_match = not order_brand or any(order_brand in b or b in order_brand or 'all' in b for b in info['brands'])
            if is_brand_match:
                score -= 12.0
            elif not allow_overflow:
                continue
            else:
                score += 20.0

            is_spec_match = any(order_appliance in s or s in order_appliance or 'all' in s for s in info['specialties'])
            if is_spec_match: score -= 10.0

            # Emergency Priority Discount
            if is_emergency: score -= 30.0

            # Workload Balancing Penalty
            score += (len(info['assigned_jobs']) / float(info['capacity'])) * 15.0

            candidates.append((name, score, dist_km))

        if candidates:
            best_tech, _, dist_km = min(candidates, key=lambda x: x[1])
            active_orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned_jobs'].append(idx)
            tracker[best_tech]['projected_revenue'] += revenue
            tracker[best_tech]['total_work_min'] += row['Est_Duration_Min']

    # 2. TSP ROUTE SEQUENCING (Feature 1 & Feature 4 - Smart Stop & Home Return Optimization)
    for name, info in tracker.items():
        job_indices = info['assigned_jobs']
        if not job_indices:
            continue
            
        current_lat = info['base_lat']
        current_lng = info['base_lng']
        unvisited = job_indices.copy()
        sequence = 1
        
        home_coords = next((c for k, c in CITY_COORDS.items() if k in info['home_zone'].upper()), MIRAGE_CENTER_COORDS)

        while unvisited:
            # Nearest Neighbor greedy TSP calculation
            next_job = None
            best_dist = float('inf')
            
            for idx in unvisited:
                row = active_orders.loc[idx]
                city_raw = str(row.get('City', '')).upper().strip()
                coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
                
                dist = fast_haversine_km(current_lat, current_lng, coords[0], coords[1])
                
                # Smart Home-Return Preference for Final Stop (Feature 4)
                if len(unvisited) == 1:
                    home_dist = fast_haversine_km(coords[0], coords[1], home_coords[0], home_coords[1])
                    dist = (dist * 0.5) + (home_dist * 0.5)

                if dist < best_dist:
                    best_dist = dist
                    next_job = idx

            active_orders.at[next_job, 'Stop_Sequence'] = sequence
            active_orders.at[next_job, 'Est_Travel_KM'] = round(best_dist, 2)
            
            info['total_dist_km'] += best_dist
            
            # Update current position to latest stop location
            city_raw = str(active_orders.loc[next_job].get('City', '')).upper().strip()
            curr_coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
            current_lat, current_lng = curr_coords[0], curr_coords[1]
            
            unvisited.remove(next_job)
            sequence += 1

    active_orders.sort_values(by=['Assigned_Tech', 'Stop_Sequence'], inplace=True)
    return active_orders, cancelled_or_postponed, tracker

# -------------------------------------------------------------------
# 5. APP NAVIGATION & UI
# -------------------------------------------------------------------
st.title(txt["title"])

nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5, nav_tab6 = st.tabs([
    txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"], txt["tab5"], txt["tab6"]
])

tech_df = get_tech_df()

# -------------------------------------------------------------------
# TAB 1: DISPATCH ENGINE
# -------------------------------------------------------------------
with nav_tab1:
    st.header(txt["upload_header"])
    col_file, col_opts = st.columns([2, 1])
    
    with col_file:
        uploaded_file = st.file_uploader(txt["upload_label"], type=["xlsx", "csv"])
        
        sample_df = pd.DataFrame([{
            "Work Order": "WO-101",
            "Brand": "Brand A",
            "Customer Name": "أحمد محمود",
            "Customer Phone": "01012345678",
            "City": "Maadi",
            "Address": "Street 9, Villa 4",
            "Time Slot": "09:00 AM - 12:00 PM",
            "Appliance": "AC",
            "Service Type": "Repair",
            "Status": "Pending",
            "Is Emergency": True,
            "Estimated Revenue": 500.0
        }, {
            "Work Order": "WO-102",
            "Brand": "Brand B",
            "Customer Name": "سارة علي",
            "Customer Phone": "01123456789",
            "City": "Shorouk",
            "Address": "District 2, Bld 10",
            "Time Slot": "12:00 PM - 03:00 PM",
            "Appliance": "Refrigerator",
            "Service Type": "Maintenance",
            "Status": "Postponed",
            "Is Emergency": False,
            "Estimated Revenue": 400.0
        }])
        
        tmpl_output = io.BytesIO()
        with pd.ExcelWriter(tmpl_output, engine='openpyxl') as writer:
            sample_df.to_excel(writer, index=False, sheet_name='Orders')
        st.download_button("📥 Download Master Template (.xlsx)", tmpl_output.getvalue(), "Orders_Template.xlsx")

    with col_opts:
        st.markdown(f"### {txt['dispatch_opts']}")
        allow_overflow = st.checkbox(txt["allow_overflow"], value=True)
        traffic_factor = st.slider(txt["traffic_factor"], 1.0, 2.0, 1.2, step=0.1)
        fuel_cost_per_km = st.number_input(txt["fuel_cost_label"], value=4.5, step=0.5)

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.success(txt["orders_loaded"].format(count=len(df_raw)))
        
        if st.button(txt["run_dispatch"], type="primary"):
            active_orders, cancelled_or_postponed, tracker = run_optimized_dispatch(df_raw, tech_df, allow_overflow, traffic_factor)
            
            st.session_state['active_orders'] = active_orders
            st.session_state['cancelled_or_postponed'] = cancelled_or_postponed
            st.session_state['tracker'] = tracker
            st.session_state['fuel_cost_per_km'] = fuel_cost_per_km

            st.subheader(txt["results_header"])
            st.dataframe(active_orders[['Stop_Sequence', 'Assigned_Tech', 'Work_Order', 'Brand', 'Customer_Name', 'City', 'Time_Slot', 'Est_Duration_Min', 'Est_Travel_KM', 'Is_Emergency']], use_container_width=True)

            # Build Multi-Sheet Excel File (Feature 19)
            multi_excel = io.BytesIO()
            with pd.ExcelWriter(multi_excel, engine='openpyxl') as writer:
                active_orders.to_excel(writer, index=False, sheet_name='Dispatched_Orders_TSP')
                
                # Build Technician Performance Excel Sheet
                tech_perf_rows = []
                for name, info in tracker.items():
                    tech_perf_rows.append({
                        "Technician Name": name,
                        "Assigned Jobs": len(info['assigned_jobs']),
                        "Capacity": info['capacity'],
                        "Capacity Utilization": f"{(len(info['assigned_jobs'])/info['capacity'])*100:.1f}%",
                        "Est Distance (KM)": round(info['total_dist_km'], 2),
                        "Total Work (Hours)": round(info['total_work_min']/60.0, 2),
                        "Projected Revenue (EGP)": info['projected_revenue'],
                        "Vehicle": info['vehicle'],
                        "Covered Brands": info['raw_brand_str']
                    })
                pd.DataFrame(tech_perf_rows).to_excel(writer, index=False, sheet_name='Technician_Performance')
                
                cancelled_or_postponed.to_excel(writer, index=False, sheet_name='Cancelled_Postponed_Orders')
                
            st.download_button(
                label=txt["download_excel"],
                data=multi_excel.getvalue(),
                file_name="Master_Dispatch_Report_MultiSheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------------------------------------------------------
# TAB 2: TSP ROUTE MAP
# -------------------------------------------------------------------
with nav_tab2:
    st.header(txt["map_header"])
    if 'active_orders' in st.session_state:
        orders = st.session_state['active_orders']
        m = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11, tiles="OpenStreetMap")
        
        folium.Marker(MIRAGE_CENTER_COORDS, popup="🏭 <b>Mirage Center</b>", icon=folium.Icon(color="red", icon="building", prefix="fa")).add_to(m)

        for _, tech in tech_df[tech_df['status'] == 'Active'].iterrows():
            eff_lat, eff_lng = get_effective_coords(tech)
            folium.Marker([eff_lat, eff_lng], popup=f"👨‍🔧 {tech['name']}", icon=folium.Icon(color="green", icon="user", prefix="fa")).add_to(m)

        for _, row in orders.iterrows():
            if row['Assigned_Tech'] == 'Unassigned': continue
            city_raw = str(row.get('City', '')).upper().strip()
            coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
            
            is_emer = row.get('Is_Emergency', False)
            icon_color = "red" if is_emer else "blue"
            
            folium.Marker(
                coords,
                popup=f"Stop #{row['Stop_Sequence']} | Tech: {row['Assigned_Tech']}<br>WO: {row.get('Work_Order')}<br>Brand: {row.get('Brand')}",
                tooltip=f"Stop #{row['Stop_Sequence']} - {row['Assigned_Tech']}",
                icon=folium.Icon(color=icon_color, icon="star" if is_emer else "wrench", prefix="fa")
            ).add_to(m)
            
        st_folium(m, width=1200, height=500)
    else:
        st.info(txt["no_data"])

# -------------------------------------------------------------------
# TAB 3: WHATSAPP MOBILE PORTAL
# -------------------------------------------------------------------
with nav_tab3:
    st.header(txt["wa_header"])
    if 'active_orders' in st.session_state:
        orders = st.session_state['active_orders']
        for tech in orders['Assigned_Tech'].unique():
            if tech == "Unassigned": continue
            tech_orders = orders[orders['Assigned_Tech'] == tech].copy().sort_values(by='Stop_Sequence')
            tech_info = tech_df[tech_df['name'] == tech].iloc[0]
            
            wa_url = generate_whatsapp_link(tech_info['phone'], tech, tech_orders, lang=selected_lang)
            
            with st.expander(f"👨‍🔧 {tech} ({len(tech_orders)} {txt['wa_jobs']})"):
                st.markdown(f"[📲 **{txt['wa_send']}**]({wa_url})", unsafe_allow_html=True)
                st.dataframe(tech_orders[['Stop_Sequence', 'Work_Order', 'Brand', 'Customer_Name', 'Customer_Phone', 'Time_Slot', 'City', 'Address', 'Est_Duration_Min', 'Is_Emergency']], use_container_width=True)
    else:
        st.info(txt["no_data"])

# -------------------------------------------------------------------
# TAB 4: TECHNICIAN & FLEET ANALYTICS
# -------------------------------------------------------------------
with nav_tab4:
    st.header(txt["analytics_header"])
    if 'tracker' in st.session_state:
        tracker = st.session_state['tracker']
        fuel_cost_rate = st.session_state.get('fuel_cost_per_km', 4.5)
        
        tech_summary = []
        for name, info in tracker.items():
            fuel_cost = info['total_dist_km'] * fuel_cost_rate
            net_profit = info['projected_revenue'] - fuel_cost
            
            tech_summary.append({
                "Technician": name,
                "Vehicle": info['vehicle'],
                "Assigned Jobs": len(info['assigned_jobs']),
                "Capacity": info['capacity'],
                "Utilization %": f"{(len(info['assigned_jobs'])/info['capacity'])*100:.1f}%",
                "Total Travel (KM)": round(info['total_dist_km'], 1),
                "Work Hours": round(info['total_work_min']/60.0, 1),
                "Revenue (EGP)": info['projected_revenue'],
                "Est. Fuel Cost (EGP)": round(fuel_cost, 1),
                "Net Margin (EGP)": round(net_profit, 1)
            })
            
        summary_df = pd.DataFrame(tech_summary)
        st.dataframe(summary_df, use_container_width=True)
    else:
        st.info(txt["no_data"])

# -------------------------------------------------------------------
# TAB 5: CANCELLED & POSTPONED ORDERS TRACKER
# -------------------------------------------------------------------
with nav_tab5:
    st.header("🚫 Cancelled & Postponed Work Orders Log")
    if 'cancelled_or_postponed' in st.session_state:
        canc_df = st.session_state['cancelled_or_postponed']
        if not canc_df.empty:
            st.warning(f"Found {len(canc_df)} order(s) marked as Cancelled or Postponed.")
            st.dataframe(canc_df, use_container_width=True)
        else:
            st.success("No cancelled or postponed orders found in the uploaded batch.")
    else:
        st.info(txt["no_data"])

# -------------------------------------------------------------------
# TAB 6: DB SETUP
# -------------------------------------------------------------------
with nav_tab6:
    st.header(txt["db_header"])
    edited_df = st.data_editor(tech_df, num_rows="dynamic", use_container_width=True)
    if st.button(txt["save_db"]):
        save_tech_df(edited_df)
        st.success(txt["db_updated"])
        st.rerun()
