import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import urllib.parse
import io
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------------
# 1. PAGE CONFIG & THEME
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Fleet Command & Dispatch Engine",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# 2. DATABASE SETUP
# -------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("dispatch_system.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            brand TEXT,
            skills TEXT,
            vehicle TEXT,
            capacity INTEGER,
            home_zone TEXT,
            shift_type TEXT DEFAULT 'Full Day',
            parts_inventory TEXT DEFAULT 'Standard Kit'
        )
    """)
    c.execute("SELECT COUNT(*) FROM technicians")
    if c.fetchone()[0] == 0:
        default_data = [
            ("أحمد عماد", "201000000001", "Brand A", "Installation,Maintenance", "Motorcycle", 8, "Shorouk", "Full Day", "Standard Kit"),
            ("شعبان", "201000000002", "Brand A", "Installation", "Car", 10, "Madinaty", "Full Day", "Heavy Kit, Replacement Parts"),
            ("كيمكو", "201000000003", "Brand B", "Installation,Maintenance", "Car", 12, "Maadi", "Full Day", "Heavy Kit, Replacement Parts"),
            ("محمد سامي", "201000000004", "Brand B", "Customer Service", "Motorcycle", 7, "Maadi", "Half Day", "Standard Kit"),
            ("تكنو", "201000000005", "Brand C", "Installation", "Car", 10, "Tagamoa", "Full Day", "Heavy Kit"),
            ("حسن", "201000000006", "Brand C", "Customer Service", "Motorcycle", 8, "Tagamoa", "Full Day", "Standard Kit"),
        ]
        c.executemany("INSERT INTO technicians (name, phone, brand, skills, vehicle, capacity, home_zone, shift_type, parts_inventory) VALUES (?,?,?,?,?,?,?,?,?)", default_data)
        conn.commit()
    conn.close()

init_db()

def get_tech_df():
    conn = sqlite3.connect("dispatch_system.db")
    df = pd.read_sql_query("SELECT * FROM technicians", conn)
    conn.close()
    return df

def save_tech_df(df):
    conn = sqlite3.connect("dispatch_system.db")
    df.to_sql("technicians", conn, if_exists="replace", index=False)
    conn.close()

# -------------------------------------------------------------------
# 3. GEOGRAPHIC & ROUTING ENGINE
# -------------------------------------------------------------------
FAR_AREAS = ["MADINATY", "MOSTAKBAL", "TAGAMOA", "OCTOBER", "ISMAILIA", "KATAMEYA", "ZAMALEK", "QALYUB"]

CITY_COORDS = {
    "MADINATY CITY ( مدينتى )": (30.0917, 31.6295),
    "TAGAMOA 5 (التجمع الخامس)": (30.0074, 31.4312),
    "TAGAMOA 1 (التجمع الأول)": (30.0511, 31.4486),
    "SHOROUK (الشروق)": (30.1458, 31.6067),
    "AL MAADI ( المعادى )": (29.9602, 31.2569),
    "HELIOPOLIS (مصر الجديدة)": (30.0889, 31.3262),
    "NASR CITY (مدينة نصر)": (30.0561, 31.3301),
    "MOKKATAM ( المقطم )": (30.0167, 31.3000),
    "6TH OF OCTOBER CITY ( 6 أكتوبر )": (29.9722, 30.9439),
    "BADR CITY (مدينه بدر)": (30.1408, 31.7454),
}

def classify_distance(city_name):
    city_str = str(city_name).upper().strip()
    return "Far" if any(area in city_str for area in FAR_AREAS) else "Near"

def get_coordinates(city_name):
    city_str = str(city_name).strip()
    return next((v for k, v in CITY_COORDS.items() if k in city_str or city_str in k), (30.0444, 31.2357))

def build_gmaps_route_link(orders_df):
    locations = []
    for _, r in orders_df.iterrows():
        c_str = str(r['City']).strip()
        coords = get_coordinates(c_str)
        locations.append(f"{coords[0]},{coords[1]}")
    
    if not locations:
        return "#"
    origin = locations[0]
    destination = locations[-1]
    waypoints = "|".join(locations[1:-1]) if len(locations) > 2 else ""
    
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    if waypoints:
        url += f"&waypoints={waypoints}"
    return url

def generate_driver_whatsapp(phone, tech_name, orders):
    gmaps_url = build_gmaps_route_link(orders)
    msg = f"📱 *Daily Route & Work Orders for {tech_name}*\n"
    msg += f"Total Jobs: {len(orders)}\n"
    msg += f"🗺️ *Google Maps Navigation Link:* {gmaps_url}\n\n"
    
    for i, (_, row) in enumerate(orders.iterrows(), 1):
        prio = "🚨 VIP" if str(row.get('Priority', '')).lower() in ['high', 'vip', 'emergency'] else "Standard"
        slot = row.get('Time_Slot', 'Morning (9 AM - 1 PM)')
        msg += f"*{i}. WO:* {row.get('Work_Order', 'N/A')} [{prio}]\n"
        msg += f"⏰ *Slot:* {slot}\n"
        msg += f"📍 *Area:* {row.get('City', 'N/A')}\n"
        msg += f"🛠️ *Type:* {row.get('Service_Type', 'Standard')}\n"
        msg += f"------------------\n"
    
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "")
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

def generate_customer_whatsapp(phone, customer_name, wo_number, tech_name, slot):
    msg = f"Dear {customer_name},\n"
    msg += f"Your Mirage Service Request *#{wo_number}* has been scheduled for today!\n"
    msg += f"👨‍🔧 *Assigned Specialist:* {tech_name}\n"
    msg += f"⏰ *Time Slot:* {slot}\n\n"
    msg += "Our technician will contact you 30 minutes before arrival. Thank you!"
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "")
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

# -------------------------------------------------------------------
# 4. ADVANCED DISPATCH ENGINE
# -------------------------------------------------------------------
def run_smart_dispatch(orders_df, tech_df, allow_overflow=True):
    orders = orders_df.copy()
    orders['Distance_Type'] = orders['City'].apply(classify_distance)
    orders['Priority_Rank'] = orders['Priority'].apply(lambda x: 0 if str(x).lower() in ['vip', 'high', 'emergency'] else 1) if 'Priority' in orders.columns else 1
    if 'Time_Slot' not in orders.columns:
        orders['Time_Slot'] = np.where(np.random.rand(len(orders)) > 0.5, "Morning (9 AM - 1 PM)", "Evening (2 PM - 6 PM)")
    
    orders['Assigned_Tech'] = "Unassigned"
    orders['Stop_Sequence'] = 0
    
    tracker = {}
    for _, row in tech_df.iterrows():
        cap = row['capacity'] if row.get('shift_type', 'Full Day') == 'Full Day' else int(row['capacity'] * 0.5)
        tracker[row['name']] = {
            'brand': str(row['brand']).strip(),
            'vehicle': row['vehicle'],
            'capacity': max(1, cap),
            'phone': row['phone'],
            'home_zone': str(row.get('home_zone', '')).lower(),
            'parts': str(row.get('parts_inventory', '')).lower(),
            'assigned': 0
        }
    
    orders = orders.sort_values(by=['Priority_Rank', 'Time_Slot', 'Distance_Type'], ascending=[True, True, True])
    
    for idx, row in orders.iterrows():
        order_brand = str(row.get('Brand', '')).strip() if pd.notna(row.get('Brand')) else None
        req_part = str(row.get('Required_Part', '')).lower() if pd.notna(row.get('Required_Part')) else ""
        city_str = str(row['City']).lower()
        dist_type = row['Distance_Type']
        
        target_vehicle = "Car" if (dist_type == "Far" or "heavy" in req_part or "replacement" in req_part) else "Motorcycle"
        
        candidates = [
            name for name, info in tracker.items()
            if (not order_brand or info['brand'].lower() == order_brand.lower())
            and info['assigned'] < info['capacity']
            and info['vehicle'] == target_vehicle
            and (not req_part or req_part in info['parts'])
        ]
        
        if not candidates:
            candidates = [
                name for name, info in tracker.items()
                if (not order_brand or info['brand'].lower() == order_brand.lower())
                and info['assigned'] < info['capacity']
            ]
            
        if not candidates and allow_overflow:
            candidates = [
                name for name, info in tracker.items()
                if info['assigned'] < info['capacity']
            ]
            
        if candidates:
            home_matches = [c for c in candidates if tracker[c]['home_zone'] and tracker[c]['home_zone'] in city_str]
            selected_pool = home_matches if home_matches else candidates
            
            best_tech = min(selected_pool, key=lambda t: tracker[t]['assigned'])
            orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned'] += 1

    for tech in orders['Assigned_Tech'].unique():
        if tech == "Unassigned": continue
        t_mask = orders['Assigned_Tech'] == tech
        orders.loc[t_mask, 'Stop_Sequence'] = range(1, t_mask.sum() + 1)

    return orders, tracker

# -------------------------------------------------------------------
# 5. DASHBOARD LAYOUT & TABS
# -------------------------------------------------------------------
st.title("⚡ AI Fleet Command & Multi-Brand Dispatch System")

nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5, nav_tab6 = st.tabs([
    "🚀 Dispatch Hub", 
    "🗺️ Interactive Map", 
    "📱 Driver & Client Portals", 
    "🖨️ Printable Manifests",
    "📊 Analytics & Payroll", 
    "⚙️ Master Database Setup"
])

tech_df = get_tech_df()

# -------------------------------------------------------------------
# TAB 1: DISPATCH HUB (SEPARATE UPLOAD SLOTS PER WING)
# -------------------------------------------------------------------
with nav_tab1:
    st.header("📂 Daily Order Allocation by Company Wing")
    
    registered_wings = sorted([str(b).strip() for b in tech_df['brand'].unique() if pd.notna(b)])
    
    col_files, col_opts = st.columns([2, 1])
    
    all_uploaded_orders = []
    
    with col_files:
        st.subheader("📤 Upload Dedicated Orders per Wing")
        st.caption("Upload each wing's Excel sheet into its corresponding box below.")
        
        # Render a separate file uploader for each registered wing
        for wing in registered_wings:
            with st.expander(f"🏢 Wing: {wing}", expanded=True):
                wing_file = st.file_uploader(
                    f"Upload order file for {wing}", 
                    type=["xlsx", "csv"], 
                    key=f"uploader_{wing}"
                )
                if wing_file:
                    df_w = pd.read_csv(wing_file) if wing_file.name.endswith('.csv') else pd.read_excel(wing_file)
                    df_w['Brand'] = wing  # Stamp brand automatically
                    all_uploaded_orders.append(df_w)
                    st.success(f"Loaded {len(df_w)} orders for {wing}")
        
        # Optional: Custom or Unlisted Wing Upload
        with st.expander("➕ Upload Orders for Other / Unlisted Wing", expanded=False):
            custom_wing_name = st.text_input("Enter Wing/Brand Name", placeholder="e.g. Brand D")
            custom_file = st.file_uploader("Upload order file", type=["xlsx", "csv"], key="uploader_custom")
            if custom_file and custom_wing_name:
                df_c = pd.read_csv(custom_file) if custom_file.name.endswith('.csv') else pd.read_excel(custom_file)
                df_c['Brand'] = custom_wing_name.strip()
                all_uploaded_orders.append(df_c)
                st.success(f"Loaded {len(df_c)} orders for {custom_wing_name}")
                
    with col_opts:
        st.markdown("### Dispatch Settings")
        allow_overflow = st.checkbox("Allow Cross-Brand Overflow", value=True, help="Allow drivers from another wing to help out if a wing is over capacity.")
        fuel_cost_per_km = st.number_input("Est. Fuel Cost per KM (EGP)", value=4.5, step=0.5)
        base_bonus_rate = st.number_input("Driver Bonus Per Job Over 5 Jobs (EGP)", value=50, step=10)

    if all_uploaded_orders:
        df_raw = pd.concat(all_uploaded_orders, ignore_index=True)
        st.session_state['df_raw'] = df_raw
        
        st.markdown("---")
        st.markdown("### 📊 Order Summary Across Wings")
        wing_summary = df_raw['Brand'].value_counts().reset_index()
        wing_summary.columns = ['Wing / Brand', 'Total Orders Loaded']
        st.dataframe(wing_summary, use_container_width=True)
        
        if st.button("⚡ Run AI Sequence & Priority Dispatch", type="primary"):
            processed_orders, tracker = run_smart_dispatch(df_raw, tech_df, allow_overflow)
            st.session_state['processed_orders'] = processed_orders
            st.session_state['tracker'] = tracker
            
            st.subheader("📋 Dispatch Allocation Results")
            display_cols = [c for c in ['Work_Order', 'Brand', 'City', 'Time_Slot', 'Priority', 'Assigned_Tech', 'Stop_Sequence'] if c in processed_orders.columns]
            st.dataframe(processed_orders[display_cols], use_container_width=True)
            
            # Excel Export
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                processed_orders.to_excel(writer, sheet_name='Master Dispatch', index=False)
            st.download_button(
                label="📥 Download Master Dispatch Excel Report",
                data=buffer.getvalue(),
                file_name="Master_Daily_Dispatch_Plan.xlsx",
                mime="application/vnd.ms-excel",
                type="secondary"
            )

# -------------------------------------------------------------------
# TAB 2: INTERACTIVE ROUTE MAP
# -------------------------------------------------------------------
with nav_tab2:
    st.header("🗺️ Geographic Route & Stop Clustering")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        m = folium.Map(location=[30.0444, 31.2357], zoom_start=11)
        
        for idx, row in orders.iterrows():
            coords = get_coordinates(row['City'])
            tech = row['Assigned_Tech']
            dist = row['Distance_Type']
            seq = row.get('Stop_Sequence', 1)
            color = "blue" if dist == "Near" else "red"
            
            folium.Marker(
                location=coords,
                popup=f"Stop #{seq}<br>Order: {row.get('Work_Order', 'N/A')}<br>Wing: {row.get('Brand', 'N/A')}<br>Tech: {tech}<br>Area: {row['City']}",
                tooltip=f"Stop {seq}: {tech} ({row['City']})",
                icon=folium.Icon(color=color, icon="info-sign")
            ).add_to(m)
            
        st_folium(m, width=1200, height=500)
    else:
        st.info("Upload wing orders and run dispatch in Tab 1 first.")

# -------------------------------------------------------------------
# TAB 3: DRIVER & CLIENT WHATSAPP PORTALS
# -------------------------------------------------------------------
with nav_tab3:
    st.header("📱 Driver Route & Customer Dispatch Portals")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        techs = orders['Assigned_Tech'].unique()
        
        col_dr, col_cl = st.columns(2)
        
        with col_dr:
            st.subheader("👨‍🔧 Driver WhatsApp Route Links")
            for tech in techs:
                if tech == "Unassigned": continue
                t_orders = orders[orders['Assigned_Tech'] == tech].sort_values(by='Stop_Sequence')
                tech_info = tech_df[tech_df['name'] == tech].iloc[0] if not tech_df[tech_df['name'] == tech].empty else None
                phone = tech_info['phone'] if tech_info is not None else "201000000000"
                wa_url = generate_driver_whatsapp(phone, tech, t_orders)
                
                with st.expander(f"📲 {tech} ({len(t_orders)} Jobs)"):
                    st.markdown(f"[🚀 **Send Route & Navigation to Driver via WhatsApp**]({wa_url})", unsafe_allow_html=True)
                    st.dataframe(t_orders[['Stop_Sequence', 'Work_Order', 'Brand', 'City', 'Time_Slot']], use_container_width=True)
                    
        with col_cl:
            st.subheader("📲 Customer Automated SMS/WhatsApp Engine")
            for idx, r in orders.iterrows():
                if r['Assigned_Tech'] == "Unassigned": continue
                cust_phone = str(r.get('Customer_Phone', '201000000000'))
                cust_name = str(r.get('Customer_Name', 'Valued Customer'))
                wo = str(r.get('Work_Order', 'N/A'))
                tech = r['Assigned_Tech']
                slot = r.get('Time_Slot', 'Morning (9 AM - 1 PM)')
                
                cust_wa_url = generate_customer_whatsapp(cust_phone, cust_name, wo, tech, slot)
                st.markdown(f"**WO #{wo}** ({cust_name}) ➔ [{tech}] | [📩 Send Customer Notification]({cust_wa_url})")
    else:
        st.info("Run dispatch to activate messaging portals.")

# -------------------------------------------------------------------
# TAB 4: PRINTABLE MANIFESTS
# -------------------------------------------------------------------
with nav_tab4:
    st.header("🖨️ Printable Daily Driver Manifests")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        selected_tech = st.selectbox("Select Driver to View Manifest", [t for t in orders['Assigned_Tech'].unique() if t != "Unassigned"])
        
        if selected_tech:
            t_orders = orders[orders['Assigned_Tech'] == selected_tech].sort_values(by='Stop_Sequence')
            st.markdown(f"### 📋 Daily Work Sheet: **{selected_tech}**")
            st.markdown("---")
            for idx, r in t_orders.iterrows():
                st.markdown(f"**Stop #{r.get('Stop_Sequence', 1)}** | **WO #:** {r.get('Work_Order', 'N/A')} | **Wing:** {r.get('Brand', 'N/A')} | **Time:** {r.get('Time_Slot', 'N/A')} | **Area:** {r.get('City', 'N/A')}")
                st.markdown("Customer Sign-off: _______________________")
                st.markdown("---")
            st.caption("Press Ctrl+P (or Cmd+P) in your browser to print this manifest.")
    else:
        st.info("Run dispatch to generate manifests.")

# -------------------------------------------------------------------
# TAB 5: ANALYTICS, FUEL & BONUS PAYROLL
# -------------------------------------------------------------------
with nav_tab5:
    st.header("📊 Performance, Fuel & Driver Bonus Analytics")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        tracker = st.session_state['tracker']
        
        col1, col2, col3, col4 = st.columns(4)
        total_orders = len(orders)
        assigned_count = len(orders[orders['Assigned_Tech'] != 'Unassigned'])
        far_count = len(orders[orders['Distance_Type'] == 'Far'])
        
        est_distance = (far_count * 35) + ((total_orders - far_count) * 12)
        total_fuel_cost = est_distance * fuel_cost_per_km
        
        col1.metric("Total Jobs", total_orders)
        col2.metric("Allocation Efficiency", f"{(assigned_count/total_orders)*100:.1f}%")
        col3.metric("Est. Fleet Distance", f"{est_distance} KM")
        col4.metric("Est. Fuel Allowance", f"{total_fuel_cost:,.0f} EGP")
        
        st.subheader("👨‍🔧 Driver Productivity & Calculated Payouts")
        payroll_rows = []
        for k, v in tracker.items():
            bonus = max(0, (v['assigned'] - 5) * base_bonus_rate)
            fuel = (v['assigned'] * 15) * fuel_cost_per_km
            payroll_rows.append({
                "Technician": k,
                "Vehicle": v['vehicle'],
                "Wing / Brand": v['brand'],
                "Jobs Completed": v['assigned'],
                "Daily Capacity": v['capacity'],
                "Fuel Allowance (EGP)": f"{fuel:,.0f}",
                "Productivity Bonus (EGP)": f"{bonus:,.0f}"
            })
        st.dataframe(pd.DataFrame(payroll_rows), use_container_width=True)
    else:
        st.info("Run dispatch to populate analytics.")

# -------------------------------------------------------------------
# TAB 6: MASTER DATABASE SETUP
# -------------------------------------------------------------------
with nav_tab6:
    st.header("⚙️ Master Multi-Brand Database & Vehicle Inventory")
    
    st.subheader("📤 Bulk Upload Brand Technician Databases")
    uploaded_brand_files = st.file_uploader("Select technician database files", type=["xlsx", "csv"], accept_multiple_files=True, key="tech_multi_uploader")
    
    if uploaded_brand_files:
        all_new_techs = []
        for file in uploaded_brand_files:
            b_df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            if 'brand' not in [c.lower() for c in b_df.columns]:
                brand_name = file.name.split('.')[0].replace('_', ' ').replace('Techs', '').replace('techs', '').strip()
                b_df['brand'] = brand_name
            all_new_techs.append(b_df)
            
        if all_new_techs and st.button("📥 Import All Brand Databases", type="primary"):
            merged_techs = pd.concat(all_new_techs, ignore_index=True)
            merged_techs.columns = [c.lower().strip() for c in merged_techs.columns]
            save_tech_df(merged_techs)
            st.success("✅ Master Database updated successfully!")
            st.rerun()
            
    st.markdown("---")
    st.subheader("✏️ Interactive Master Technician Table")
    edited_df = st.data_editor(tech_df, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Save Database Changes"):
        save_tech_df(edited_df)
        st.success("Database saved successfully!")
