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
# 1. PAGE CONFIG & UI TRANSLATIONS
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Dispatch Command Center",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Central Mirage Service Center Location
MIRAGE_CENTER_COORDS = (30.0074, 31.4312)

T = {
    "English": {
        "title": "⚡ AI Fleet Command & Proximity Dispatch System",
        "tab1": "🚀 Dispatch Hub",
        "tab2": "🗺️ Interactive Map",
        "tab3": "📱 Driver WhatsApp Portal",
        "tab4": "📊 Analytics & Costs",
        "tab5": "⚙️ Advanced Tech Database",
        # Tab 1
        "upload_header": "📂 Daily Order Allocation",
        "upload_label": "Upload Daily Excel / CSV Order Sheet",
        "dispatch_opts": "Dispatch Options",
        "allow_overflow": "Allow Cross-Brand Overflow",
        "overflow_help": "If a brand team is full, allow other available drivers to assist.",
        "fuel_cost_label": "Est. Fuel Cost per KM (EGP)",
        "run_dispatch": "⚡ Run AI Proximity Dispatch",
        "results_header": "📋 Dispatch Allocation Results",
        "download_excel": "📥 Download Dispatched Sheet (Excel)",
        "orders_loaded": "Loaded {count} orders successfully!",
        # Tab 2
        "map_header": "🗺️ Geographic Route & Tech Base Clustering",
        "map_info": "Run the AI Dispatcher in the 'Dispatch Hub' tab to view map routes.",
        # Tab 3
        "wa_header": "📱 Technician Dispatch & Mobile View",
        "wa_send": "📲 Send Work Orders via WhatsApp",
        "wa_jobs": "Jobs assigned",
        "no_data": "No active dispatch data available yet.",
        "vehicle": "Vehicle",
        "phone": "Phone",
        "status": "Status",
        # Tab 4
        "analytics_header": "📊 Performance & Transport Cost Analytics",
        "total_jobs": "Total Jobs",
        "allocated": "Allocated",
        "est_dist": "Est. Total Fleet Distance",
        "est_fuel_cost": "Est. Fleet Fuel Cost",
        "heatmap": "Fleet Capacity & Proximity Matrix",
        "run_analytics_first": "Run dispatch to populate analytics dashboard.",
        # Tab 5
        "db_header": "⚙️ Master Technician Profile Setup",
        "db_sub": "Configure start location (Mirage Center vs. Home), GPS base coordinates, max travel radius, experience, and active status.",
        "save_db": "💾 Save Database Changes",
        "db_updated": "Technician profiles updated successfully!",
        "lang_select": "🌐 Language / اللغة",
    },
    "العربية": {
        "title": "⚡ نظام إدارة وتوزيع الأسطول الذكي حسب الموقع",
        "tab1": "🚀 مركز التوزيع",
        "tab2": "🗺️ الخريطة التفاعلية",
        "tab3": "📱 بوابة واتساب للفنيين",
        "tab4": "📊 التحليلات والتكاليف",
        "tab5": "⚙️ قاعدة بيانات الفنيين المتقدمة",
        # Tab 1
        "upload_header": "📂 توزيع أوامر العمل اليومية",
        "upload_label": "رفع ملف أوامر العمل (Excel أو CSV)",
        "dispatch_opts": "خيارات التوزيع",
        "allow_overflow": "السماح بالتوزيع بين العلامات التجارية",
        "overflow_help": "إذا كانت سعة فريق علامة معينة مكتملة، يتم الاستعانة بفنيين آخرين قريبي الموقع.",
        "fuel_cost_label": "متوسط تكلفة الوقود لكل كم (جنيه)",
        "run_dispatch": "⚡ تشغيل التوزيع الذكي حسب المسافة",
        "results_header": "📋 نتائج توزيع المهام",
        "download_excel": "📥 تحميل جدول التوزيع (Excel)",
        "orders_loaded": "تم تحميل {count} أمر عمل بنجاح!",
        # Tab 2
        "map_header": "🗺️ خريطة مسارات الفنيين ومواقع الانطلاق",
        "map_info": "قم بتشغيل الموزع الذكي في تبويب 'مركز التوزيع' لعرض المسارات على الخريطة.",
        # Tab 3
        "wa_header": "📱 تفاصيل مهام الفنيين والعرض المباشر",
        "wa_send": "📲 إرسال أوامر العمل عبر واتساب",
        "wa_jobs": "مهام مُسندة",
        "no_data": "لا توجد بيانات توزيع نشطة حالياً.",
        "vehicle": "وسيلة النقل",
        "phone": "الهاتف",
        "status": "الحالة",
        # Tab 4
        "analytics_header": "📊 تحليلات الأداء وتكاليف النقل",
        "total_jobs": "إجمالي المهام",
        "allocated": "نسبة التوزيع",
        "est_dist": "إجمالي المسافة التقديرية",
        "est_fuel_cost": "تكلفة الوقود التقديرية",
        "heatmap": "مصفوفة سعة الأسطول والنطاق الجغرافي",
        "run_analytics_first": "قم بتشغيل التوزيع لعرض تحليلات الأداء.",
        # Tab 5
        "db_header": "⚙️ إعداد البروفايل التفصيلي للفنيين",
        "db_sub": "تحديد نقطة الانطلاق (مركز ميراج أو المنزل)، الإحداثيات، نطاق الحركة الأقصى، الخبرة، وحالة التواجد.",
        "save_db": "💾 حفظ التغييرات في قاعدة البيانات",
        "db_updated": "تم تحديث بيانات الفنيين بنجاح!",
        "lang_select": "🌐 اختر اللغة / Language",
    }
}

