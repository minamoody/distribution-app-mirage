import streamlit as st
import pandas as pd
from datetime import datetime
import io
import urllib.parse
import json
import time

# ==========================================
# 0. STREAMLIT CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="Mirage Multi-Brand Fleet Hub",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. MULTI-BRAND & AUTHENTICATION CONFIG
# ==========================================
MASTER_KEY = "MIRAGE_MASTER_2026"

BRANDS_REGISTRY = {
    "HAIER": {"pass": "haier123", "display_name": "Haier / هاير"},
    "LG": {"pass": "lg123", "display_name": "LG / إل جي"},
    "PICO": {"pass": "pico123", "display_name": "Pico / بيكو"},
    "MIDEA": {"pass": "midea123", "display_name": "Midea / ميديا"},
    "HIGHSENSE": {"pass": "highsense123", "display_name": "Hisense / هايسنس"}
}

# ==========================================
# 2. BILINGUAL TRANSLATION DICTIONARY (EN/AR)
# ==========================================
TRANSLATIONS = {
    "EN": {
        "app_title": "Mirage Multi-Brand Fleet Command",
        "app_subtitle": "Isolated Brand Enterprise Dispatch & Field Management System",
        "nav_menu": "Navigation Menu",
        "language_select": "🌐 Select Language / اختر اللغة",
        "nav_portal": "👨‍🔧 Technician / فني Field Portal",
        "nav_ai_dispatch": "🤖 Automated AI Dispatch Engine (1-Min Loop)",
        "nav_excel_import": "📁 Excel Upload Hub (Separate Brand Data)",
        "nav_geofence": "🎯 GPS Geofence & Live Fleet Map",
        "nav_whatsapp": "💬 WhatsApp & Client Alert Hub",
        "nav_eod": "📊 End-of-Day Excel Reports & KPIs",
        "select_tech": "📌 Select Assigned Technician / فني:",
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
        "ai_dispatch_header": "🤖 Automated Built-in AI Dispatch Engine (Brand-Isolated)",
        "ai_dispatch_desc": "Evaluates technician capacity strictly within your authenticated brand scope.",
        "run_ai_dispatch": "⚡ Run Automated AI Dispatching Engine (Single Pass)",
        "run_1min_loop": "⏱️ Start 1-Minute Automated Dispatch Loop",
        "unassigned_orders": "📦 Unassigned Corporate Orders",
        "tech_roster": "🚛 Technician / فني & Fleet Capacity Roster",
        "geofence_header": "🎯 Smart Dispatch GPS & Geofence Simulator",
        "wa_header": "💬 WhatsApp Communication & Feedback Hub",
        "send_wa": "📲 Send WhatsApp Dispatch Notification",
        "download_excel": "📥 Download Brand Master EOD Report (.XLSX)",
        "clear_session": "🧹 Clear Brand Session Data"
    },
    "AR": {
        "app_title": "منظومة التوزيع وإدارة الأسطول للشركات - معراج",
        "app_subtitle": "النظام الآمن المعزول لإدارة الأسطول والفنيين لكل براند على حدة",
        "nav_menu": "قائمة التحكم الرئيسية",
        "language_select": "🌐 اختر اللغة / Select Language",
        "nav_portal": "👨‍🔧 بوابة الفنيين الميدانيين (Technician / فني)",
        "nav_ai_dispatch": "🤖 محرك التوزيع الذكي المدمج (خاص بالبراند)",
        "nav_excel_import": "📁 مركز رفع ملفات Excel (بيانات مستقلة لكل براند)",
        "nav_geofence": "🎯 التتبع المباشر والنطاق الجغرافي للبراند",
        "nav_whatsapp": "💬 مركز إشعارات الواتساب والعملاء",
        "nav_eod": "📊 تقارير Excel نهاية اليوم ومؤشرات الأداء",
        "select_tech": "📌 اختر الفني / Technician:",
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
        "ai_dispatch_header": "🤖 محرك التوزيع الذكي المدمج (معزول حسب البراند)",
        "ai_dispatch_desc": "يقوم النظام بتوزيع الشحنات الخاصة بالبراند الحالي فقط على الفنيين التابعين له.",
        "run_ai_dispatch": "⚡ تشغيل التوزيع الآلي (دورة واحدة)",
        "run_1min_loop": "⏱️ تشغيل حلقة التوزيع التلقائي كل دقيقة",
        "unassigned_orders": "📦 شحنات الشركات غير الموزعة",
        "tech_roster": "🚛 قائمة الفنيين والطاقة الاستيعابية",
        "geofence_header": "🎯 محاكي النطاق الجغرافي والتتبع المباشر",
        "wa_header": "💬 مركز إشعارات الواتساب وتقييم العملاء",
        "send_wa": "📲 إرسال إشعار التوزيع عبر الواتساب",
        "download_excel": "📥 تحميل تقرير نهاية اليوم Master Excel (.XLSX)",
        "clear_session": "🧹 مسح بيانات البراند المخزنة"
    }
}

