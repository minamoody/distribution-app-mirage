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
# 0. AI DEPENDENCY IMPORT & KEY SETUP
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

# ==========================================
# 1. BILINGUAL TRANSLATION DICTIONARY
# ==========================================
TRANSLATIONS = {
    "EN": {
        "app_title": "Mirage Distribution & Fleet Command",
        "app_subtitle": "Enterprise Automated AI Dispatch, GPS Logistics & Field Management System",
        "nav_menu": "Navigation Menu",
        "language_select": "🌐 Select Language / اختر اللغة",
        "nav_portal": "👨‍🔧 Driver & Tech Field Portal",
        "nav_ai_dispatch": "🤖 Automated AI Dispatch Engine (1-Min Loop)",
        "nav_excel_import": "📁 Excel Upload Hub (Techs & Orders)",
        "nav_geofence": "🎯 GPS Geofence & Live Fleet Map",
        "nav_whatsapp": "💬 WhatsApp & Client Alert Hub",
        "nav_eod": "📊 End-of-Day Excel Reports & KPIs",
        "sys_status": "System Operational Status",
        "ai_active": "🟢 Gemini AI Engine: Active",
        "ai_offline": "⚠️ Gemini AI: Enter API Key below",
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
        "submit_summary": "🚀 Submit Log & Sync to EOD Excel",
        "ai_dispatch_header": "🤖 Automated AI Dispatch Engine (1-Minute Distribution Loop)",
        "ai_dispatch_desc": "Evaluates technician capacity from your uploaded Excel and automatically dispatches orders in 1-minute timed intervals.",
        "run_ai_dispatch": "⚡ Run Automated AI Dispatching Engine (Single Pass)",
        "run_1min_loop": "⏱️ Start 1-Minute Automated Dispatch Loop",
        "unassigned_orders": "📦 Unassigned Corporate Orders",
        "driver_roster": "🚛 Driver & Fleet Capacity Roster",
        "geofence_header": "🎯 Smart Dispatch GPS & Geofence Simulator",
        "wa_header": "💬 WhatsApp Communication & Feedback Hub",
        "send_wa": "📲 Send WhatsApp Dispatch Notification",
        "download_excel": "📥 Download Master EOD Report (.XLSX)",
        "clear_session": "🧹 Clear All Session Data & Memory"
    },
    "AR": {
        "app_title": "منظومة التوزيع وإدارة الأسطول - معراج",
        "app_subtitle": "النظام الذكي للتوزيع الآلي بالذكاء الاصطناعي وتتبع الأسطول الميداني",
        "nav_menu": "قائمة التحكم الرئيسية",
        "language_select": "🌐 اختر اللغة / Select Language",
        "nav_portal": "👨‍🔧 بوابة السائقين والفنيين الميدانيين",
        "nav_ai_dispatch": "🤖 محرك التوزيع الآلي (دورة كل دقيقة)",
        "nav_excel_import": "📁 مركز رفع ملفات Excel (الفنيين والطلبات)",
        "nav_geofence": "🎯 التتبع المباشر والنطاق الجغرافي",
        "nav_whatsapp": "💬 مركز إشعارات الواتساب والعملاء",
        "nav_eod": "📊 تقارير Excel ل نهاية اليوم والمؤشرات",
        "sys_status": "حالة النظام Operational",
        "ai_active": "🟢 محرك الذكاء الاصطناعي: نشط",
        "ai_offline": "⚠️ الذكاء الاصطناعي: أدخل مفتاح API أدناه",
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
        "submit_summary": "🚀 إرسال التقرير ومزامنة ملف Excel",
        "ai_dispatch_header": "🤖 محرك التوزيع الآلي (دورة توزيع كل دقيقة)",
        "ai_dispatch_desc": "يقوم النظام بتوزيع الشحنات المرفوعة تلقائياً على الفنيين بفواصل زمنية مدتها دقيقة واحدة.",
        "run_ai_dispatch": "⚡ تشغيل التوزيع الآلي (دورة واحدة)",
        "run_1min_loop": "⏱️ تشغيل حلقة التوزيع التلقائي كل دقيقة",
        "unassigned_orders": "📦 شحنات الشركات غير الموزعة",
        "driver_roster": "🚛 قائمة السائقين والطاقة الاستيعابية",
        "geofence_header": "🎯 محاكي النطاق الجغرافي والتتبع المباشر",
        "wa_header": "💬 مركز إشعارات الواتساب وتقييم العملاء",
        "send_wa": "📲 إرسال إشعار التوزيع عبر الواتساب",
        "download_excel": "📥 تحميل تقرير نهاية اليوم Master Excel (.XLSX)",
        "clear_session": "🧹 مسح كل البيانات المخزنة والذاكرة"
    }
}

