import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# ==============================================================================
# 1. APP CONFIGURATION & STYLES
# ==============================================================================
st.set_page_config(
    page_title="Mirage AI Distribution & Logistics Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
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
        "mod_map": "🗺️ Interactive Map & Routes",
        "mod_ai": "🤖 AI-Powered Distributor",
        "mod_logistics": "📦 Logistics Center",
        "mod_hub": "ℹ️ Central Info Hub",
        "reset_btn": "🗑️ Clear All Database Records",
        "reset_msg": "Database wiped clean!",
        
        # Map Module
        "map_title": "🗺️ Geographic Dispatch & Route Line Map",
        "map_sub": "Visual map rendering dynamic dispatch lines connecting technicians to their active work orders.",
        "kpi_orders": "Active Orders Mapped",
        "kpi_techs": "Technicians in Field",
        "kpi_zones": "Active Zones",
        "no_map_points": "No coordinates available yet. Upload data containing 'lat' and 'lon' columns in the Central Info Hub.",
        "map_legend": "🔵 Cyan Pins: Technicians | 🟠 Orange Pins: Work Orders | ⚡ Lines: Active Dispatch Connections",

        # AI Module
        "ai_title": "🤖 AI-Powered Smart Dispatch Engine",
        "ai_sub": "Instantly distribute incoming work orders to the optimal technician line with dynamic route visualization.",
        "dispatch_matcher": "🎯 Dispatch Matcher",
        "ai_settings": "⚙️ Customize AI Priority Weights",
        "weight_zone": "Zone Match Importance",
        "weight_skill": "Skill Match Importance",
        "weight_cap": "Capacity Availability Bonus",
        "select_order": "Select Work Order to Dispatch",
        "select_zone": "Select Delivery / Service Zone",
        "select_skill": "Required Specialty / Skill",
        "run_match": "⚡ Run AI Dispatch Match",
        "rec_tech": "Recommended Technician",
        "match_score": "AI Match Score",
        "assign_btn": "⚡ Confirm & Assign to Technician Line",
        "assign_success": "Work order successfully assigned to {tech}!",
        "dispatch_vis": "📍 Target Dispatch Line Preview",
        "tech_capacity": "📋 Technician Lines & Capacity",
        "no_techs": "No technician records found. Upload technician data in the Central Info Hub.",
        "no_orders_to_dispatch": "No unassigned work orders available.",
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
        "mod_map": "🗺️ الخريطة التفاعلية والمسارات",
        "mod_ai": "🤖 الموزع الذكي بالذكاء الاصطناعي",
        "mod_logistics": "📦 مركز اللوجستيات",
        "mod_hub": "ℹ️ مركز المعلومات والرفع",
        "reset_btn": "🗑️ مسح كافة بيانات قاعدة البيانات",
        "reset_msg": "تم مسح جميع البيانات بنجاح!",
        
        # Map Module
        "map_title": "🗺️ خريطة التوزيع الميداني وخطوط المسارات",
        "map_sub": "عرض تفاعلي ثلاثي الأبعاد لخطوط التوصيل التي تربط الفنيين بالطلبات المسندة إليهم.",
        "kpi_orders": "الطلبات النشطة على الخريطة",
        "kpi_techs": "الفنيون في الميدان",
        "kpi_zones": "المناطق النشطة",
        "no_map_points": "لا توجد إحداثيات حالياً. يرجى رفع ملف يحتوي على أعمدة 'lat' و 'lon' من مركز المعلومات.",
        "map_legend": "🔵 نقاط سماوية: الفنيون | 🟠 نقاط برتقالية: أوامر العمل | ⚡ الخطوط: مسارات التوزيع النشطة",

        # AI Module
        "ai_title": "🤖 محرك التوزيع الذكي بالذكاء الاصطناعي",
        "ai_sub": "توزيع طلبات الخدمة فورياً على خط الفني الأنسب مع معاينة مرئية للمسار.",
        "dispatch_matcher": "🎯 مطابقة التوزيع",
        "ai_settings": "⚙️ تخصيص معايير وأوزان الذكاء الاصطناعي",
        "weight_zone": "أهمية مطابقة المنطقة الجغرافية",
        "weight_skill": "أهمية مطابقة التخصص والمهارة",
        "weight_cap": "مكافأة السعة الاستيعابية المتاحة",
        "select_order": "اختر امر العمل للتوزيع",
        "select_zone": "اختر منطقة الخدمة / التوصيل",
        "select_skill": "التخصص أو المهارة المطلوبة",
        "run_match": "⚡ تشغيل مطابقة الذكاء الاصطناعي",
        "rec_tech": "الفني الموصى به",
        "match_score": "درجة المطابقة",
        "assign_btn": "⚡ تأكيد وتعيين إلى خط الفني",
        "assign_success": "تم إسناد أوردر العمل بنجاح إلى الفني {tech}!",
        "dispatch_vis": "📍 معاينة خط مسار التوزيع المستهدف",
        "tech_capacity": "📋 خطوط الفنيين والسعة اليومية",
        "no_techs": "لا يوجد فنيون مسجلون. قم برفع بيانات الفنيين من مركز المعلومات.",
        "no_orders_to_dispatch": "لا توجد أوامر عمل غير مسندة حالياً.",
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

# Neon Color Palette for Technicians
TECH_COLORS = [
    [59, 130, 246],   # Electric Blue
    [16, 185, 129],   # Emerald Green
    [168, 85, 247],   # Purple
    [236, 72, 153],   # Pink
    [245, 158, 11],   # Amber
    [14, 165, 233],   # Sky Blue
]


# ==============================================================================
# 3. SESSION STATE INITIALIZATION (CLEAN SLATE)
# ==============================================================================
def init_session_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "EN"

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
        return None, "N/A", 0
    
    scores = []
    for _, tech in techs.iterrows():
        score = 0.0
        
        # Zone match
        if "Assigned Zone" in tech and pd.notnull(tech["Assigned Zone"]):
            if str(tech["Assigned Zone"]).strip().lower() == str(zone).strip().lower():
                score += float(w_zone)
        
        # Skill match
        if "Primary Skill" in tech and pd.notnull(tech["Primary Skill"]):
            if str(skill).strip().lower() in str(tech["Primary Skill"]).strip().lower():
                score += float(w_skill)
        
        # Capacity bonus
        try:
            active = float(tech.get("Active Jobs", 0))
            max_cap = float(tech.get("Max Capacity", 5))
            if active < max_cap:
                avail_ratio = (max_cap - active) / max_cap if max_cap > 0 else 0
                score += float(w_cap) * avail_ratio
        except:
            pass

        tech_name = tech.get("Name", "Unknown Tech") if pd.notnull(tech.get("Name")) else "Tech"
        tech_id = tech.get("Tech ID", "N/A") if pd.notnull(tech.get("Tech ID")) else "N/A"
        scores.append((tech, tech_name, tech_id, score))

    scores.sort(key=lambda x: x[3], reverse=True)
    return scores[0] if scores else (None, "N/A", 0)


# ==============================================================================
# 5. PYDECK MAP BUILDER (LINES & ROUTE CONNECTIONS)
# ==============================================================================
def render_route_map(focused_line=None):
    techs_df = st.session_state.technicians_df.copy()
    orders_df = st.session_state.work_orders_df.copy()

    # Clean numeric coordinates
    tech_points = []
    if not techs_df.empty:
        for idx, t_row in techs_df.iterrows():
            try:
                lat, lon = float(t_row["lat"]), float(t_row["lon"])
                if not (np.isnan(lat) or np.isnan(lon)):
                    color = TECH_COLORS[idx % len(TECH_COLORS)]
                    tech_points.append({
                        "name": str(t_row.get("Name", "Tech")),
                        "id": str(t_row.get("Tech ID", "N/A")),
                        "lat": lat,
                        "lon": lon,
                        "color": color
                    })
            except: pass

    order_points = []
    lines = []
    
    if not orders_df.empty:
        for idx, w_row in orders_df.iterrows():
            try:
                w_lat, w_lon = float(w_row["lat"]), float(w_row["lon"])
                if not (np.isnan(w_lat) or np.isnan(w_lon)):
                    assigned_tech = str(w_row.get("Assigned Tech", "")).strip()
                    
                    # Find matching technician to draw line
                    matched_tech = next((tp for tp in tech_points if tp["name"].strip().lower() == assigned_tech.lower() or tp["id"].strip().lower() == assigned_tech.lower()), None)
                    
                    line_color = matched_tech["color"] if matched_tech else [245, 158, 11] # Orange for unassigned
                    
                    order_points.append({
                        "ticket": str(w_row.get("Ticket ID", "WO")),
                        "client": str(w_row.get("Client Name", "Client")),
                        "lat": w_lat,
                        "lon": w_lon,
                        "assigned": assigned_tech or "Unassigned",
                        "color": line_color
                    })

                    if matched_tech:
                        lines.append({
                            "from_name": matched_tech["name"],
                            "to_ticket": str(w_row.get("Ticket ID", "WO")),
                            "start": [matched_tech["lon"], matched_tech["lat"]],
                            "end": [w_lon, w_lat],
                            "color": matched_tech["color"]
                        })
            except: pass

    # If single focused line preview from AI Dispatch
    if focused_line:
        lines.append(focused_line)

    all_lats = [p["lat"] for p in tech_points + order_points]
    all_lons = [p["lon"] for p in tech_points + order_points]
    
    center_lat = np.mean(all_lats) if all_lats else 30.0444
    center_lon = np.mean(all_lons) if all_lons else 31.2357

    # Pydeck Layers
    layers = []

    # 1. Dispatch Connection Lines Layer
    if lines:
        layers.append(
            pdk.Layer(
                "LineLayer",
                data=lines,
                get_source_position="start",
                get_target_position="end",
                get_color="color",
                get_width=5,
                pickable=True
            )
        )

    # 2. Technician Pins Layer (Cyan/Blue Rings)
    if tech_points:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=tech_points,
                get_position=["lon", "lat"],
                get_color="color",
                get_radius=300,
                pickable=True
            )
        )

    # 3. Work Order Pins Layer (Orange Rings)
    if order_points:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=order_points,
                get_position=["lon", "lat"],
                get_color="color",
                get_radius=180,
                pickable=True
            )
        )

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=11,
        pitch=35
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={"text": "{name}{ticket} ({assigned})\nLat: {lat}, Lon: {lon}"},
            map_style="mapbox://styles/mapbox/dark-v11"
        )
    )