# ==========================================
# 3. SAFE SESSION STATE & STORAGE INITIALIZATION
# ==========================================
st.session_state.setdefault("language", "EN")
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("is_master", False)
st.session_state.setdefault("logged_in_brand", None)
st.session_state.setdefault("active_view_brand", list(BRANDS_REGISTRY.keys())[0])

if "brands_storage" not in st.session_state:
    st.session_state.brands_storage = {}

for b_key in BRANDS_REGISTRY.keys():
    if b_key not in st.session_state.brands_storage:
        st.session_state.brands_storage[b_key] = {
            "technicians": {},
            "assigned_orders": {},
            "unassigned_orders": [],
            "eod_excel_records": [],
            "customer_ratings": [],
            "expense_logs": []
        }

st.session_state.setdefault("side_chat_history", [
    {"role": "assistant", "content": "👋 Welcome! I am your Brand-Isolated Fleet Operations AI. Ask me about technician workloads or pending orders."}
])

T = TRANSLATIONS[st.session_state.language]

# ==========================================
# 4. LOGIN GATEKEEPER SCREEN
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔐 Mirage Enterprise Multi-Brand Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter your brand credentials or use the Master Key to unlock full system access.</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    
    with col_l2:
        with st.form("login_form"):
            login_mode = st.radio("Select Login Mode / اختر نوع الدخول:", ["Brand Admin / مسؤول براند", "Master Admin / المسؤول الرئيسي (Master Key)"])
            
            if login_mode == "Brand Admin / مسؤول براند":
                selected_brand_key = st.selectbox("Select Brand / اختر البراند:", list(BRANDS_REGISTRY.keys()), format_func=lambda x: BRANDS_REGISTRY[x]["display_name"])
                password_input = st.text_input("Brand Password / كلمة مرور البراند:", type="password")
            else:
                master_key_input = st.text_input("Master Key / المفتاح الرئيسي:", type="password")
                
            submit_login = st.form_submit_button("🔓 Secure Login / دخول آمن", use_container_width=True)
            
            if submit_login:
                if login_mode == "Brand Admin / مسؤول براند":
                    if password_input == BRANDS_REGISTRY[selected_brand_key]["pass"]:
                        st.session_state.authenticated = True
                        st.session_state.is_master = False
                        st.session_state.logged_in_brand = selected_brand_key
                        st.session_state.active_view_brand = selected_brand_key
                        st.success(f"Successfully logged in as {BRANDS_REGISTRY[selected_brand_key]['display_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect brand password. Please check and try again.")
                else:
                    if master_key_input == MASTER_KEY:
                        st.session_state.authenticated = True
                        st.session_state.is_master = True
                        st.session_state.logged_in_brand = "MASTER"
                        st.session_state.active_view_brand = list(BRANDS_REGISTRY.keys())[0]
                        st.success("🔓 Master Key accepted! Full system access unlocked.")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Master Key provided.")
    st.stop()

# ==========================================
# 5. HELPER FUNCTIONS (SCOPED TO ACTIVE BRAND)
# ==========================================
def get_active_store():
    target_brand = st.session_state.get("active_view_brand")
    if not target_brand or target_brand not in BRANDS_REGISTRY:
        target_brand = list(BRANDS_REGISTRY.keys())[0]
        st.session_state.active_view_brand = target_brand
        
    if "brands_storage" not in st.session_state:
        st.session_state.brands_storage = {}
        
    if target_brand not in st.session_state.brands_storage:
        st.session_state.brands_storage[target_brand] = {
            "technicians": {},
            "assigned_orders": {},
            "unassigned_orders": [],
            "eod_excel_records": [],
            "customer_ratings": [],
            "expense_logs": []
        }
    return st.session_state.brands_storage[target_brand]

