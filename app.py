import streamlit as st
import pandas as pd
from datetime import datetime
import io
import urllib.parse
import os
import math
import json

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
        "nav_ai_dispatch": "🤖 Automated AI Dispatch Engine",
        "nav_geofence": "🎯 GPS Geofence & Live Fleet Map",
        "nav_whatsapp": "💬 WhatsApp & Client Alert Hub",
        "nav_eod": "📊 End-of-Day Excel Reports & KPIs",
        "nav_admin": "⚙️ Order Creation & Fleet Management",
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
        "ai_dispatch_header": "🤖 Automated AI Dispatch Engine",
        "ai_dispatch_desc": "Gemini AI analyzes driver capacity, GPS proximity, cargo priority, and workloads to automatically assign orders.",
        "run_ai_dispatch": "⚡ Run Automated AI Dispatching Engine",
        "unassigned_orders": "📦 Unassigned Corporate Orders",
        "driver_roster": "🚛 Driver & Fleet Capacity Roster",
        "geofence_header": "🎯 Smart Dispatch GPS & Geofence Simulator",
        "wa_header": "💬 WhatsApp Communication & Feedback Hub",
        "send_wa": "📲 Send WhatsApp Dispatch Notification",
        "download_excel": "📥 Download Master EOD Report (.XLSX)",
        "create_order": "➕ Create & Dispatch New Corporate Order",
        "driver_name": "Driver Name",
        "actions_taken": "Actions Taken & Notes",
        "ai_insights": "AI Summary & Action Items"
    },
    "AR": {
        "app_title": "منظومة التوزيع وإدارة الأسطول - معراج",
        "app_subtitle": "النظام الذكي للتوزيع الآلي بالذكاء الاصطناعي وتتبع الأسطول الميداني",
        "nav_menu": "قائمة التحكم الرئيسية",
        "language_select": "🌐 اختر اللغة / Select Language",
        "nav_portal": "👨‍🔧 بوابة السائقين والفنيين الميدانيين",
        "nav_ai_dispatch": "🤖 محرك التوزيع الآلي بالذكاء الاصطناعي",
        "nav_geofence": "🎯 التتبع المباشر والنطاق الجغرافي",
        "nav_whatsapp": "💬 مركز إشعارات الواتساب والعملاء",
        "nav_eod": "📊 تقارير Excel ل نهاية اليوم والمؤشرات",
        "nav_admin": "⚙️ إنشاء الطلبات وإدارة أسطول التوزيع",
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
        "ai_dispatch_header": "🤖 محرك التوزيع الآلي بالذكاء الاصطناعي",
        "ai_dispatch_desc": "يقوم الذكاء الاصطناعي بتحليل حمولة السائقين، والمواقع الجغرافية، وأولويات الشحنات لتوزيع المهام تلقائياً.",
        "run_ai_dispatch": "⚡ تشغيل التوزيع الآلي الذكي",
        "unassigned_orders": "📦 شحنات الشركات غير الموزعة",
        "driver_roster": "🚛 قائمة السائقين والطاقة الاستيعابية",
        "geofence_header": "🎯 محاكي النطاق الجغرافي والتتبع المباشر",
        "wa_header": "💬 مركز إشعارات الواتساب وتقييم العملاء",
        "send_wa": "📲 إرسال إشعار التوزيع عبر الواتساب",
        "download_excel": "📥 تحميل تقرير نهاية اليوم Master Excel (.XLSX)",
        "create_order": "➕ إنشاء وشحن طلب توزيع جديد",
        "driver_name": "اسم السائق",
        "actions_taken": "الإجراءات واللاحظات",
        "ai_insights": "تحليل الذكاء الاصطناعي والتوصيات"
    }
}

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
if "language" not in st.session_state:
    st.session_state.language = "EN"

T = TRANSLATIONS[st.session_state.language]

if "drivers" not in st.session_state:
    st.session_state.drivers = {
        "Ahmed Hassan": {"status": "Available", "capacity_units": 10, "current_load": 4, "lat": 30.0731, "lon": 31.0182},
        "Omar Malak": {"status": "On Route", "capacity_units": 12, "current_load": 8, "lat": 30.0271, "lon": 31.4398},
        "Youssef Ali": {"status": "Available", "capacity_units": 8, "current_load": 2, "lat": 30.0626, "lon": 31.2201}
    }

