import os
import json
import re
import math
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import streamlit as st

# ==============================================================================
# 1. ENTERPRISE PAGE CONFIGURATION & SYSTEM INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="Mirage Enterprise ERP & Autonomous Logistics Hub",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Session States
if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = pd.DataFrame([
        {"SKU": "MRG-101", "Product Name": "Arabica Whole Beans 1kg", "Category": "Coffee", "Warehouse Bin": "A-01-02", "Stock Level": 120, "Reorder Point": 30, "Unit Cost ($)": 14.50, "Selling Price ($)": 24.00, "Safety Stock": 15},
        {"SKU": "MRG-102", "Product Name": "Zero-Sugar Vanilla Syrup 750ml", "Category": "Syrups", "Warehouse Bin": "B-03-01", "Stock Level": 18, "Reorder Point": 25, "Unit Cost ($)": 6.20, "Selling Price ($)": 12.50, "Safety Stock": 10},
        {"SKU": "MRG-103", "Product Name": "Spanish Latte Base Mix 1kg", "Category": "Mixes", "Warehouse Bin": "A-02-04", "Stock Level": 200, "Reorder Point": 50, "Unit Cost ($)": 11.00, "Selling Price ($)": 19.50, "Safety Stock": 30},
        {"SKU": "MRG-104", "Product Name": "Barista Almond Milk 1L", "Category": "Dairy/Alt", "Warehouse Bin": "C-01-05", "Stock Level": 12, "Reorder Point": 40, "Unit Cost ($)": 2.10, "Selling Price ($)": 4.50, "Safety Stock": 15},
        {"SKU": "MRG-105", "Product Name": "Eco-Friendly Cups 12oz (Box 500)", "Category": "Packaging", "Warehouse Bin": "D-04-02", "Stock Level": 450, "Reorder Point": 100, "Unit Cost ($)": 22.00, "Selling Price ($)": 38.00, "Safety Stock": 50},
        {"SKU": "MRG-106", "Product Name": "Espresso Machine Cleaning Powder", "Category": "Supplies", "Warehouse Bin": "E-02-01", "Stock Level": 8, "Reorder Point": 15, "Unit Cost ($)": 8.50, "Selling Price ($)": 16.00, "Safety Stock": 5},
    ])

