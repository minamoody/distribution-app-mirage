import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & GLOBAL SETUP
# ==========================================
st.set_page_config(
    page_title="Mirage Enterprise ERP & Distribution System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 2. LOCALIZATION / MULTI-LANGUAGE SYSTEM
# ==========================================
TRANSLATIONS = {
    "English": {
        "app_title": "Mirage Logistics & Enterprise Resource Planning",
        "app_subtitle": "Distribution, Inventory, Order Fulfillment & Analytics Engine",
        "nav_label": "Select Module Navigation",
        "nav_overview": "🚀 Executive Command Center",
        "nav_inventory": "📊 Inventory Control & Stock Audit",
        "nav_orders": "🚚 Dispatch, Orders & Fulfillment",
        "nav_customers": "👥 Client & Branch Directory",
        "nav_analytics": "📈 Advanced Analytics & Financials",
        "nav_data": "⚙️ Data Management & Settings",
        "language_select": "🌐 Language / اللّغة",
        "theme_select": "🎨 Theme Accent",
        "system_controls": "System Maintenance",
        "reset_btn": "🗑️ Reset System Data",
        "reset_confirm": "Are you sure you want to restore factory default state?",
        "reset_success": "Database reset to baseline state successfully!",
        "currency_symbol": "$",
        "search_ph": "Search by keyword, SKU, ID, or name...",
        "save_changes": "💾 Commit & Save Changes",
        "save_success": "Changes persisted successfully across session state!",
        "export_csv": "📥 Export CSV",
        "export_json": "📥 Export JSON",
        # Modules
        "kpi_total_val": "Total Stock Asset Value",
        "kpi_total_cost": "Total Asset Cost Basis",
        "kpi_net_margin": "Potential Gross Profit",
        "kpi_low_stock": "Stock Alert Thresholds",
        "kpi_active_orders": "Active Operational Shipments",
        "kpi_completed_orders": "Fulfilling Orders (Completed)",
        "tab_live_stock": "Live Inventory Registry",
        "tab_add_item": "Single Item Provisioning",
        "tab_bulk_upload": "Batch CSV/JSON Import",
        "tab_restock": "Automated Reorder Planning",
        "sku": "SKU Code",
        "product_name": "Product Description",
        "category": "Category",
        "warehouse_loc": "Warehouse Bin Location",
        "stock_qty": "Current Quantity",
        "reorder_pt": "Reorder Point",
        "unit_cost": "Unit Cost ($)",
        "unit_price": "Unit Price ($)",
        "margin_pct": "Margin (%)",
        "stock_status": "Stock Status",
        "status_ok": "Sufficient",
        "status_low": "Low Stock Alert",
        "status_critical": "Critical Shortage",
        "actions": "Operational Actions",
        "order_id": "Order Ref ID",
        "customer_name": "Client / Branch Entity",
        "dest_zone": "Fulfillment Zone",
        "payment_type": "Payment Method",
        "order_status": "Fulfillment State",
        "driver_assigned": "Assigned Logistics Carrier",
        "order_date": "Timestamp",
        "total_val": "Total Order Value",
        "create_order": "Book Shipment Order",
        "zone_distribution": "Regional Volume Summary",
        "analytics_title": "Logistics & Inventory Intelligence",
        "financial_summary": "Financial Performance & Profit Margins",
        "download_section": "System Data Extraction Portal",
    },
    "Arabic (العربية)": {
        "app_title": "منظومة ميراج لإدارة التوزيع والتخطيط المؤسسي",
        "app_subtitle": "المحرك المركزي لإدارة المخزون، الطلبات، اللوجستيات والتحليلات",
        "nav_label": "اختر الوحدة التشغيلية",
        "nav_overview": "🚀 لوحة التحكم التنفيذية",
        "nav_inventory": "📊 مراقبة المخزون وتدقيق المنتجات",
        "nav_orders": "🚚 إدارة الطلبات والشحن والتوزيع",
        "nav_customers": "👥 دليل العملاء والفروع",
        "nav_analytics": "📈 التحليلات المتقدمة والتقارير المالية",
        "nav_data": "⚙️ إدارة البيانات والإعدادات",
        "language_select": "🌐 Language / اللّغة",
        "theme_select": "🎨 نسق الألوان",
        "system_controls": "صيانة النظام",
        "reset_btn": "🗑️ إعادة ضبط بيانات النظام",
        "reset_confirm": "هل أنت أصلًا متأكد من استعادة الحالة الافتراضية للبيانات؟",
        "reset_success": "تمت إعادة ضبط قاعدة البيانات بنجاح!",
        "currency_symbol": "ج.م",
        "search_ph": "ابحث بالرمز أو الرقم المرجعي أو الاسم...",
        "save_changes": "💾 حفظ وحفظ التغييرات",
        "save_success": "تم حفظ التغييرات بنجاح في الجلسة!",
        "export_csv": "📥 تصدير CSV",
        "export_json": "📥 تصدير JSON",
        # Modules
        "kpi_total_val": "القيمة الإجمالية للمخزون",
        "kpi_total_cost": "التكلفة الإجمالية للأصول",
        "kpi_net_margin": "هامش الربح المتوقع",
        "kpi_low_stock": "تنبيهات نقص المخزون",
        "kpi_active_orders": "الطلبات النشطة جاري شحنها",
        "kpi_completed_orders": "الطلبات المكتملة التسليم",
        "tab_live_stock": "سجل المخزون المباشر",
        "tab_add_item": "إضافة منتج جديد",
        "tab_bulk_upload": "رفع جماعي (CSV/JSON)",
        "tab_restock": "تخطيط إعادة الطلب التلقائي",
        "sku": "رمز SKU",
        "product_name": "وصف المنتج",
        "category": "الفئة",
        "warehouse_loc": "موقع التخزين (المستودع)",
        "stock_qty": "الكمية المتاحة",
        "reorder_pt": "حد إعادة الطلب",
        "unit_cost": "تكلفة الوحدة",
        "unit_price": "سعر البيع للوحدة",
        "margin_pct": "نسبة الهامش (%)",
        "stock_status": "حالة المخزون",
        "status_ok": "مستقر",
        "status_low": "منخفض",
        "status_critical": "نقص حرج",
        "actions": "إجراءات تشغيلية",
        "order_id": "رقم الشحنة المرجعي",
        "customer_name": "العميل / الفرع",
        "dest_zone": "منطقة التوزيع",
        "payment_type": "طريقة الدفع",
        "order_status": "حالة التنفيذ",
        "driver_assigned": "السائق / مندوب الشحن",
        "order_date": "التاريخ والوقت",
        "total_val": "الإجمالي",
        "create_order": "تأكيد وإنشاء طلب شحن",
        "zone_distribution": "ملخص التوزيع الجغرافي",
        "analytics_title": "ذكاء اللوجستيات والمخزون",
        "financial_summary": "الأداء المالي وهوامش الأرباح",
        "download_section": "بوابة استخراج وتقارير البيانات",
    },
    "French (Français)": {
        "app_title": "Système de Gestion Mirage ERP & Distribution",
        "app_subtitle": "Plateforme Centrale Logistique, Inventaire & Commandes",
        "nav_label": "Sélectionner un module",
        "nav_overview": "🚀 Tableau de Bord Exécutif",
        "nav_inventory": "📊 Contrôle des Stocks & Audit",
        "nav_orders": "🚚 Expéditions, Commandes & Livraisons",
        "nav_customers": "👥 Répertoire Clients & Succursales",
        "nav_analytics": "📈 Analyses Avancées & Finances",
        "nav_data": "⚙️ Gestion des Données & Paramètres",
        "language_select": "🌐 Langue / Language",
        "theme_select": "🎨 Thème Visuel",
        "system_controls": "Maintenance du Système",
        "reset_btn": "🗑️ Réinitialiser les Données",
        "reset_confirm": "Êtes-vous sûr de vouloir tout réinitialiser ?",
        "reset_success": "Base de données réinitialisée avec succès !",
        "currency_symbol": "€",
        "search_ph": "Rechercher par référence, SKU ou nom...",
        "save_changes": "💾 Enregistrer les Modifications",
        "save_success": "Modifications enregistrées avec succès !",
        "export_csv": "📥 Exporter CSV",
        "export_json": "📥 Exporter JSON",
        # Modules
        "kpi_total_val": "Valeur Totale du Stock",
        "kpi_total_cost": "Coût Total des Actifs",
        "kpi_net_margin": "Marge Brute Projetée",
        "kpi_low_stock": "Alertes de Réapprovisionnement",
        "kpi_active_orders": "Expéditions en Cours",
        "kpi_completed_orders": "Commandes Livrées",
        "tab_live_stock": "Inventaire en Direct",
        "tab_add_item": "Ajouter un Produit",
        "tab_bulk_upload": "Importation en Masse (CSV)",
        "tab_restock": "Planification Automatique",
        "sku": "Code SKU",
        "product_name": "Description du Produit",
        "category": "Catégorie",
        "warehouse_loc": "Emplacement Entrepôt",
        "stock_qty": "Quantité en Stock",
        "reorder_pt": "Seuil de Commande",
        "unit_cost": "Coût Unitaire",
        "unit_price": "Prix Unitaire",
        "margin_pct": "Marge (%)",
        "stock_status": "Statut du Stock",
        "status_ok": "Suffisant",
        "status_low": "Stock Bas",
        "status_critical": "Rupture Critique",
        "actions": "Actions Opérationnelles",
        "order_id": "Réf. Commande",
        "customer_name": "Client / Succursale",
        "dest_zone": "Zone de Livraison",
        "payment_type": "Mode de Paiement",
        "order_status": "Statut de Livraison",
        "driver_assigned": "Chauffeur Assigné",
        "order_date": "Horodatage",
        "total_val": "Valeur Totale",
        "create_order": "Créer la Commande",
        "zone_distribution": "Répartition Régionale",
        "analytics_title": "Intelligence Logistique & Stock",
        "financial_summary": "Performance Financière & Marges",
        "download_section": "Portail d'Exportation des Données",
    },
    "German (Deutsch)": {
        "app_title": "Mirage Enterprise ERP & Logistiksystem",
        "app_subtitle": "Zentrale Plattform für Bestandsführung & Auftragsabwicklung",
        "nav_label": "Modul Navigation Auswählen",
        "nav_overview": "🚀 Übersicht & Dashboard",
        "nav_inventory": "📊 Lagerbestand & Prüfung",
        "nav_orders": "🚚 Versand, Aufträge & Abwicklung",
        "nav_customers": "👥 Kunden- & Filialverzeichnis",
        "nav_analytics": "📈 Analysen & Finanzberichte",
        "nav_data": "⚙️ Datenverwaltung & Einstellungen",
        "language_select": "🌐 Sprache / Language",
        "theme_select": "🎨 Farbthema",
        "system_controls": "Systemwartung",
        "reset_btn": "🗑️ Systemdaten Zurücksetzen",
        "reset_confirm": "Möchten Sie wirklich alle Daten zurücksetzen?",
        "reset_success": "Datenbank erfolgreich zurückgesetzt!",
        "currency_symbol": "€",
        "search_ph": "Suchen nach SKU, Name oder ID...",
        "save_changes": "💾 Änderungen Speichern",
        "save_success": "Änderungen erfolgreich gespeichert!",
        "export_csv": "📥 CSV Exportieren",
        "export_json": "📥 JSON Exportieren",
        # Modules
        "kpi_total_val": "Gesamter Lagerwert",
        "kpi_total_cost": "Gesamtkostenbasis",
        "kpi_net_margin": "Prognostizierter Gewinn",
        "kpi_low_stock": "Nachbestell-Warnungen",
        "kpi_active_orders": "Aktive Lieferungen",
        "kpi_completed_orders": "Abgeschlossene Aufträge",
        "tab_live_stock": "Echtzeit-Lagerbestand",
        "tab_add_item": "Artikel Hinzufügen",
        "tab_bulk_upload": "Massen-Import (CSV)",
        "tab_restock": "Automatisierte Nachbestellung",
        "sku": "SKU-Code",
        "product_name": "Produktbezeichnung",
        "category": "Kategorie",
        "warehouse_loc": "Lagerplatz",
        "stock_qty": "Bestandsmenge",
        "reorder_pt": "Meldebestand",
        "unit_cost": "Stückkosten",
        "unit_price": "Verkaufspreis",
        "margin_pct": "Marge (%)",
        "stock_status": "Lagerstatus",
        "status_ok": "Ausreichend",
        "status_low": "Niedriger Bestand",
        "status_critical": "Kritischer Engpass",
        "actions": "Aktionen",
        "order_id": "Auftrags-ID",
        "customer_name": "Kunde / Filiale",
        "dest_zone": "Lieferzone",
        "payment_type": "Zahlungsart",
        "order_status": "Auftragsstatus",
        "driver_assigned": "Zugeordneter Fahrer",
        "order_date": "Zeitstempel",
        "total_val": "Gesamtwert",
        "create_order": "Auftrag Erstellen",
        "zone_distribution": "Regionale Verteilung",
        "analytics_title": "Logistik & Bestand Intelligence",
        "financial_summary": "Finanzielle Leistung & Margen",
        "download_section": "Datenexport-Portal",
    }
}

# Language selection persistent state
if "lang" not in st.session_state:
    st.session_state.lang = "English"

def t(key):
    """Retrieve translated string safely with English fallback."""
    return TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["English"]).get(key, key)

