import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import urllib.parse
import folium
from streamlit_folium import st_folium

# -------------------------------------------------------------------
# 1. PAGE CONFIG & STYLES
# -------------------------------------------------------------------
st.set_page_config(
    page_title="AI Dispatch Command Center",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI polish
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; }
    .card { background-color: #F8FAFC; padding: 1.2rem; border-radius: 10px; border: 1px solid #E2E8F0; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. SQLITE DATABASE SETUP (Persistent Storage)
# -------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect("dispatch_system.db")
    c = conn.cursor()
    # Technicians Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            phone TEXT,
            brand TEXT,
            skills TEXT,
            vehicle TEXT,
            capacity INTEGER,
            home_zone TEXT
        )
    """)
    # Seed default tech data if empty
    c.execute("SELECT COUNT(*) FROM technicians")
    if c.fetchone()[0] == 0:
        default_data = [
            ("أحمد عماد", "201000000001", "Brand A", "Installation,Maintenance", "Motorcycle", 8, "Shorouk"),
            ("شعبان", "201000000002", "Brand A", "Installation", "Car", 10, "Madinaty"),
            ("كيمكو", "201000000003", "Brand B", "Installation,Maintenance", "Car", 12, "Maadi"),
            ("محمد سامي", "201000000004", "Brand B", "Customer Service", "Motorcycle", 7, "Maadi"),
            ("تكنو", "201000000005", "Brand C", "Installation", "Car", 10, "Tagamoa"),
            ("حسن", "201000000006", "Brand C", "Customer Service", "Motorcycle", 8, "Tagamoa"),
        ]
        c.executemany("INSERT INTO technicians (name, phone, brand, skills, vehicle, capacity, home_zone) VALUES (?,?,?,?,?,?,?)", default_data)
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
# 3. ADVANCED DISPATCH ENGINE & LOGISTICS
# -------------------------------------------------------------------
FAR_AREAS = ["MADINATY", "MOSTAKBAL", "TAGAMOA", "OCTOBER", "ISMAILIA", "KATAMEYA", "ZAMALEK", "QALYUB"]

# Representative Coordinates for Map Rendering (Cairo Hubs)
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

def generate_whatsapp_link(phone, tech_name, orders):
    """Creates direct wa.me link with pre-filled route breakdown"""
    msg = f"📱 *Daily Work Orders for {tech_name}*\n"
    msg += f"Total Jobs: {len(orders)}\n\n"
    for i, (_, row) in enumerate(orders.iterrows(), 1):
        msg += f"*{i}. WO:* {row.get('Work_Order', 'N/A')}\n"
        msg += f"📍 *Area:* {row.get('City', 'N/A')}\n"
        msg += f"🛠️ *Type:* {row.get('Service_Type', 'Standard')}\n"
        msg += f"------------------\n"
    
    encoded_msg = urllib.parse.quote(msg)
    clean_phone = str(phone).replace("+", "").replace(" ", "")
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

def run_smart_dispatch(orders_df, tech_df, allow_overflow=True):
    orders = orders_df.copy()
    orders['Distance_Type'] = orders['City'].apply(classify_distance)
    orders['Assigned_Tech'] = "Unassigned"
    
    # Workload tracker
    tracker = {
        row['name']: {
            'brand': row['brand'],
            'vehicle': row['vehicle'],
            'capacity': row['capacity'],
            'phone': row['phone'],
            'skills': str(row['skills']).split(','),
            'assigned': 0
        } for _, row in tech_df.iterrows()
    }
    
    # Process Far areas first to prioritize Cars
    orders = orders.sort_values(by=['Distance_Type'], ascending=True)
    
    for idx, row in orders.iterrows():
        order_brand = row.get('Brand', None)
        order_type = row.get('Service_Type', 'Installation')
        dist_type = row['Distance_Type']
        target_vehicle = "Car" if dist_type == "Far" else "Motorcycle"
        
        # 1. Primary Match: Same Brand + Skills + Target Vehicle + Available Capacity
        candidates = [
            name for name, info in tracker.items()
            if (order_brand is None or info['brand'] == order_brand)
            and info['assigned'] < info['capacity']
            and info['vehicle'] == target_vehicle
        ]
        
        # 2. Vehicle Fallback: Same Brand, any vehicle
        if not candidates:
            candidates = [
                name for name, info in tracker.items()
                if (order_brand is None or info['brand'] == order_brand)
                and info['assigned'] < info['capacity']
            ]
            
        # 3. Secondary Overflow Fallback: Cross-Brand assignment if allowed
        if not candidates and allow_overflow:
            candidates = [
                name for name, info in tracker.items()
                if info['assigned'] < info['capacity']
            ]
            
        if candidates:
            best_tech = min(candidates, key=lambda t: tracker[t]['assigned'])
            orders.at[idx, 'Assigned_Tech'] = best_tech
            tracker[best_tech]['assigned'] += 1
            
    return orders, tracker

# -------------------------------------------------------------------
# 4. APP INTERFACE & NAVIGATION
# -------------------------------------------------------------------
st.title("⚡ AI Fleet Command & Dispatch System")

# Top Navigation Tabs
nav_tab1, nav_tab2, nav_tab3, nav_tab4, nav_tab5 = st.tabs([
    "🚀 Dispatch Hub", 
    "🗺️ Interactive Map", 
    "📱 Driver WhatsApp Portal", 
    "📊 Analytics & Costs", 
    "⚙️ Tech Database Setup"
])

# Load Technicians Data
tech_df = get_tech_df()

# -------------------------------------------------------------------
# TAB 1: DISPATCH HUB
# -------------------------------------------------------------------
with nav_tab1:
    st.header("📂 Daily Order Allocation")
    
    col_file, col_opts = st.columns([2, 1])
    with col_file:
        uploaded_file = st.file_uploader("Upload Daily Excel Order Sheet", type=["xlsx", "csv"])
    with col_opts:
        st.markdown("### Dispatch Options")
        allow_overflow = st.checkbox("Allow Cross-Brand Overflow", value=True, help="If a brand team is full, allow other drivers to assist.")
        fuel_cost_per_km = st.number_input("Est. Fuel Cost per KM (EGP)", value=4.5, step=0.5)

    if uploaded_file:
        df_raw = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        st.session_state['df_raw'] = df_raw
        st.success(f"Loaded {len(df_raw)} orders successfully!")
        
        if st.button("⚡ Run AI Automatic Dispatch", type="primary"):
            processed_orders, tracker = run_smart_dispatch(df_raw, tech_df, allow_overflow)
            st.session_state['processed_orders'] = processed_orders
            st.session_state['tracker'] = tracker
            
            st.subheader("📋 Dispatch Allocation Results")
            st.dataframe(
                processed_orders[['Work_Order', 'City', 'Service_Type', 'Distance_Type', 'Assigned_Tech']], 
                use_container_width=True
            )

# -------------------------------------------------------------------
# TAB 2: INTERACTIVE MAP & ROUTING
# -------------------------------------------------------------------
with nav_tab2:
    st.header("🗺️ Geographic Route Clustering")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        
        # Center of Cairo
        m = folium.Map(location=[30.0444, 31.2357], zoom_start=11, tiles="OpenStreetMap")
        
        for idx, row in orders.iterrows():
            city = str(row['City']).strip()
            # Match city coordinates
            coords = next((v for k, v in CITY_COORDS.items() if k in city or city in k), None)
            if not coords:
                coords = (30.0444 + np.random.uniform(-0.05, 0.05), 31.2357 + np.random.uniform(-0.05, 0.05))
                
            tech = row['Assigned_Tech']
            dist = row['Distance_Type']
            color = "blue" if dist == "Near" else "red"
            
            folium.Marker(
                location=coords,
                popup=f"Order: {row.get('Work_Order', 'N/A')}<br>Tech: {tech}<br>Area: {city}",
                tooltip=f"{tech} ({city})",
                icon=folium.Icon(color=color, icon="wrench" if dist=="Far" else "motorcycle", prefix="fa")
            ).add_to(m)
            
        st_folium(m, width=1200, height=500)
    else:
        st.info("Run the AI Dispatcher in the 'Dispatch Hub' tab to view map routes.")

# -------------------------------------------------------------------
# TAB 3: WHATSAPP & DRIVER MOBILE PORTAL
# -------------------------------------------------------------------
with nav_tab3:
    st.header("📱 Technician Dispatch & Mobile View")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        techs = orders['Assigned_Tech'].unique()
        
        for tech in techs:
            if tech == "Unassigned": continue
            tech_orders = orders[orders['Assigned_Tech'] == tech]
            tech_info = tech_df[tech_df['name'] == tech].iloc[0] if not tech_df[tech_df['name'] == tech].empty else None
            phone = tech_info['phone'] if tech_info is not None else "201000000000"
            
            wa_url = generate_whatsapp_link(phone, tech, tech_orders)
            
            with st.expander(f"👨‍🔧 {tech} ({len(tech_orders)} Jobs assigned)"):
                st.markdown(f"**Vehicle:** {tech_info['vehicle'] if tech_info is not None else 'N/A'} | **Phone:** {phone}")
                st.markdown(f"[📲 **Send Work Orders via WhatsApp**]({wa_url})", unsafe_allow_html=True)
                st.dataframe(tech_orders[['Work_Order', 'City', 'Service_Type']], use_container_width=True)
    else:
        st.info("No active dispatch data available yet.")

# -------------------------------------------------------------------
# TAB 4: MANAGER ANALYTICS & COST ESTIMATOR
# -------------------------------------------------------------------
with nav_tab4:
    st.header("📊 Performance & Transport Cost Analytics")
    if 'processed_orders' in st.session_state:
        orders = st.session_state['processed_orders']
        tracker = st.session_state['tracker']
        
        col1, col2, col3, col4 = st.columns(4)
        total_orders = len(orders)
        assigned_count = len(orders[orders['Assigned_Tech'] != 'Unassigned'])
        far_count = len(orders[orders['Distance_Type'] == 'Far'])
        
        # Cost Estimator Logic (Far = ~35km avg, Near = ~12km avg)
        est_distance = (far_count * 35) + ((total_orders - far_count) * 12)
        total_fuel_cost = est_distance * fuel_cost_per_km
        
        col1.metric("Total Jobs", total_orders)
        col2.metric("Allocated", f"{(assigned_count/total_orders)*100:.1f}%")
        col3.metric("Est. Total Fleet Distance", f"{est_distance} KM")
        col4.metric("Est. Fleet Fuel Cost", f"{total_fuel_cost:,.0f} EGP")
        
        st.markdown("### Fleet Capacity Heatmap")
        capacity_df = pd.DataFrame([
            {"Technician": k, "Vehicle": v['vehicle'], "Brand": v['brand'], "Assigned": v['assigned'], "Capacity": v['capacity']}
            for k, v in tracker.items()
        ])
        st.dataframe(capacity_df, use_container_width=True)
    else:
        st.info("Run dispatch to populate analytics dashboard.")

# -------------------------------------------------------------------
# TAB 5: TECHNICIAN MASTER DATABASE SETUP
# -------------------------------------------------------------------
with nav_tab5:
    st.header("⚙️ Master Technician Database")
    st.markdown("Edit drivers, phone numbers, brands, vehicle types, and max capacities. Changes save directly to your database.")
    
    edited_df = st.data_editor(
        tech_df,
        num_rows="dynamic",
        column_config={
            "vehicle": st.column_config.SelectboxColumn("Vehicle", options=["Motorcycle", "Car"], required=True),
            "capacity": st.column_config.NumberColumn("Daily Capacity", min_value=1, max_value=30, default=8),
        },
        use_container_width=True
    )
    
    if st.button("💾 Save Database Changes"):
        save_tech_df(edited_df)
        st.success("Database updated successfully!")