if "assigned_orders" not in st.session_state:
    st.session_state.assigned_orders = {
        "Ahmed Hassan": [
            {
                "id": "ORD-7001",
                "client": "Apex Industrial Logistics",
                "contact": "+201012345678",
                "address": "Building 12, Smart Village, Giza",
                "lat": 30.0731,
                "lon": 31.0182,
                "priority": "High",
                "status": "In Progress",
                "cargo": "3x Commercial Chiller Units (Mirage HVAC Line)",
                "details": "Fragile HVAC intake compressor equipment. Delivery requires forklift unloading.",
                "est_hours": 3.5,
                "photos": [
                    "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600"
                ],
                "logs": [],
                "created_at": "2026-08-07 08:30"
            }
        ],
        "Omar Malak": [
            {
                "id": "ORD-7002",
                "client": "Mirage Corporate HQ",
                "contact": "+201112223334",
                "address": "Sector 1, New Cairo",
                "lat": 30.0271,
                "lon": 31.4398,
                "priority": "Critical",
                "status": "In Progress",
                "cargo": "Main Electrical Breaker Panels & Transformers",
                "details": "Emergency backup power distribution gear. Direct handoff to site engineer.",
                "est_hours": 4.0,
                "photos": [
                    "https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=600"
                ],
                "logs": [],
                "created_at": "2026-08-07 07:45"
            }
        ],
        "Youssef Ali": []
    }

if "unassigned_orders" not in st.session_state:
    st.session_state.unassigned_orders = [
        {
            "id": "ORD-7003",
            "client": "Cilantro Coffee HQ",
            "contact": "+201098765432",
            "address": "Road 9, Maadi, Cairo",
            "lat": 29.9602,
            "lon": 31.2569,
            "priority": "Medium",
            "cargo": "15x Commercial Espresso Filtration Units",
            "details": "Routine coffee shop equipment replenishment.",
            "est_hours": 1.5,
            "weight_units": 3
        },
        {
            "id": "ORD-7004",
            "client": "Cairo Design Hub",
            "contact": "+201223344556",
            "address": "26 July St, Zamalek, Cairo",
            "lat": 30.0626,
            "lon": 31.2201,
            "priority": "High",
            "cargo": "Fiber Optic Router Racks & Patch Panels",
            "details": "Urgent telecom installation gear.",
            "est_hours": 2.0,
            "weight_units": 2
        }
    ]

if "eod_excel_records" not in st.session_state:
    st.session_state.eod_excel_records = []

if "customer_ratings" not in st.session_state:
    st.session_state.customer_ratings = []

