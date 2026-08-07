import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai
import io
import urllib.parse
import os

# ==========================================
# 1. APPLICATION & PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Fleet Command & Field Service Hub",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Data if not already present
if "work_orders" not in st.session_state:
    st.session_state.work_orders = {
        "Ahmed Hassan": [
            {
                "id": "WO-8801",
                "client": "Apex Industrial Logistics",
                "contact": "+201012345678",
                "address": "Building 12, Smart Village, Giza",
                "lat": 30.0731,
                "lon": 31.0182,
                "priority": "High",
                "status": "In Progress",
                "service_type": "HVAC System Failure",
                "details": "Main chiller unit overheating. Error code E-402 on central panel.",
                "est_hours": 3.5,
                "photos": [
                    "https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=500",
                    "https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=500"
                ],
                "logs": []
            },
            {
                "id": "WO-8804",
                "client": "Cilantro Coffee HQ",
                "contact": "+201098765432",
                "address": "Road 9, Maadi, Cairo",
                "lat": 29.9602,
                "lon": 31.2569,
                "priority": "Medium",
                "status": "Pending",
                "service_type": "Espresso Machine Calibration",
                "details": "Water pressure fluctuations on Group Head 2 during peak hours.",
                "est_hours": 1.5,
                "photos": [
                    "https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500"
                ],
                "logs": []
            }
        ],
        "Omar Malak": [
            {
                "id": "WO-8802",
                "client": "Mirage Corporate Center",
                "contact": "+201112223334",
                "address": "New Cairo, Sector 1",
                "lat": 30.0271,
                "lon": 31.4398,
                "priority": "Critical",
                "status": "In Progress",
                "service_type": "Electrical Substation Audit",
                "details": "Secondary breaker trippings under heavy load. Urgent diagnostic required.",
                "est_hours": 4.0,
                "photos": [
                    "https://images.unsplash.com/photo-1544724569-5f546fd6f2b5?w=500"
                ],
                "logs": []
            }
        ],
        "Youssef Ali": [
            {
                "id": "WO-8803",
                "client": "Cairo Design Hub",
                "contact": "+201223344556",
                "address": "Zamalek, Nile St.",
                "lat": 30.0626,
                "lon": 31.2201,
                "priority": "Low",
                "status": "Pending",
                "service_type": "Routine Fiber Network Maintenance",
                "details": "Quarterly inspection of patch panels and router rack grounding.",
                "est_hours": 2.0,
                "photos": [],
                "logs": []
            }
        ]
    }

if "eod_records" not in st.session_state:
    st.session_state.eod_records = []

# Configure Gemini API safely
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# ==========================================
# 2. HELPER FUNCTIONS & AI ENGINE
# ==========================================
def run_gemini_summary_analysis(raw_summary_text):
    """
    Calls Gemini API to structure technician notes into clear executive insights.
    """
    if not GEMINI_KEY:
        return {
            "key_actions": "API Key Missing - Saved Raw Text",
            "issues": "None recorded",
            "exec_summary": raw_summary_text
        }
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        You are a Fleet Command Dispatch AI. Analyze this field technician's work log submission:
        
        Raw Log: "{raw_summary_text}"
        
        Provide a structured evaluation in exactly 3 bullet points:
        - Key Actions Performed: [Summary of completed work]
        - Outstanding Issues/Escalations: [List any unresolved problems or follow-ups needed]
        - Executive One-Liner: [A single professional sentence summarizing job status]
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Processing Error: {str(e)}"

def append_to_eod_excel(tech_name, work_order_id, raw_notes, ai_analysis):
    """
    Logs structured job entries into the master EOD Excel state.
    """
    entry = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Technician Name": tech_name,
        "Work Order ID": work_order_id,
        "Raw Tech Summary": raw_notes,
        "AI Analysis & Next Steps": ai_analysis
    }
    st.session_state.eod_records.append(entry)

def check_geofence_status(tech_lat, tech_lon, target_lat, target_lon, threshold_km=0.5):
    """
    Simulates distance calculation to check if technician is inside site geofence.
    """
    lat_diff = abs(tech_lat - target_lat) * 111
    lon_diff = abs(tech_lon - target_lon) * 111
    total_dist_km = (lat_diff**2 + lon_diff**2)**0.5
    return total_dist_km <= threshold_km, round(total_dist_km, 2)

def generate_whatsapp_link(phone_number, message):
    """
    Generates a pre-filled direct WhatsApp link for dispatch notifications.
    """
    clean_phone = phone_number.replace("+", "").replace(" ", "")
    encoded_msg = urllib.parse.quote(message)
    return f"https://wa.me/{clean_phone}?text={encoded_msg}"

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
st.sidebar.title("🚚 Fleet Operations")
st.sidebar.markdown("**System Version:** 2.4.0 (Production)")