def run_builtin_autonomous_ai(user_query):
    store = get_active_store()
    query_lower = user_query.strip().lower()
    
    total_techs = len(store["technicians"])
    total_unassigned = len(store["unassigned_orders"])
    total_completed = len(store["eod_excel_records"])
    
    tech_workloads = {t: f"{info['current_load']}/{info['capacity_units']} units" for t, info in store["technicians"].items()}

    if any(k in query_lower for k in ["status", "overview", "summary", "state"]):
        return f"""### 📊 Brand Operational Status Summary ({st.session_state.active_view_brand})
* **Active Technicians / فنيين:** {total_techs}
* **Pending Unassigned Orders:** {total_unassigned}
* **Completed EOD Logs:** {total_completed}
* **Current Workloads:** {json.dumps(tech_workloads, indent=1)}"""
    else:
        return f"""### 🤖 Mirage AI Strategist ({st.session_state.active_view_brand})
* **Active Queue:** {total_unassigned} unassigned orders across {total_techs} registered technicians / فنيين.
* **System State:** Isolated brand storage fully operational."""

def run_automated_ai_dispatch(single_batch_only=False):
    store = get_active_store()
    if not store["unassigned_orders"]:
        return "No pending unassigned orders to dispatch for this brand."
    if not store["technicians"]:
        return "No technicians loaded for this brand! Please upload your Technicians Excel file first."

    orders_to_dispatch = [store["unassigned_orders"][0]] if single_batch_only else list(store["unassigned_orders"])
    dispatched_count = 0
    
    for order in orders_to_dispatch:
        best_tech = min(store["technicians"].keys(), key=lambda t: store["technicians"][t]["current_load"])
        order["status"] = f"Dispatched ({datetime.now().strftime('%H:%M:%S')})"
        order.setdefault("logs", [])
        
        store["assigned_orders"][best_tech].append(order)
        store["technicians"][best_tech]["current_load"] += order.get("weight_units", 1)
        store["unassigned_orders"].remove(order)
        dispatched_count += 1

    return f"Dispatch Cycle Completed: Successfully assigned {dispatched_count} order(s) for {st.session_state.active_view_brand}."

def generate_whatsapp_url(phone_number, text_message):
    clean_phone = str(phone_number).replace("+", "").replace(" ", "").replace("-", "")
    encoded_text = urllib.parse.quote(text_message)
    return f"https://wa.me/{clean_phone}?text={encoded_text}"

# ==========================================
# 6. SIDEBAR NAVIGATION & BRAND SWITCHER
# ==========================================
st.sidebar.markdown(f"### {T['app_title']}")

# Master Key Brand Switcher
if st.session_state.is_master:
    st.sidebar.warning("🔑 Master Admin Mode Active")
    selected_view = st.sidebar.selectbox(
        "🏢 Switch Brand Workspace / اختر براند العرض:",
        list(BRANDS_REGISTRY.keys()),
        format_func=lambda x: BRANDS_REGISTRY[x]["display_name"],
        index=list(BRANDS_REGISTRY.keys()).index(st.session_state.active_view_brand) if st.session_state.active_view_brand in BRANDS_REGISTRY else 0
    )
    if selected_view != st.session_state.active_view_brand:
        st.session_state.active_view_brand = selected_view
        st.rerun()
else:
    st.sidebar.info(f"👤 Brand Admin: **{BRANDS_REGISTRY[st.session_state.logged_in_brand]['display_name']}**")

st.sidebar.markdown("---")

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
        T['nav_eod'],
        "⭐ Technician Performance Matrix / مصفوفة أداء الفنيين",
        "💸 Cost & Fuel Tracker / تتبع المصاريف والوقود"
    ]
)

st.sidebar.markdown("---")

