import os
from datetime import datetime
import pandas as pd
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Mirage Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS safely wrapped in triple-quoted strings
st.markdown(
    """
<style>
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0e1117;
    }
    ::-webkit-scrollbar-thumb {
        background: #262730;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #41444c;
    }

    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .stMetric {
        background-color: #1e222a;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #2d3139;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 2. SESSION STATE INITIALIZATION (CLEAN DATA)
# ==========================================
if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = pd.DataFrame(
        columns=[
            "SKU",
            "Product Name",
            "Category",
            "Stock Level",
            "Reorder Point",
            "Unit Cost ($)",
            "Selling Price ($)",
        ]
    )

if "orders_df" not in st.session_state:
    st.session_state.orders_df = pd.DataFrame(
        columns=[
            "Order ID",
            "Customer / Entity",
            "Zone",
            "Items Summary",
            "Total Quantity",
            "Total Amount ($)",
            "Status",
            "Assigned Driver",
            "Created Date",
        ]
    )

if "customers_df" not in st.session_state:
    st.session_state.customers_df = pd.DataFrame(
        columns=["Customer ID", "Name", "Zone", "Contact Number", "Total Orders"]
    )


# ==========================================
# 3. CLASSIC SIDEBAR MENU NAVIGATION
# ==========================================
st.sidebar.title("🏢 Mirage Operations")
st.sidebar.caption("Distribution & Logistics Hub")

# Classic Selectbox Menu Style restored
page = st.sidebar.selectbox(
    "Select View Module",
    [
        "Executive Overview",
        "Inventory & Stock Control",
        "Dispatch & Order Operations",
        "Customer Directory",
        "Data Import / Export & Reports",
    ],
)

st.sidebar.divider()

# System Quick Controls
st.sidebar.subheader("System Controls")
if st.sidebar.button("🗑️ Clear All Operational Data"):
    st.session_state.inventory_df = pd.DataFrame(
        columns=[
            "SKU",
            "Product Name",
            "Category",
            "Stock Level",
            "Reorder Point",
            "Unit Cost ($)",
            "Selling Price ($)",
        ]
    )
    st.session_state.orders_df = pd.DataFrame(
        columns=[
            "Order ID",
            "Customer / Entity",
            "Zone",
            "Items Summary",
            "Total Quantity",
            "Total Amount ($)",
            "Status",
            "Assigned Driver",
            "Created Date",
        ]
    )
    st.session_state.customers_df = pd.DataFrame(
        columns=["Customer ID", "Name", "Zone", "Contact Number", "Total Orders"]
    )
    st.success("Database cleared!")
    st.rerun()


# ==========================================
# 4. MODULE 1: EXECUTIVE OVERVIEW
# ==========================================
if page == "Executive Overview":
    st.title("Executive Dashboard")
    st.markdown("High-level performance monitoring and distribution metrics.")

    inv_df = st.session_state.inventory_df
    ord_df = st.session_state.orders_df

    # Calculated Financials & Stock KPIs
    total_val = (
        (inv_df["Stock Level"] * inv_df["Selling Price ($)"]).sum()
        if not inv_df.empty
        else 0.0
    )
    total_cost = (
        (inv_df["Stock Level"] * inv_df["Unit Cost ($)"]).sum()
        if not inv_df.empty
        else 0.0
    )
    potential_profit = total_val - total_cost

    low_stock = (
        len(inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]])
        if not inv_df.empty
        else 0
    )
    active_orders = (
        len(ord_df[ord_df["Status"].isin(["Pending", "Out for Delivery"])])
        if not ord_df.empty
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inventory Value", f"${total_val:,.2f}")
    c2.metric("Projected Margin", f"${potential_profit:,.2f}")
    c3.metric("Active Deliveries", active_orders)
    c4.metric(
        "Low Stock Alerts",
        low_stock,
        delta="-Action Needed" if low_stock > 0 else "Normal",
        delta_color="inverse" if low_stock > 0 else "normal",
    )

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📋 Active Order Dispatch Stream")
        if ord_df.empty:
            st.info("No active orders in the pipeline. Create orders in 'Dispatch & Order Operations'.")
        else:
            st.dataframe(
                ord_df[ord_df["Status"] != "Delivered"],
                use_container_width=True,
                hide_index=True,
            )

    with col_right:
        st.subheader("⚠️ Stock Replenishment Warnings")
        if inv_df.empty:
            st.info("No products logged in inventory.")
        else:
            reorder_needed = inv_df[inv_df["Stock Level"] <= inv_df["Reorder Point"]]
            if reorder_needed.empty:
                st.success("All stock levels are above reorder thresholds.")
            else:
                st.dataframe(
                    reorder_needed[["SKU", "Product Name", "Stock Level", "Reorder Point"]],
                    use_container_width=True,
                    hide_index=True,
                )


# ==========================================
# 5. MODULE 2: INVENTORY & STOCK CONTROL
# ==========================================
elif page == "Inventory & Stock Control":
    st.title("Stock & Warehouse Management")

    tab1, tab2, tab3 = st.tabs(["Stock Directory & Edit", "➕ Single Item Intake", "📥 Bulk CSV Import"])

    # --- Tab 1: Live Interactive Table ---
    with tab1:
        st.subheader("Live Warehouse Inventory")
        if st.session_state.inventory_df.empty:
            st.info("Inventory table is empty. Add items using the intake form or bulk upload.")
        else:
            search = st.text_input("🔍 Search by SKU, Name, or Category", "")
            filtered = st.session_state.inventory_df[
                st.session_state.inventory_df["Product Name"].str.contains(search, case=False, na=False)
                | st.session_state.inventory_df["SKU"].str.contains(search, case=False, na=False)
                | st.session_state.inventory_df["Category"].str.contains(search, case=False, na=False)
            ]

            edited_df = st.data_editor(
                filtered,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="inventory_editor",
            )

            if st.button("💾 Commit Inventory Changes"):
                st.session_state.inventory_df = edited_df
                st.success("Inventory updated successfully!")
                st.rerun()

    # --- Tab 2: Single Product Intake ---
    with tab2:
        st.subheader("Add Single Product")
        with st.form("add_product_form", clear_on_submit=True):
            i1, i2, i3 = st.columns(3)
            sku = i1.text_input("SKU / Code", value=f"MRG-SKU-{len(st.session_state.inventory_df)+101}")
            p_name = i2.text_input("Product Title")
            cat = i3.text_input("Category (e.g. Raw Material, Packaging)")

            i4, i5, i6, i7 = st.columns(4)
            stock = i4.number_input("Starting Quantity", min_value=0, value=0)
            reorder = i5.number_input("Reorder Threshold", min_value=0, value=10)
            cost = i6.number_input("Unit Purchase Cost ($)", min_value=0.0, value=0.0, step=0.5)
            price = i7.number_input("Unit Selling Price ($)", min_value=0.0, value=0.0, step=0.5)

            if st.form_submit_button("Create Inventory Entry"):
                if p_name and sku:
                    new_item = pd.DataFrame([
                        {
                            "SKU": sku,
                            "Product Name": p_name,
                            "Category": cat,
                            "Stock Level": stock,
                            "Reorder Point": reorder,
                            "Unit Cost ($)": cost,
                            "Selling Price ($)": price,
                        }
                    ])
                    st.session_state.inventory_df = pd.concat(
                        [st.session_state.inventory_df, new_item], ignore_index=True
                    )
                    st.success(f"Item '{p_name}' created!")
                    st.rerun()
                else:
                    st.error("Please provide both product title and SKU.")

    # --- Tab 3: Bulk Upload ---
    with tab3:
        st.subheader("Batch Import Inventory via CSV")
        st.caption("CSV columns required: SKU, Product Name, Category, Stock Level, Reorder Point, Unit Cost ($), Selling Price ($)")
        uploaded_file = st.file_uploader("Choose Inventory CSV File", type=["csv"])
        if uploaded_file is not None:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df.head(), use_container_width=True)
                if st.button("Merge Uploaded File into Active Inventory"):
                    st.session_state.inventory_df = pd.concat(
                        [st.session_state.inventory_df, imported_df], ignore_index=True
                    ).drop_duplicates(subset=["SKU"], keep="last")
                    st.success("Batch import completed successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to process file: {e}")


# ==========================================
# 6. MODULE 3: DISPATCH & ORDER OPERATIONS
# ==========================================
elif page == "Dispatch & Order Operations":
    st.title("Order Booking & Delivery Dispatch")

    o_tab1, o_tab2 = st.tabs(["Create & Dispatch Order", "Manage Existing Orders"])

    with o_tab1:
        st.subheader("New Shipment Request")
        if st.session_state.inventory_df.empty:
            st.warning("Please add items to your inventory before generating orders.")
        else:
            with st.form("new_order_form", clear_on_submit=True):
                o1, o2 = st.columns(2)
                cust_name = o1.text_input("Customer / Entity Name")
                zone = o2.selectbox("Destination Zone", ["Cairo Central", "Maadi", "New Cairo", "Giza", "6th of October", "Other Area"])

                # Select Product from Live Inventory
                selected_sku = st.selectbox(
                    "Select Product",
                    options=st.session_state.inventory_df["SKU"] + " - " + st.session_state.inventory_df["Product Name"]
                )
                
                o3, o4 = st.columns(2)
                qty = o3.number_input("Order Quantity", min_value=1, value=1)
                driver = o4.text_input("Assign Driver Name", value="Unassigned")

                if st.form_submit_button("Book Shipment"):
                    target_sku = selected_sku.split(" - ")[0]
                    inv_match = st.session_state.inventory_df[st.session_state.inventory_df["SKU"] == target_sku]

                    if not inv_match.empty:
                        item_price = inv_match.iloc[0]["Selling Price ($)"]
                        item_title = inv_match.iloc[0]["Product Name"]
                        current_stock = inv_match.iloc[0]["Stock Level"]

                        if current_stock < qty:
                            st.error(f"Insufficient stock! Available quantity: {current_stock}")
                        else:
                            # Auto-deduct stock level
                            st.session_state.inventory_df.loc[
                                st.session_state.inventory_df["SKU"] == target_sku, "Stock Level"
                            ] -= qty

                            total_price = item_price * qty
                            order_id = f"ORD-{len(st.session_state.orders_df)+1001}"
                            new_ord = pd.DataFrame([{
                                "Order ID": order_id,
                                "Customer / Entity": cust_name,
                                "Zone": zone,
                                "Items Summary": f"{item_title} (x{qty})",
                                "Total Quantity": qty,
                                "Total Amount ($)": total_price,
                                "Status": "Out for Delivery" if driver != "Unassigned" else "Pending",
                                "Assigned Driver": driver,
                                "Created Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            }])

                            st.session_state.orders_df = pd.concat([st.session_state.orders_df, new_ord], ignore_index=True)
                            st.success(f"Order {order_id} recorded and inventory automatically updated!")
                            st.rerun()

    with o_tab2:
        st.subheader("Manage Active Orders Workflow")
        if st.session_state.orders_df.empty:
            st.info("No orders logged in the system.")
        else:
            orders_edited = st.data_editor(
                st.session_state.orders_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Pending", "Out for Delivery", "Delivered", "Cancelled"],
                    )
                },
                key="orders_editor",
            )
            if st.button("💾 Update Order Statuses"):
                st.session_state.orders_df = orders_edited
                st.success("Order records updated!")
                st.rerun()


# ==========================================
# 7. MODULE 4: CUSTOMER DIRECTORY
# ==========================================
elif page == "Customer Directory":
    st.title("Client & Customer Registry")

    c_col1, c_col2 = st.columns([1, 2])

    with c_col1:
        st.subheader("Register New Customer")
        with st.form("cust_form", clear_on_submit=True):
            c_name = st.text_input("Customer / Business Name")
            c_zone = st.selectbox("Operating Zone", ["Cairo Central", "Maadi", "New Cairo", "Giza", "6th of October", "Other Area"])
            c_phone = st.text_input("Contact Number")

            if st.form_submit_button("Add Customer"):
                if c_name:
                    cid = f"CUST-{len(st.session_state.customers_df)+101}"
                    new_c = pd.DataFrame([{
                        "Customer ID": cid,
                        "Name": c_name,
                        "Zone": c_zone,
                        "Contact Number": c_phone,
                        "Total Orders": 0,
                    }])
                    st.session_state.customers_df = pd.concat([st.session_state.customers_df, new_c], ignore_index=True)
                    st.success("Customer profile registered!")
                    st.rerun()

    with c_col2:
        st.subheader("Customer Profiles")
        if st.session_state.customers_df.empty:
            st.info("No registered customers.")
        else:
            st.dataframe(st.session_state.customers_df, use_container_width=True, hide_index=True)


# ==========================================
# 8. MODULE 5: DATA EXPORT & REPORTS
# ==========================================
elif page == "Data Import / Export & Reports":
    st.title("Data Export Center & Reporting")

    st.markdown("Extract live snapshot reports of your inventory, dispatches, and customer data.")

    exp1, exp2, exp3 = st.columns(3)

    with exp1:
        st.subheader("Warehouse Inventory")
        inv_csv = st.session_state.inventory_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Inventory Report (CSV)",
            data=inv_csv,
            file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    with exp2:
        st.subheader("Orders Log")
        ord_csv = st.session_state.orders_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Orders Log (CSV)",
            data=ord_csv,
            file_name=f"orders_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    with exp3:
        st.subheader("Customer Directory")
        cust_csv = st.session_state.customers_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Customer Directory (CSV)",
            data=cust_csv,
            file_name=f"customers_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