app_mode = st.sidebar.radio(
    "Navigation Engine",
    [
        "👨‍🔧 Technician Portal & Work Orders",
        "🎯 Smart Dispatch & Geofencing",
        "💬 WhatsApp & Client Alerts",
        "📊 End-of-Day Excel Reports & Scorecards"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("System Status: 🟢 All Dispatch Nodes Active")

# ==========================================
# 4. MODULE 1: TECHNICIAN PORTAL (DRILL-DOWN)
# ==========================================
if app_mode == "👨‍🔧 Technician Portal & Work Orders":
    st.title("👨‍🔧 Field Technician Portal")
    st.markdown("Select a technician to review assigned work orders, view job photos, submit job notes, and run AI EOD processing.")
    
    col_select, col_meta = st.columns([2, 1])
    with col_select:
        tech_names = list(st.session_state.work_orders.keys())
        selected_tech = st.selectbox("📌 Select Field Technician:", tech_names)
    
    assigned_orders = st.session_state.work_orders[selected_tech]
    
    with col_meta:
        st.metric("Total Assigned Jobs", len(assigned_orders))
    
    st.markdown("---")
    
    if not assigned_orders:
        st.info("No active work orders currently assigned to this technician.")
    else:
        # Step 1: Work Order Selection Cards
        st.subheader(f"Active Jobs for {selected_tech}")
        
        order_list_display = [f"{order['id']} - {order['client']} ({order['priority']} Priority)" for order in assigned_orders]
        selected_order_idx = st.selectbox("Select Active Work Order to Inspect:", range(len(order_list_display)), format_func=lambda x: order_list_display[x])
        
        current_order = assigned_orders[selected_order_idx]
        
        # Step 2: Work Order Deep Dive Detail View
        with st.container():
            st.markdown(f"### Work Order Details: `{current_order['id']}`")
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"**Client:** {current_order['client']}")
            c1.markdown(f"**Contact:** {current_order['contact']}")
            c2.markdown(f"**Priority:** `{current_order['priority']}`")
            c2.markdown(f"**Status:** `{current_order['status']}`")
            c3.markdown(f"**Service Type:** {current_order['service_type']}")
            c3.markdown(f"**Estimated Hours:** {current_order['est_hours']} hrs")
            
            st.markdown(f"**Site Address:** {current_order['address']}")
            st.info(f"**Issue Description:** {current_order['details']}")
            
            # Step 3: Photo & Document Gallery
            st.markdown("#### 📷 Site Photos & Attached Media")
            if current_order["photos"]:
                img_cols = st.columns(len(current_order["photos"]))
                for i, img_url in enumerate(current_order["photos"]):
                    with img_cols[i]:
                        st.image(img_url, caption=f"Attachment #{i+1}", use_container_width=True)
            else:
                st.warning("No site photos attached to this work order yet.")
            
            # Photo Upload Simulator
            uploaded_file = st.file_uploader(f"Upload new job photo for {current_order['id']}", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                st.success("New site image attached successfully!")
            
            st.markdown("---")
            
            # Step 4: Summary Input & AI Excel Engine Pipeline
            st.markdown("#### 📝 Submit Work Completion Summary")
            st.caption("Write your technical completion notes below. The AI pipeline will automatically analyze issues, draft action items, and log it to the master Excel End-of-Day report.")
            
            tech_summary_input = st.text_area(
                "Technician Field Notes / Parts Used / Actions Taken:",
                placeholder="E.g., Replaced primary capacitor on chiller unit. System test passed at 14:00. Note: Compressor relay switch shows slight wear, may require replacement next month."
            )
            
            if st.button("🚀 Process Notes with AI & Save to EOD Excel", type="primary"):
                if tech_summary_input.strip() == "":
                    st.error("Please enter completion notes before submitting.")
                else:
                    with st.spinner("AI Analysis Engine parsing technician report..."):
                        ai_result = run_gemini_summary_analysis(tech_summary_input)
                        
                        # Save to Excel session database
                        append_to_eod_excel(
                            tech_name=selected_tech,
                            work_order_id=current_order['id'],
                            raw_notes=tech_summary_input,
                            ai_analysis=ai_result
                        )
                        
                        # Update Order Status
                        current_order['status'] = "Completed"
                        current_order['logs'].append(tech_summary_input)
                        
                    st.success(f"Work Order {current_order['id']} marked as COMPLETED and logged to Excel!")
                    st.markdown("### 🤖 AI Processing Output")
                    st.info(ai_result)

# ==========================================
# 5. MODULE 2: SMART DISPATCH & GEOFENCING
# ==========================================
elif app_mode == "🎯 Smart Dispatch & Geofencing":
    st.title("🎯 Smart Dispatch Engine & Geofencing")
    st.markdown("Automated route optimization, arrival duration forecasting, and live GPS radius updates.")
    
    col_map, col_controls = st.columns([2, 1])
    
    # Compile all tech order coordinates for map display
    map_data = []
    for tech, orders in st.session_state.work_orders.items():
        for order in orders:
            map_data.append({
                "lat": order["lat"],
                "lon": order["lon"],
                "tech": tech,
                "order_id": order["id"],
                "client": order["client"]
            })
    df_map = pd.DataFrame(map_data)
    
    with col_map:
        st.subheader("🗺️ Live Dispatch Map")
        st.map(df_map, zoom=10, use_container_width=True)
    
    with col_controls:
        st.subheader("📡 Live Geofence Simulator")
        st.caption("Test automatic status changes based on technician proximity to site.")
        
        selected_job_id = st.selectbox("Target Order ID:", df_map["order_id"].tolist())
        target_job = next(item for sublist in st.session_state.work_orders.values() for item in sublist if item["id"] == selected_job_id)
        
        st.write(f"**Target Location:** {target_job['address']}")
        
        st.markdown("**Simulated Tech GPS Coordinates:**")
        sim_lat = st.number_input("Tech Latitude:", value=target_job["lat"] + 0.002, format="%.4f")
        sim_lon = st.number_input("Tech Longitude:", value=target_job["lon"] - 0.001, format="%.4f")
        
        is_inside, dist_km = check_geofence_status(sim_lat, sim_lon, target_job["lat"], target_job["lon"])
        
        st.write(f"**Calculated Distance:** `{dist_km} km`")
        if is_inside:
            st.success("🟢 WITHIN GEOFENCE (Inside 500m radius)")
            st.caption("Automatic Action: Job status flipped to **'On Site / In Progress'**")
        else:
            st.warning("🔴 OUTSIDE GEOFENCE")
            st.caption("Automatic Action: Technician en route.")

# ==========================================
# 6. MODULE 3: WHATSAPP & CLIENT ALERTS
# ==========================================
elif app_mode == "💬 WhatsApp & Client Alerts":
    st.title("💬 Customer & WhatsApp Communication Hub")
    st.markdown("Trigger instant automated customer dispatches and tracking updates directly via WhatsApp.")
    
    # Flatten orders list
    all_orders = [order for sublist in st.session_state.work_orders.values() for order in sublist]
    order_labels = [f"{o['id']} - {o['client']} ({o['contact']})" for o in all_orders]
    
    selected_idx = st.selectbox("Select Customer Order to Contact:", range(len(order_labels)), format_func=lambda x: order_labels[x])
    chosen_order = all_orders[selected_idx]
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("✉️ Automated Notification Composer")
        eta_minutes = st.slider("Estimated Arrival Time (Minutes):", 10, 120, 30)
        
        default_message = f"Hello {chosen_order['client']}, your field technician for service {chosen_order['id']} is en route and estimated to arrive in approximately {eta_minutes} minutes. Please ensure job site access."
        
        custom_message = st.text_area("Message Preview:", value=default_message, height=120)
        
        wa_url = generate_whatsapp_link(chosen_order['contact'], custom_message)
        
        st.markdown(f"""
            <a href="{wa_url}" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    📲 Launch WhatsApp Dispatch Message
                </button>
            </a>
        """, unsafe_allow_html=True)
        
    with c2:
        st.subheader("⭐ Post-Job Customer Feedback Loop")
        st.caption("Simulate customer rating submissions post-service completion.")
        
        rating = st.select_slider("Customer Rating:", options=[1, 2, 3, 4, 5], value=5)
        feedback_comments = st.text_input("Customer Feedback Notes:", "Technician arrived on time and fixed the chiller fast!")
        
        if st.button("Log Customer Feedback"):
            st.success(f"Feedback logged for Order {chosen_order['id']}! Rating: {rating}/5 Stars")

# ==========================================
# 7. MODULE 4: EXCEL EOD REPORTS & SCORECARDS
# ==========================================
elif app_mode == "📊 End-of-Day Excel Reports & Scorecards":
    st.title("📊 End-of-Day Excel Reports & Analytics")
    st.markdown("Consolidated daily field logs, AI analytical reports, and executable Excel downloads.")
    
    if not st.session_state.eod_records:
        st.warning("No End-of-Day submissions logged yet. Go to the 'Technician Portal' tab to submit completion notes!")
    else:
        df_eod = pd.DataFrame(st.session_state.eod_records)
        
        st.subheader("📋 Master End-of-Day Log Table")
        st.dataframe(df_eod, use_container_width=True)
        
        # Excel File Stream Export Engine
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_eod.to_excel(writer, index=False, sheet_name='EOD_Report')
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Download Master EOD Report (.XLSX)",
            data=excel_data,
            file_name=f"EOD_Field_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
    
    st.markdown("---")
    st.subheader("📈 Field Technician Performance Scorecards")
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("First-Time Fix Rate", "94.2%", "+2.1%")
    sc2.metric("Avg Response Time", "38 mins", "-5 mins")
    sc3.metric("Customer Satisfaction", "4.87 / 5.0", "+0.12")
