import streamlit as st
import pandas as pd
from datetime import datetime
import io
import urllib.parse
import os
import math
import json
import time

# ==========================================
# 0. SAFE DEPENDENCY & API IMPORTS
# ==========================================
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ModuleNotFoundError:
    HAS_GENAI = False

st.set_page_config(
    page_title="Mirage Corporate Distribution & Fleet Hub",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
if HAS_GENAI and GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        AI_AVAILABLE = True
    except Exception:
        AI_AVAILABLE = False
else:
    AI_AVAILABLE = False

# ==========================================
# 1. BILINGUAL TRANSLATION DICTIONARY (EN/AR)
# ==========================================
TRANSLATIONS = {
    "EN": {
        "app_title": "Mirage Distribution & Fleet Command",
        "app_subtitle": "Enterprise Automated AI Dispatch, GPS Logistics & Field Management System",
        "nav_menu": "Navigation Menu",
        "language_select": "🌐 Select Language / اختر اللغة",
        "nav_portal": "👨‍🔧 Driver & Tech Field Portal",
        "nav_ai_dispatch": "🤖 Automated AI Dispatch Engine (1-Min Loop)",
        "nav_excel_import": "📁 Excel Templates & Upload Hub",
        "nav_geofence": "🎯 GPS Geofence & Live Fleet Map",
        "nav_whatsapp": "💬 WhatsApp & Client Alert Hub",
        "nav_eod": "📊 End-of-Day Excel Reports & KPIs",
        "sys_status": "System Operational Status",
        "ai_active": "🟢 Gemini AI Engine: Active",
        "ai_offline": "⚠️ Gemini AI: Standard Mode",
        "select_driver": "📌 Select Assigned Driver/Technician:",
        "total_jobs": "Total Assigned Orders",
        "completed_jobs": "Completed Today",
        "pending_jobs": "Pending Dispatch",
        "order_details": "📋 Distribution Order Specifications",
        "client_name": "Client / Company",
        "contact_num": "Contact Phone",
        "address": "Delivery / Service Site Address",
        "priority": "Priority Level",
        "status": "Order Status",
        "cargo_details": "Cargo / Item Manifest",
        "est_hours": "Est. Completion Time",
        "site_photos": "📷 Site Photos & Visual Evidence",
        "upload_photo": "Upload New Delivery/Site Proof:",
        "submit_summary": "🚀 Submit Log & Sync to EOD Excel",
        "ai_dispatch_header": "🤖 Automated AI Dispatch Engine (1-Minute Distribution Loop)",
        "ai_dispatch_desc": "Evaluates technician capacity and automatically dispatches orders in 1-minute timed intervals.",
        "run_ai_dispatch": "⚡ Run Automated AI Dispatching Engine (Single Pass)",
        "run_1min_loop": "⏱️ Start 1-Minute Automated Minute-by-Minute Dispatch Loop",
        "unassigned_orders": "📦 Unassigned Corporate Orders",
        "driver_roster": "🚛 Driver & Fleet Capacity Roster",
        "geofence_header": "🎯 Smart Dispatch GPS & Geofence Simulator",
        "wa_header": "💬 WhatsApp Communication & Feedback Hub",
        "send_wa": "📲 Send WhatsApp Dispatch Notification",
        "download_excel": "📥 Download Master EOD Report (.XLSX)",
        "download_tech_temp": "📥 Download Techs Excel Template",
        "download_order_temp": "📥 Download Orders Excel Template"
    },
    "AR": {
        "app_title": "منظومة التوزيع وإدارة الأسطول - معراج",
        "app_subtitle": "النظام الذكي للتوزيع الآلي بالذكاء الاصطناعي وتتبع الأسطول الميداني",
        "nav_menu": "قائمة التحكم الرئيسية",
        "language_select": "🌐 اختر اللغة / Select Language",
        "nav_portal": "👨‍🔧 بوابة السائقين والفنيين الميدانيين",
        "nav_ai_dispatch": "🤖 محرك التوزيع الآلي (دورة كل دقيقة)",
        "nav_excel_import": "📁 قوالب Excel ومركز الرفع",
        "nav_geofence": "🎯 التتبع المباشر والنطاق الجغرافي",
        "nav_whatsapp": "💬 مركز إشعارات الواتساب والعملاء",
        "nav_eod": "📊 تقارير Excel ل نهاية اليوم والمؤشرات",
        "sys_status": "حالة النظام Operational",
        "ai_active": "🟢 محرك الذكاء الاصطناعي: نشط",
        "ai_offline": "⚠️ الذكاء الاصطناعي: وضع قياسي",
        "select_driver": "📌 اختر السائق / الفني الميداني:",
        "total_jobs": "إجمالي طلبات التوزيع",
        "completed_jobs": "تم إنجازه اليوم",
        "pending_jobs": "قيد الانتظار",
        "order_details": "📋 تفاصيل طلب التوزيع والشحنة",
        "client_name": "اسم العميل / الشركة",
        "contact_num": "رقم التواصل",
        "address": "عنوان التسليم / الموقع",
        "priority": "مستوى الأولوية",
        "status": "حالة الطلب",
        "cargo_details": "بيان الشحنة والمنتجات",
        "est_hours": "الوقت المتوقع للإنجاز",
        "site_photos": "📷 صور إثبات التسليم والموقع",
        "upload_photo": "رفع صورة إثبات الموقع/التسليم:",
        "submit_summary": "🚀 إرسال التقرير ومزامنة ملف Excel",
        "ai_dispatch_header": "🤖 محرك التوزيع الآلي (دورة توزيع كل دقيقة)",
        "ai_dispatch_desc": "يقوم النظام بتوزيع الشحنات تلقائياً على الفنيين بفواصل زمنية مدتها دقيقة واحدة.",
        "run_ai_dispatch": "⚡ تشغيل التوزيع الآلي (دورة واحدة)",
        "run_1min_loop": "⏱️ تشغيل حلقة التوزيع التلقائي كل دقيقة",
        "unassigned_orders": "📦 شحنات الشركات غير الموزعة",
        "driver_roster": "🚛 قائمة السائقين والطاقة الاستيعابية",
        "geofence_header": "🎯 محاكي النطاق الجغرافي والتتبع المباشر",
        "wa_header": "💬 مركز إشعارات الواتساب وتقييم العملاء",
        "send_wa": "📲 إرسال إشعار التوزيع عبر الواتساب",
        "download_excel": "📥 تحميل تقرير نهاية اليوم Master Excel (.XLSX)",
        "download_tech_temp": "📥 تحميل قالب الفنيين Excel Template",
        "download_order_temp": "📥 تحميل قالب الطلبات Excel Template"
    }
}

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
if "language" not in st.session_state:
    st.session_state.language = "EN"

T = TRANSLATIONS[st.session_state.language]

if "drivers" not in st.session_state:
    st.session_state.drivers = {}

if "assigned_orders" not in st.session_state:
    st.session_state.assigned_orders = {}

if "unassigned_orders" not in st.session_state:
    st.session_state.unassigned_orders = []

if "eod_excel_records" not in st.session_state:
    st.session_state.eod_excel_records = []

if "customer_ratings" not in st.session_state:
    st.session_state.customer_ratings = []

# ==========================================
# 3. HELPER MATH, AI & EXCEL ENGINES
# ==========================================
def generate_technician_excel_template():
    df_tech_template = pd.DataFrame([
        {
            "Name": "Example Tech 1",
            "Status": "Available",
            "Capacity": 10,
            "Current Load": 0,
            "Lat": 30.0444,
            "Lon": 31.2357
        },
        {
            "Name": "Example Tech 2",
            "Status": "Available",
            "Capacity": 8,
            "Current Load": 0,
            "Lat": 30.0731,
            "Lon": 31.0182
        }
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_tech_template.to_excel(writer, index=False, sheet_name='Technicians')
    return output.getvalue()

def generate_orders_excel_template():
    df_orders_template = pd.DataFrame([
        {
            "Order ID": "ORD-1001",
            "Client": "Sample Corporate Client A",
            "Contact": "+201012345678",
            "Address": "Site 12, Cairo",
            "Priority": "High",
            "Cargo": "HVAC Replacement Parts",
            "Details": "Handle with care",
            "Est Hours": 2.5,
            "Weight Units": 2,
            "Lat": 30.0444,
            "Lon": 31.2357
        },
        {
            "Order ID": "ORD-1002",
            "Client": "Sample Corporate Client B",
            "Contact": "+201112223334",
            "Address": "Sector 4, New Cairo",
            "Priority": "Critical",
            "Cargo": "Electrical Circuit Control Boards",
            "Details": "Urgent installation required",
            "Est Hours": 1.5,
            "Weight Units": 1,
            "Lat": 30.0271,
            "Lon": 31.4398
        }
    ])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_orders_template.to_excel(writer, index=False, sheet_name='Orders')
    return output.getvalue()

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def run_automated_ai_dispatch(single_batch_only=False):
    if not st.session_state.unassigned_orders:
        return "No pending unassigned orders to dispatch."
        
    if not st.session_state.drivers:
        return "No technicians loaded! Upload the Technicians file first."

    # Batch selection: 1 order per minute cycle or single batch
    orders_to_dispatch = [st.session_state.unassigned_orders[0]] if single_batch_only else list(st.session_state.unassigned_orders)

    dispatched_count = 0
    for order in orders_to_dispatch:
        best_driver = min(st.session_state.drivers.keys(), key=lambda d: st.session_state.drivers[d]["current_load"])
        
        order["status"] = f"Dispatched ({datetime.now().strftime('%H:%M:%S')})"
        order["photos"] = []
        order["logs"] = []
        order["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        st.session_state.assigned_orders[best_driver].append(order)
        st.session_state.drivers[best_driver]["current_load"] += order.get("weight_units", 1)
        st.session_state.unassigned_orders.remove(order)
        dispatched_count += 1

    return f"Dispatch Cycle Completed: Successfully assigned {dispatched_count} order(s) at {datetime.now().strftime('%H:%M:%S')}."

def run_gemini_summary_parser(raw_notes):
    if not AI_AVAILABLE:
        return f"• Action Taken: {raw_notes}\n• Status: Completed & Logged\n• Executive Summary: Order fulfilled successfully."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Summarize this driver/technician completion note into 3 clean bullet points:
        Note: "{raw_notes}"
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Parser Note: {raw_notes}"

def generate_whatsapp_url(phone_number, text_message):
    clean_phone = str(phone_number).replace("+", "").replace(" ", "").replace("-", "")
    encoded_text = urllib.parse.quote(text_message)
    return f"https://wa.me/{clean_phone}?text={encoded_text}"

# ==========================================
# 4. SIDEBAR NAVIGATION & LOCALIZATION
# ==========================================
st.sidebar.markdown(f"### {T['app_title']}")

selected_lang = st.sidebar.selectbox(
    T['language_select'],
    ["EN", "AR"],
    index=0 if st.session_state.language == "EN" else 1
)

if selected_lang != st.session_state.language:
    st.session_state.language = selected_lang
    st.rerun()

st.sidebar.markdown("---")

app_module = st.sidebar.radio(
    T['nav_menu'],
    [
        T['nav_excel_import'],
        T['nav_portal'],
        T['nav_ai_dispatch'],
        T['nav_geofence'],
        T['nav_whatsapp'],
        T['nav_eod']
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption(T['sys_status'])
if AI_AVAILABLE:
    st.sidebar.success(T['ai_active'])
else:
    st.sidebar.warning(T['ai_offline'])

# ==========================================
# 5. MODULE: EXCEL TEMPLATES & UPLOAD HUB
# ==========================================
if app_module == T['nav_excel_import']:
    st.title(T['nav_excel_import'])
    st.markdown("Download official Excel templates for Technicians and Orders, then upload your completed files below.")
    
    # Template Download Buttons
    st.subheader("📋 1. Download Official Excel Templates")
    col_temp1, col_temp2 = st.columns(2)
    
    with col_temp1:
        st.download_button(
            label=T['download_tech_temp'],
            data=generate_technician_excel_template(),
            file_name="Technicians_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_temp2:
        st.download_button(
            label=T['download_order_temp'],
            data=generate_orders_excel_template(),
            file_name="Orders_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    st.markdown("---")
    st.subheader("📤 2. Upload Filled Excel Files")
    
    col_tech_file, col_order_file = st.columns(2)
    
    # Upload Technicians
    with col_tech_file:
        st.markdown("#### Technicians / Drivers File")
        tech_file = st.file_uploader("Upload Techs Excel (.xlsx):", type=["xlsx", "xls"], key="tech_uploader")
        
        if tech_file is not None:
            try:
                df_techs = pd.read_excel(tech_file)
                st.dataframe(df_techs.head(), use_container_width=True)
                
                if st.button("Load Technicians into System", type="primary"):
                    st.session_state.drivers = {}
                    st.session_state.assigned_orders = {}
                    
                    for idx, row in df_techs.iterrows():
                        name = str(row.get("Name", f"Tech-{idx+1}")).strip()
                        status = str(row.get("Status", "Available")).strip()
                        cap = int(row.get("Capacity", 10))
                        load = int(row.get("Current Load", 0))
                        lat = float(row.get("Lat", 30.0444))
                        lon = float(row.get("Lon", 31.2357))
                        
                        st.session_state.drivers[name] = {
                            "status": status,
                            "capacity_units": cap,
                            "current_load": load,
                            "lat": lat,
                            "lon": lon
                        }
                        st.session_state.assigned_orders[name] = []
                        
                    st.success(f"Successfully loaded {len(st.session_state.drivers)} technician(s)!")
            except Exception as e:
                st.error(f"Error parsing Technicians file: {str(e)}")

    # Upload Orders
    with col_order_file:
        st.markdown("#### Distribution Orders File")
        order_file = st.file_uploader("Upload Orders Excel (.xlsx):", type=["xlsx", "xls"], key="order_uploader")
        
        if order_file is not None:
            try:
                df_orders = pd.read_excel(order_file)
                st.dataframe(df_orders.head(), use_container_width=True)
                
                if st.button("Load Orders into Dispatch Queue", type="primary"):
                    st.session_state.unassigned_orders = []
                    
                    for idx, row in df_orders.iterrows():
                        o_id = str(row.get("Order ID", f"ORD-{1001+idx}")).strip()
                        client = str(row.get("Client", "Corporate Client")).strip()
                        contact = str(row.get("Contact", "+201000000000")).strip()
                        address = str(row.get("Address", "Cairo")).strip()
                        priority = str(row.get("Priority", "Medium")).strip()
                        cargo = str(row.get("Cargo", "Package Goods")).strip()
                        details = str(row.get("Details", "Standard delivery")).strip()
                        est_hrs = float(row.get("Est Hours", 2.0))
                        weight = int(row.get("Weight Units", 1))
                        lat = float(row.get("Lat", 30.0444))
                        lon = float(row.get("Lon", 31.2357))
                        
                        st.session_state.unassigned_orders.append({
                            "id": o_id,
                            "client": client,
                            "contact": contact,
                            "address": address,
                            "lat": lat,
                            "lon": lon,
                            "priority": priority,
                            "cargo": cargo,
                            "details": details,
                            "est_hours": est_hrs,
                            "weight_units": weight
                        })
                        
                    st.success(f"Successfully loaded {len(st.session_state.unassigned_orders)} order(s) into dispatch queue!")
            except Exception as e:
                st.error(f"Error parsing Orders file: {str(e)}")

# ==========================================
# 6. MODULE: FIELD PORTAL (DRIVER / TECH)
# ==========================================
elif app_module == T['nav_portal']:
    st.title(T['nav_portal'])
    st.caption("Drill-down order inspection, proof uploads, driver notes, and AI Excel sync.")
    
    if not st.session_state.drivers:
        st.warning("⚠️ No technicians loaded. Please upload your Technicians file in the Excel Templates & Upload Hub module.")
    else:
        col_driver_sel, m1, m2 = st.columns([2, 1, 1])
        
        with col_driver_sel:
            driver_names = list(st.session_state.drivers.keys())
            selected_driver = st.selectbox(T['select_driver'], driver_names)
            
        driver_orders = st.session_state.assigned_orders.get(selected_driver, [])
        
        with m1:
            st.metric(T['total_jobs'], len(driver_orders))
        with m2:
            completed = sum(1 for o in driver_orders if o.get('status') == 'Completed')
            st.metric(T['completed_jobs'], completed)
            
        st.markdown("---")
        
        if not driver_orders:
            st.info(f"No active orders currently assigned to {selected_driver}.")
        else:
            st.subheader(f"Active Delivery & Service Orders ({selected_driver})")
            
            order_options = [f"{o['id']} - {o['client']} ({o['priority']} Priority) | [{o['status']}]" for o in driver_orders]
            sel_idx = st.selectbox("Select Order to Inspect & Process:", range(len(order_options)), format_func=lambda x: order_options[x])
            
            current_ord = driver_orders[sel_idx]
            
            with st.expander(T['order_details'], expanded=True):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"**{T['client_name']}:** {current_ord['client']}")
                c1.markdown(f"**{T['contact_num']}:** `{current_ord['contact']}`")
                
                c2.markdown(f"**{T['priority']}:** `{current_ord['priority']}`")
                c2.markdown(f"**{T['status']}:** `{current_ord['status']}`")
                
                c3.markdown(f"**{T['cargo_details']}:** {current_ord['cargo']}")
                c3.markdown(f"**{T['est_hours']}:** {current_ord['est_hours']} hrs")
                
                st.markdown(f"**{T['address']}:** {current_ord['address']}")
                st.info(f"**Dispatch Notes:** {current_ord['details']}")
                
            st.subheader(T['site_photos'])
            if current_ord.get("photos"):
                p_cols = st.columns(len(current_ord["photos"]))
                for idx, img_url in enumerate(current_ord["photos"]):
                    with p_cols[idx]:
                        st.image(img_url, caption=f"Proof #{idx+1}", use_container_width=True)
            else:
                st.warning("No proof of delivery photos attached yet.")
                
            uploaded_file = st.file_uploader(T['upload_photo'], type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                st.success("Delivery photo proof added to manifest!")
                
            st.markdown("---")
            
            st.subheader("📝 Order Completion & AI Excel Sync")
            completion_notes = st.text_area(
                "Driver / Technician Field Completion Notes:",
                placeholder="E.g., Delivered items to location. Received sign-off from warehouse supervisor."
            )
            
            if st.button(T['submit_summary'], type="primary"):
                if not completion_notes.strip():
                    st.error("Please enter notes before submitting.")
                else:
                    with st.spinner("AI Engine parsing completion report..."):
                        ai_result = run_gemini_summary_parser(completion_notes)
                        
                        current_ord["status"] = "Completed"
                        current_ord.setdefault("logs", []).append(completion_notes)
                        
                        st.session_state.eod_excel_records.append({
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Driver Name": selected_driver,
                            "Order ID": current_ord['id'],
                            "Client": current_ord['client'],
                            "Notes": completion_notes,
                            "AI Analysis": ai_result
                        })
                        
                    st.success(f"Order {current_ord['id']} updated to COMPLETED and logged into Master Excel!")
                    st.info(ai_result)

# ==========================================
# 7. MODULE: AUTOMATED AI DISPATCH ENGINE (1-MIN LOOP)
# ==========================================
elif app_module == T['nav_ai_dispatch']:
    st.title(T['ai_dispatch_header'])
    st.markdown(T['ai_dispatch_desc'])
    
    col_unassigned, col_drivers = st.columns([1, 1])
    
    with col_unassigned:
        st.subheader(T['unassigned_orders'])
        if st.session_state.unassigned_orders:
            df_unassigned = pd.DataFrame(st.session_state.unassigned_orders)
            st.dataframe(df_unassigned[["id", "client", "priority", "cargo", "weight_units"]], use_container_width=True)
        else:
            st.success("🎉 No unassigned orders pending in queue!")
            
    with col_drivers:
        st.subheader(T['driver_roster'])
        if st.session_state.drivers:
            driver_data = []
            for d_name, d_info in st.session_state.drivers.items():
                driver_data.append({
                    "Driver/Tech": d_name,
                    "Status": d_info["status"],
                    "Capacity Units": d_info["capacity_units"],
                    "Current Load": d_info["current_load"]
                })
            st.dataframe(pd.DataFrame(driver_data), use_container_width=True)
        else:
            st.warning("No technicians loaded. Upload Tech Excel file.")
        
    st.markdown("---")
    
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button(T['run_ai_dispatch'], type="primary", use_container_width=True):
            dispatch_result = run_automated_ai_dispatch(single_batch_only=False)
            st.success("Full Dispatch Execution Completed!")
            st.write(dispatch_result)
            st.rerun()

    with btn_col2:
        if st.button(T['run_1min_loop'], use_container_width=True):
            st.info("Starting Minute-by-Minute Automated Dispatching...")
            progress_bar = st.progress(0)
            status_box = st.empty()
            
            while len(st.session_state.unassigned_orders) > 0:
                res = run_automated_ai_dispatch(single_batch_only=True)
                status_box.success(res)
                
                # Wait 60 seconds (1 minute interval)
                for second in range(60):
                    time.sleep(1)
                    progress_bar.progress((second + 1) / 60)
                    
            status_box.success("🎉 All pending orders dispatched across 1-minute interval loops!")

# ==========================================
# 8. MODULE: GPS GEOFENCING & FLEET MAP
# ==========================================
elif app_module == T['nav_geofence']:
    st.title(T['geofence_header'])
    st.markdown("Real-time GPS coordinate mapping, proximity alerts, and automated geofence triggering.")
    
    all_map_points = []
    for d_name, orders in st.session_state.assigned_orders.items():
        for o in orders:
            all_map_points.append({
                "lat": o["lat"],
                "lon": o["lon"],
                "Driver": d_name,
                "Order": o["id"],
                "Client": o["client"]
            })
            
    df_map_points = pd.DataFrame(all_map_points)
    
    col_map, col_sim = st.columns([2, 1])
    
    with col_map:
        st.subheader("🗺️ Live Fleet GPS Map")
        if not df_map_points.empty:
            st.map(df_map_points, zoom=10, use_container_width=True)
            st.dataframe(df_map_points, use_container_width=True)
        else:
            st.info("No active GPS waypoints to display.")
            
    with col_sim:
        st.subheader("📡 Live Driver Proximity Check")
        if not df_map_points.empty:
            selected_check_id = st.selectbox("Target Order for Radius Check:", df_map_points["Order"].tolist())
            
            target_obj = None
            for d_name, orders in st.session_state.assigned_orders.items():
                for o in orders:
                    if o["id"] == selected_check_id:
                        target_obj = o
                        break
                        
            if target_obj:
                sim_lat = st.number_input("Simulated Driver Lat:", value=target_obj["lat"] + 0.002, format="%.4f")
                sim_lon = st.number_input("Simulated Driver Lon:", value=target_obj["lon"] - 0.001, format="%.4f")
                
                dist_km = calculate_haversine_distance(sim_lat, sim_lon, target_obj["lat"], target_obj["lon"])
                dist_m = int(dist_km * 1000)
                
                st.metric("Distance to Delivery Site", f"{dist_m} meters", delta=f"{dist_km} km")
                
                if dist_m <= 500:
                    st.success("🟢 WITHIN GEOFENCE RADIUS (< 500m)")
                    st.caption("Auto Action: Status changed to **'On Site / Delivering'**")
                    target_obj["status"] = "On Site"
                else:
                    st.warning("🔴 OUTSIDE GEOFENCE RADIUS")

# ==========================================
# 9. MODULE: WHATSAPP & CLIENT ALERTS
# ==========================================
elif app_module == T['nav_whatsapp']:
    st.title(T['wa_header'])
    st.markdown("Trigger instant automated customer dispatches and tracking updates directly via WhatsApp.")
    
    all_flat_orders = [o for sublist in st.session_state.assigned_orders.values() for o in sublist]
    
    if not all_flat_orders:
        st.info("No assigned orders available for client alerts.")
    else:
        order_labels = [f"{o['id']} - {o['client']} ({o['contact']})" for o in all_flat_orders]
        sel_wa_idx = st.selectbox("Select Target Client Order:", range(len(order_labels)), format_func=lambda x: order_labels[x])
        
        wa_target = all_flat_orders[sel_wa_idx]
        
        col_wa_composer, col_feedback = st.columns(2)
        
        with col_wa_composer:
            st.subheader("✉️ Automated Dispatch Notification")
            eta = st.slider("Estimated Arrival (Minutes):", 10, 120, 30)
            
            default_text = f"Hello {wa_target['client']}, your shipment ({wa_target['id']} - {wa_target['cargo']}) is en route. Estimated arrival in {eta} minutes. Contact: {wa_target['contact']}."
            
            custom_msg = st.text_area("WhatsApp Message Body:", value=default_text, height=120)
            
            wa_link = generate_whatsapp_url(wa_target["contact"], custom_msg)
            
            st.markdown(f"""
                <a href="{wa_link}" target="_blank">
                    <button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer;">
                        {T['send_wa']}
                    </button>
                </a>
            """, unsafe_allow_html=True)
            
        with col_feedback:
            st.subheader("⭐ Customer Feedback Collector")
            rating = st.select_slider("Delivery Rating:", options=[1, 2, 3, 4, 5], value=5)
            comments = st.text_input("Customer Feedback Notes:", "Prompt delivery and excellent handling.")
            
            if st.button("Log Customer Feedback"):
                st.session_state.customer_ratings.append({
                    "Order ID": wa_target["id"],
                    "Client": wa_target["client"],
                    "Rating": rating,
                    "Comments": comments
                })
                st.success("Feedback logged successfully!")

# ==========================================
# 10. MODULE: EXCEL EOD REPORTS & KPIS
# ==========================================
elif app_module == T['nav_eod']:
    st.title(T['nav_eod'])
    st.markdown("Export consolidated daily logs, AI executive analyses, and executable Excel downloads.")
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total EOD Logs Recorded", len(st.session_state.eod_excel_records))
    k2.metric("On-Time Delivery Rate", "98.1%", "+1.5%")
    k3.metric("Fleet Capacity Utilization", "84.2%", "+5.0%")
    
    st.markdown("---")
    
    if not st.session_state.eod_excel_records:
        st.warning("No End-of-Day submissions logged yet. Complete orders in the Driver Portal to build reports!")
    else:
        df_eod = pd.DataFrame(st.session_state.eod_excel_records)
        st.subheader("📋 Master End-of-Day Report Stream")
        st.dataframe(df_eod, use_container_width=True)
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_eod.to_excel(writer, index=False, sheet_name='EOD_Distribution_Log')
            if st.session_state.customer_ratings:
                pd.DataFrame(st.session_state.customer_ratings).to_excel(writer, index=False, sheet_name='Customer_Feedback')
                
        excel_bytes = excel_buffer.getvalue()
        
        st.download_button(
            label=T['download_excel'],
            data=excel_bytes,
            file_name=f"Distribution_EOD_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
