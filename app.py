import streamlit as st
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# Setup Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_summary_with_ai(raw_text):
    prompt = f"""
    Analyze this field technician work summary and return a concise evaluation with two parts:
    1. Key Actions Performed
    2. Escalations/Issues (if any)
    
    Raw Summary: "{raw_text}"
    """
    response = model.generate_content(prompt)
    return response.text

def save_to_excel(tech_name, order_id, raw_summary, ai_analysis, excel_file="EOD_Report.xlsx"):
    new_data = pd.DataFrame([{
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Technician": tech_name,
        "Work Order ID": order_id,
        "Raw Summary": raw_summary,
        "AI Analysis": ai_analysis
    }])
    
    try:
        df = pd.read_excel(excel_file)
        df = pd.concat([df, new_data], ignore_index=True)
    except FileNotFoundError:
        df = new_data
        
    df.to_excel(excel_file, index=False)

# --- STREAMLIT UI ---
st.title("Technician Portal")

# 1. Select Tech
tech_list = ["Ahmed Hassan", "Omar Malak", "Youssef Ali"]
selected_tech = st.selectbox("Select Technician Name:", tech_list)

# Mock Data for Work Orders
work_orders = {
    "Ahmed Hassan": [
        {"id": "WO-101", "client": "ACME Corp", "details": "HVAC Routine Service", "photos": ["https://via.placeholder.com/150"]},
        {"id": "WO-102", "client": "Global Logistics", "details": "Compressor Replacement", "photos": []}
    ],
    "Omar Malak": [
        {"id": "WO-201", "client": "City Mall", "details": "Electrical Panel Check", "photos": []}
    ]
}

# 2. Select Work Order
tech_orders = work_orders.get(selected_tech, [])
if tech_orders:
    order_ids = [order["id"] for order in tech_orders]
    selected_order_id = st.selectbox("Select Work Order:", order_ids)
    
    # Get selected order details
    order_data = next(item for item in tech_orders if item["id"] == selected_order_id)
    
    st.subheader(f"Details for {order_data['id']}")
    st.write(f"**Client:** {order_data['client']}")
    st.write(f"**Job Details:** {order_data['details']}")
    
    # Display Photos
    if order_data["photos"]:
        st.write("**Attached Photos:**")
        st.image(order_data["photos"], width=150)
    
    # 3. Summary & AI Analysis Section
    st.markdown("---")
    st.subheader("Submit Work Completion Summary")
    summary_input = st.text_area("Write job completion notes:")
    
    if st.button("Submit & Log to Excel"):
        if summary_input.strip():
            with st.spinner("Analyzing summary with AI..."):
                ai_output = analyze_summary_with_ai(summary_input)
                save_to_excel(selected_tech, selected_order_id, summary_input, ai_output)
                
            st.success("Work Order updated and logged to End-of-Day Excel report!")
            st.markdown("### AI Summary Preview")
            st.info(ai_output)
        else:
            st.warning("Please enter a summary before submitting.")
else:
    st.info("No active work orders found for this technician.")