# ==========================================
# 2. SESSION STATE INITIALIZATION
# ==========================================
st.session_state.setdefault("language", "EN")
st.session_state.setdefault("drivers", {})
st.session_state.setdefault("assigned_orders", {})
st.session_state.setdefault("unassigned_orders", [])
st.session_state.setdefault("eod_excel_records", [])
st.session_state.setdefault("customer_ratings", [])
st.session_state.setdefault("show_ai_panel", False)
st.session_state.setdefault("user_api_key", "")
st.session_state.setdefault("side_chat_history", [
    {"role": "assistant", "content": "👋 Hi! I'm Gemini. Ask me anything about your current fleet data, operations, coding, or analytics!"}
])

T = TRANSLATIONS[st.session_state.language]

def initialize_empty_state():
    st.session_state.drivers = {}
    st.session_state.assigned_orders = {}
    st.session_state.unassigned_orders = []
    st.session_state.eod_excel_records = []
    st.session_state.customer_ratings = []
    st.session_state.show_ai_panel = False
    st.session_state.side_chat_history = [
        {"role": "assistant", "content": "👋 Hi! I'm Gemini. Ask me anything about your current fleet data, operations, coding, or analytics!"}
    ]

# ==========================================
# 3. CHATABLE GEMINI ENGINE (MULTI-TURN)
# ==========================================
def run_chatable_gemini_query(user_query, api_key):
    if not api_key:
        return (
            "⚠️ **Gemini API Key Required**\n\n"
            "To chat with real AI, please paste your Gemini API Key in the **Sidebar** field under '🔑 Enter Gemini API Key'."
        )

    if not HAS_GENAI:
        return "❌ `google-generativeai` package is not installed."

    try:
        genai.configure(api_key=api_key)
        
        # Prepare Live Context
        context_data = {
            "loaded_technicians": list(st.session_state.drivers.keys()),
            "unassigned_orders_count": len(st.session_state.unassigned_orders),
            "completed_eod_logs": len(st.session_state.eod_excel_records)
        }
        
        system_instruction = f"""
        You are Gemini, an expert AI collaborator and operations assistant for Mirage Distribution & Fleet Hub.
        Be helpful, energetic, and intelligent. 
        
        Current Live Application State:
        {json.dumps(context_data, indent=2)}
        """

        # Format past chat history for model.start_chat()
        formatted_history = []
        for msg in st.session_state.side_chat_history[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg["content"]]})

        # Try gemini-2.5-flash, fallback to gemini-1.5-flash
        try:
            model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(user_query)
            return response.text
        except Exception:
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_instruction)
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(user_query)
            return response.text

    except Exception as e:
        return f"❌ **API Error:** {str(e)}"

# ==========================================
# 4. HELPER MATH & DISPATCH ENGINES
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