# Dynamic Language Selector in Top Sidebar
st.sidebar.markdown("### 🌐 Localization Settings")
selected_language = st.sidebar.selectbox(
    t("language_select"),
    options=list(TRANSLATIONS.keys()),
    index=list(TRANSLATIONS.keys()).index(st.session_state.lang),
    key="lang_selector",
)
if selected_language != st.session_state.lang:
    st.session_state.lang = selected_language
    st.rerun()

# Dynamic Direction (RTL support for Arabic)
is_rtl = st.session_state.lang == "Arabic (العربية)"
direction_css = "rtl" if is_rtl else "ltr"
text_align_css = "right" if is_rtl else "left"

# ==========================================
# 3. ADVANCED CUSTOM STYLING (SAFE STRINGS)
# ==========================================
st.markdown(
    f"""
<style>
    body {{
        direction: {direction_css};
        text-align: {text_align_css};
    }}
    
    /* Sleek Custom Scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: #0e1117;
    }}
    ::-webkit-scrollbar-thumb {{
        background: #262730;
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: #363945;
    }}

    /* Card Metrics Styling */
    div[data-testid="stMetricValue"] {{
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }}
    
    .stMetric {{
        background-color: #1a1d24;
        padding: 16px 22px;
        border-radius: 12px;
        border: 1px solid #2e323d;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}

    /* Table & Dataframe Polishing */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
    }}

    /* Alert Badge Accent */
    .badge-ok {{
        background-color: #1c3b2b;
        color: #4ade80;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }}
    .badge-low {{
        background-color: #423115;
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }}
    .badge-critical {{
        background-color: #451a1a;
        color: #f87171;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }}
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4. ROBUST DATA INITIALIZATION & SEED
# ==========================================
def get_initial_inventory():
    return pd.DataFrame([
        {"SKU": "MRG-101", "Product Name": "Arabica Whole Beans 1kg", "Category": "Coffee", "Warehouse Bin": "A-01-02", "Stock Level": 120, "Reorder Point": 30, "Unit Cost ($)": 14.50, "Selling Price ($)": 24.00},
        {"SKU": "MRG-102", "Product Name": "Zero-Sugar Vanilla Syrup 750ml", "Category": "Syrups", "Warehouse Bin": "B-03-01", "Stock Level": 18, "Reorder Point": 25, "Unit Cost ($)": 6.20, "Selling Price ($)": 12.50},
        {"SKU": "MRG-103", "Product Name": "Spanish Latte Base Mix 1kg", "Category": "Mixes", "Warehouse Bin": "A-02-04", "Stock Level": 200, "Reorder Point": 50, "Unit Cost ($)": 11.00, "Selling Price ($)": 19.50},
        {"SKU": "MRG-104", "Product Name": "Barista Almond Milk 1L", "Category": "Dairy/Alt", "Warehouse Bin": "C-01-05", "Stock Level": 12, "Reorder Point": 40, "Unit Cost ($)": 2.10, "Selling Price ($)": 4.50},
        {"SKU": "MRG-105", "Product Name": "Eco-Friendly Cups 12oz (Box 500)", "Category": "Packaging", "Warehouse Bin": "D-04-02", "Stock Level": 450, "Reorder Point": 100, "Unit Cost ($)": 22.00, "Selling Price ($)": 38.00},
        {"SKU": "MRG-106", "Product Name": "Espresso Machine Cleaning Powder", "Category": "Supplies", "Warehouse Bin": "E-02-01", "Stock Level": 8, "Reorder Point": 15, "Unit Cost ($)": 8.50, "Selling Price ($)": 16.00},
    ])

def get_initial_orders():
    now = datetime.now()
    return pd.DataFrame([
        {"Order ID": "ORD-2026-101", "Client / Branch": "Maadi Flagship Branch", "Zone": "Maadi", "SKU": "MRG-101", "Item Name": "Arabica Whole Beans 1kg", "Quantity": 20, "Total Value ($)": 480.0, "Payment Terms": "Credit (30 Days)", "Status": "Out for Delivery", "Driver": "Ahmed Hassan", "Timestamp": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")},
        {"Order ID": "ORD-2026-102", "Client / Branch": "New Cairo Hub", "Zone": "New Cairo", "SKU": "MRG-103", "Item Name": "Spanish Latte Base Mix 1kg", "Quantity": 35, "Total Value ($)": 682.5, "Payment Terms": "Direct Cash", "Status": "Delivered", "Driver": "Karim Zaki", "Timestamp": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")},
        {"Order ID": "ORD-2026-103", "Client / Branch": "Giza Central Express", "Zone": "Giza", "SKU": "MRG-105", "Item Name": "Eco-Friendly Cups 12oz (Box 500)", "Quantity": 10, "Total Value ($)": 380.0, "Payment Terms": "Bank Transfer", "Status": "Processing", "Driver": "Unassigned", "Timestamp": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")},
    ])

def get_initial_customers():
    return pd.DataFrame([
        {"Customer ID": "CUST-501", "Entity Name": "Maadi Flagship Branch", "Zone": "Maadi", "Contact Person": "Mahmoud Aly", "Phone": "+20 100 123 4567", "Credit Limit ($)": 10000.0, "Active Orders": 1},
        {"Customer ID": "CUST-502", "Entity Name": "New Cairo Hub", "Zone": "New Cairo", "Contact Person": "Sarah Sherif", "Phone": "+20 111 987 6543", "Credit Limit ($)": 15000.0, "Active Orders": 0},
        {"Customer ID": "CUST-503", "Entity Name": "Giza Central Express", "Zone": "Giza", "Contact Person": "Tarek Omar", "Phone": "+20 122 555 4433", "Credit Limit ($)": 8000.0, "Active Orders": 1},
    ])

if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = get_initial_inventory()

if "orders_df" not in st.session_state:
    st.session_state.orders_df = get_initial_orders()

if "customers_df" not in st.session_state:
    st.session_state.customers_df = get_initial_customers()


# ==========================================
# 5. CLASSIC DROP-DOWN NAVIGATION MENU
# ==========================================
st.sidebar.title(t("app_title"))
st.sidebar.caption(t("app_subtitle"))
st.sidebar.divider()

# Classic Selectbox Navigation
nav_page = st.sidebar.selectbox(
    t("nav_label"),
    options=[
        t("nav_overview"),
        t("nav_inventory"),
        t("nav_orders"),
        t("nav_customers"),
        t("nav_analytics"),
        t("nav_data"),
    ],
    index=0,
)

st.sidebar.divider()

# System Maintenance Options in Sidebar
st.sidebar.subheader(t("system_controls"))
if st.sidebar.button(t("reset_btn"), use_container_width=True):
    st.session_state.inventory_df = get_initial_inventory()
    st.session_state.orders_df = get_initial_orders()
    st.session_state.customers_df = get_initial_customers()
    st.sidebar.success(t("reset_success"))
    st.rerun()


# ==========================================
# 6. MODULE 1: EXECUTIVE COMMAND CENTER
# ==========================================
if nav_page == t("nav_overview"):
    st.title(t("nav_overview"))
    st.caption("Live enterprise operational pulse, inventory valuations, and order flow metrics.")

    inv_df = st.session_state.inventory_df
    ord_df = st.session_state.orders_df

    # Financial Calculations
    inv_df["Total Value"] = inv_df["Stock Level"] * inv_df["Selling Price ($)"]
    inv_df["Total Cost"] = inv_df["Stock Level"] * inv_df["Unit Cost ($)"]

    total_val = inv_df["Total Value"].sum() if not inv_df.empty else 0.0
    total_cost = inv_df["Total Cost"].sum() if not inv_df.empty else 0.0
    gross_margin = total_val - total_cost

    low_stock_items = inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]]
    low_stock_count = len(low_stock_items)

    active_orders = ord_df[ord_df["Status"].isin(["Pending", "Processing", "Out for Delivery"])] if not ord_df.empty else []
    completed_orders = ord_df[ord_df["Status"] == "Delivered"] if not ord_df.empty else []

    # KPI Top Banner
    k1, k2, k3, k4, k5 = st.columns(5)
    sym = t("currency_symbol")
    
    k1.metric(t("kpi_total_val"), f"{sym} {total_val:,.2f}")
    k2.metric(t("kpi_total_cost"), f"{sym} {total_cost:,.2f}")
    k3.metric(t("kpi_net_margin"), f"{sym} {gross_margin:,.2f}", delta=f"{((gross_margin/total_val)*100 if total_val > 0 else 0):.1f}%")
    k4.metric(
        t("kpi_low_stock"),
        low_stock_count,
        delta="-Action Required" if low_stock_count > 0 else "Optimal",
        delta_color="inverse" if low_stock_count > 0 else "normal",
    )
    k5.metric(t("kpi_active_orders"), len(active_orders), delta=f"{len(completed_orders)} Completed")

    st.divider()

    col_a, col_b = st.columns([1.6, 1])

    with col_a:
        st.subheader("🚛 Live Shipment & Dispatch Feed")
        if ord_df.empty:
            st.info("No active dispatch orders recorded.")
        else:
            st.dataframe(
                ord_df[["Order ID", "Client / Branch", "Zone", "Item Name", "Quantity", "Total Value ($)", "Status", "Driver"]],
                use_container_width=True,
                hide_index=True,
            )

    with col_b:
        st.subheader("🚨 Critical Reorder Alerts")
        if low_stock_items.empty:
            st.success("All inventory stock levels are well above defined safety reorder thresholds.")
        else:
            st.dataframe(
                low_stock_items[["SKU", "Product Name", "Stock Level", "Reorder Point", "Warehouse Bin"]],
                use_container_width=True,
                hide_index=True,
            )


# ==========================================
# 7. MODULE 2: INVENTORY CONTROL & AUDIT
# ==========================================
elif nav_page == t("nav_inventory"):
    st.title(t("nav_inventory"))

    tab1, tab2, tab3, tab4 = st.tabs([
        t("tab_live_stock"),
        t("tab_add_item"),
        t("tab_bulk_upload"),
        t("tab_restock")
    ])

    # --- TAB 1: Live Interactive Inventory ---
    with tab1:
        st.subheader(t("tab_live_stock"))
        inv_df = st.session_state.inventory_df

        if inv_df.empty:
            st.info("Inventory table is currently empty.")
        else:
            # Multi-Filter bar
            f_col1, f_col2 = st.columns([2, 1])
            search = f_col1.text_input(t("search_ph"), "")
            cat_filter = f_col2.selectbox("Filter Category", ["All"] + list(inv_df["Category"].unique()))

            filtered_df = inv_df.copy()
            if search:
                filtered_df = filtered_df[
                    filtered_df["Product Name"].str.contains(search, case=False, na=False)
                    | filtered_df["SKU"].str.contains(search, case=False, na=False)
                    | filtered_df["Category"].str.contains(search, case=False, na=False)
                ]
            if cat_filter != "All":
                filtered_df = filtered_df[filtered_df["Category"] == cat_filter]

            # Dynamic stock status badge generation
            filtered_df["Margin (%)"] = (
                ((filtered_df["Selling Price ($)"] - filtered_df["Unit Cost ($)"]) / filtered_df["Selling Price ($)"]) * 100
            ).round(1)

            edited_inv = st.data_editor(
                filtered_df,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="inv_editor_grid",
            )

            if st.button(t("save_changes"), key="save_inv_btn"):
                st.session_state.inventory_df.update(edited_inv)
                st.success(t("save_success"))
                st.rerun()

    # --- TAB 2: Single Product Entry ---
    with tab2:
        st.subheader(t("tab_add_item"))
        with st.form("add_product_form_advanced", clear_on_submit=True):
            p1, p2, p3 = st.columns(3)
            sku = p1.text_input(t("sku"), value=f"MRG-{len(st.session_state.inventory_df)+101}")
            p_name = p2.text_input(t("product_name"))
            cat = p3.text_input(t("category"), value="General Supply")

            p4, p5, p6, p7 = st.columns(4)
            bin_loc = p4.text_input(t("warehouse_loc"), value="A-01-01")
            stock = p5.number_input(t("stock_qty"), min_value=0, value=50)
            reorder = p6.number_input(t("reorder_pt"), min_value=0, value=15)
            cost = p7.number_input(t("unit_cost"), min_value=0.0, value=10.0, step=0.5)
            price = st.number_input(t("unit_price"), min_value=0.0, value=18.0, step=0.5)

            if st.form_submit_button("➕ Provision Product into Stock"):
                if p_name and sku:
                    new_item = pd.DataFrame([{
                        "SKU": sku,
                        "Product Name": p_name,
                        "Category": cat,
                        "Warehouse Bin": bin_loc,
                        "Stock Level": stock,
                        "Reorder Point": reorder,
                        "Unit Cost ($)": cost,
                        "Selling Price ($)": price,
                    }])
                    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, new_item], ignore_index=True)
                    st.success(f"Product '{p_name}' successfully added to database!")
                    st.rerun()
                else:
                    st.error("Error: Product Description and SKU Code are mandatory fields.")

    # --- TAB 3: Batch Upload ---
    with tab3:
        st.subheader(t("tab_bulk_upload"))
        st.caption("Upload CSV file matching required schema: SKU, Product Name, Category, Warehouse Bin, Stock Level, Reorder Point, Unit Cost ($), Selling Price ($)")
        uploaded_file = st.file_uploader("Upload Inventory CSV File", type=["csv"])
        if uploaded_file is not None:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df, use_container_width=True)
                if st.button("Merge Uploaded Data into Active System"):
                    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, imported_df], ignore_index=True).drop_duplicates(subset=["SKU"], keep="last")
                    st.success("Batch database merger completed!")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to process CSV file: {e}")

    # --- TAB 4: Automated Restock Calculation ---
    with tab4:
        st.subheader(t("tab_restock"))
        inv_df = st.session_state.inventory_df
        restock_candidates = inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]].copy()
        if restock_candidates.empty:
            st.success("No restock purchase orders are required at this moment.")
        else:
            restock_candidates["Suggested Reorder Qty"] = (restock_candidates["Reorder Point"] * 2.5) - restock_candidates["Stock Level"]
            restock_candidates["Est. Reorder Cost ($)"] = restock_candidates["Suggested Reorder Qty"] * restock_candidates["Unit Cost ($)"]
            
            st.dataframe(
                restock_candidates[["SKU", "Product Name", "Stock Level", "Reorder Point", "Suggested Reorder Qty", "Est. Reorder Cost ($)"]],
                use_container_width=True,
                hide_index=True,
            )
            st.info(f"Total Estimated Purchase Order Value Required: ${restock_candidates['Est. Reorder Cost ($)'].sum():,.2f}")


# ==========================================
# 8. MODULE 3: DISPATCH & ORDER FULFILLMENT
# ==========================================
elif nav_page == t("nav_orders"):
    st.title(t("nav_orders"))

    o_tab1, o_tab2 = st.tabs(["📝 Book New Shipment Order", "🚚 Fulfillment & Order Status Pipeline"])

    with o_tab1:
        st.subheader("Book New Distribution Shipment")
        inv_df = st.session_state.inventory_df

        if inv_df.empty:
            st.warning("Please add products to your inventory before creating sales orders.")
        else:
            with st.form("new_shipment_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                client = c1.text_input("Client / Branch Entity")
                zone = c2.selectbox(t("dest_zone"), ["Maadi", "New Cairo", "Cairo Central", "Giza", "6th of October", "Alexandria Corridor", "Other Area"])
                pay_terms = c3.selectbox(t("payment_type"), ["Credit (30 Days)", "Direct Cash", "Bank Transfer", "Letter of Credit"])

                # Dynamic Product Selection linked to inventory
                product_list = [f"{row['SKU']} - {row['Product Name']} (Avail: {row['Stock Level']})" for _, row in inv_df.iterrows()]
                selected_prod = st.selectbox("Select Item from Active Inventory", product_list)

                o4, o5 = st.columns(2)
                order_qty = o4.number_input("Order Quantity", min_value=1, value=5)
                assigned_driver = o5.text_input(t("driver_assigned"), value="Unassigned")

                if st.form_submit_button(t("create_order")):
                    sku_code = selected_prod.split(" - ")[0]
                    matched_item = inv_df[inv_df["SKU"] == sku_code].iloc[0]

                    if matched_item["Stock Level"] < order_qty:
                        st.error(f"Cannot fulfill order! Selected quantity ({order_qty}) exceeds available stock ({matched_item['Stock Level']}).")
                    else:
                        # Auto-deduct inventory
                        st.session_state.inventory_df.loc[st.session_state.inventory_df["SKU"] == sku_code, "Stock Level"] -= order_qty

                        order_val = matched_item["Selling Price ($)"] * order_qty
                        new_order_entry = pd.DataFrame([{
                            "Order ID": f"ORD-2026-{len(st.session_state.orders_df)+101}",
                            "Client / Branch": client if client else "Walk-in Branch",
                            "Zone": zone,
                            "SKU": sku_code,
                            "Item Name": matched_item["Product Name"],
                            "Quantity": order_qty,
                            "Total Value ($)": order_val,
                            "Payment Terms": pay_terms,
                            "Status": "Out for Delivery" if assigned_driver != "Unassigned" else "Pending",
                            "Driver": assigned_driver,
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }])

                        st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_order_entry], ignore_index=True)
                        st.success(f"Shipment created! ${order_val:,.2f} billed and inventory updated automatically.")
                        st.rerun()

    with o_tab2:
        st.subheader("Manage Active Orders Pipeline")
        if st.session_state.orders_df.empty:
            st.info("No active or historical orders found.")
        else:
            updated_orders = st.data_editor(
                st.session_state.orders_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Processing", "Out for Delivery", "Delivered", "Cancelled"],
                    )
                },
                key="orders_pipeline_editor",
            )
            if st.button("💾 Persist Order Pipeline Changes"):
                st.session_state.orders_df = updated_orders
                st.success("Order states updated!")
                st.rerun()


# ==========================================
# 9. MODULE 4: CLIENT DIRECTORY
# ==========================================
elif nav_page == t("nav_customers"):
    st.title(t("nav_customers"))

    cust_col1, cust_col2 = st.columns([1, 1.8])

    with cust_col1:
        st.subheader("Register Client / Branch")
        with st.form("add_client_form", clear_on_submit=True):
            c_name = st.text_input("Entity / Client Name")
            c_zone = st.selectbox("Operating Zone", ["Maadi", "New Cairo", "Cairo Central", "Giza", "6th of October", "Alexandria Corridor"])
            c_person = st.text_input("Contact Manager")
            c_phone = st.text_input("Telephone / Mobile")
            c_limit = st.number_input("Approved Credit Limit ($)", min_value=0.0, value=5000.0, step=500.0)

            if st.form_submit_button("Register Client Profile"):
                if c_name:
                    new_cust = pd.DataFrame([{
                        "Customer ID": f"CUST-{len(st.session_state.customers_df)+501}",
                        "Entity Name": c_name,
                        "Zone": c_zone,
                        "Contact Person": c_person,
                        "Phone": c_phone,
                        "Credit Limit ($)": c_limit,
                        "Active Orders": 0,
                    }])
                    st.session_state.customers_df = pd.concat([st.session_state.customers_df, new_cust], ignore_index=True)
                    st.success("Client profile established!")
                    st.rerun()

    with cust_col2:
        st.subheader("Client Directory Registry")
        if st.session_state.customers_df.empty:
            st.info("No client accounts registered.")
        else:
            st.dataframe(st.session_state.customers_df, use_container_width=True, hide_index=True)


# ==========================================
# 10. MODULE 5: ADVANCED ANALYTICS & FINANCIALS
# ==========================================
elif nav_page == t("nav_analytics"):
    st.title(t("analytics_title"))

    orders_df = st.session_state.orders_df
    inventory_df = st.session_state.inventory_df

    st.subheader(t("financial_summary"))
    a1, a2 = st.columns(2)

    with a1:
        st.markdown("#### Revenue Generation by Zone")
        if not orders_df.empty:
            zone_rev = orders_df.groupby("Zone")["Total Value ($)"].sum().reset_index()
            st.bar_chart(zone_rev, x="Zone", y="Total Value ($)")
        else:
            st.info("Insufficient order data for zone analysis.")

    with a2:
        st.markdown("#### Inventory Asset Valuation by Category")
        if not inventory_df.empty:
            inventory_df["Category Valuation"] = inventory_df["Stock Level"] * inventory_df["Selling Price ($)"]
            cat_val = inventory_df.groupby("Category")["Category Valuation"].sum().reset_index()
            st.bar_chart(cat_val, x="Category", y="Category Valuation")
        else:
            st.info("No stock inventory data available.")


# ==========================================
# 11. MODULE 6: DATA MANAGEMENT & EXPORT
# ==========================================
elif nav_page == t("nav_data"):
    st.title(t("download_section"))

    d1, d2, d3 = st.columns(3)

    with d1:
        st.subheader("Inventory Records")
        csv_inv = st.session_state.inventory_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            t("export_csv") + " - Inventory",
            data=csv_inv,
            file_name=f"mirage_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with d2:
        st.subheader("Dispatches & Orders")
        csv_ord = st.session_state.orders_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            t("export_csv") + " - Orders",
            data=csv_ord,
            file_name=f"mirage_orders_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with d3:
        st.subheader("Client Directory")
        csv_cust = st.session_state.customers_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            t("export_csv") + " - Clients",
            data=csv_cust,
            file_name=f"mirage_clients_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
