import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. APP CONFIGURATION & STYLES
# ==============================================================================
st.set_page_config(
    page_title="Mirage AI Distribution & Logistics Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern UI Styling
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    .kpi-card {
        background-color: #0f172a;
        border-left: 5px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        color: white;
    }
    .kpi-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. BILINGUAL DICTIONARY (ENGLISH / ARABIC)
# ==============================================================================
TRANSLATIONS = {
    "EN": {
        "app_title": "⚡ AI Distributor & Logistics Hub",
        "sidebar_title": "⚡ AI Distributor Hub",
        "sidebar_caption": "Logistics & Dispatch Management",
        "select_lang": "🌐 Select Language / اختر اللغة",
        "select_module": "Select Module",
        "mod_map": "🗺️ Interactive Map",
        "mod_ai": "🤖 AI-Powered Distributor",
        "mod_logistics": "📦 Logistics Center",
        "mod_hub": "ℹ️ Central Info Hub",
        "reset_btn": "🗑️ Clear All Database Records",
        "reset_msg": "Database wiped clean!",
        
        # Map Module
        "map_title": "🗺️ Geographic Dispatch & Ticket Map",
        "map_sub": "Visual map tracking technician lines and active work orders.",
        "kpi_orders": "Active Orders Mapped",
        "kpi_techs": "Technicians in Field",
        "kpi_zones": "Active Zones",
        "no_map_points": "No coordinates available yet. Upload data containing 'lat' and 'lon' columns in the Central Info Hub.",
        
        # AI Module
        "ai_title": "🤖 AI-Powered Smart Dispatch Engine",
        "ai_sub": "Instantly distribute incoming work orders to the optimal technician line.",
        "dispatch_matcher": "🎯 Dispatch Matcher",
        "ai_settings": "⚙️ Customize AI Priority Weights",
        "weight_zone": "Zone Match Importance",
        "weight_skill": "Skill Match Importance",
        "weight_cap": "Capacity Availability Bonus",
        "select_zone": "Select Delivery / Service Zone",
        "select_skill": "Required Specialty / Skill",
        "run_match": "⚡ Run AI Dispatch Match",
        "rec_tech": "Recommended Technician",
        "match_score": "AI Match Score",
        "tech_capacity": "📋 Technician Lines & Capacity",
        "no_techs": "No technician records found. Upload technician data in the Central Info Hub.",
        "no_zones_opt": "No zones found (Upload data first)",
        "no_skills_opt": "No skills found (Upload data first)",

        # Logistics Module
        "logistics_title": "📦 Logistics & Inventory Center",
        "logistics_sub": "Manage spare parts, stock levels, and bin locations.",
        "low_stock_alert": "⚠️ Logistics Alert: {count} items are at or below minimum reorder thresholds!",
        "inv_master": "Inventory Master List",
        "save_stock": "💾 Save Stock Changes",
        "stock_saved": "Logistics inventory updated!",

        # Info Hub Module
        "hub_title": "ℹ️ Central Info Hub & Bulk Import Gateway",
        "hub_sub": "Upload bulk CSV/Excel files to populate your database, or edit active work orders in an Excel grid.",
        "tab_upload": "📤 Bulk Data Uploads",
        "tab_editor": "📝 Active Work Tickets (Excel Editor)",
        "upload_sub": "Upload CSV / Excel Data Files",
        "select_target": "Select Target Dataset",
        "target_techs": "Technicians Database",
        "target_orders": "Work Orders Database",
        "target_inv": "Inventory Database",
        "choose_file": "Choose a CSV or Excel file",
        "preview": "Uploaded File Preview:",
        "confirm_import": "Confirm Data Import",
        "import_success": "Successfully imported {count} records!",
        "grid_sub": "Interactive Work Order Grid (Excel Mode)",
        "grid_desc": "Edit ticket status, client info, or assign technicians directly in the cells below.",
        "save_orders": "💾 Save Work Order Changes",
        "orders_saved": "Work orders updated successfully!"
    },
    "AR": {
        "app_title": "⚡ مركز التوزيع واللوجستيات بالذكاء الاصطناعي",
        "sidebar_title": "⚡ مركز التوزيع الذكي",
        "sidebar_caption": "إدارة اللوجستيات والتوزيع الميداني",
        "select_lang": "🌐 Select Language / اختر اللغة",
        "select_module": "اختر القسم",
        "mod_map": "🗺️ الخريطة التفاعلية",
        "mod_ai": "🤖 الموزع الذكي بالذكاء الاصطناعي",
        "mod_logistics": "📦 مركز اللوجستيات",
        "mod_hub": "ℹ️ مركز المعلومات والرفع",
        "reset_btn": "🗑️ مسح كافة بيانات قاعدة البيانات",
        "reset_msg": "تم مسح جميع البيانات بنجاح!",
        
        # Map Module
        "map_title": "🗺️ خريطة التوزيع الميداني والطلبات",
        "map_sub": "خريطة تفاعلية لتتبع مواقع الفنيين والطلبات النشطة.",
        "kpi_orders": "الطلبات النشطة على الخريطة",
        "kpi_techs": "الفنيون في الميدان",
        "kpi_zones": "المناطق النشطة",
        "no_map_points": "لا توجد إحداثيات حالياً. يرجى رفع ملف يحتوي على أعمدة 'lat' و 'lon' من مركز المعلومات.",
        
        # AI Module
        "ai_title": "🤖 محرك التوزيع الذكي بالذكاء الاصطناعي",
        "ai_sub": "توزيع طلبات الخدمة فورياً على خط الفني الأنسب.",
        "dispatch_matcher": "🎯 مطابقة التوزيع",
        "ai_settings": "⚙️ تخصيص معايير وأوزان الذكاء الاصطناعي",
        "weight_zone": "أهمية مطابقة المنطقة الجغرافية",
        "weight_skill": "أهمية مطابقة التخصص والمهارة",
        "weight_cap": "مكافأة السعة الاستيعابية المتاحة",
        "select_zone": "اختر منطقة الخدمة / التوصيل",
        "select_skill": "التخصص أو المهارة المطلوبة",
        "run_match": "⚡ تشغيل مطابقة الذكاء الاصطناعي",
        "rec_tech": "الفني الموصى به",
        "match_score": "درجة المطابقة",
        "tech_capacity": "📋 خطوط الفنيين والسعة اليومية",
        "no_techs": "لا يوجد فنيون مسجلون. قم برفع بيانات الفنيين من مركز المعلومات.",
        "no_zones_opt": "لا توجد مناطق متاحة (برجاء رفع البيانات أولاً)",
        "no_skills_opt": "لا توجد مهارات متاحة (برجاء رفع البيانات أولاً)",

        # Logistics Module
        "logistics_title": "📦 مركز اللوجستيات والمخزون",
        "logistics_sub": "إدارة قطع الغيار، مستويات المخزون، وأماكن التخزين.",
        "low_stock_alert": "⚠️ تنبيه لوجستي: {count} أصناف وصلت أو تجاوزت حد إعادة الطلب الأدنى!",
        "inv_master": "قائمة المخزون الرئيسية",
        "save_stock": "💾 حفظ تغييرات المخزون",
        "stock_saved": "تم تحديث بيانات المخزون بنجاح!",

        # Info Hub Module
        "hub_title": "ℹ️ مركز المعلومات وبوابة الرفع",
        "hub_sub": "قم برفع ملفات CSV/Excel لبناء قاعدة بياناتك، أو قم بتعديل الطلبات في جدول تفاعلي.",
        "tab_upload": "📤 رفع البيانات (CSV/Excel)",
        "tab_editor": "📝 الطلبات النشطة (محرر إكسل)",
        "upload_sub": "رفع ملفات CSV أو Excel",
        "select_target": "اختر قاعدة البيانات المستهدفة",
        "target_techs": "قاعدة بيانات الفنيين",
        "target_orders": "قاعدة بيانات أوامر العمل",
        "target_inv": "قاعدة بيانات المخزون",
        "choose_file": "اختر ملف CSV أو Excel",
        "preview": "معاينة الملف المرفوع:",
        "confirm_import": "تأكيد استيراد البيانات",
        "import_success": "تم استيراد {count} سجل بنجاح!",
        "grid_sub": "جدول الطلبات التفاعلي (نمط إكسل)",
        "grid_desc": "تعديل حالة الطلب، بيانات العملاء، أو تعيين الفنيين مباشرة داخل الخلايا.",
        "save_orders": "💾 حفظ تغييرات الطلبات",
        "orders_saved": "تم تحديث الطلبات بنجاح!"
    }
}


# ==============================================================================
# 3. SESSION STATE INITIALIZATION (CLEAN EMPTY SLATE)
# ==============================================================================
def init_session_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "EN"

    # Clean Schemas (No sample rows)
    if "inventory_df" not in st.session_state:
        st.session_state.inventory_df = pd.DataFrame(columns=[
            "SKU", "Part Name", "Category", "Bin Location", "Stock Qty", "Min Threshold"
        ])

    if "technicians_df" not in st.session_state:
        st.session_state.technicians_df = pd.DataFrame(columns=[
            "Tech ID", "Name", "Assigned Zone", "Primary Skill", "Active Jobs", "Max Capacity", "lat", "lon"
        ])

    if "work_orders_df" not in st.session_state:
        st.session_state.work_orders_df = pd.DataFrame(columns=[
            "Ticket ID", "Client Name", "Appliance Issue", "Zone", "Assigned Tech", "Priority", "Status", "lat", "lon"
        ])

init_session_state()

def t(key):
    """Translation helper function."""
    lang = st.session_state.get("lang", "EN")
    return TRANSLATIONS[lang].get(key, key)


# ==============================================================================
# 4. CUSTOMIZABLE AI MATCHING ENGINE
# ==============================================================================
def smart_ai_dispatch(zone, skill, w_zone=40, w_skill=40, w_cap=20):
    techs = st.session_state.technicians_df.copy()
    if techs.empty:
        return "N/A", "N/A", 0
    
    scores = []
    for _, tech in techs.iterrows():
        score = 0.0
        
        # Zone match score
        if "Assigned Zone" in tech and pd.notnull(tech["Assigned Zone"]):
            if str(tech["Assigned Zone"]).strip().lower() == str(zone).strip().lower():
                score += float(w_zone)
        
        # Skill match score
        if "Primary Skill" in tech and pd.notnull(tech["Primary Skill"]):
            if str(skill).strip().lower() in str(tech["Primary Skill"]).strip().lower():
                score += float(w_skill)
        
        # Capacity availability score
        try:
            active = float(tech.get("Active Jobs", 0))
            max_cap = float(tech.get("Max Capacity", 5))
            if active < max_cap:
                # Proportional score based on available slots
                avail_ratio = (max_cap - active) / max_cap if max_cap > 0 else 0
                score += float(w_cap) * avail_ratio
        except:
            pass

        tech_name = tech.get("Name", "Unknown Tech") if pd.notnull(tech.get("Name")) else "Tech"
        tech_id = tech.get("Tech ID", "N/A") if pd.notnull(tech.get("Tech ID")) else "N/A"
        scores.append((tech_name, tech_id, score))

    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[0] if scores else ("N/A", "N/A", 0)


# ==============================================================================
# 5. SIDEBAR NAVIGATION & LANGUAGE TOGGLE
# ==============================================================================
st.sidebar.title(t("sidebar_title"))
st.sidebar.caption(t("sidebar_caption"))

# Language Switcher
selected_language = st.sidebar.selectbox(
    t("select_lang"),
    options=["English", "العربية"],
    index=0 if st.session_state.lang == "EN" else 1
)

st.session_state.lang = "EN" if selected_language == "English" else "AR"

st.sidebar.markdown("---")

nav_choice = st.sidebar.radio(
    t("select_module"),
    [
        t("mod_map"),
        t("mod_ai"),
        t("mod_logistics"),
        t("mod_hub")
    ]
)

st.sidebar.markdown("---")
if st.sidebar.button(t("reset_btn")):
    st.session_state.inventory_df = pd.DataFrame(columns=["SKU", "Part Name", "Category", "Bin Location", "Stock Qty", "Min Threshold"])
    st.session_state.technicians_df = pd.DataFrame(columns=["Tech ID", "Name", "Assigned Zone", "Primary Skill", "Active Jobs", "Max Capacity", "lat", "lon"])
    st.session_state.work_orders_df = pd.DataFrame(columns=["Ticket ID", "Client Name", "Appliance Issue", "Zone", "Assigned Tech", "Priority", "Status", "lat", "lon"])
    st.sidebar.success(t("reset_msg"))
    st.rerun()


# ==============================================================================
# MODULE 1: INTERACTIVE MAP
# ==============================================================================
if nav_choice == t("mod_map"):
    st.title(t("map_title"))
    st.markdown(t("map_sub"))

    # Safely compute KPI counts
    orders_count = len(st.session_state.work_orders_df)
    techs_count = len(st.session_state.technicians_df)
    
    active_zones_count = 0
    if not st.session_state.technicians_df.empty and "Assigned Zone" in st.session_state.technicians_df.columns:
        active_zones_count = st.session_state.technicians_df["Assigned Zone"].dropna().nunique()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">{t("kpi_orders")}</div><div class="kpi-value">{orders_count}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #10b981;"><div class="kpi-title">{t("kpi_techs")}</div><div class="kpi-value">{techs_count}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card" style="border-left-color: #8b5cf6;"><div class="kpi-title">{t("kpi_zones")}</div><div class="kpi-value">{active_zones_count}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Safely build map points
    map_points = []
    
    if not st.session_state.technicians_df.empty:
        for _, t_row in st.session_state.technicians_df.iterrows():
            if "lat" in t_row and "lon" in t_row:
                try:
                    lat, lon = float(t_row["lat"]), float(t_row["lon"])
                    if not (np.isnan(lat) or np.isnan(lon)):
                        map_points.append({"lat": lat, "lon": lon})
                except: pass

    if not st.session_state.work_orders_df.empty:
        for _, w_row in st.session_state.work_orders_df.iterrows():
            if "lat" in w_row and "lon" in w_row:
                try:
                    lat, lon = float(w_row["lat"]), float(w_row["lon"])
                    if not (np.isnan(lat) or np.isnan(lon)):
                        map_points.append({"lat": lat, "lon": lon})
                except: pass

    if map_points:
        st.map(pd.DataFrame(map_points), latitude="lat", longitude="lon", size=20)
    else:
        st.info(t("no_map_points"))


# ==============================================================================
# MODULE 2: AI-POWERED DISTRIBUTOR (WITH CUSTOMIZABLE WEIGHTS)
# ==============================================================================
elif nav_choice == t("mod_ai"):
    st.title(t("ai_title"))
    st.markdown(t("ai_sub"))

    # Customizable AI Parameters Expander
    with st.expander(t("ai_settings"), expanded=True):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            w_zone = st.slider(t("weight_zone"), 0, 100, 40)
        with sc2:
            w_skill = st.slider(t("weight_skill"), 0, 100, 40)
        with sc3:
            w_cap = st.slider(t("weight_cap"), 0, 100, 20)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(t("dispatch_matcher"))
        
        # Populate available zones safely
        zones_list = []
        if not st.session_state.technicians_df.empty and "Assigned Zone" in st.session_state.technicians_df.columns:
            zones_list = [str(z).strip() for z in st.session_state.technicians_df["Assigned Zone"].dropna().unique() if str(z).strip()]
        
        if not zones_list:
            zones_list = [t("no_zones_opt")]

        # Populate available skills safely
        skills_list = []
        if not st.session_state.technicians_df.empty and "Primary Skill" in st.session_state.technicians_df.columns:
            skills_list = [str(s).strip() for s in st.session_state.technicians_df["Primary Skill"].dropna().unique() if str(s).strip()]
        
        if not skills_list:
            skills_list = [t("no_skills_opt")]

        sel_zone = st.selectbox(t("select_zone"), zones_list)
        sel_skill = st.selectbox(t("select_skill"), skills_list)
        
        if st.button(t("run_match")):
            if st.session_state.technicians_df.empty:
                st.warning(t("no_techs"))
            else:
                best_tech, tech_id, score = smart_ai_dispatch(sel_zone, sel_skill, w_zone, w_skill, w_cap)
                if best_tech != "N/A":
                    st.success(f"**{t('rec_tech')}:** {best_tech} ({tech_id})")
                    st.info(f"**{t('match_score')}:** {score:.0f} points")
                else:
                    st.warning(t("no_techs"))

    with col2:
        st.subheader(t("tech_capacity"))
        if not st.session_state.technicians_df.empty:
            st.dataframe(st.session_state.technicians_df, use_container_width=True, hide_index=True)
        else:
            st.info(t("no_techs"))


# ==============================================================================
# MODULE 3: LOGISTICS CENTER
# ==============================================================================
elif nav_choice == t("mod_logistics"):
    st.title(t("logistics_title"))
    st.markdown(t("logistics_sub"))

    # Safely check low stock
    if not st.session_state.inventory_df.empty and "Stock Qty" in st.session_state.inventory_df.columns and "Min Threshold" in st.session_state.inventory_df.columns:
        try:
            stock_q = pd.to_numeric(st.session_state.inventory_df["Stock Qty"], errors='coerce')
            min_t = pd.to_numeric(st.session_state.inventory_df["Min Threshold"], errors='coerce')
            low_stock = st.session_state.inventory_df[stock_q <= min_t]
            if not low_stock.empty:
                st.warning(t("low_stock_alert").format(count=len(low_stock)))
        except: pass

    st.subheader(t("inv_master"))
    
    edited_inv = st.data_editor(
        st.session_state.inventory_df,
        use_container_width=True,
        num_rows="dynamic"
    )
    
    if st.button(t("save_stock")):
        st.session_state.inventory_df = edited_inv
        st.success(t("stock_saved"))


# ==============================================================================
# MODULE 4: CENTRAL INFO HUB
# ==============================================================================
elif nav_choice == t("mod_hub"):
    st.title(t("hub_title"))
    st.markdown(t("hub_sub"))

    tab1, tab2 = st.tabs([t("tab_upload"), t("tab_editor")])

    with tab1:
        st.subheader(t("upload_sub"))
        
        target_dataset = st.selectbox(
            t("select_target"),
            [t("target_techs"), t("target_orders"), t("target_inv")]
        )
        
        uploaded_file = st.file_uploader(t("choose_file"), type=["csv", "xlsx"])

        if uploaded_file:
            try:
                df_up = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.write(t("preview"), df_up.head())
                
                if st.button(t("confirm_import")):
                    if target_dataset == t("target_techs"):
                        st.session_state.technicians_df = pd.concat([st.session_state.technicians_df, df_up], ignore_index=True)
                    elif target_dataset == t("target_orders"):
                        st.session_state.work_orders_df = pd.concat([st.session_state.work_orders_df, df_up], ignore_index=True)
                    elif target_dataset == t("target_inv"):
                        st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, df_up], ignore_index=True)
                    
                    st.success(t("import_success").format(count=len(df_up)))
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

    with tab2:
        st.subheader(t("grid_sub"))
        st.markdown(t("grid_desc"))
        
        edited_orders = st.data_editor(
            st.session_state.work_orders_df,
            use_container_width=True,
            num_rows="dynamic"
        )
        
        if st.button(t("save_orders")):
            st.session_state.work_orders_df = edited_orders
            st.success(t("orders_saved"))
