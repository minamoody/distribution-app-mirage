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
    page_title="AI Dynamic Multi-Brand Dispatch Command Center",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Central Mirage Hub Location
MIRAGE_CENTER_COORDS = (30.0074, 31.4312)

# Dynamic Neighborhood / Area Location Lookup
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

T = {
    "English": {
        "title": "⚡ Dynamic Multi-Brand AI Dispatch & Scheduling Command Center",
        "tab1": "🚀 Dynamic Dispatch Hub",
        "tab2": "🗺️ Dynamic Route Map",
        "tab3": "📱 Driver WhatsApp Portal",
        "tab4": "📊 Fleet & Financial Analytics",
        "tab5": "⚙️ Tech Profiles & Multi-Brand DB",
        "upload_header": "📂 Upload Daily Work Orders Sheet",
        "upload_label": "Upload Excel or CSV Order Sheet",
        "dispatch_opts": "Dynamic Routing Options",
        "allow_overflow": "Allow Dynamic Cross-Brand Dispatch",
        "overflow_help": "Allows technicians assigned to multiple brands or generalists to seamlessly fulfill orders across brands when efficient.",
        "fuel_cost_label": "Est. Fuel Cost per KM (EGP)",
        "run_dispatch": "⚡ Run Dynamic Multi-Factor AI Dispatch",
        "results_header": "📋 AI Dynamic Allocation Results",
        "download_excel": "📥 Download Dispatched Sheet (Excel)",
        "orders_loaded": "Loaded {count} orders successfully!",
        "map_header": "🗺️ Geographic Route & Multi-Brand Clustering",
        "map_info": "Run the AI Dispatcher in the 'Dynamic Dispatch Hub' tab to view live routes.",
        "wa_header": "📱 Technician Dispatch & Mobile View",
        "wa_send": "📲 Send Work Orders via WhatsApp",
        "wa_jobs": "Jobs assigned",
        "no_data": "No active dispatch data available yet.",
        "vehicle": "Vehicle",
        "phone": "Phone",
        "status": "Status",
        "analytics_header": "📊 Multi-Brand Fleet & Capacity Analytics",
        "total_jobs": "Total Jobs",
        "allocated": "Allocated Ratio",
        "est_dist": "Est. Fleet Distance",
        "est_fuel_cost": "Est. Fuel Cost",
        "total_rev": "Total Projected Revenue",
        "net_margin": "Est. Net Fleet Margin",
        "util_rate": "Fleet Capacity Utilization",
        "heatmap": "Technician Capacity, Brands & Revenue Breakdown",
        "run_analytics_first": "Run dispatch to populate dynamic analytics dashboard.",
        "db_header": "⚙️ Master Technician Profile & Multi-Brand Setup",
        "db_sub": "Configure multi-brand coverage, appliance specialties, specific repair skills, base location, max radius, vehicle type, and capacity.",
        "save_db": "💾 Save Database Changes",
        "db_updated": "Technician multi-brand profiles updated successfully!",
        "lang_select": "🌐 Language / اللغة",
    },
    "العربية": {
        "title": "⚡ نظام التوزيع والتوجيه الذكي الديناميكي متعدد العلامات التجارية",
        "tab1": "🚀 مركز التوزيع الديناميكي",
        "tab2": "🗺️ الخريطة التفاعلية",
        "tab3": "📱 بوابة واتساب للفنيين",
        "tab4": "📊 تحليلات الأداء والأسطول",
        "tab5": "⚙️ بروفايل الفنيين والعلامات التجارية",
        "upload_header": "📂 رفع جدول أوامر العمل اليومية",
        "upload_label": "رفع ملف أوامر العمل (Excel أو CSV)",
        "dispatch_opts": "خيارات التوزيع الديناميكي",
        "allow_overflow": "السماح بالتوزيع التبادلي بين العلامات",
        "overflow_help": "يتيح للفنيين المعتمدين لأكثر من علامة تجارية أو الفريق المساعد التغطية عند الحاجة.",
        "fuel_cost_label": "متوسط تكلفة الوقود لكل كم (جنيه)",
        "run_dispatch": "⚡ تشغيل التوزيع الذكي الشامل",
        "results_header": "📋 نتائج التوزيع الشامل والذكي",
        "download_excel": "📥 تحميل جدول التوزيع (Excel)",
        "orders_loaded": "تم تحميل {count} أمر عمل بنجاح!",
        "map_header": "🗺️ خريطة مسارات الفنيين ومواقع الانطلاق",
        "map_info": "قم بتشغيل الموزع الذكي في 'مركز التوزيع' لعرض المسارات تفاعلياً.",
        "wa_header": "📱 تفاصيل مهام الفنيين وإرسال واتساب",
        "wa_send": "📲 إرسال المهام عبر واتساب",
        "wa_jobs": "مهام مُسندة",
        "no_data": "لا توجد بيانات توزيع نشطة حالياً.",
        "vehicle": "وسيلة النقل",
        "phone": "الهاتف",
        "status": "الحالة",
        "analytics_header": "📊 تحليلات الأداء والإيرادات والسعة الاستيعابية",
        "total_jobs": "إجمالي المهام",
        "allocated": "نسبة التوزيع",
        "est_dist": "إجمالي المسافة",
        "est_fuel_cost": "تكلفة الوقود",
        "total_rev": "إجمالي الإيراد المتوقع",
        "net_margin": "صافي الربح التقديري",
        "util_rate": "نسبة استغلال سعة الأسطول",
        "heatmap": "مصفوفة أداء وسعة وساعات الفنيين والإيرادات",
        "run_analytics_first": "قم بتشغيل التوزيع لعرض تحليلات الأداء.",
        "db_header": "⚙️ إعداد البروفايل الشامل متعدد العلامات التجارية للفنيين",
        "db_sub": "تحديد العلامات التجارية المغطاة (علامة واحدة أو متعددة)، التخصصات، المهارات، نطاق الحركة، والقدرة الاستيعابية.",
        "save_db": "💾 حفظ التغييرات في قاعدة البيانات",
        "db_updated": "تم تحديث بيانات البروفايل بنجاح!",
        "lang_select": "🌐 اختر اللغة / Language",
    }
}