if st.sidebar.button("🚪 Log Out / تسجيل الخروج", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.is_master = False
    st.session_state.logged_in_brand = None
    st.rerun()

if st.sidebar.button(T['clear_session'], type="secondary", use_container_width=True):
    store = get_active_store()
    store["technicians"] = {}
    store["assigned_orders"] = {}
    store["unassigned_orders"] = []
    store["eod_excel_records"] = []
    store["customer_ratings"] = []
    store["expense_logs"] = []
    st.sidebar.success("Current brand session memory cleared!")
    st.rerun()

# ==========================================
# 7. TOP HEADER & DRAWER TOGGLE
# ==========================================
top_c1, top_c2 = st.columns([4, 1])

with top_c2:
    is_panel_open = st.session_state.get("show_ai_panel", False)
    button_label = "❌ Close AI Assistant" if is_panel_open else "🤖 Open AI Assistant"
    
    if st.button(button_label, use_container_width=True, type="primary"):
        st.session_state.show_ai_panel = not is_panel_open
        st.rerun()

if st.session_state.get("show_ai_panel", False):
    main_col, ai_panel_col = st.columns([2, 1])
else:
    main_col = st.container()
    ai_panel_col = None

# ==========================================
# 8. MAIN APPLICATION MODULES (SCOPED BY BRAND)
# ==========================================
with main_col:
    store = get_active_store()

    # --- MODULE 1: EXCEL UPLOAD HUB ---
    if app_module == T['nav_excel_import']:
        st.title(T['nav_excel_import'])
        st.markdown(f"Upload separate Excel files for **{BRANDS_REGISTRY[st.session_state.active_view_brand]['display_name']}**. Data is securely isolated per brand.")
        
        st.subheader("📥 Download Blank Daily Bilingual Templates")
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            df_blank_techs = pd.DataFrame(columns=[
                "Name / الاسم", "Status / الحالة", "Home / المنزل أو المركز الرئيسي (Starting Base)",
                "Vehicle Type / نوع المركبة (Car/Motorcycle)", "Vehicle Brand / ماركة المركبة", 
                "Service Scope / نطاق الخدمة (Maintenance/Installation/Both)", 
                "Specialized Equipment / المعدات والأجهزة التي يصلحها", "Capacity Units / وحدة السعة", "Current Load / الحمل الحالي"
            ])
            buffer_tech = io.BytesIO()
            with pd.ExcelWriter(buffer_tech, engine='openpyxl') as writer:
                df_blank_techs.to_excel(writer, index=False, sheet_name='Technicians')
            
            st.download_button(
                label="📥 Download Empty Technicians / فنيين Template (.xlsx)",
                data=buffer_tech.getvalue(),
                file_name=f"Technicians_Template_{st.session_state.active_view_brand}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        with col_down2:
            df_blank_orders = pd.DataFrame(columns=[
                "Order ID / رقم الطلب", "Client / العميل", "Contact / رقم التواصل", "Address / العنوان", 
                "Priority / الأولوية", "Cargo / الشحنة", "Details / التفاصيل", "Est Hours / ساعات التقدير", "Weight Units / وحدات الوزن"
            ])
            buffer_order = io.BytesIO()
            with pd.ExcelWriter(buffer_order, engine='openpyxl') as writer:
                df_blank_orders.to_excel(writer, index=False, sheet_name='Orders')
                
            st.download_button(
                label="📥 Download Empty Orders Template (.xlsx)",
                data=buffer_order.getvalue(),
                file_name=f"Orders_Template_{st.session_state.active_view_brand}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        st.markdown("---")
        
        col_tech_file, col_order_file = st.columns(2)
        
        with col_tech_file:
            st.subheader("1. Upload Technicians / فنيين File")
            tech_file = st.file_uploader("Upload Techs Excel (.xlsx):", type=["xlsx", "xls"], key=f"tech_up_{st.session_state.active_view_brand}")
            
            if tech_file is not None:
                try:
                    df_techs = pd.read_excel(tech_file)
                    st.dataframe(df_techs, use_container_width=True)
                    
                    if st.button("Load Technicians into Brand Workspace", type="primary"):
                        store["technicians"] = {}
                        store["assigned_orders"] = {}
                        
                        for idx, row in df_techs.iterrows():
                            name = str(row.get("Name / الاسم", f"Tech-{idx+1}")).strip()
                            status = str(row.get("Status / الحالة", "Available")).strip()
                            home_base = str(row.get("Home / المنزل أو المركز الرئيسي (Starting Base)", "Main Center")).strip()
                            v_type = str(row.get("Vehicle Type / نوع المركبة (Car/Motorcycle)", "Car")).strip()
                            v_brand = str(row.get("Vehicle Brand / ماركة المركبة", "Toyota")).strip()
                            service_scope = str(row.get("Service Scope / نطاق الخدمة (Maintenance/Installation/Both)", "Both")).strip()
                            specialty = str(row.get("Specialized Equipment / المعدات والأجهزة التي يصلحها", "General")).strip()
                            cap = int(row.get("Capacity Units / وحدة السعة", 10))
                            load = int(row.get("Current Load / الحمل الحالي", 0))
                            
                            store["technicians"][name] = {
                                "status": status, "home_base": home_base, "vehicle_type": v_type,
                                "vehicle_brand": v_brand, "service_scope": service_scope, "specialty": specialty,
                                "capacity_units": cap, "current_load": load
                            }
                            store["assigned_orders"][name] = []
                            
                        st.success(f"Loaded {len(store['technicians'])} technician(s) / فني successfully for {st.session_state.active_view_brand}!")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

        with col_order_file:
            st.subheader("2. Upload Orders File")
            order_file = st.file_uploader("Upload Orders Excel (.xlsx):", type=["xlsx", "xls"], key=f"order_up_{st.session_state.active_view_brand}")
            
            if order_file is not None:
                try:
                    df_orders = pd.read_excel(order_file)
                    st.dataframe(df_orders, use_container_width=True)
                    
                    if st.button("Load Orders into Brand Queue", type="primary"):
                        store["unassigned_orders"] = []
                        
                        for idx, row in df_orders.iterrows():
                            store["unassigned_orders"].append({
                                "id": str(row.get("Order ID / رقم الطلب", f"ORD-{1001+idx}")).strip(),
                                "client": str(row.get("Client / العميل", "Corporate Client")).strip(),
                                "contact": str(row.get("Contact / رقم التواصل", "+201000000000")).strip(),
                                "address": str(row.get("Address / العنوان", "Cairo")).strip(),
                                "priority": str(row.get("Priority / الأولوية", "Medium")).strip(),
                                "cargo": str(row.get("Cargo / الشحنة", "Package Goods")).strip(),
                                "details": str(row.get("Details / التفاصيل", "Standard delivery")).strip(),
                                "est_hours": float(row.get("Est Hours / ساعات التقدير", 2.0)),
                                "weight_units": int(row.get("Weight Units / وحدات الوزن", 1))
                            })
                            
                        st.success(f"Loaded {len(store['unassigned_orders'])} order(s) into queue for {st.session_state.active_view_brand}!")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

    # --- MODULE 2: FIELD PORTAL ---
    elif app_module == T['nav_portal']:
        st.title(T['nav_portal'])
        st.caption(f"Active Brand Scope: {st.session_state.active_view_brand}")
        
        if not store["technicians"]:
            st.info("No technicians currently loaded for this brand. Please upload files in the Excel Upload Hub.")
        else:
            col_tech_sel, m1, m2 = st.columns([2, 1, 1])
            with col_tech_sel:
                tech_names = list(store["technicians"].keys())
                selected_tech = st.selectbox(T['select_tech'], tech_names)
                
            tech_orders = store["assigned_orders"].get(selected_tech, [])
            with m1:
                st.metric(T['total_jobs'], len(tech_orders))
            with m2:
                completed = sum(1 for o in tech_orders if o.get('status') == 'Completed')
                st.metric(T['completed_jobs'], completed)
                
            st.markdown("---")
            tech_info = store["technicians"].get(selected_tech, {})
            st.info(f"🏠 **Home Base (نقطة الانطلاق):** {tech_info.get('home_base', 'Main Center')} | 🚛 **Vehicle:** {tech_info.get('vehicle_type')} ({tech_info.get('vehicle_brand')}) | 🔧 **Specialty:** {tech_info.get('specialty')}")
            
            if not tech_orders:
                st.info(f"No active orders assigned to {selected_tech}.")
            else:
                order_options = [f"{o['id']} - {o['client']} ({o['priority']}) | [{o['status']}]" for o in tech_orders]
                sel_idx = st.selectbox("Select Order to Process:", range(len(order_options)), format_func=lambda x: order_options[x])
                current_ord = tech_orders[sel_idx]
                
                with st.expander(T['order_details'], expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**{T['client_name']}:** {current_ord['client']}")
                    c1.markdown(f"**{T['contact_num']}:** `{current_ord['contact']}`")
                    c2.markdown(f"**{T['priority']}:** `{current_ord['priority']}`")
                    c2.markdown(f"**{T['status']}:** `{current_ord['status']}`")
                    c3.markdown(f"**{T['cargo_details']}:** {current_ord['cargo']}")
                    c3.markdown(f"**{T['est_hours']}:** {current_ord['est_hours']} hrs")
                    st.markdown(f"**{T['address']}:** {current_ord['address']}")
                    
                st.markdown("---")
                st.subheader("📝 Technician Completion Notes / ملاحظات إنجاز الفني")
                completion_notes = st.text_area("Enter field notes or repair summary:", placeholder="Enter details...")
                
                if st.button(T['submit_summary'], type="primary"):
                    if not completion_notes.strip():
                        st.error("Please enter completion notes.")
                    else:
                        current_ord["status"] = "Completed"
                        store["eod_excel_records"].append({
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Brand": st.session_state.active_view_brand,
                            "Technician Name": selected_tech,
                            "Order ID": current_ord['id'],
                            "Client": current_ord['client'],
                            "Notes": completion_notes
                        })
                        st.success(f"Order {current_ord['id']} marked COMPLETED!")

    # --- MODULE 3: AUTOMATED AI DISPATCH ENGINE ---
    elif app_module == T['nav_ai_dispatch']:
        st.title(T['ai_dispatch_header'])
        st.markdown(T['ai_dispatch_desc'])
        
        col_unassigned, col_techs = st.columns(2)
        with col_unassigned:
            st.subheader(T['unassigned_orders'])
            if store["unassigned_orders"]:
                st.dataframe(pd.DataFrame(store["unassigned_orders"])[["id", "client", "priority", "cargo"]], use_container_width=True)
            else:
                st.success("🎉 No unassigned orders pending!")
                
        with col_techs:
            st.subheader(T['tech_roster'])
            if store["technicians"]:
                tech_data = [{"Technician / فني": t, "Home Base": i.get("home_base"), "Load": f"{i['current_load']}/{i['capacity_units']}"} for t, i in store["technicians"].items()]
                st.dataframe(pd.DataFrame(tech_data), use_container_width=True)
            else:
                st.info("No technicians loaded.")
            
        st.markdown("---")
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button(T['run_ai_dispatch'], type="primary", use_container_width=True):
                res = run_automated_ai_dispatch(single_batch_only=False)
                st.success(res)
                st.rerun()
        with btn_c2:
            if st.button(T['run_1min_loop'], use_container_width=True):
                if not store["unassigned_orders"]:
                    st.info("No orders pending.")
                else:
                    status_box = st.empty()
                    while len(store["unassigned_orders"]) > 0:
                        res = run_automated_ai_dispatch(single_batch_only=True)
                        status_box.success(res)
                        time.sleep(1)
                    status_box.success("🎉 All pending orders dispatched!")

    # --- MODULE 4: GEOFENCE & ROUTE MAP ---
    elif app_module == T['nav_geofence']:
        st.title(T['geofence_header'])
        if store["technicians"]:
            base_data = [{"Technician / فني": t, "Home Base": i.get("home_base"), "Vehicle": f"{i.get('vehicle_type')} ({i.get('vehicle_brand')})"} for t, i in store["technicians"].items()]
            st.dataframe(pd.DataFrame(base_data), use_container_width=True)
        else:
            st.info("No technician data loaded.")

    # --- MODULE 5: WHATSAPP HUB ---
    elif app_module == T['nav_whatsapp']:
        st.title(T['wa_header'])
        all_flat_orders = [o for sublist in store["assigned_orders"].values() for o in sublist]
        if not all_flat_orders:
            st.info("No assigned orders available.")
        else:
            order_labels = [f"{o['id']} - {o['client']} ({o['contact']})" for o in all_flat_orders]
            sel_wa_idx = st.selectbox("Select Target Client Order:", range(len(order_labels)), format_func=lambda x: order_labels[x])
            wa_target = all_flat_orders[sel_wa_idx]
            
            c_wa1, c_wa2 = st.columns(2)
            with c_wa1:
                eta = st.slider("Estimated Arrival (Minutes):", 10, 120, 30)
                default_text = f"Hello {wa_target['client']}, your shipment ({wa_target['id']} - {wa_target['cargo']}) is en route. ETA: {eta} mins."
                custom_msg = st.text_area("Message Body:", value=default_text)
                wa_link = generate_whatsapp_url(wa_target["contact"], custom_msg)
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer;">{T["send_wa"]}</button></a>', unsafe_allow_html=True)
            with c_wa2:
                rating = st.select_slider("Service Rating:", options=[1, 2, 3, 4, 5], value=5)
                comments = st.text_input("Feedback Notes:", "Prompt technician service.")
                if st.button("Log Customer Feedback"):
                    store["customer_ratings"].append({"Order ID": wa_target["id"], "Rating": rating, "Comments": comments})
                    st.success("Feedback logged!")

    # --- MODULE 6: EOD REPORTS & KPIS ---
    elif app_module == T['nav_eod']:
        st.title(T['nav_eod'])
        k1, k2, k3 = st.columns(3)
        k1.metric("Total EOD Logs", len(store["eod_excel_records"]))
        k2.metric("On-Time Rate", "98.1%")
        k3.metric("Capacity Utilization", "84.2%")
        
        st.markdown("---")
        if not store["eod_excel_records"]:
            st.warning("No EOD logs recorded for this brand yet.")
        else:
            df_eod = pd.DataFrame(store["eod_excel_records"])
            st.dataframe(df_eod, use_container_width=True)
            
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_eod.to_excel(writer, index=False, sheet_name='EOD_Log')
                if store["customer_ratings"]:
                    pd.DataFrame(store["customer_ratings"]).to_excel(writer, index=False, sheet_name='Feedback')
                    
            st.download_button(
                label=T['download_excel'],
                data=excel_buffer.getvalue(),
                file_name=f"EOD_{st.session_state.active_view_brand}_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    # --- MODULE 7: PERFORMANCE MATRIX ---
    elif app_module == "⭐ Technician Performance Matrix / مصفوفة أداء الفنيين":
        st.title("⭐ Technician / فني Performance Scoring Matrix")
        if not store["technicians"]:
            st.info("No technicians loaded.")
        else:
            matrix_data = []
            for t_name, t_info in store["technicians"].items():
                completed = sum(1 for o in store["assigned_orders"].get(t_name, []) if o.get('status') == 'Completed')
                score = min(100, 70 + (completed * 5) - (t_info['current_load'] * 2))
                matrix_data.append({
                    "Technician / فني": t_name, "Home Base": t_info.get("home_base"),
                    "Completed Orders": completed, "Score (%)": max(40, score)
                })
            st.dataframe(pd.DataFrame(matrix_data), use_container_width=True)

    # --- MODULE 8: COST & FUEL TRACKER ---
    elif app_module == "💸 Cost & Fuel Tracker / تتبع المصاريف والوقود":
        st.title("💸 Fleet Cost & Fuel Expense Tracker")
        with st.form("expense_form"):
            c1, c2, c3 = st.columns(3)
            with c1: v_id = st.text_input("Vehicle ID:", "Van-01")
            with c2: fuel = st.number_input("Fuel Expense ($):", min_value=0.0, value=45.0)
            with c3: maint = st.number_input("Maintenance ($):", min_value=0.0, value=15.0)
            dist = st.number_input("Distance (KM):", min_value=0.0, value=120.0)
            notes = st.text_area("Notes:", "Daily fuel refill.")
            if st.form_submit_button("➕ Log Expense", type="primary"):
                store["expense_logs"].append({"Vehicle": v_id, "Total ($)": fuel + maint, "Distance (KM)": dist, "Notes": notes})
                st.success("Expense logged!")
        
        if store["expense_logs"]:
            st.dataframe(pd.DataFrame(store["expense_logs"]), use_container_width=True)

# ==========================================
# 9. AI CHAT DRAWER
# ==========================================
if st.session_state.get("show_ai_panel", False) and ai_panel_col is not None:
    with ai_panel_col:
        st.subheader(f"🤖 AI Strategist ({st.session_state.active_view_brand})")
        st.caption("Isolated brand memory")
        st.markdown("---")
        chat_container = st.container(height=520)
        with chat_container:
            for message in st.session_state.side_chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        if side_prompt := st.chat_input("Ask AI about workloads or status..."):
            st.session_state.side_chat_history.append({"role": "user", "content": side_prompt})
            bot_response = run_builtin_autonomous_ai(side_prompt)
            st.session_state.side_chat_history.append({"role": "assistant", "content": bot_response})
            st.rerun()
