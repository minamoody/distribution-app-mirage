import streamlit as st
import pandas as pd
from datetime import datetime, time
import io
import urllib.parse
import os
import math

# ==========================================
# 0. SAFE DEPENDENCY & API IMPORTS
# ==========================================
# Import Google Generative AI with fallback protection
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ModuleNotFoundError:
    HAS_GENAI = False

# Setup Streamlit Page Config
st.set_page_config(
    page_title="Mirage Fleet Command & Field Logistics",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe API Key Initialization
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
# 1. GLOBAL CSS & CUSTOM STYLING
# ==========================================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .status-badge-pending {
        background-color: #FEF3C7;
        color: #D97706;
        padding: 0.2rem 0.6rem;
        border-radius: 0.25rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-badge-progress {
        background-color: #DBEAFE;
        color: #2563EB;
        padding: 0.2rem 0.6rem;
        border-radius: 0.25rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-badge-completed {
        background-color: #D1FAE5;
        color: #059669;
        padding: 0.2rem 0.6rem;
        border-radius: 0.25rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. SESSION STATE DATA INITIALIZATION
# ==========================================
if "work_orders" not in st.session_state:
    st.session_state.work_orders = {
        "Ahmed Hassan": [
            {
                "id": "WO-901",
                "client": "Apex Logistics Hub",
                "contact": "+201012345678",
                "address": "Plot 44, Smart Village, Giza",
                "lat": 30.0731,
                "lon": 31.0182,
                "priority": "High",
                "status": "In Progress",
                "service_type": "HVAC Central Cooling Failure",
                "details": "Main intake compressor overheating. Error Code E-402 visible on main control board.",
                "est_hours": 3.5,
                "actual_hours": 0.0,
                "photos": [
                    "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600",
                    "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=600"
                ],
                "logs": [],
                "created_at": "2026-08-07 08:30"
            },
            {
                "id": "WO-904",
                "client": "Cilantro Coffee Branch #4",
                "contact": "+201098765432",
                "address": "Road 9, Maadi, Cairo",
                "lat": 29.9602,
                "lon": 31.2569,
                "priority": "Medium",
                "status": "Pending",
                "service_type": "Espresso Machine Calibration",
                "details": "Group Head 2 experiencing pressure drop during peak hours. Needs gasket replacement.",
                "est_hours": 1.5,
                "actual_hours": 0.0,
                "photos": [
                    "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=600"
                ],
                "logs": [],
                "created_at": "2026-08-07 10:15"
            }
        ],
        "Omar Malak": [
            {
                "id": "WO-902",
                "client": "Mirage Corporate HQ",
                "contact": "+201112223334",
                "address": "Sector 1, New Cairo",
                "lat": 30.0271,
                "lon": 31.4398,
                "priority": "Critical",
                "status": "In Progress",
                "service_type": "Main Electrical Substation Audit",
                "details": "Secondary breaker tripping under peak load. Thermal camera inspection required immediately.",
                "est_hours": 4.0,
                "actual_hours": 1.5,
                "photos": [
                    "https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=600"
                ],
                "logs": [],
                "created_at": "2026-08-07 07:45"
            },
            {
                "id": "WO-905",
                "client": "Starbucks Maadi Sarayat",
                "contact": "+201005554433",
                "address": "Street 14, Maadi, Cairo",
                "lat": 29.9580,
                "lon": 31.2610,
                "priority": "Low",
                "status": "Pending",
                "service_type": "Water Filter System Flush",
                "details": "Quarterly preventative maintenance for filtration rig.",
                "est_hours": 1.0,
                "actual_hours": 0.0,
                "photos": [],
                "logs": [],
                "created_at": "2026-08-07 11:00"
            }
        ],
        "Youssef Ali": [
            {
                "id": "WO-903",
                "client": "Zamalek Design Studio",
                "contact": "+201223344556",
                "address": "26 July Street, Zamalek, Cairo",
                "lat": 30.0626,
                "lon": 31.2201,
                "priority": "Low",
                "status": "Pending",
                "service_type": "Fiber Network Rack Re-cabling",
                "details": "Re-organize patch cables and verify server room grounding.",
                "est_hours": 2.0,
                "actual_hours": 0.0,
                "photos": [],
                "logs": [],
                "created_at": "2026-08-07 09:00"
            }
        ]
    }

if "eod_excel_records" not in st.session_state:
    st.session_state.eod_excel_records = []

if "technician_ratings" not in st.session_state:
    st.session_state.technician_ratings = [
        {"tech": "Ahmed Hassan", "order_id": "WO-880", "rating": 5, "feedback": "Fast resolution, very clean work."},
        {"tech": "Omar Malak", "order_id": "WO-879", "rating": 5, "feedback": "Excellent technical knowledge on breaker panels."}
    ]


# ==========================================
# 3. HELPER MATH & AI PROCESSING FUNCTIONS
# ==========================================
def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points in kilometers.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)

def run_gemini_ai_parser(raw_summary_text):
    """
    Parses field technician notes into structured executive summaries using Gemini API.
    Falls back gracefully if API or library is unavailable.
    """
    if not AI_AVAILABLE:
        # Fallback structured response
        return f"""
        • **Key Actions:** Processed technician log locally (AI Offline or API key not set).
        • **Escalations/Issues:** Manual review recommended.
        • **Executive Summary:** {raw_summary_text[:120]}...
        """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are an expert Fleet Logistics Dispatcher AI. Analyze this field technician work completion log:
        
        Raw Summary: "{raw_summary_text}"
        
        Extract and format the response into exactly three bullet points:
        - **Key Actions:** [Summary of work completed and parts serviced]
        - **Escalations & Unresolved Issues:** [List any outstanding issues, required parts, or follow-ups]
        - **Executive Summary:** [One clean sentence suitable for executive reports]
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"• **AI Processing Error:** {str(e)}\n• **Raw Text Logged:** {raw_summary_text}"

def log_to_eod_excel(tech_name, order_id, client, raw_notes, ai_analysis):
    """
    Appends processed technician summaries into the Master End-of-Day record state.
    """
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Technician Name": tech_name,
        "Work Order ID": order_id,
        "Client Name": client,
        "Technician Summary Notes": raw_notes,
        "AI Analysis & Action Plan": ai_analysis
    }
    st.session_state.eod_excel_records.append(entry)

def generate_whatsapp_url(phone_number, text_message):
    """
    Encodes phone number and text into a direct web WhatsApp link.
    """
    clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")
    encoded_text = urllib.parse.quote(text_message)
    return f"https://wa.me/{clean_phone}?text={encoded_text}"


# ==========================================
# 4. SIDEBAR NAVIGATION CONTROLLER
# ==========================================
st.sidebar.image("https://via.placeholder.com/250x70.png?text=MIRAGE+FLEET+COMMAND", use_container_width=True)
st.sidebar.markdown("---")

nav_choice = st.sidebar.radio(
    "Navigation Menu",
    [
        "👨‍🔧 Technician Portal & Work Orders",
        "🎯 Smart Dispatch & Geofence Engine",
        "💬 WhatsApp & Customer Portal",
        "📊 End-of-Day Excel Reports & Scorecards",
        "⚙️ Fleet Admin & Data Management"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("System Status")
if AI_AVAILABLE:
    st.sidebar.success("🟢 Gemini AI Engine: Active")
else:
    st.sidebar.warning("⚠️ Gemini AI: Standard Mode")

st.sidebar.info(f"📅 Current Date: {datetime.now().strftime('%Y-%m-%d')}")


# ==========================================
# 5. MODULE 1: TECHNICIAN PORTAL (DRILL-DOWN)
# ==========================================
if nav_choice == "👨‍🔧 Technician Portal & Work Orders":
    st.markdown('<div class="main-header">👨‍🔧 Field Technician Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Drill down into technician assignments, inspect work order details, view photos, and run AI End-of-Day report sync.</div>', unsafe_allow_html=True)
    
    # Technician Selection Header
    col_tech_select, col_stats_1, col_stats_2 = st.columns([2, 1, 1])
    
    with col_tech_select:
        tech_list = list(st.session_state.work_orders.keys())
        selected_tech = st.selectbox("📌 Select Field Technician:", tech_list)
    
    tech_orders = st.session_state.work_orders[selected_tech]
    
    with col_stats_1:
        st.metric("Total Jobs Assigned", len(tech_orders))
    with col_stats_2:
        completed_count = sum(1 for o in tech_orders if o['status'] == 'Completed')
        st.metric("Completed Today", completed_count)
        
    st.markdown("---")
    
    if not tech_orders:
        st.info(f"No active work orders found for **{selected_tech}**.")
    else:
        # Step 1: Work Order Drill-Down Selection
        st.subheader(f"Assigned Work Orders for {selected_tech}")
        
        # Format selector display labels
        order_options = []
        for o in tech_orders:
            status_symbol = "🟡" if o["status"] == "Pending" else ("🔵" if o["status"] == "In Progress" else "🟢")
            order_options.append(f"{status_symbol} {o['id']} | {o['client']} ({o['priority']} Priority)")
            
        selected_order_idx = st.selectbox("Click to Select & Inspect Work Order:", range(len(order_options)), format_func=lambda x: order_options[x])
        
        current_wo = tech_orders[selected_order_idx]
        
        # Step 2: Comprehensive Work Order Inspection Interface
        st.markdown(f"### Work Order Card: `{current_wo['id']}`")
        
        # Work Order Details Card Grid
        with st.expander("📋 Full Work Order Specifications", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(f"**Client Name:** {current_wo['client']}")
                st.markdown(f"**Contact Number:** `{current_wo['contact']}`")
                st.markdown(f"**Created At:** {current_wo['created_at']}")
                
            with col_b:
                st.markdown(f"**Service Category:** {current_wo['service_type']}")
                st.markdown(f"**Priority Level:** `{current_wo['priority']}`")
                st.markdown(f"**Current Status:** `{current_wo['status']}`")
                
            with col_c:
                st.markdown(f"**Est. Duration:** {current_wo['est_hours']} hrs")
                st.markdown(f"**GPS Coordinates:** `{current_wo['lat']}, {current_wo['lon']}`")
                st.markdown(f"**Location Address:** {current_wo['address']}")
                
            st.markdown("---")
            st.markdown("**Detailed Issue Description & Dispatch Notes:**")
            st.info(current_wo['details'])
            
        # Step 3: Attached Photos & Document Evidence
        st.subheader("📷 Site Photos & Visual Evidence")
        
        if current_wo["photos"]:
            photo_cols = st.columns(min(len(current_wo["photos"]), 3))
            for i, photo_url in enumerate(current_wo["photos"]):
                with photo_cols[i % 3]:
                    st.image(photo_url, caption=f"Attachment #{i+1} for {current_wo['id']}", use_container_width=True)
        else:
            st.warning("No photos currently attached to this work order.")
            
        # Photo Upload Pipeline Simulator
        with st.form(key=f"upload_form_{current_wo['id']}"):
            uploaded_img = st.file_uploader("Upload New Site Photo / Evidence:", type=["jpg", "png", "jpeg"])
            upload_submit = st.form_submit_button("Upload Attachment")
            if upload_submit:
                if uploaded_img is not None:
                    # Simulate adding photo to list
                    current_wo["photos"].append("https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=600")
                    st.success("Photo successfully attached to work order record!")
                    st.rerun()
                else:
                    st.warning("Please choose an image file first.")

        st.markdown("---")
        
        # Step 4: Technician Completion Summary & AI EOD Excel Pipeline
        st.subheader("📝 Work Completion Summary & AI EOD Logging")
        st.caption("Enter the technician's notes below. The Gemini AI engine will structure the job notes, extract key actions, and automatically sync it to the master End-of-Day Excel report.")
        
        with st.form(key=f"summary_form_{current_wo['id']}"):
            actual_hrs = st.number_input("Actual Time Spent (Hours):", min_value=0.25, max_value=24.0, value=current_wo["est_hours"], step=0.25)
            
            summary_notes = st.text_area(
                "Technician Field Summary / Work Performed / Parts Replaced:",
                placeholder="E.g., Arrived at site, performed diagnostic on chiller unit. Replaced faulty capacitor and pressure valve. Tested unit for 45 minutes under load—temperature stabilized at 4°C. Client signed off on completion.",
                height=130
            )
            
            submit_eod_btn = st.form_submit_button("🚀 Submit Notes & Sync to EOD Excel", type="primary")
            
            if submit_eod_btn:
                if not summary_notes.strip():
                    st.error("Please enter completion notes before submitting.")
                else:
                    with st.spinner("AI Engine parsing completion notes and compiling EOD log..."):
                        # Run AI Analysis
                        ai_parsed_result = run_gemini_ai_parser(summary_notes)
                        
                        # Update session state work order
                        current_wo["status"] = "Completed"
                        current_wo["actual_hours"] = actual_hrs
                        current_wo["logs"].append(summary_notes)
                        
                        # Log to Excel Database
                        log_to_eod_excel(
                            tech_name=selected_tech,
                            order_id=current_wo['id'],
                            client=current_wo['client'],
                            raw_notes=summary_notes,
                            ai_analysis=ai_parsed_result
                        )
                        
                    st.success(f"Work Order {current_wo['id']} marked as COMPLETED and saved to EOD Excel Master!")
                    st.markdown("#### 🤖 Generated AI Analysis & Executive Summary")
                    st.info(ai_parsed_result)


# ==========================================
# 6. MODULE 2: SMART DISPATCH & GEOFENCING
# ==========================================
elif nav_choice == "🎯 Smart Dispatch & Geofence Engine":
    st.markdown('<div class="main-header">🎯 Smart Dispatch & GPS Geofence Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time GPS tracking, automatic proximity status triggers, and distance calculation algorithms.</div>', unsafe_allow_html=True)
    
    col_map_view, col_geo_tools = st.columns([2, 1])
    
    # Compile coordinates
    map_records = []
    for tech, orders in st.session_state.work_orders.items():
        for order in orders:
            map_records.append({
                "lat": order["lat"],
                "lon": order["lon"],
                "Technician": tech,
                "Work Order": order["id"],
                "Client": order["client"],
                "Status": order["status"]
            })
    df_map = pd.DataFrame(map_records)
    
    with col_map_view:
        st.subheader("🗺️ Live Dispatch GPS Location Map")
        st.map(df_map, zoom=10, use_container_width=True)
        st.dataframe(df_map[["Work Order", "Technician", "Client", "Status", "lat", "lon"]], use_container_width=True)
        
    with col_geo_tools:
        st.subheader("📡 Live Geofence Simulator")
        st.caption("Simulate a technician's live phone GPS coordinates to test automatic status transitions.")
        
        target_wo_id = st.selectbox("Target Work Order:", df_map["Work Order"].tolist())
        
        # Locate selected order
        matched_order = None
        for tech, orders in st.session_state.work_orders.items():
            for o in orders:
                if o["id"] == target_wo_id:
                    matched_order = o
                    break
                    
        if matched_order:
            st.markdown(f"**Target Site:** {matched_order['client']}")
            st.markdown(f"**Site Coordinates:** `{matched_order['lat']}, {matched_order['lon']}`")
            
            st.markdown("---")
            st.markdown("**Simulate Live Tech Coordinates:**")
            
            sim_lat = st.number_input("Tech GPS Lat:", value=matched_order["lat"] + 0.003, format="%.4f")
            sim_lon = st.number_input("Tech GPS Lon:", value=matched_order["lon"] - 0.002, format="%.4f")
            
            # Haversine Distance
            dist_km = calculate_haversine_distance(sim_lat, sim_lon, matched_order["lat"], matched_order["lon"])
            dist_meters = int(dist_km * 1000)
            
            st.metric("Distance to Site", f"{dist_meters} meters", delta=f"{dist_km} km")
            
            # Geofence Threshold Check (500m)
            if dist_meters <= 500:
                st.success("🟢 WITHIN GEOFENCE RADIUS (< 500m)")
                st.info("⚡ Automatic System Action: Status toggled to **'In Progress / On Site'**")
                matched_order["status"] = "In Progress"
            else:
                st.warning("🔴 OUTSIDE GEOFENCE RADIUS")
                st.caption("Technician is currently en route.")


# ==========================================
# 7. MODULE 3: WHATSAPP & CUSTOMER PORTAL
# ==========================================
elif nav_choice == "💬 WhatsApp & Customer Portal":
    st.markdown('<div class="main-header">💬 WhatsApp Dispatch & Customer Service</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Send automated WhatsApp notifications, generate shareable links, and collect client feedback.</div>', unsafe_allow_html=True)
    
    # Gather all orders
    all_flat_orders = [o for sublist in st.session_state.work_orders.values() for o in sublist]
    order_labels = [f"{o['id']} - {o['client']} ({o['contact']})" for o in all_flat_orders]
    
    col_wa_1, col_wa_2 = st.columns(2)
    
    with col_wa_1:
        st.subheader("✉️ Automated WhatsApp Dispatcher")
        
        selected_wa_idx = st.selectbox("Select Customer Work Order:", range(len(order_labels)), format_func=lambda x: order_labels[x])
        target_wa_order = all_flat_orders[selected_wa_idx]
        
        eta_min = st.slider("Technician ETA (Minutes):", 5, 120, 25)
        
        msg_template = f"Hello {target_wa_order['client']}, your field technician for service {target_wa_order['id']} ({target_wa_order['service_type']}) is en route. Estimated arrival in {eta_min} minutes. Please ensure job site access."
        
        custom_wa_msg = st.text_area("Message Content:", value=msg_template, height=130)
        
        wa_url = generate_whatsapp_url(target_wa_order["contact"], custom_wa_msg)
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer;">
                    📲 Open WhatsApp & Send Notification
                </button>
            </a>
        """, unsafe_allow_html=True)
        
    with col_wa_2:
        st.subheader("⭐ Post-Service Customer Ratings")
        st.caption("Simulate customer feedback logging post-service completion.")
        
        with st.form(key="rating_form"):
            tech_rated = st.selectbox("Technician Name:", list(st.session_state.work_orders.keys()))
            rated_order_id = st.text_input("Work Order ID:", value=target_wa_order["id"])
            stars = st.select_slider("Rating Stars:", options=[1, 2, 3, 4, 5], value=5)
            comments = st.text_area("Customer Comments:", "Technician arrived on time, was polite, and fixed the equipment fast.")
            
            submit_rating = st.form_submit_button("Submit Rating & Log")
            if submit_rating:
                st.session_state.technician_ratings.append({
                    "tech": tech_rated,
                    "order_id": rated_order_id,
                    "rating": stars,
                    "feedback": comments
                })
                st.success("Customer feedback logged successfully!")


# ==========================================
# 8. MODULE 4: EXCEL EOD REPORTS & SCORECARDS
# ==========================================
elif nav_choice == "📊 End-of-Day Excel Reports & Scorecards":
    st.markdown('<div class="main-header">📊 End-of-Day Excel Reports & Scorecards</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Export consolidated daily logs, AI executive analyses, and technician KPIs directly to Excel.</div>', unsafe_allow_html=True)
    
    # Top Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total EOD Logs", len(st.session_state.eod_excel_records))
    m2.metric("First-Time Fix Rate", "95.4%", "+1.2%")
    m3.metric("Avg Response Time", "34 Mins", "-4 Mins")
    m4.metric("Avg Customer Rating", "4.9 / 5.0", "⭐")
    
    st.markdown("---")
    
    st.subheader("📋 Master End-of-Day Summary Table")
    
    if not st.session_state.eod_excel_records:
        st.warning("No End-of-Day entries logged yet. Complete a work order in the 'Technician Portal' to build your daily report!")
    else:
        df_eod_master = pd.DataFrame(st.session_state.eod_excel_records)
        st.dataframe(df_eod_master, use_container_width=True)
        
        # Excel File Stream Generator using OpenPyXL / BytesIO
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_eod_master.to_excel(writer, index=False, sheet_name='EOD_Work_Summary')
            
            # Additional Sheet: Ratings
            df_ratings = pd.DataFrame(st.session_state.technician_ratings)
            df_ratings.to_excel(writer, index=False, sheet_name='Customer_Ratings')
            
        excel_data_bytes = excel_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Master End-of-Day Excel File (.XLSX)",
            data=excel_data_bytes,
            file_name=f"Mirage_EOD_Report_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
        
    st.markdown("---")
    st.subheader("🌟 Technician Ratings & Feedback Log")
    st.dataframe(pd.DataFrame(st.session_state.technician_ratings), use_container_width=True)


# ==========================================
# 9. MODULE 5: FLEET ADMIN & DATA MANAGEMENT
# ==========================================
elif nav_choice == "⚙️ Fleet Admin & Data Management":
    st.markdown('<div class="main-header">⚙️ Fleet Admin & Work Order Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Create new work orders, reassign technicians, and manage fleet master records.</div>', unsafe_allow_html=True)
    
    st.subheader("➕ Create & Dispatch New Work Order")
    
    with st.form(key="new_wo_form"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            new_id = f"WO-{len(all_flat_orders if 'all_flat_orders' in locals() else [1,2,3,4,5,6]) + 901}"
            st.text_input("Work Order ID (Auto-Generated):", value=new_id, disabled=True)
            new_client = st.text_input("Client / Company Name:")
            new_contact = st.text_input("Contact Phone Number:", value="+2010")
            new_address = st.text_input("Site Address:")
            
        with col_f2:
            assigned_tech = st.selectbox("Assign Field Technician:", list(st.session_state.work_orders.keys()))
            new_priority = st.selectbox("Priority Level:", ["Low", "Medium", "High", "Critical"])
            new_service = st.selectbox("Service Category:", [
                "HVAC Repair & Maintenance",
                "Electrical Substation Service",
                "Plumbing & Filtration",
                "Network & Telecom Inspection",
                "General Facility Audit"
            ])
            new_est_hrs = st.number_input("Estimated Hours:", min_value=0.5, max_value=12.0, value=2.0)
            
        new_details = st.text_area("Issue Description & Requirements:")
        
        submit_new_wo = st.form_submit_button("🚀 Create & Assign Work Order", type="primary")
        
        if submit_new_wo:
            if not new_client or not new_details:
                st.error("Please fill in the client name and issue description.")
            else:
                new_wo_obj = {
                    "id": new_id,
                    "client": new_client,
                    "contact": new_contact,
                    "address": new_address,
                    "lat": 30.0444,  # Cairo Default
                    "lon": 31.2357,
                    "priority": new_priority,
                    "status": "Pending",
                    "service_type": new_service,
                    "details": new_details,
                    "est_hours": new_est_hrs,
                    "actual_hours": 0.0,
                    "photos": [],
                    "logs": [],
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                st.session_state.work_orders[assigned_tech].append(new_wo_obj)
                st.success(f"Work Order {new_id} successfully created and assigned to {assigned_tech}!")