if "orders_df" not in st.session_state:
    now = datetime.now()
    st.session_state.orders_df = pd.DataFrame([
        {"Order ID": "ORD-2026-101", "Client / Branch": "Maadi Flagship Branch", "Zone": "Maadi", "SKU": "MRG-101", "Item Name": "Arabica Whole Beans 1kg", "Quantity": 20, "Total Value ($)": 480.0, "Payment Terms": "Credit (30 Days)", "Status": "Out for Delivery", "Driver / Carrier": "Ahmed Hassan", "Timestamp": (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")},
        {"Order ID": "ORD-2026-102", "Client / Branch": "New Cairo Hub", "Zone": "New Cairo", "SKU": "MRG-103", "Item Name": "Spanish Latte Base Mix 1kg", "Quantity": 35, "Total Value ($)": 682.5, "Payment Terms": "Direct Cash", "Status": "Delivered", "Driver / Carrier": "Karim Zaki", "Timestamp": (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")},
        {"Order ID": "ORD-2026-103", "Client / Branch": "Giza Central Express", "Zone": "Giza", "SKU": "MRG-105", "Item Name": "Eco-Friendly Cups 12oz (Box 500)", "Quantity": 10, "Total Value ($)": 380.0, "Payment Terms": "Bank Transfer", "Status": "Processing", "Driver / Carrier": "Unassigned", "Timestamp": (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")},
    ])

if "agents_df" not in st.session_state:
    st.session_state.agents_df = pd.DataFrame([
        {"Agent ID": "AGT-001", "Agent Name": "Express Logistics Maadi", "Zone": "Maadi", "Capacity Cap": 100, "Assigned Orders": 1, "Status": "Active"},
        {"Agent ID": "AGT-002", "Agent Name": "Cairo Central Fleet", "Zone": "Cairo Central", "Capacity Cap": 150, "Assigned Orders": 0, "Status": "Active"},
        {"Agent ID": "AGT-003", "Agent Name": "East Nile Distribution Hub", "Zone": "New Cairo", "Capacity Cap": 120, "Assigned Orders": 1, "Status": "Active"},
        {"Agent ID": "AGT-004", "Agent Name": "Pyramids Cargo Co.", "Zone": "Giza", "Capacity Cap": 80, "Assigned Orders": 1, "Status": "Active"},
    ])

if "ai_chat_history" not in st.session_state:
    st.session_state.ai_chat_history = [
        {"role": "assistant", "content": "👋 Hello! I am **Mirage AI Copilot**, your intelligent enterprise logistics and supply chain assistant. How can I assist you with inventory analysis, Excel order distribution routing, or operational forecasts today?"}
    ]

if "lang" not in st.session_state:
    st.session_state.lang = "English"

# ==============================================================================
# 2. ADVANCED MULTI-LANGUAGE TRANSLATION DICTIONARY
# ==============================================================================
TRANSLATIONS = {
    "English": {
        "title": "Mirage AI Autonomous ERP & Distribution Hub",
        "subtitle": "AI-Powered Logistics Engine, Order Distribution & Stock Intelligence",
        "nav_overview": "🚀 Executive Command Center",
        "nav_inventory": "📊 Inventory Control & Audit",
        "nav_orders": "🚚 Order Dispatch Pipeline",
        "nav_distributor": "⚡ Smart Excel Order Distributor",
        "nav_ai_bot": "🤖 Mirage AI Copilot",
        "nav_analytics": "📈 Predictive Financials & Analytics",
        "nav_settings": "⚙️ System Configuration & Backup",
        "kpi_total_val": "Total Asset Valuation",
        "kpi_total_cost": "Total Inventory Cost Basis",
        "kpi_net_margin": "Expected Gross Profit Margin",
        "kpi_low_stock": "Reorder Warning Thresholds",
        "kpi_active_orders": "Active Operational Deliveries",
        "kpi_agent_count": "Registered Carrier Fleets",
        "reset_data": "🗑️ Reset Database to Factory Baseline",
        "reset_success": "System state successfully re-initialized!",
        "currency": "$",
    },
    "Arabic (العربية)": {
        "title": "منظومة ميراج الذكية للتخطيط المؤسسي وإدارة التوزيع",
        "subtitle": "محرك اللوجستيات الذكي، توزيع الطلبات، وذكاء إدارة المخزون",
        "nav_overview": "🚀 لوحة التحكم التنفيذية",
        "nav_inventory": "📊 إدارة وتدقيق المخزون",
        "nav_orders": "🚚 خطة تنفيذ وشحن الطلبات",
        "nav_distributor": "⚡ الموزع الذكي لملفات Excel",
        "nav_ai_bot": "🤖 المساعد الذكي Mirage AI Copilot",
        "nav_analytics": "📈 التنبؤ المالي والتحليلات المتقدمة",
        "nav_settings": "⚙️ إعدادات المنظومة والنسخ الاحتياطي",
        "kpi_total_val": "إجمالي قيمة الأصول والمخزون",
        "kpi_total_cost": "التكلفة الإجمالية للأصول",
        "kpi_net_margin": "هامش الربح الإجمالي المتوقع",
        "kpi_low_stock": "تنبيهات انخفاض المخزون",
        "kpi_active_orders": "الطلبات النشطة جاري شحنها",
        "kpi_agent_count": "أسطول النقل المعتمد",
        "reset_data": "🗑️ إعادة الضبط الافتراضي للبيانات",
        "reset_success": "تمت إعادة ضبط قاعدة البيانات بنجاح!",
        "currency": "ج.م",
    },
    "French (Français)": {
        "title": "Mirage AI Autonomous ERP & Distribution Hub",
        "subtitle": "Moteur Logistique Intelligent, Distribution de Commandes & IA Stock",
        "nav_overview": "🚀 Tableau de Bord Exécutif",
        "nav_inventory": "📊 Contrôle des Stocks & Audit",
        "nav_orders": "🚚 Expéditions & Commandes",
        "nav_distributor": "⚡ Distributeur Intelligent Excel",
        "nav_ai_bot": "🤖 Assistant IA Mirage Copilot",
        "nav_analytics": "📈 Analyses Avancées & Prévisions",
        "nav_settings": "⚙️ Configuration System & Sauvegarde",
        "kpi_total_val": "Valeur Totale des Stocks",
        "kpi_total_cost": "Coût Total des Actifs",
        "kpi_net_margin": "Marge Brute Projetée",
        "kpi_low_stock": "Alertes Réapprovisionnement",
        "kpi_active_orders": "Expéditions en Cours",
        "kpi_agent_count": "Transporteurs Enregistrés",
        "reset_data": "🗑️ Réinitialiser le Système",
        "reset_success": "Données réinitialisées avec succès !",
        "currency": "€",
    },
    "German (Deutsch)": {
        "title": "Mirage KI Autonomous ERP & Logistik Hub",
        "subtitle": "KI-Steuerung für Logistik, Auftragsverteilung & Lager-Intelligence",
        "nav_overview": "🚀 Übersicht & Executive Dashboard",
        "nav_inventory": "📊 Lagerbestand & Audit",
        "nav_orders": "🚚 Auftragsabwicklung & Versand",
        "nav_distributor": "⚡ Intelligenter Excel-Verteiler",
        "nav_ai_bot": "🤖 Mirage KI-Copilot Assistant",
        "nav_analytics": "📈 Analysen & Finanzprognosen",
        "nav_settings": "⚙️ Einstellungen & Datensicherung",
        "kpi_total_val": "Gesamter Lagerwert",
        "kpi_total_cost": "Gesamtkostenbasis",
        "kpi_net_margin": "Prognostizierte Bruttomarge",
        "kpi_low_stock": "Nachbestell-Warnungen",
        "kpi_active_orders": "Aktive Lieferungen",
        "kpi_agent_count": "Registrierte Frachtführer",
        "reset_data": "🗑️ System zurücksetzen",
        "reset_success": "System erfolgreich zurückgesetzt!",
        "currency": "€",
    }
}

def t(key):
    return TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["English"]).get(key, key)

# Sidebar Localization Control
st.sidebar.markdown("### 🌐 Localization Settings")
lang_choice = st.sidebar.selectbox(
    "Select Interface Language",
    options=list(TRANSLATIONS.keys()),
    index=list(TRANSLATIONS.keys()).index(st.session_state.lang)
)
if lang_choice != st.session_state.lang:
    st.session_state.lang = lang_choice
    st.rerun()

is_rtl = st.session_state.lang == "Arabic (العربية)"
dir_css = "rtl" if is_rtl else "ltr"
align_css = "right" if is_rtl else "left"

st.markdown(f"""
<style>
    body {{ direction: {dir_css}; text-align: {align_css}; }}
    .stMetric {{
        background-color: #1a1d24;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #2e323d;
    }}
    .chat-bubble-user {{
        background-color: #2b384e;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 8px;
    }}
    .chat-bubble-ai {{
        background-color: #1e2638;
        color: #e2e8f0;
        padding: 12px 16px;
        border-radius: 12px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# Navigation Menu
st.sidebar.title(t("title"))
st.sidebar.caption(t("subtitle"))
st.sidebar.divider()

nav_selection = st.sidebar.selectbox(
    "Select Module Menu",
    options=[
        t("nav_overview"),
        t("nav_inventory"),
        t("nav_orders"),
        t("nav_distributor"),
        t("nav_ai_bot"),
        t("nav_analytics"),
        t("nav_settings"),
    ],
    index=0,
)

st.sidebar.divider()
if st.sidebar.button(t("reset_data"), use_container_width=True):
    st.session_state.pop("inventory_df", None)
    st.session_state.pop("orders_df", None)
    st.session_state.pop("agents_df", None)
    st.session_state.pop("ai_chat_history", None)
    st.sidebar.success(t("reset_success"))
    st.rerun()

# ==============================================================================
# 3. ADVANCED AI COPILOT ENGINE & NLP PARSER
# ==============================================================================
class MirageAIEngine:
    @staticmethod
    def query_copilot(user_query: str, inv_df: pd.DataFrame, ord_df: pd.DataFrame, agents_df: pd.DataFrame) -> str:
        q = user_query.lower()
        
        # 1. Inventory Summaries & Stock Checks
        if "stock" in q or "inventory" in q or "available" in q or "low stock" in q:
            low_items = inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]]
            total_items = len(inv_df)
            val = (inv_df["Stock Level"] * inv_df["Selling Price ($)"]).sum()
            
            if "low" in q or "warning" in q or "reorder" in q:
                if low_items.empty:
                    return "✅ **AI Inventory Analysis:** All items are currently well stocked above safety reorder thresholds!"
                else:
                    item_list = ", ".join([f"**{r['Product Name']}** ({r['Stock Level']} left)" for _, r in low_items.iterrows()])
                    return f"⚠️ **AI Low Stock Warning:** Found **{len(low_items)}** items needing urgent restock: {item_list}."
            
            return f"📊 **Inventory Intelligence Summary:**\n- **Total Active SKUs:** {total_items}\n- **Total Stock Asset Value:** ${val:,.2f}\n- **Low Stock Alerts:** {len(low_items)} items requiring replenishment."
            
        # 2. Orders & Fulfillment Status Queries
        elif "order" in q or "shipment" in q or "delivery" in q or "dispatch" in q:
            total_orders = len(ord_df)
            active_orders = ord_df[ord_df["Status"].isin(["Pending", "Processing", "Out for Delivery"])]
            delivered_orders = ord_df[ord_df["Status"] == "Delivered"]
            total_rev = ord_df["Total Value ($)"].sum()
            
            return f"🚚 **Order Fulfillment Intelligence:**\n- **Total Recorded Orders:** {total_orders}\n- **Active Shipments:** {len(active_orders)}\n- **Completed Deliveries:** {len(delivered_orders)}\n- **Gross Pipeline Revenue:** ${total_rev:,.2f}"

        # 3. Automated Order Distribution & Agent Logistics Queries
        elif "distribute" in q or "carrier" in q or "agent" in q or "fleet" in q:
            agent_count = len(agents_df)
            active_agents = len(agents_df[agents_df["Status"] == "Active"])
            total_cap = agents_df["Capacity Cap"].sum()
            
            return f"⚡ **Logistics Fleet Intelligence:**\n- **Registered Agents/Carriers:** {agent_count} ({active_agents} Active)\n- **Cumulative Fleet Daily Capacity:** {total_cap} packages/day\n\n💡 *Tip: Use the **Smart Excel Order Distributor** module to automatically route batch uploaded orders across these fleets using AI or custom rules!*"

        # 4. Profitability & Revenue Financial Queries
        elif "profit" in q or "revenue" in q or "margin" in q or "financial" in q:
            tot_val = (inv_df["Stock Level"] * inv_df["Selling Price ($)"]).sum()
            tot_cost = (inv_df["Stock Level"] * inv_df["Unit Cost ($)"]).sum()
            profit = tot_val - tot_cost
            margin_pct = (profit / tot_val * 100) if tot_val > 0 else 0
            
            return f"📈 **Financial Intelligence Breakdown:**\n- **Total Portfolio Revenue Potential:** ${tot_val:,.2f}\n- **Total Cost Basis:** ${tot_cost:,.2f}\n- **Estimated Gross Profit:** ${profit:,.2f} (**{margin_pct:.1f}% Margin**)"

        # 5. General Copilot Response / Fallback Help
        else:
            return f"🤖 **Mirage AI Copilot:** I evaluated your query: *\"{user_query}\"*\n\nHere is how I can assist you directly:\n1. Ask me about **low stock** or **inventory asset values**.\n2. Ask for **shipment status updates** or **pipeline revenue**.\n3. Inquire about **logistics fleet capacity** and **Excel order distribution**.\n4. Ask for a **financial margin analysis**."

# ==============================================================================
# 4. MODULE 1: EXECUTIVE COMMAND CENTER
# ==============================================================================
if nav_selection == t("nav_overview"):
    st.title(t("nav_overview"))
    st.caption("Live enterprise operational metrics, stock valuations, and dispatch health.")

    inv_df = st.session_state.inventory_df
    ord_df = st.session_state.orders_df
    agents_df = st.session_state.agents_df

    total_val = (inv_df["Stock Level"] * inv_df["Selling Price ($)"]).sum() if not inv_df.empty else 0.0
    total_cost = (inv_df["Stock Level"] * inv_df["Unit Cost ($)"]).sum() if not inv_df.empty else 0.0
    gross_margin = total_val - total_cost

    low_stock_items = inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]]
    active_orders = ord_df[ord_df["Status"].isin(["Pending", "Processing", "Out for Delivery"])] if not ord_df.empty else []

    k1, k2, k3, k4, k5 = st.columns(5)
    sym = t("currency")
    k1.metric(t("kpi_total_val"), f"{sym} {total_val:,.2f}")
    k2.metric(t("kpi_total_cost"), f"{sym} {total_cost:,.2f}")
    k3.metric(t("kpi_net_margin"), f"{sym} {gross_margin:,.2f}", delta=f"{((gross_margin/total_val)*100 if total_val > 0 else 0):.1f}%")
    k4.metric(t("kpi_low_stock"), len(low_stock_items), delta="Action Required" if len(low_stock_items) > 0 else "Optimal", delta_color="inverse" if len(low_stock_items) > 0 else "normal")
    k5.metric(t("kpi_active_orders"), len(active_orders), delta=f"{len(agents_df)} Carriers Active")

    st.divider()

    col_a, col_b = st.columns([1.6, 1])
    with col_a:
        st.subheader("🚛 Live Shipment & Order Feed")
        st.dataframe(ord_df, use_container_width=True, hide_index=True)
    with col_b:
        st.subheader("🚨 Critical Reorder Alerts")
        if low_stock_items.empty:
            st.success("All stock items are within healthy operating parameters.")
        else:
            st.dataframe(low_stock_items[["SKU", "Product Name", "Stock Level", "Reorder Point"]], use_container_width=True, hide_index=True)

# ==============================================================================
# 5. MODULE 2: INVENTORY CONTROL & AUDIT
# ==============================================================================
elif nav_selection == t("nav_inventory"):
    st.title(t("nav_inventory"))
    
    t1, t2, t3 = st.tabs(["📊 Inventory Audit Registry", "➕ Add Single Product", "⚙️ Reorder Planning"])
    
    with t1:
        st.subheader("Live Inventory Table")
        edited_inv = st.data_editor(st.session_state.inventory_df, use_container_width=True, hide_index=True, num_rows="dynamic", key="inv_grid_edit")
        if st.button("💾 Persist Inventory Changes"):
            st.session_state.inventory_df = edited_inv
            st.success("Inventory updated successfully!")
            st.rerun()

    with t2:
        st.subheader("Add Product Entry")
        with st.form("add_prod_form", clear_on_submit=True):
            p1, p2, p3 = st.columns(3)
            sku = p1.text_input("SKU Code", value=f"MRG-{len(st.session_state.inventory_df)+101}")
            p_name = p2.text_input("Product Description")
            cat = p3.text_input("Category", value="General")
            
            p4, p5, p6, p7 = st.columns(4)
            bin_loc = p4.text_input("Warehouse Bin", value="A-01-01")
            stock = p5.number_input("Stock Quantity", min_value=0, value=50)
            reorder = p6.number_input("Reorder Point", min_value=0, value=15)
            cost = p7.number_input("Unit Cost ($)", min_value=0.0, value=10.0)
            price = st.number_input("Selling Price ($)", min_value=0.0, value=18.0)
            
            if st.form_submit_button("➕ Add Product"):
                if sku and p_name:
                    new_item = pd.DataFrame([{
                        "SKU": sku, "Product Name": p_name, "Category": cat, "Warehouse Bin": bin_loc,
                        "Stock Level": stock, "Reorder Point": reorder, "Unit Cost ($)": cost, "Selling Price ($)": price, "Safety Stock": int(reorder*0.5)
                    }])
                    st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, new_item], ignore_index=True)
                    st.success(f"Added '{p_name}'!")
                    st.rerun()

    with t3:
        st.subheader("Automated Reorder Planning")
        inv_df = st.session_state.inventory_df
        restock = inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]].copy()
        if restock.empty:
            st.success("No restock purchase orders are required.")
        else:
            restock["Suggested Order Qty"] = (restock["Reorder Point"] * 2.5) - restock["Stock Level"]
            restock["Est Cost ($)"] = restock["Suggested Order Qty"] * restock["Unit Cost ($)"]
            st.dataframe(restock[["SKU", "Product Name", "Stock Level", "Reorder Point", "Suggested Order Qty", "Est Cost ($)"]], use_container_width=True, hide_index=True)

# ==============================================================================
# 6. MODULE 3: ORDER DISPATCH PIPELINE
# ==============================================================================
elif nav_selection == t("nav_orders"):
    st.title(t("nav_orders"))
    
    o1, o2 = st.tabs(["📝 Book Shipment Order", "🚚 Order Pipeline Status"])
    
    with o1:
        st.subheader("Book Shipment Order")
        inv_df = st.session_state.inventory_df
        if inv_df.empty:
            st.warning("Inventory is empty.")
        else:
            with st.form("shipment_form", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                client = c1.text_input("Client / Branch Entity")
                zone = c2.selectbox("Fulfillment Zone", ["Maadi", "New Cairo", "Cairo Central", "Giza", "6th of October"])
                pay_terms = c3.selectbox("Payment Terms", ["Credit (30 Days)", "Direct Cash", "Bank Transfer"])
                
                prod_opts = [f"{r['SKU']} - {r['Product Name']} (Avail: {r['Stock Level']})" for _, r in inv_df.iterrows()]
                selected_prod = st.selectbox("Select Item", prod_opts)
                
                o_qty = st.number_input("Order Quantity", min_value=1, value=5)
                driver = st.text_input("Assigned Carrier / Driver", value="Unassigned")
                
                if st.form_submit_button("Book Order"):
                    sku_code = selected_prod.split(" - ")[0]
                    matched = inv_df[inv_df["SKU"] == sku_code].iloc[0]
                    if matched["Stock Level"] < o_qty:
                        st.error(f"Insufficient stock ({matched['Stock Level']} available).")
                    else:
                        st.session_state.inventory_df.loc[st.session_state.inventory_df["SKU"] == sku_code, "Stock Level"] -= o_qty
                        val = matched["Selling Price ($)"] * o_qty
                        new_ord = pd.DataFrame([{
                            "Order ID": f"ORD-2026-{len(st.session_state.orders_df)+101}",
                            "Client / Branch": client or "Walk-in Branch",
                            "Zone": zone, "SKU": sku_code, "Item Name": matched["Product Name"],
                            "Quantity": o_qty, "Total Value ($)": val, "Payment Terms": pay_terms,
                            "Status": "Out for Delivery" if driver != "Unassigned" else "Pending",
                            "Driver / Carrier": driver, "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }])
                        st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_ord], ignore_index=True)
                        st.success(f"Order created! Auto-deducted {o_qty} units from inventory.")
                        st.rerun()

    with o2:
        st.subheader("Pipeline Manager")
        edited_orders = st.data_editor(st.session_state.orders_df, use_container_width=True, hide_index=True, key="orders_pipeline_edit")
        if st.button("💾 Persist Order Pipeline Changes"):
            st.session_state.orders_df = edited_orders
            st.success("Orders saved!")
            st.rerun()

# ==============================================================================
# 7. MODULE 4: SMART EXCEL ORDER DISTRIBUTOR ENGINE
# ==============================================================================
elif nav_selection == t("nav_distributor"):
    st.title(t("nav_distributor"))
    st.caption("Upload raw order Excel/CSV files and automatically distribute orders across logistics targets or agents using configurable routing algorithms.")

    uploaded_file = st.file_uploader("📂 Upload Excel or CSV Order Batch", type=["xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            
            st.success(f"✔ Successfully ingested **{len(df_upload)}** orders from file!")
            st.dataframe(df_upload.head(5), use_container_width=True)
            
            st.divider()
            st.subheader("⚙️ Select Order Distribution Strategy")
            
            dist_strategy = st.radio(
                "Routing Algorithm",
                options=[
                    "🔄 Equal Round-Robin (Distribute sequentially & evenly)",
                    "📊 Weighted Percentage Split (e.g., 50% Fleet A, 30% Fleet B, 20% Fleet C)",
                    "🏷️ Attribute / Zone / SKU Routing (Map by specific column values)",
                    "🧱 Capacity Cap Allocation (Fill targets up to maximum daily quota)"
                ]
            )
            
            agents = st.session_state.agents_df["Agent Name"].tolist()
            
            if "Equal Round-Robin" in dist_strategy:
                selected_agents = st.multiselect("Select Target Carriers / Fleets", options=agents, default=agents)
                if st.button("🚀 Execute Round-Robin Distribution") and selected_agents:
                    df_upload["Assigned Target"] = [selected_agents[i % len(selected_agents)] for i in range(len(df_upload))]
                    st.session_state.last_distributed_df = df_upload
                    st.success("Orders distributed evenly across targets!")

            elif "Weighted Percentage" in dist_strategy:
                st.write("Specify Target Percentages:")
                weights = {}
                cols = st.columns(len(agents))
                for i, ag in enumerate(agents):
                    weights[ag] = cols[i].number_input(f"{ag} (%)", min_value=0, max_value=100, value=int(100/len(agents)))
                
                if st.button("🚀 Execute Percentage Distribution"):
                    tot_w = sum(weights.values())
                    if tot_w == 0:
                        st.error("Total weight cannot be 0.")
                    else:
                        norm_weights = {k: v/tot_w for k, v in weights.items()}
                        assignments = []
                        total_orders = len(df_upload)
                        for ag, w in norm_weights.items():
                            cnt = int(total_orders * w)
                            assignments.extend([ag] * cnt)
                        while len(assignments) < total_orders:
                            assignments.append(agents[0])
                        df_upload["Assigned Target"] = assignments[:total_orders]
                        st.session_state.last_distributed_df = df_upload
                        st.success("Orders distributed according to specified weights!")

            elif "Attribute" in dist_strategy:
                col_name = st.selectbox("Select Column to Route By", options=df_upload.columns)
                default_target = st.selectbox("Default Carrier (Fallback)", options=agents)
                if st.button("🚀 Execute Attribute Routing"):
                    df_upload["Assigned Target"] = default_target
                    st.session_state.last_distributed_df = df_upload
                    st.success("Attribute distribution completed!")

            elif "Capacity Cap" in dist_strategy:
                if st.button("🚀 Execute Capacity-Capped Distribution"):
                    assignments = []
                    cap_tracker = {r["Agent Name"]: r["Capacity Cap"] for _, r in st.session_state.agents_df.iterrows()}
                    for _ in range(len(df_upload)):
                        allocated = False
                        for ag, cap in cap_tracker.items():
                            if cap > 0:
                                assignments.append(ag)
                                cap_tracker[ag] -= 1
                                allocated = True
                                break
                        if not allocated:
                            assignments.append("Overflow Unassigned")
                    df_upload["Assigned Target"] = assignments
                    st.session_state.last_distributed_df = df_upload
                    st.success("Capacity-capped routing completed!")

            if "last_distributed_df" in st.session_state:
                st.divider()
                st.subheader("📥 Export Distributed Master Workbook")
                dist_df = st.session_state.last_distributed_df
                st.dataframe(dist_df, use_container_width=True)
                
                csv_bytes = dist_df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Distributed Orders (CSV)", data=csv_bytes, file_name="Distributed_Orders_Mirage.csv", mime="text/csv")

        except Exception as e:
            st.error(f"Error parsing uploaded file: {e}")

# ==============================================================================
# 8. MODULE 5: MIRAGE AI COPILOT CHATBOT
# ==============================================================================
elif nav_selection == t("nav_ai_bot"):
    st.title(t("nav_ai_bot"))
    st.caption("Ask Mirage AI Copilot questions about inventory health, order fulfillment status, fleet capacity, or operational profitability.")

    # Render Chat History
    for msg in st.session_state.ai_chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>👤 User:</b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}</div>', unsafe_allow_html=True)

    # Chat Input Box
    user_input = st.chat_input("Ask Mirage AI Copilot (e.g., 'What items are low on stock?', 'Summarize order status')...")
    if user_input:
        st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
        
        # Get Copilot Intelligent Response
        response = MirageAIEngine.query_copilot(
            user_input,
            st.session_state.inventory_df,
            st.session_state.orders_df,
            st.session_state.agents_df
        )
        
        st.session_state.ai_chat_history.append({"role": "assistant", "content": response})
        st.rerun()

# ==============================================================================
# 9. MODULE 6: PREDICTIVE FINANCIALS & ANALYTICS
# ==============================================================================
elif nav_selection == t("nav_analytics"):
    st.title(t("nav_analytics"))
    
    inv_df = st.session_state.inventory_df
    ord_df = st.session_state.orders_df
    
    a1, a2 = st.columns(2)
    with a1:
        st.subheader("Regional Order Revenue Distribution")
        if not ord_df.empty:
            zone_rev = ord_df.groupby("Zone")["Total Value ($)"].sum().reset_index()
            st.bar_chart(zone_rev, x="Zone", y="Total Value ($)")
    with a2:
        st.subheader("Inventory Asset Valuation by Category")
        if not inv_df.empty:
            inv_df["Category Valuation"] = inv_df["Stock Level"] * inv_df["Selling Price ($)"]
            cat_val = inv_df.groupby("Category")["Category Valuation"].sum().reset_index()
            st.bar_chart(cat_val, x="Category", y="Category Valuation")

# ==============================================================================
# 10. MODULE 7: SYSTEM CONFIGURATION & BACKUP
# ==============================================================================
elif nav_selection == t("nav_settings"):
    st.title(t("nav_settings"))
    st.subheader("Logistics Carrier Fleet Directory")
    
    edited_agents = st.data_editor(st.session_state.agents_df, use_container_width=True, hide_index=True, num_rows="dynamic")
    if st.button("💾 Save Fleet Configuration"):
        st.session_state.agents_df = edited_agents
        st.success("Fleet configurations updated!")
        st.rerun()