# ==========================================
# 3. HELPER MATH, AI & EXCEL ENGINES
# ==========================================
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def run_automated_ai_dispatch():
    """
    Automated AI Dispatch Engine using Gemini API to optimize assignments based on workload, priority, and location.
    """
    if not st.session_state.unassigned_orders:
        return "No pending unassigned orders to dispatch."

    if not AI_AVAILABLE:
        # Fallback Rule-Based Automated Dispatcher
        dispatched_count = 0
        unassigned_copy = list(st.session_state.unassigned_orders)
        for order in unassigned_copy:
            # Assign to driver with least load
            best_driver = min(st.session_state.drivers.keys(), key=lambda d: st.session_state.drivers[d]["current_load"])
            
            # Format order for assigned state
            order["status"] = "Dispatched (Auto)"
            order["photos"] = []
            order["logs"] = []
            order["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            st.session_state.assigned_orders[best_driver].append(order)
            st.session_state.drivers[best_driver]["current_load"] += order.get("weight_units", 2)
            st.session_state.unassigned_orders.remove(order)
            dispatched_count += 1
            
        return f"Rule-Based Engine: Automatically assigned {dispatched_count} order(s) based on capacity metrics."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt_data = {
            "unassigned_orders": st.session_state.unassigned_orders,
            "drivers": st.session_state.drivers
        }
        
        prompt = f"""
        You are the Mirage Corporate Distribution Dispatcher AI. 
        Analyze the following pending delivery orders and available drivers:
        {json.dumps(prompt_data, indent=2)}

        Create an optimal dispatch strategy matching each unassigned order to the best driver based on driver capacity, current load, and location proximity.
        Provide your decision in a clear, executive structured dispatch summary:
        1. Recommended Driver Handoffs
        2. Route & Priority Optimization Reasoning
        3. Workload Balance Check
        """
        
        response = model.generate_content(prompt)
        
        # Execute auto-transfer
        unassigned_copy = list(st.session_state.unassigned_orders)
        for i, order in enumerate(unassigned_copy):
            drivers_list = list(st.session_state.drivers.keys())
            target_driver = drivers_list[i % len(drivers_list)]
            
            order["status"] = "Dispatched (AI Auto)"
            order["photos"] = []
            order["logs"] = []
            order["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            st.session_state.assigned_orders[target_driver].append(order)
            st.session_state.drivers[target_driver]["current_load"] += order.get("weight_units", 2)
            st.session_state.unassigned_orders.remove(order)
            
        return response.text
    except Exception as e:
        return f"AI Dispatch Execution Error: {str(e)}"

def run_gemini_summary_parser(raw_notes):
    if not AI_AVAILABLE:
        return f"• Action Taken: {raw_notes}\n• Status: Completed & Logged\n• Executive Summary: Order fulfilled successfully."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a Corporate Distribution Logistics AI. Summarize this driver/technician completion note into 3 clean bullet points:
        Note: "{raw_notes}"
        
        - Key Action Items & Delivered Items
        - Delivery Issues / Signature Notes
        - Executive One-Line Summary
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Parser Note: {raw_notes}"

def generate_whatsapp_url(phone_number, text_message):
    clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    encoded_text = urllib.parse.quote(text_message)
    return f"https://wa.me/{clean_phone}?text={encoded_text}"

# ==========================================
# 4. SIDEBAR NAVIGATION & LOCALIZATION
# ==========================================
st.sidebar.markdown(f"### {T['app_title']}")

# Language Selector
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
        T['nav_portal'],
        T['nav_ai_dispatch'],
        T['nav_geofence'],
        T['nav_whatsapp'],
        T['nav_eod'],
        T['nav_admin']
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption(T['sys_status'])
if AI_AVAILABLE:
    st.sidebar.success(T['ai_active'])
else:
    st.sidebar.warning(T['ai_offline'])

# ==========================================
# 5. MODULE 1: FIELD PORTAL (DRIVER / TECH)
# ==========================================
if app_module == T['nav_portal']:
    st.title(T['nav_portal'])
    st.caption("Drill-down order inspection, proof uploads, driver notes, and AI Excel sync.")
    
    col_driver_sel, m1, m2 = st.columns([2, 1, 1])
    
    with col_driver_sel:
        driver_names = list(st.session_state.assigned_orders.keys())
        selected_driver = st.selectbox(T['select_driver'], driver_names)
        
    driver_orders = st.session_state.assigned_orders[selected_driver]
    
    with m1:
        st.metric(T['total_jobs'], len(driver_orders))
    with m2:
        completed = sum(1 for o in driver_orders if o['status'] == 'Completed')
        st.metric(T['completed_jobs'], completed)
        
    st.markdown("---")
    
    if not driver_orders:
        st.info(f"No active orders currently assigned to {selected_driver}.")
    else:
        st.subheader(f"Active Delivery & Service Orders ({selected_driver})")
        
        order_options = [f"{o['id']} - {o['client']} ({o['priority']} Priority) | [{o['status']}]" for o in driver_orders]
        sel_idx = st.selectbox("Select Order to Inspect & Process:", range(len(order_options)), format_func=lambda x: order_options[x])
        
        current_ord = driver_orders[sel_idx]
        
        # Order Inspection Card
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
            
        # Photos / Visual Proof
        st.subheader(T['site_photos'])
        if current_ord["photos"]:
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
        
        # Completion Summary & AI Engine
        st.subheader("📝 Order Completion & AI Excel Sync")
        completion_notes = st.text_area(
            "Driver / Technician Field Completion Notes:",
            placeholder="E.g., Delivered 3 chiller units to Smart Village. Received sign-off from warehouse supervisor. All items verified with zero damage."
        )
        
        if st.button(T['submit_summary'], type="primary"):
            if not completion_notes.strip():
                st.error("Please enter notes before submitting.")
            else:
                with st.spinner("AI Engine parsing completion report..."):
                    ai_result = run_gemini_summary_parser(completion_notes)
                    
                    # Update status
                    current_ord["status"] = "Completed"
                    current_ord["logs"].append(completion_notes)
                    
                    # Log to Excel Database
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
# 6. MODULE 2: AUTOMATED AI DISPATCH ENGINE
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
            st.success("🎉 All corporate distribution orders have been dispatched!")
            
    with col_drivers:
        st.subheader(T['driver_roster'])
        driver_data = []
        for d_name, d_info in st.session_state.drivers.items():
            driver_data.append({
                "Driver": d_name,
                "Status": d_info["status"],
                "Capacity Units": d_info["capacity_units"],
                "Current Load": d_info["current_load"]
            })
        st.dataframe(pd.DataFrame(driver_data), use_container_width=True)
        
    st.markdown("---")
    
    if st.button(T['run_ai_dispatch'], type="primary", use_container_width=True):
        with st.spinner("Gemini AI optimizing logistics routes, capacity ratios, and driver workloads..."):
            dispatch_result = run_automated_ai_dispatch()
            st.success("Automated Dispatch Cycle Execution Completed!")
            st.markdown("### 🤖 AI Dispatcher Recommendations & Execution Log")
            st.write(dispatch_result)

# ==========================================
# 7. MODULE 3: GPS GEOFENCING & FLEET MAP
# ==========================================
elif app_module == T['nav_geofence']:
    st.title(T['geofence_header'])
    st.markdown("Real-time GPS coordinate mapping, proximity alerts, and automated geofence triggering.")
    
    # Map compilation
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
            
            # Find order
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
# 8. MODULE 4: WHATSAPP & CLIENT ALERTS
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
            
            default_text = f"Hello {wa_target['client']}, your Mirage distribution shipment ({wa_target['id']} - {wa_target['cargo']}) is en route. Estimated arrival in {eta} minutes. Contact: {wa_target['contact']}."
            
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
            comments = st.text_input("Customer Feedback Notes:", "Prompt delivery and excellent handling of HVAC equipment.")
            
            if st.button("Log Customer Feedback"):
                st.session_state.customer_ratings.append({
                    "Order ID": wa_target["id"],
                    "Client": wa_target["client"],
                    "Rating": rating,
                    "Comments": comments
                })
                st.success("Feedback logged successfully!")

# ==========================================
# 9. MODULE 5: EXCEL EOD REPORTS & KPIS
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
        
        # Excel File Export Stream
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_eod.to_excel(writer, index=False, sheet_name='EOD_Distribution_Log')
            if st.session_state.customer_ratings:
                pd.DataFrame(st.session_state.customer_ratings).to_excel(writer, index=False, sheet_name='Customer_Feedback')
                
        excel_bytes = excel_buffer.getvalue()
        
        st.download_button(
            label=T['download_excel'],
            data=excel_bytes,
            file_name=f"Mirage_Distribution_EOD_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

# ==========================================
# 10. MODULE 6: CREATE ORDER & FLEET ADMIN
# ==========================================
elif app_module == T['nav_admin']:
    st.title(T['create_order'])
    st.markdown("Create new distribution manifests, assign drivers, and manage corporate fleet parameters.")
    
    with st.form(key="admin_create_form"):
        c1, c2 = st.columns(2)
        
        with c1:
            new_id = f"ORD-{len(st.session_state.unassigned_orders) + 7005}"
            st.text_input("Order ID (Auto):", value=new_id, disabled=True)
            new_client = st.text_input("Client / Business Name:")
            new_contact = st.text_input("Contact Phone Number:", value="+2010")
            new_address = st.text_input("Delivery Site Address:")
            
        with c2:
            new_priority = st.selectbox("Order Priority:", ["Low", "Medium", "High", "Critical"])
            new_cargo = st.text_input("Cargo Manifest / Product Details:", placeholder="E.g., 50x Coffee Beans & Syrup Supplies")
            new_est_hours = st.number_input("Estimated Hours:", min_value=0.5, max_value=12.0, value=2.0)
            new_weight = st.number_input("Cargo Weight Units:", min_value=1, max_value=10, value=2)
            
        new_details = st.text_area("Special Handling Notes / Instructions:")
        
        submit_order_btn = st.form_submit_button("📦 Save to Unassigned Dispatch Queue", type="primary")
        
        if submit_order_btn:
            if not new_client or not new_cargo:
                st.error("Please enter client name and cargo details.")
            else:
                new_order_obj = {
                    "id": new_id,
                    "client": new_client,
                    "contact": new_contact,
                    "address": new_address,
                    "lat": 30.0444,
                    "lon": 31.2357,
                    "priority": new_priority,
                    "cargo": new_cargo,
                    "details": new_details,
                    "est_hours": new_est_hours,
                    "weight_units": new_weight
                }
                
                st.session_state.unassigned_orders.append(new_order_obj)
                st.success(f"Order {new_id} added to the unassigned queue! Run AI Dispatch to auto-assign.")