# -------------------------------------------------------------------
# 2. SIDEBAR LANGUAGE SELECTION
# -------------------------------------------------------------------
st.sidebar.title("⚙️ Settings / الإعدادات")
selected_lang = st.sidebar.selectbox("🌐 Language / اللغة", options=["English", "العربية"], index=0)
txt = T[selected_lang]

if selected_lang == "العربية":
    st.markdown("""
        <style>
        .main { text-align: right; direction: rtl; }
        .stSelectbox, .stTextInput, .stNumberInput, .stCheckbox { text-align: right; }
        </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# 3. DATABASE SETUP & INITIALIZATION
# -------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("dispatch_system.db")
    c = conn.cursor()
    
    c.execute("PRAGMA table_info(technicians)")
    existing_cols = [col[1] for col in c.fetchall()]
    
    # Refresh DB if schema is older version
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
        # Initial multi-brand tech profile setup
        default_data = [
            ("أحمد عماد", "201000000001", "Brand A, Brand B", "AC, Refrigerator", "Installation, Maintenance", "Motorcycle", 8, "Mirage Service Center", "Shorouk", 25, "Senior", "Active"),
            ("شعبان", "201000000002", "Brand A", "Refrigerator, AC", "Installation, Repair", "Car", 10, "Mirage Service Center", "Madinaty", 40, "Senior", "Active"),
            ("كيمكو", "201000000003", "Brand B, Brand C", "Washing Machine, Oven", "Installation, Maintenance, Repair", "Car", 12, "Home / Outside", "Maadi", 35, "Mid", "Active"),
            ("محمد سامي", "201000000004", "Brand A, Brand B, Brand C", "AC, Refrigerator", "Maintenance, Repair", "Motorcycle", 7, "Home / Outside", "Maadi", 15, "Junior", "Active"),
            ("تكنو", "201000000005", "All Brands", "Oven, Washing Machine, Other Appliances", "Installation, Repair", "Car", 10, "Mirage Service Center", "Tagamoa", 30, "Senior", "Active"),
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
    df.drop(columns=['base_lat', 'base_lng'], errors='ignore', inplace=True)
    return df

def save_tech_df(df):
    conn = sqlite3.connect("dispatch_system.db")
    df_clean = df.drop(columns=['base_lat', 'base_lng'], errors='ignore')
    df_clean.to_sql("technicians", conn, if_exists="replace", index=False)
    conn.close()

def get_effective_coords(row):
    if row.get('start_type') == "Mirage Service Center":
        return MIRAGE_CENTER_COORDS
    zone_raw = str(row.get('home_zone', '')).upper().strip()
    return next((coords for k, coords in CITY_COORDS.items() if k in zone_raw or zone_raw in k), MIRAGE_CENTER_COORDS)

# -------------------------------------------------------------------
# 4. GEO-DISTANCE & UTILITIES
# -------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def classify_distance(city_name):
    FAR_AREAS = ["MADINATY", "MOSTAKBAL", "TAGAMOA", "OCTOBER", "ISMAILIA", "KATAMEYA", "ZAMALEK", "QALYUB", "BADR"]
    city_str = str(city_name).upper().strip()
    return "Far" if any(area in city_str for area in FAR_AREAS) else "Near"

def generate_google_maps_url(address, city):
    full_loc = f"{address}, {city}, Egypt" if address else f"{city}, Egypt"
    encoded = urllib.parse.quote(full_loc)
    return f"https://www.google.com/maps/search/?api=1&query={encoded}"

def generate_whatsapp_link(phone, tech_name, orders, lang="English"):
    if lang == "العربية":
        msg = f"📱 *أوامر العمل اليومية لـ {tech_name}*\n"
        msg += f"إجمالي المهام: {len(orders)}\n\n"
        for i, (_, row) in enumerate(orders.iterrows(), 1):
            addr = row.get('Address', row.get('Full_Address', 'N/A'))
            city = row.get('City', 'N/A')
            gmaps_link = generate_google_maps_url(addr, city)
            time_slot = row.get('Time_Slot', row.get('Preferred_Time', '09:00 AM - 05:00 PM'))

            msg += f"📋 *مهمة رقم #{i}*\n"
            msg += f"🔹 *رقم الطلب:* {row.get('Work_Order', row.get('Order_Id', 'N/A'))}\n"
            msg += f"🏢 *العلامة التجارية:* {row.get('Brand', 'N/A')}\n"
            msg += f"👤 *اسم العميل:* {row.get('Customer_Name', row.get('Client', 'N/A'))}\n"
            msg += f"📞 *هاتف العميل:* {row.get('Customer_Phone', row.get('Client_Phone', 'N/A'))}\n"
            msg += f"⏰ *الموعد:* {time_slot}\n"
            msg += f"📍 *المنطقة:* {city}\n"
            msg += f"🏠 *العنوان:* {addr}\n"
            msg += f"🗺️ *رابط Google Maps:* {gmaps_link}\n"
            msg += f"❄️ *الجهاز:* {row.get('Appliance', row.get('Appliance_Type', 'N/A'))}\n"
            msg += f"🛠️ *نوع الخدمة:* {row.get('Service_Type', 'N/A')}\n"
            if 'Notes' in row and pd.notna(row['Notes']) and str(row['Notes']).strip() != "":
                msg += f"📝 *ملاحظات:* {row['Notes']}\n"
            msg += f"----------------------------------\n"
    else:
        msg = f"📱 *Daily Work Orders for {tech_name}*\n"
        msg += f"Total Jobs: {len(orders)}\n\n"
        for i, (_, row) in enumerate(orders.iterrows(), 1):
            addr = row.get('Address', row.get('Full_Address', 'N/A'))
            city = row.get('City', 'N/A')
            gmaps_link = generate_google_maps_url(addr, city)
            time_slot = row.get('Time_Slot', row.get('Preferred_Time', '09:00 AM - 05:00 PM'))

            msg += f"📋 *Job #{i}*\n"
            msg += f"🔹 *WO #:* {row.get('Work_Order', row.get('Order_Id', 'N/A'))}\n"
            msg += f"🏢 *Brand:* {row.get('Brand', 'N/A')}\n"
            msg += f"👤 *Customer:* {row.get('Customer_Name', row.get('Client', 'N/A'))}\n"
            msg += f"📞 *Phone:* {row.get('Customer_Phone', row.get('Client_Phone', 'N/A'))}\n"
            msg += f"⏰ *Time Slot:* {time_slot}\n"
            msg += f"📍 *Area:* {city}\n"
            msg += f"🏠 *Address:* {addr}\n"
            msg += f"🗺️ *Google Maps:* {gmaps_link}\n"
            msg += f"❄️ *Appliance:* {row.get('Appliance', row.get('Appliance_Type', 'N/A'))}\n"
            msg += f"🛠️ *Service Type:* {row.get('Service_Type', 'N/A')}\n"
            if 'Notes' in row and pd.notna(row['Notes']) and str(row['Notes']).strip() != "":
                msg += f"📝 *Notes:* {row['Notes']}\n"
            msg += f"----------------------------------\n"
    
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "").split(".")[0]
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

# -------------------------------------------------------------------
# 5. DYNAMIC MULTI-FACTOR & MULTI-BRAND DISPATCH ENGINE
# -------------------------------------------------------------------
def run_smart_dispatch(orders_df, tech_df, allow_overflow=True):
    orders = orders_df.copy()
    
    col_map = {c: c.strip().title().replace(" ", "_") for c in orders.columns}
    orders.rename(columns=col_map, inplace=True)
    
    if 'City' not in orders.columns and 'Area' in orders.columns:
        orders.rename(columns={'Area': 'City'}, inplace=True)

    orders['Distance_Type'] = orders['City'].apply(classify_distance) if 'City' in orders.columns else "Near"
    orders['Assigned_Tech'] = "Unassigned"
    
    if 'Estimated_Revenue' not in orders.columns and 'Revenue' in orders.columns:
        orders.rename(columns={'Revenue': 'Estimated_Revenue'}, inplace=True)
    if 'Estimated_Revenue' not in orders.columns:
        orders['Estimated_Revenue'] = 350.0

    if 'Time_Slot' not in orders.columns and 'Preferred_Time' in orders.columns:
        orders.rename(columns={'Preferred_Time': 'Time_Slot'}, inplace=True)
    if 'Time_Slot' not in orders.columns:
        orders['Time_Slot'] = '09:00 AM - 12:00 PM'

    active_techs = tech_df[tech_df['status'] == 'Active'].copy()
    
    tracker = {}
    for _, row in active_techs.iterrows():
        eff_lat, eff_lng = get_effective_coords(row)
        
        # Parse multi-brands, specialties, and skills as clean lists
        brands = [b.strip().lower() for b in str(row.get('brand', 'General')).split(',')]
        specialties = [s.strip().lower() for s in str(row.get('appliance_specialty', 'AC')).split(',')]
        skills = [sk.strip().lower() for sk in str(row.get('skills', '')).split(',')]

        tracker[row['name']] = {
            'brands': brands,
            'raw_brand_str': str(row.get('brand', 'General')),
            'specialties': specialties,
            'raw_specialty_str': str(row.get('appliance_specialty', 'AC')),
            'skills': skills,
            'vehicle': str(row.get('vehicle', 'Motorcycle')),
            'capacity': int(row.get('capacity', 8)),
            'phone': str(row.get('phone', '201000000000')),
            'start_type': str(row.get('start_type', 'Mirage Service Center')),
            'base_lat': eff_lat,
            'base_lng': eff_lng,
            'max_radius_km': float(row.get('max_radius_km', 25)),
            'experience': str(row.get('experience', 'Mid')),
            'assigned': 0,
            'projected_revenue': 0.0
        }
    
    # Sort orders chronologically by Time Slot, then Far distance
    orders = orders.sort_values(by=['Time_Slot', 'Distance_Type'], ascending=[True, True])
    
    for idx, row in orders.iterrows():
        order_brand = str(row.get('Brand', '')).strip().lower()
        order_appliance = str(row.get('Appliance', row.get('Appliance_Type', ''))).strip().lower()
        order_service = str(row.get('Service_Type', '')).strip().lower()
        city_raw = str(row.get('City', '')).upper().strip()
        dist_type = row.get('Distance_Type', 'Near')
        revenue = float(row.get('Estimated_Revenue', 350.0))
        
        order_coords = next((coords for k, coords in CITY_COORDS.items() if k in city_raw or city_raw in k), (30.0444, 31.2357))
        
        candidates = []
        for name, info in tracker.items():
            # Check maximum daily capacity
            if info['assigned'] >= info['capacity']:
                continue
                
            # Proximity check vs max operational radius
            dist_km = haversine_km(info['base_lat'], info['base_lng'], order_coords[0], order_coords[1])
            if dist_km > info['max_radius_km']:
                continue
                
            # -------------------------------------------------------------
            # DYNAMIC MULTI-FACTOR SCORE CALCULATION (LOWER SCORE = BEST MATCH)
            # -------------------------------------------------------------
            score = dist_km  # Base Score = Actual Physical KM Distance
            
            # 1. Multi-Brand Dynamic Matching Engine
            is_brand_match = False
            if not order_brand or order_brand in ['nan', 'general', 'none', '']:
                is_brand_match = True
            elif any(order_brand in b or b in order_brand or 'all' in b for b in info['brands']):
                is_brand_match = True

            if is_brand_match:
                score -= 10.0  # Priority discount for direct brand capability
            else:
                if not allow_overflow:
                    continue  # Skip if cross-brand dynamic overflow is turned off
                score += 25.0 # Penalty for non-native brand: favors native techs first

            # 2. Appliance Specialty Matching
            is_spec_match = any(order_appliance in s or s in order_appliance or 'all' in s for s in info['specialties'])
            if is_spec_match:
                score -= 12.0
            else:
                score += 18.0

            # 3. Service Skill Matching (e.g. Repair vs Maintenance vs Installation)
            if order_service and any(order_service in sk or sk in order_service for sk in info['skills']):
                score -= 5.0

            # 4. Vehicle & Distance Optimization
            if dist_type == "Far" and info['vehicle'].lower() == "car":
                score -= 8.0  # Prefer cars for far highway jobs
            elif dist_type == "Far" and info['vehicle'].lower() == "motorcycle":
                score += 10.0

            # 5. Workload Balancing Penalty (distributes work evenly across technicians)
            capacity_utilization = info['assigned'] / float(info['capacity'])
            score += capacity_utilization * 15.0  # Dynamically penalizes techs who are almost full
            
            candidates.append((name, score))
            
        if candidates:
            # Pick tech with lowest overall penalty/distance match score
            best_tech = min(candidates, key=lambda x: x[1])[0]
            orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned'] += 1
            tracker[best_tech]['projected_revenue'] += revenue

    return orders, tracker

# -------------------------------------------------------------------
# 6. APP INTERFACE & NAVIGATION
# -------------------------------------------------------------------
st.title(txt["title"])

nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"], txt["tab5"]
])

tech_df = get_tech_df()

# -------------------------------------------------------------------
# TAB 1: DYNAMIC DISPATCH HUB
# -------------------------------------------------------------------
with nav_tab1:
    st.header(txt["upload_header"])
    
    col_file, col_opts = st.columns([2, 1])
    with col_file:
        uploaded_file = st.file_uploader(txt["upload_label"], type=["xlsx", "csv"])
        
        # Sample Multi-Brand Orders Template
        sample_orders_df = pd.DataFrame([{
            "Work Order": "WO-9901",
            "Brand": "Brand A",
            "Customer Name": "محمد السيد",
            "Customer Phone": "01012345678",
            "City": "Maadi",
            "Address": "Street 9, Building 14, Apt 3",
            "Time Slot": "09:00 AM - 12:00 PM",
            "Appliance": "AC",
            "Service Type": "Maintenance",
            "Estimated Revenue": 450.0,
            "Notes": "Compressor checking"
        }, {
            "Work Order": "WO-9902",
            "Brand": "Brand B",
            "Customer Name": "أحمد علي",
            "Customer Phone": "01123456789",
            "City": "Shorouk",
            "Address": "Villa 12, District 3",
            "Time Slot": "12:00 PM - 03:00 PM",
            "Appliance": "Refrigerator",
            "Service Type": "Repair",
            "Estimated Revenue": 600.0,
            "Notes": "Freon gas leak check"
        }, {
            "Work Order": "WO-9903",
            "Brand": "Brand C",
            "Customer Name": "مصطفى محمود",
            "Customer Phone": "01234567890",
            "City": "Tagamoa",
            "Address": "South 90th Street, Mall 4",
            "Time Slot": "03:00 PM - 06:00 PM",
            "Appliance": "Oven",
            "Service Type": "Installation",
            "Estimated Revenue": 500.0,
            "Notes": "New oven installation"
        }])
        tmpl_output = io.BytesIO()
        with pd.ExcelWriter(tmpl_output, engine='openpyxl') as writer:
            sample_orders_df.to_excel(writer, index=False, sheet_name='Multi_Brand_Orders')
        st.download_button(
            label="📥 Download Multi-Brand Work Order Template (.xlsx)",
            data=tmpl_output.getvalue(),
            file_name="Multi_Brand_Work_Orders_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
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
            display_cols = [c for c in ['Work_Order', 'Brand', 'Customer_Name', 'Customer_Phone', 'City', 'Address', 'Time_Slot', 'Appliance', 'Service_Type', 'Estimated_Revenue', 'Assigned_Tech'] if c in processed_orders.columns]
            st.dataframe(processed_orders[display_cols], use_container_width=True)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                processed_orders.to_excel(writer, index=False, sheet_name='Dispatched_Orders')
            excel_data = output.getvalue()
            
            st.download_button(
                label=txt["download_excel"],
                data=excel_data,
                file_name="Multi_Brand_Dispatched_Orders.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------------------------------------------------------
# TAB 2: INTERACTIVE ROUTE MAP
# -------------------------------------------------------------------
with nav_tab2:
    st.header(txt["map_header"])
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        
        m = folium.Map(location=MIRAGE_CENTER_COORDS, zoom_start=11, tiles="OpenStreetMap")
        
        folium.Marker(
            location=MIRAGE_CENTER_COORDS,
            popup="🏭 <b>Mirage Central Hub</b>",
            icon=folium.Icon(color="red", icon="building", prefix="fa")
        ).add_to(m)

        for _, tech in tech_df[tech_df['status'] == 'Active'].iterrows():
            eff_lat, eff_lng = get_effective_coords(tech)
            start_label = tech['start_type']
            
            folium.Marker(
                location=[eff_lat, eff_lng],
                popup=f"👨‍🔧 <b>{tech['name']}</b><br>Brands: {tech.get('brand', 'N/A')}<br>Specialties: {tech.get('appliance_specialty', 'N/A')}<br>Start: {start_label}<br>Radius: {tech['max_radius_km']} KM",
                icon=folium.Icon(color="green" if start_label=="Home / Outside" else "purple", icon="user", prefix="fa")
            ).add_to(m)
            
            folium.Circle(
                radius=tech['max_radius_km'] * 1000,
                location=[eff_lat, eff_lng],
                color="purple" if start_label=="Mirage Service Center" else "green",
                fill=True,
                fill_opacity=0.04
            ).add_to(m)
        
        for idx, row in orders.iterrows():
            city_raw = str(row.get('City', '')).upper().strip()
            coords = next((c for k, c in CITY_COORDS.items() if k in city_raw or city_raw in k), None)
            
            if not coords:
                coords = (30.0444 + np.random.uniform(-0.04, 0.04), 31.2357 + np.random.uniform(-0.04, 0.04))
                
            tech = row.get('Assigned_Tech', 'Unassigned')
            dist = row.get('Distance_Type', 'Near')
            time_slot = row.get('Time_Slot', 'N/A')
            color = "blue" if dist == "Near" else "orange"
            
            folium.Marker(
                location=coords,
                popup=f"Order: {row.get('Work_Order', 'N/A')}<br>Brand: {row.get('Brand', 'N/A')}<br>Slot: {time_slot}<br>Tech: {tech}<br>Area: {city_raw}",
                tooltip=f"{tech} | {row.get('Brand', '')} ({time_slot})",
                icon=folium.Icon(color=color, icon="wrench" if dist=="Far" else "motorcycle", prefix="fa")
            ).add_to(m)
            
        st_folium(m, width=1200, height=500)
    else:
        st.info(txt["map_info"])

# -------------------------------------------------------------------
# TAB 3: WHATSAPP MOBILE PORTAL
# -------------------------------------------------------------------
with nav_tab3:
    st.header(txt["wa_header"])
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        techs = orders['Assigned_Tech'].unique()
        
        for tech in techs:
            if tech == "Unassigned": continue
            tech_orders = orders[orders['Assigned_Tech'] == tech].copy()
            tech_match = tech_df[tech_df['name'] == tech]
            tech_info = tech_match.iloc[0] if not tech_match.empty else None
            phone = tech_info['phone'] if tech_info is not None else "201000000000"
            
            tech_orders['Google_Maps'] = tech_orders.apply(
                lambda r: generate_google_maps_url(r.get('Address', ''), r.get('City', '')), axis=1
            )
            
            wa_url = generate_whatsapp_link(phone, tech, tech_orders, lang=selected_lang)
            
            with st.expander(f"👨‍🔧 {tech} ({len(tech_orders)} {txt['wa_jobs']})"):
                st.markdown(f"**Brands Covered:** {tech_info.get('brand', 'N/A')} | **{txt['vehicle']}:** {tech_info['vehicle']} | **Specialty:** {tech_info.get('appliance_specialty', 'N/A')} | **{txt['phone']}:** {phone}")
                st.markdown(f"[📲 **{txt['wa_send']}**]({wa_url})", unsafe_allow_html=True)
                
                show_cols = [c for c in ['Work_Order', 'Brand', 'Customer_Name', 'Customer_Phone', 'Time_Slot', 'City', 'Address', 'Appliance', 'Service_Type', 'Notes'] if c in tech_orders.columns]
                st.dataframe(
                    tech_orders[show_cols],
                    column_config={
                        "Google_Maps": st.column_config.LinkColumn("🗺️ Google Maps Link", display_text="Open Map")
                    },
                    use_container_width=True
                )
    else:
        st.info(txt["no_data"])

# -------------------------------------------------------------------
# TAB 4: FINANCIAL & CAPACITY ANALYTICS
# -------------------------------------------------------------------
with nav_tab4:
    st.header(txt["analytics_header"])
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        tracker = st.session_state['tracker']
        fuel_cost_rate = st.session_state.get('fuel_cost_per_km', 4.5)
        
        total_orders = len(orders)
        assigned_orders = orders[orders['Assigned_Tech'] != 'Unassigned']
        assigned_count = len(assigned_orders)
        far_count = len(orders[orders['Distance_Type'] == 'Far'])
        
        total_revenue = orders['Estimated_Revenue'].sum() if 'Estimated_Revenue' in orders.columns else assigned_count * 350.0
        est_distance = (far_count * 35) + ((total_orders - far_count) * 12)
        total_fuel_cost = est_distance * fuel_cost_rate
        net_margin = total_revenue - total_fuel_cost
        
        total_capacity = sum([v['capacity'] for v in tracker.values()])
        utilization = (assigned_count / total_capacity * 100) if total_capacity > 0 else 0
        
        # Row 1 KPIs
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(txt["total_jobs"], total_orders)
        c2.metric(txt["allocated"], f"{(assigned_count/total_orders)*100:.1f}%")
        c3.metric(txt["est_dist"], f"{est_distance} KM")
        c4.metric(txt["util_rate"], f"{utilization:.1f}%")
        
        # Row 2 Financial Metrics
        st.markdown("---")
        f1, f2, f3 = st.columns(3)
        f1.metric(txt["total_rev"], f"{total_revenue:,.0f} EGP")
        f2.metric(txt["est_fuel_cost"], f"{total_fuel_cost:,.0f} EGP")
        f3.metric(txt["net_margin"], f"{net_margin:,.0f} EGP")
        
        st.markdown("---")
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown(f"### {txt['heatmap']}")
            capacity_df = pd.DataFrame([
                {
                    "Technician": k, 
                    "Covered Brands": v['raw_brand_str'],
                    "Specialties": v['raw_specialty_str'],
                    "Vehicle": v['vehicle'], 
                    "Assigned Jobs": v['assigned'], 
                    "Capacity": v['capacity'],
                    "Projected Rev (EGP)": f"{v['projected_revenue']:,.0f}"
                }
                for k, v in tracker.items()
            ])
            st.dataframe(capacity_df, use_container_width=True)

        with col_right:
            st.markdown("### 🏢 Orders by Brand")
            if 'Brand' in orders.columns:
                brand_counts = orders['Brand'].value_counts()
                st.bar_chart(brand_counts)
    else:
        st.info(txt["run_analytics_first"])

# -------------------------------------------------------------------
# TAB 5: TECHNICIAN MULTI-BRAND DATABASE SETUP
# -------------------------------------------------------------------
with nav_tab5:
    st.header(txt["db_header"])
    st.markdown(txt["db_sub"])
    
    st.subheader("📤 Bulk Import Multi-Brand Technicians Master List")
    
    col_up, col_tmpl = st.columns([3, 1])
    
    with col_up:
        tech_file = st.file_uploader("Upload Technician Master List (.xlsx or .csv)", type=["xlsx", "csv"], key="tech_uploader")
        
    with col_tmpl:
        st.write("Need a template?")
        sample_df = pd.DataFrame([{
            "Name": "أحمد عماد",
            "Phone": "201000000001",
            "Brand": "Brand A, Brand B",
            "Appliance Specialty": "AC, Refrigerator",
            "Skills": "Installation, Maintenance",
            "Vehicle": "Motorcycle",
            "Capacity": 8,
            "Start Location": "Mirage Service Center",
            "Home Zone": "Shorouk",
            "Max Radius (KM)": 25,
            "Experience": "Senior",
            "Status": "Active"
        }])
        tmpl_output = io.BytesIO()
        with pd.ExcelWriter(tmpl_output, engine='openpyxl') as writer:
            sample_df.to_excel(writer, index=False, sheet_name='Technicians_Template')
        st.download_button(
            label="📥 Download Excel Template",
            data=tmpl_output.getvalue(),
            file_name="Multi_Brand_Technicians_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    if tech_file:
        try:
            uploaded_tech_df = pd.read_csv(tech_file) if tech_file.name.endswith('.csv') else pd.read_excel(tech_file)
            
            rename_map = {
                'Name': 'name', 
                'Phone': 'phone', 
                'Brand': 'brand',
                'Appliance Specialty': 'appliance_specialty',
                'Appliance_Specialty': 'appliance_specialty',
                'Skills': 'skills', 
                'Vehicle': 'vehicle', 
                'Capacity': 'capacity',
                'Start Location': 'start_type', 
                'Home Zone': 'home_zone',
                'Max Radius (KM)': 'max_radius_km', 
                'Experience': 'experience', 
                'Status': 'status'
            }
            uploaded_tech_df.rename(columns=rename_map, inplace=True)
            uploaded_tech_df.drop(columns=['base_lat', 'base_lng'], errors='ignore', inplace=True)
            
            if st.button("🚀 Import and Overwrite Database", type="primary"):
                save_tech_df(uploaded_tech_df)
                st.success("✅ Multi-brand technician list imported successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Error reading technician file: {e}")

    st.markdown("---")
    st.subheader("📋 Current Active Technicians Database")
    st.info("💡 **Tip:** You can enter multiple brands separated by commas (e.g., `Brand A, Brand B, Brand C` or `All Brands`).")
    
    edited_df = st.data_editor(
        tech_df,
        num_rows="dynamic",
        column_config={
            "brand": st.column_config.TextColumn("Covered Brand(s)", help="Comma-separated list (e.g., Brand A, Brand B or All Brands)"),
            "appliance_specialty": st.column_config.TextColumn("Appliance Specialty", help="Comma-separated list (e.g., AC, Refrigerator)"),
            "skills": st.column_config.TextColumn("Specific Skills", help="e.g., Installation, Repair, Maintenance"),
            "start_type": st.column_config.SelectboxColumn("Start Location", options=["Mirage Service Center", "Home / Outside"], required=True),
            "vehicle": st.column_config.SelectboxColumn("Vehicle", options=["Motorcycle", "Car"], required=True),
            "status": st.column_config.SelectboxColumn("Status", options=["Active", "On Leave", "Inactive"], required=True),
            "experience": st.column_config.SelectboxColumn("Experience Level", options=["Junior", "Mid", "Senior"], required=True),
            "capacity": st.column_config.NumberColumn("Daily Capacity", min_value=1, max_value=30, default=8),
            "max_radius_km": st.column_config.NumberColumn("Max Radius (KM)", min_value=5, max_value=150, default=25),
        },
        use_container_width=True
    )
    
    if st.button(txt["save_db"]):
        save_tech_df(edited_df)
        st.success(txt["db_updated"])
        st.rerun()