# ==============================================================================
# 6. SIDEBAR NAVIGATION & LANGUAGE TOGGLE
# ==============================================================================
st.sidebar.title(t("sidebar_title"))
st.sidebar.caption(t("sidebar_caption"))

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
# MODULE 1: INTERACTIVE MAP & ROUTE LINES
# ==============================================================================
if nav_choice == t("mod_map"):
    st.title(t("map_title"))
    st.markdown(t("map_sub"))

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
    st.caption(t("map_legend"))

    if techs_count == 0 and orders_count == 0:
        st.info(t("no_map_points"))
    else:
        render_route_map()


# ==============================================================================
# MODULE 2: AI-POWERED DISTRIBUTOR (WITH DYNAMIC DISPATCH VISUALIZER)
# ==============================================================================
elif nav_choice == t("mod_ai"):
    st.title(t("ai_title"))
    st.markdown(t("ai_sub"))

    with st.expander(t("ai_settings"), expanded=False):
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
        
        # Select target order if present
        target_ticket = None
        target_order_row = None
        if not st.session_state.work_orders_df.empty and "Ticket ID" in st.session_state.work_orders_df.columns:
            order_opts = st.session_state.work_orders_df["Ticket ID"].dropna().unique().tolist()
            if order_opts:
                target_ticket = st.selectbox(t("select_order"), order_opts)
                target_order_row = st.session_state.work_orders_df[st.session_state.work_orders_df["Ticket ID"] == target_ticket].iloc[0]

        # Select zone & skill
        zones_list = []
        if not st.session_state.technicians_df.empty and "Assigned Zone" in st.session_state.technicians_df.columns:
            zones_list = [str(z).strip() for z in st.session_state.technicians_df["Assigned Zone"].dropna().unique() if str(z).strip()]
        if not zones_list: zones_list = [t("no_zones_opt")]

        skills_list = []
        if not st.session_state.technicians_df.empty and "Primary Skill" in st.session_state.technicians_df.columns:
            skills_list = [str(s).strip() for s in st.session_state.technicians_df["Primary Skill"].dropna().unique() if str(s).strip()]
        if not skills_list: skills_list = [t("no_skills_opt")]

        sel_zone = st.selectbox(t("select_zone"), zones_list, index=0)
        sel_skill = st.selectbox(t("select_skill"), skills_list, index=0)
        
        if st.button(t("run_match")):
            if st.session_state.technicians_df.empty:
                st.warning(t("no_techs"))
            else:
                tech_row, best_tech, tech_id, score = smart_ai_dispatch(sel_zone, sel_skill, w_zone, w_skill, w_cap)
                if best_tech != "N/A":
                    st.success(f"**{t('rec_tech')}:** {best_tech} ({tech_id})")
                    st.info(f"**{t('match_score')}:** {score:.0f} points")
                    
                    # Confirm dispatch assignment button
                    if target_ticket and st.button(t("assign_btn")):
                        st.session_state.work_orders_df.loc[
                            st.session_state.work_orders_df["Ticket ID"] == target_ticket, "Assigned Tech"
                        ] = best_tech
                        
                        # Increment active jobs count
                        st.session_state.technicians_df.loc[
                            st.session_state.technicians_df["Name"] == best_tech, "Active Jobs"
                        ] = pd.to_numeric(tech_row.get("Active Jobs", 0), errors='coerce') + 1

                        st.success(t("assign_success").format(tech=best_tech))
                        st.rerun()

                    # Render dispatch connection line preview
                    if target_order_row is not None and tech_row is not None:
                        try:
                            t_lat, t_lon = float(tech_row["lat"]), float(tech_row["lon"])
                            o_lat, o_lon = float(target_order_row["lat"]), float(target_order_row["lon"])
                            
                            focused_line = {
                                "from_name": best_tech,
                                "to_ticket": target_ticket,
                                "start": [t_lon, t_lat],
                                "end": [o_lon, o_lat],
                                "color": [239, 68, 68] # Bright Red
                            }
                            st.subheader(t("dispatch_vis"))
                            render_route_map(focused_line=focused_line)
                        except: pass
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

    if not st.session_state.inventory_df.empty and "Stock Qty" in st.session_state.inventory_df.columns and "Min Threshold" in st.session_state.inventory_df.columns:
        try:
            stock_q = pd.to_numeric(st.session_state.inventory_df["Stock Qty"], errors='coerce')
            min_t = pd.to_numeric(st.session_state.inventory_df["Min Threshold"], errors='coerce')
            low_stock = st.session_state.inventory_df[stock_q <= min_t]
            if not low_stock.empty:
                st.warning(t("low_stock_alert").format(count=len(low_stock)))
        except: pass

    st.subheader(t("inv_master"))
    edited_inv = st.data_editor(st.session_state.inventory_df, use_container_width=True, num_rows="dynamic")
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