def run_automated_ai_dispatch(single_batch_only=False):
    if not st.session_state.unassigned_orders:
        return "No pending unassigned orders to dispatch."
        
    if not st.session_state.drivers:
        return "No technicians loaded! Please upload your Technicians Excel file first."

    orders_to_dispatch = [st.session_state.unassigned_orders[0]] if single_batch_only else list(st.session_state.unassigned_orders)

    dispatched_count = 0
    for order in orders_to_dispatch:
        best_driver = min(st.session_state.drivers.keys(), key=lambda d: st.session_state.drivers[d]["current_load"])
        
        order["status"] = f"Dispatched ({datetime.now().strftime('%H:%M:%S')})"
        order["logs"] = []
        order["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        st.session_state.assigned_orders[best_driver].append(order)
        st.session_state.drivers[best_driver]["current_load"] += order.get("weight_units", 1)
        st.session_state.unassigned_orders.remove(order)
        dispatched_count += 1

    return f"Dispatch Cycle Completed: Successfully assigned {dispatched_count} order(s) at {datetime.now().strftime('%H:%M:%S')}."

def generate_whatsapp_url(phone_number, text_message):
    clean_phone = str(phone_number).replace("+", "").replace(" ", "").replace("-", "")
    encoded_text = urllib.parse.quote(text_message)
    return f"https://wa.me/{clean_phone}?text={encoded_text}"

# ==========================================
# 5. SIDEBAR NAVIGATION & API KEY CONFIG
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

# Retrieve API Key from Secrets or UI Input
secret_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
if secret_key:
    active_api_key = secret_key
else:
    active_api_key = st.sidebar.text_input("🔑 Enter Gemini API Key:", value=st.session_state.user_api_key, type="password")
    st.session_state.user_api_key = active_api_key

st.sidebar.caption(T['sys_status'])
if active_api_key:
    st.sidebar.success(T['ai_active'])
else:
    st.sidebar.warning(T['ai_offline'])

if st.sidebar.button(T['clear_session'], type="secondary", use_container_width=True):
    initialize_empty_state()
    st.sidebar.success("Session memory cleared!")
    st.rerun()

# ==========================================
# 6. TOP HEADER & DRAWER TOGGLE
# ==========================================
top_c1, top_c2 = st.columns([4, 1])

with top_c2:
    is_panel_open = st.session_state.get("show_ai_panel", False)
    button_label = "❌ Close Gemini AI" if is_panel_open else "🤖 Open Gemini AI Panel"
    
    if st.button(button_label, use_container_width=True, type="primary"):
        st.session_state.show_ai_panel = not is_panel_open
        st.rerun()

if st.session_state.get("show_ai_panel", False):
    main_col, ai_panel_col = st.columns([2, 1])
else:
    main_col = st.container()
    ai_panel_col = None

# ==========================================
# 7. MAIN APPLICATION MODULES
# ==========================================
with main_col:
    if app_module == T['nav_excel_import']:
        st.title(T['nav_excel_import'])
        st.markdown("Upload your separate Excel files for Technicians and Orders.")
        
        col_tech_file, col_order_file = st.columns(2)
        
        with col_tech_file:
            st.subheader("1. Technicians Excel File")
            tech_file = st.file_uploader("Upload Techs Excel (.xlsx, .xls):", type=["xlsx", "xls"], key="tech_uploader")
            
            if tech_file is not None:
                try:
                    df_techs = pd.read_excel(tech_file)
                    st.dataframe(df_techs, use_container_width=True)
                    
                    if st.button("Load Technicians into System", type="primary"):
                        st.session_state.drivers = {}
                        st.session_state.assigned_orders = {}
                        
                        for idx, row in df_techs.iterrows():
                            name = str(row.get("Name", row.get("Driver", row.get("Technician", f"Tech-{idx+1}")))).strip()
                            status = str(row.get("Status", "Available")).strip()
                            cap = int(row.get("Capacity", row.get("Capacity Units", 10)))
                            load = int(row.get("Current Load", row.get("Load", 0)))
                            lat = float(row.get("Lat", row.get("Latitude", 30.0444)))
                            lon = float(row.get("Lon", row.get("Longitude", 31.2357)))
                            
                            st.session_state.drivers[name] = {
                                "status": status,
                                "capacity_units": cap,
                                "current_load": load,
                                "lat": lat,
                                "lon": lon
                            }
                            st.session_state.assigned_orders[name] = []
                            
                        st.success(f"Loaded {len(st.session_state.drivers)} technician(s) successfully!")
                except Exception as e:
                    st.error(f"Error reading Technicians Excel file: {str(e)}")

        with col_order_file:
            st.subheader("2. Distribution Orders Excel File")
            order_file = st.file_uploader("Upload Orders Excel (.xlsx, .xls):", type=["xlsx", "xls"], key="order_uploader")
            
            if order_file is not None:
                try:
                    df_orders = pd.read_excel(order_file)
                    st.dataframe(df_orders, use_container_width=True)
                    
                    if st.button("Load Orders into Dispatch Queue", type="primary"):
                        st.session_state.unassigned_orders = []
                        
                        for idx, row in df_orders.iterrows():
                            o_id = str(row.get("Order ID", row.get("ID", f"ORD-{1001+idx}"))).strip()
                            client = str(row.get("Client", row.get("Company", "Corporate Client"))).strip()
                            contact = str(row.get("Contact", row.get("Phone", "+201000000000"))).strip()
                            address = str(row.get("Address", row.get("Location", "Cairo"))).strip()
                            priority = str(row.get("Priority", "Medium")).strip()
                            cargo = str(row.get("Cargo", row.get("Items", "Package Goods"))).strip()
                            details = str(row.get("Details", row.get("Notes", "Standard delivery"))).strip()
                            est_hrs = float(row.get("Est Hours", row.get("Hours", 2.0)))
                            weight = int(row.get("Weight Units", row.get("Weight", 1)))
                            lat = float(row.get("Lat", row.get("Latitude", 30.0444)))
                            lon = float(row.get("Lon", row.get("Longitude", 31.2357)))
                            
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
                            
                        st.success(f"Loaded {len(st.session_state.unassigned_orders)} order(s) into dispatch queue!")
                except Exception as e:
                    st.error(f"Error reading Orders Excel file: {str(e)}")

    elif app_module == T['nav_portal']:
        st.title(T['nav_portal'])
        
        if not st.session_state.drivers:
            st.warning("⚠️ No technicians currently loaded. Upload Excel files first.")
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
                order_options = [f"{o['id']} - {o['client']} ({o['priority']} Priority) | [{o['status']}]" for o in driver_orders]
                sel_idx = st.selectbox("Select Order to Process:", range(len(order_options)), format_func=lambda x: order_options[x])
                
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
                    
                st.markdown("---")
                completion_notes = st.text_area("Technician Field Completion Notes:", placeholder="Enter completion details...")
                
                if st.button(T['submit_summary'], type="primary"):
                    if completion_notes.strip():
                        current_ord["status"] = "Completed"
                        current_ord.setdefault("logs", []).append(completion_notes)
                        st.session_state.eod_excel_records.append({
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Driver Name": selected_driver,
                            "Order ID": current_ord['id'],
                            "Client": current_ord['client'],
                            "Notes": completion_notes
                        })
                        st.success(f"Order {current_ord['id']} marked COMPLETED!")

    elif app_module == T['nav_ai_dispatch']:
        st.title(T['ai_dispatch_header'])
        col_unassigned, col_drivers = st.columns([1, 1])
        
        with col_unassigned:
            st.subheader(T['unassigned_orders'])
            if st.session_state.unassigned_orders:
                st.dataframe(pd.DataFrame(st.session_state.unassigned_orders)[["id", "client", "priority", "cargo"]], use_container_width=True)
            else:
                st.success("🎉 No unassigned orders pending!")
                
        with col_drivers:
            st.subheader(T['driver_roster'])
            if st.session_state.drivers:
                driver_data = [{"Driver/Tech": k, "Load": v["current_load"], "Capacity": v["capacity_units"]} for k, v in st.session_state.drivers.items()]
                st.dataframe(pd.DataFrame(driver_data), use_container_width=True)
            else:
                st.warning("No technicians loaded.")
            
        st.markdown("---")
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button(T['run_ai_dispatch'], type="primary", use_container_width=True):
                res = run_automated_ai_dispatch(single_batch_only=False)
                st.success(res)
                st.rerun()

        with btn_col2:
            if st.button(T['run_1min_loop'], use_container_width=True):
                if st.session_state.unassigned_orders and st.session_state.drivers:
                    progress_bar = st.progress(0)
                    status_box = st.empty()
                    while len(st.session_state.unassigned_orders) > 0:
                        res = run_automated_ai_dispatch(single_batch_only=True)
                        status_box.success(res)
                        for sec in range(60):
                            time.sleep(1)
                            progress_bar.progress((sec + 1) / 60)
                    status_box.success("🎉 All orders dispatched!")

    elif app_module == T['nav_geofence']:
        st.title(T['geofence_header'])
        all_points = [{"lat": o["lat"], "lon": o["lon"], "Driver": d, "Order": o["id"]} for d, orders in st.session_state.assigned_orders.items() for o in orders]
        df_map = pd.DataFrame(all_points)
        
        if not df_map.empty:
            st.map(df_map, zoom=10, use_container_width=True)
        else:
            st.info("No active waypoints to display on GPS map.")

    elif app_module == T['nav_whatsapp']:
        st.title(T['wa_header'])
        all_orders = [o for sub in st.session_state.assigned_orders.values() for o in sub]
        if all_orders:
            sel_wa_idx = st.selectbox("Select Target Client:", range(len(all_orders)), format_func=lambda x: f"{all_orders[x]['id']} - {all_orders[x]['client']}")
            wa_target = all_orders[sel_wa_idx]
            custom_msg = st.text_area("Message Body:", value=f"Hello {wa_target['client']}, your shipment ({wa_target['id']}) is en route!")
            wa_link = generate_whatsapp_url(wa_target["contact"], custom_msg)
            st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer;">Send WhatsApp</button></a>', unsafe_allow_html=True)

    elif app_module == T['nav_eod']:
        st.title(T['nav_eod'])
        if st.session_state.eod_excel_records:
            df_eod = pd.DataFrame(st.session_state.eod_excel_records)
            st.dataframe(df_eod, use_container_width=True)

# ==========================================
# 8. RETRACTABLE GEMINI AI CHAT DRAWER
# ==========================================
if st.session_state.get("show_ai_panel", False) and ai_panel_col is not None:
    with ai_panel_col:
        st.subheader("🤖 Gemini Chat Assistant")
        st.caption("Live AI assistant with conversational memory")
        st.markdown("---")

        chat_container = st.container(height=520)
        
        # Render past history
        with chat_container:
            for message in st.session_state.side_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Interactive Chat Input
        if side_prompt := st.chat_input("Ask Gemini anything..."):
            st.session_state.side_chat_history.append({"role": "user", "content": side_prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(side_prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner("Gemini is thinking..."):
                        bot_response = run_chatable_gemini_query(side_prompt, active_api_key)
                        st.markdown(bot_response)
                        st.session_state.side_chat_history.append({"role": "assistant", "content": bot_response})
            st.rerun()