# -------------------------------------------------------------------
# 2. SIDEBAR LANGUAGE SELECTION & STYLING
# -------------------------------------------------------------------
st.sidebar.title("⚙️ Settings / الإعدادات")
selected_lang = st.sidebar.selectbox("🌐 Language / اللغة", options=["English", "العربية"], index=0)
txt = T[selected_lang]

if selected_lang == "العربية":
    st.markdown("""
        <style>
        .main { text-align: right; direction: rtl; }
        .stSelectbox, .stTextInput, .stNumberInput, .stCheckbox { text-align: right; }
        .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
        </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. DATABASE SETUP WITH AUTO MIGRATION & SAFE RECOVERY
# -------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("dispatch_system.db")
    c = conn.cursor()
    
    # Check existing table schema
    c.execute("PRAGMA table_info(technicians)")
    existing_cols = [col[1] for col in c.fetchall()]
    
    # Reset table if it exists without updated columns
    if existing_cols and ("status" not in existing_cols or "start_type" not in existing_cols):
        c.execute("DROP TABLE technicians")
        conn.commit()
        existing_cols = []
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            brand TEXT,
            skills TEXT,
            vehicle TEXT,
            capacity INTEGER,
            start_type TEXT,
            home_zone TEXT,
            base_lat REAL,
            base_lng REAL,
            max_radius_km INTEGER,
            experience TEXT,
            status TEXT
        )
    """)
    
    c.execute("SELECT COUNT(*) FROM technicians")
    if c.fetchone()[0] == 0:
        default_data = [
            ("أحمد عماد", "201000000001", "Brand A", "Installation,Maintenance", "Motorcycle", 8, "Mirage Service Center", "Shorouk", 30.1458, 31.6067, 25, "Senior", "Active"),
            ("شعبان", "201000000002", "Brand A", "Installation", "Car", 10, "Mirage Service Center", "Madinaty", 30.0917, 31.6295, 40, "Senior", "Active"),
            ("كيمكو", "201000000003", "Brand B", "Installation,Maintenance", "Car", 12, "Home / Outside", "Maadi", 29.9602, 31.2569, 35, "Mid", "Active"),
            ("محمد سامي", "201000000004", "Brand B", "Customer Service", "Motorcycle", 7, "Home / Outside", "Maadi", 29.9602, 31.2569, 15, "Junior", "Active"),
            ("تكنو", "201000000005", "Brand C", "Installation", "Car", 10, "Mirage Service Center", "Tagamoa", 30.0074, 31.4312, 30, "Senior", "Active"),
            ("حسن", "201000000006", "Brand C", "Customer Service", "Motorcycle", 8, "Home / Outside", "Tagamoa", 30.0074, 31.4312, 20, "Mid", "On Leave"),
        ]
        c.executemany("""
            INSERT INTO technicians 
            (name, phone, brand, skills, vehicle, capacity, start_type, home_zone, base_lat, base_lng, max_radius_km, experience, status) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, default_data)
        conn.commit()
    conn.close()

init_db()

def get_tech_df():
    conn = sqlite3.connect("dispatch_system.db")
    df = pd.read_sql_query("SELECT * FROM technicians", conn)
    conn.close()
    
    # Guarantee critical columns exist in memory
    defaults = {
        'start_type': 'Mirage Service Center',
        'base_lat': 30.0074,
        'base_lng': 31.4312,
        'max_radius_km': 25,
        'experience': 'Mid',
        'status': 'Active'
    }
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val
            
    return df

def save_tech_df(df):
    conn = sqlite3.connect("dispatch_system.db")
    df.to_sql("technicians", conn, if_exists="replace", index=False)
    conn.close()

def get_effective_coords(row):
    if row.get('start_type') == "Mirage Service Center":
        return MIRAGE_CENTER_COORDS
    return (row.get('base_lat', MIRAGE_CENTER_COORDS[0]), row.get('base_lng', MIRAGE_CENTER_COORDS[1]))

# -------------------------------------------------------------------
# 4. GEO-DISTANCE CALCULATIONS & DISPATCH ENGINE
# -------------------------------------------------------------------
CITY_COORDS = {
    "MADINATY": (30.0917, 31.6295),
    "TAGAMOA": (30.0074, 31.4312),
    "SHOROUK": (30.1458, 31.6067),
    "MAADI": (29.9602, 31.2569),
    "HELIOPOLIS": (30.0889, 31.3262),
    "NASR CITY": (30.0561, 31.3301),
    "MOKKATAM": (30.0167, 31.3000),
    "OCTOBER": (29.9722, 30.9439),
    "BADR": (30.1408, 31.7454),
}

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth's radius in KM
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def classify_distance(city_name):
    FAR_AREAS = ["MADINATY", "MOSTAKBAL", "TAGAMOA", "OCTOBER", "ISMAILIA", "KATAMEYA", "ZAMALEK", "QALYUB"]
    city_str = str(city_name).upper().strip()
    return "Far" if any(area in city_str for area in FAR_AREAS) else "Near"

def generate_whatsapp_link(phone, tech_name, orders, lang="English"):
    if lang == "العربية":
        msg = f"📱 *أوامر العمل اليومية لـ {tech_name}*\n"
        msg += f"إجمالي المهام: {len(orders)}\n\n"
        for i, (_, row) in enumerate(orders.iterrows(), 1):
            msg += f"*{i}. رقم الطلب:* {row.get('Work_Order', 'N/A')}\n"
            msg += f"📍 *المنطقة:* {row.get('City', 'N/A')}\n"
            msg += f"🛠️ *نوع الخدمة:* {row.get('Service_Type', 'Standard')}\n"
            msg += f"------------------\n"
    else:
        msg = f"📱 *Daily Work Orders for {tech_name}*\n"
        msg += f"Total Jobs: {len(orders)}\n\n"
        for i, (_, row) in enumerate(orders.iterrows(), 1):
            msg += f"*{i}. WO:* {row.get('Work_Order', 'N/A')}\n"
            msg += f"📍 *Area:* {row.get('City', 'N/A')}\n"
            msg += f"🛠️ *Type:* {row.get('Service_Type', 'Standard')}\n"
            msg += f"------------------\n"
    
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "")
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

def run_smart_dispatch(orders_df, tech_df, allow_overflow=True):
    orders = orders_df.copy()
    
    col_map = {c: c.strip().title().replace(" ", "_") for c in orders.columns}
    orders.rename(columns=col_map, inplace=True)
    if 'City' not in orders.columns and 'Area' in orders.columns:
        orders.rename(columns={'Area': 'City'}, inplace=True)

    orders['Distance_Type'] = orders['City'].apply(classify_distance)
    orders['Assigned_Tech'] = "Unassigned"
    
    # Filter active technicians safely
    active_techs = tech_df[tech_df['status'] == 'Active'].copy()
    
    tracker = {}
    for _, row in active_techs.iterrows():
        eff_lat, eff_lng = get_effective_coords(row)
        tracker[row['name']] = {
            'brand': row.get('brand', 'General'),
            'vehicle': row.get('vehicle', 'Motorcycle'),
            'capacity': row.get('capacity', 8),
            'phone': row.get('phone', '0000000000'),
            'skills': str(row.get('skills', '')).split(','),
            'start_type': row.get('start_type', 'Mirage Service Center'),
            'base_lat': eff_lat,
            'base_lng': eff_lng,
            'max_radius_km': row.get('max_radius_km', 25),
            'experience': row.get('experience', 'Mid'),
            'assigned': 0
        }
    
    orders = orders.sort_values(by=['Distance_Type'], ascending=True)
    
    for idx, row in orders.iterrows():
        order_brand = row.get('Brand', None)
        city_raw = str(row.get('City', '')).upper().strip()
        dist_type = row['Distance_Type']
        target_vehicle = "Car" if dist_type == "Far" else "Motorcycle"
        
        order_coords = next((coords for k, coords in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
        
        valid_candidates = []
        for name, info in tracker.items():
            if info['assigned'] >= info['capacity']:
                continue
                
            dist_to_order = haversine_km(info['base_lat'], info['base_lng'], order_coords[0], order_coords[1])
            if dist_to_order > info['max_radius_km']:
                continue
                
            score = dist_to_order
            
            if order_brand is not None and info['brand'] == order_brand:
                score -= 10
            if info['vehicle'] == target_vehicle:
                score -= 5
                
            valid_candidates.append((name, score))
            
        if valid_candidates:
            best_tech = min(valid_candidates, key=lambda x: x[1])[0]
            orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned'] += 1
        elif allow_overflow:
            available = [t for t, info in tracker.items() if info['assigned'] < info['capacity']]
            if available:
                best_tech = min(available, key=lambda t: tracker[t]['assigned'])
                orders.at[idx, 'Assigned_Tech'] = best_tech
                tracker[best_tech]['assigned'] += 1
                
    return orders, tracker

# -------------------------------------------------------------------
# 5. APP INTERFACE & NAVIGATION
# -------------------------------------------------------------------
st.title(txt["title"])

nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"], txt["tab5"]
])

tech_df = get_tech_df()

# -------------------------------------------------------------------
# TAB 1: DISPATCH HUB
# -------------------------------------------------------------------
with nav_tab1:
    st.header(txt["upload_header"])
    
    col_file, col_opts = st.columns([2, 1])
    with col_file:
        uploaded_file = st.file_uploader(txt["upload_label"], type=["xlsx", "csv"])
    with col_opts:
        st.markdown(f"### {txt['dispatch_opts']}")
        allow_overflow = st.checkbox(txt["allow_overflow"], value=True, help=txt["overflow_help"])
        fuel_cost_per_km = st.number_input(txt["fuel_cost_label"], value=4.5, step=0.5)

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.session_state['df_raw'] = df_raw
        st.success(txt["orders_loaded"].format(count=len(df_raw)))
        
        if st.button(txt["run_dispatch"], type="primary"):
            processed_orders, tracker = run_smart_dispatch(df_raw, tech_df, allow_overflow)
            st.session_state['processed_orders'] = processed_orders
            st.session_state['tracker'] = tracker
            st.session_state['fuel_cost_per_km'] = fuel_cost_per_km
            
            st.subheader(txt["results_header"])
            display_cols = [c for c in ['Work_Order', 'City', 'Service_Type', 'Distance_Type', 'Assigned_Tech'] if c in processed_orders.columns]
            st.dataframe(processed_orders[display_cols], use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                processed_orders.to_excel(writer, index=False, sheet_name='Dispatched_Orders')
            excel_data = output.getvalue()
            
            st.download_button(
                label=txt["download_excel"],
                data=excel_data,
                file_name="Dispatched_Work_Orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------------------------------------------------------
# TAB 2: INTERACTIVE MAP & ROUTING
# -------------------------------------------------------------------
with nav_tab2:
    st.header(txt["map_header"])
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        
        m = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11, tiles="OpenStreetMap")
        
        # Plot Central Mirage Service Center Hub
        folium.Marker(
            location=MIRAGE_CENTER_COORDS,
            popup="🏭 <b>Mirage Service Center (Central Hub)</b>",
            icon=folium.Icon(color="red", icon="building", prefix="fa")
        ).add_to(m)

        # Plot Active Tech Base Locations
        for _, tech in tech_df[tech_df['status'] == 'Active'].iterrows():
            eff_lat, eff_lng = get_effective_coords(tech)
            start_label = tech['start_type']
            
            folium.Marker(
                location=[eff_lat, eff_lng],
                popup=f"👨‍🔧 <b>{tech['name']}</b><br>Start: {start_label}<br>Radius: {tech['max_radius_km']} KM",
                icon=folium.Icon(color="green" if start_label=="Home / Outside" else "purple", icon="user", prefix="fa")
            ).add_to(m)
            
            folium.Circle(
                radius=tech['max_radius_km'] * 1000,
                location=[eff_lat, eff_lng],
                color="purple" if start_label=="Mirage Service Center" else "green",
                fill=True,
                fill_opacity=0.04
            ).add_to(m)
        
        # Plot Order Markers
        for idx, row in orders.iterrows():
            city_raw = str(row.get('City', '')).upper().strip()
            coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), None)
            
            if not coords:
                coords = (30.0444 + np.random.uniform(-0.04, 0.04), 31.2357 + np.random.uniform(-0.04, 0.04))
                
            tech = row.get('Assigned_Tech', 'Unassigned')
            dist = row.get('Distance_Type', 'Near')
            color = "blue" if dist == "Near" else "orange"
            
            folium.Marker(
                location=coords,
                popup=f"Order: {row.get('Work_Order', 'N/A')}<br>Tech: {tech}<br>Area: {city_raw}",
                tooltip=f"{tech} ({city_raw})",
                icon=folium.Icon(color=color, icon="wrench" if dist=="Far" else "motorcycle", prefix="fa")
            ).add_to(m)
            
        st_folium(m, width=1200, height=500)
    else:
        st.info(txt["map_info"])

# -------------------------------------------------------------------
# TAB 3: WHATSAPP & DRIVER MOBILE PORTAL
# -------------------------------------------------------------------
with nav_tab3:
    st.header(txt["wa_header"])
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        techs = orders['Assigned_Tech'].unique()
        
        for tech in techs:
            if tech == "Unassigned": continue
            tech_orders = orders[orders['Assigned_Tech'] == tech]
            tech_match = tech_df[tech_df['name'] == tech]
            tech_info = tech_match.iloc[0] if not tech_match.empty else None
            phone = tech_info['phone'] if tech_info is not None else "201000000000"
            
            wa_url = generate_whatsapp_link(phone, tech, tech_orders, lang=selected_lang)
            
            with st.expander(f"👨‍🔧 {tech} ({len(tech_orders)} {txt['wa_jobs']})"):
                st.markdown(f"**{txt['vehicle']}:** {tech_info['vehicle']} | **Start Location:** {tech_info['start_type']} | **{txt['phone']}:** {phone}")
                st.markdown(f"[📲 **{txt['wa_send']}**]({wa_url})", unsafe_allow_html=True)
                show_cols = [c for c in ['Work_Order', 'City', 'Service_Type'] if c in tech_orders.columns]
                st.dataframe(tech_orders[show_cols], use_container_width=True)
    else:
        st.info(txt["no_data"])

# -------------------------------------------------------------------
# TAB 4: MANAGER ANALYTICS & COST ESTIMATOR
# -------------------------------------------------------------------
with nav_tab4:
    st.header(txt["analytics_header"])
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        tracker = st.session_state['tracker']
        fuel_cost_rate = st.session_state.get('fuel_cost_per_km', 4.5)
        
        col1, col2, col3, col4 = st.columns(4)
        total_orders = len(orders)
        assigned_count = len(orders[orders['Assigned_Tech'] != 'Unassigned'])
        far_count = len(orders[orders['Distance_Type'] == 'Far'])
        
        est_distance = (far_count * 35) + ((total_orders - far_count) * 12)
        total_fuel_cost = est_distance * fuel_cost_rate
        
        col1.metric(txt["total_jobs"], total_orders)
        col2.metric(txt["allocated"], f"{(assigned_count/total_orders)*100:.1f}%")
        col3.metric(txt["est_dist"], f"{est_distance} KM")
        col4.metric(txt["est_fuel_cost"], f"{total_fuel_cost:,.0f} EGP")
        
        st.markdown(f"### {txt['heatmap']}")
        capacity_df = pd.DataFrame([
            {
                "Technician": k, 
                "Start Location": v['start_type'],
                "Vehicle": v['vehicle'], 
                "Brand": v['brand'], 
                "Experience": v['experience'],
                "Max Radius (KM)": v['max_radius_km'],
                "Assigned": v['assigned'], 
                "Capacity": v['capacity']
            }
            for k, v in tracker.items()
        ])
        st.dataframe(capacity_df, use_container_width=True)
    else:
        st.info(txt["run_analytics_first"])

# -------------------------------------------------------------------
# TAB 5: ADVANCED TECHNICIAN DATABASE SETUP
# -------------------------------------------------------------------
with nav_tab5:
    st.header(txt["db_header"])
    st.markdown(txt["db_sub"])
    
    edited_df = st.data_editor(
        tech_df,
        num_rows="dynamic",
        column_config={
            "start_type": st.column_config.SelectboxColumn("Start Location", options=["Mirage Service Center", "Home / Outside"], required=True),
            "vehicle": st.column_config.SelectboxColumn("Vehicle", options=["Motorcycle", "Car"], required=True),
            "status": st.column_config.SelectboxColumn("Status", options=["Active", "On Leave", "Inactive"], required=True),
            "experience": st.column_config.SelectboxColumn("Experience Level", options=["Junior", "Mid", "Senior"], required=True),
            "capacity": st.column_config.NumberColumn("Daily Capacity", min_value=1, max_value=30, default=8),
            "max_radius_km": st.column_config.NumberColumn("Max Radius (KM)", min_value=5, max_value=150, default=25),
            "base_lat": st.column_config.NumberColumn("Base Latitude (Home)", format="%.4f"),
            "base_lng": st.column_config.NumberColumn("Base Longitude (Home)", format="%.4f"),
        },
        use_container_width=True
    )
    
    if st.button(txt["save_db"]):
        save_tech_df(edited_df)
        st.success(txt["db_updated"])
        st.rerun()
