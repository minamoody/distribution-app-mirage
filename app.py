import os
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# ==========================================
st.set_page_config(
    page_title="Mirage Distribution Center",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS with proper string formatting to prevent syntax errors
st.markdown(
    """
<style>
    /* Sleek Custom Scrollbar */
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

    /* Metric Card Styling */
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
# 2. MOCK DATA GENERATION (PERSISTENT STATE)
# ==========================================
@st.cache_data
def load_initial_data():
    np.random.seed(42)

    # Inventory Data
    products = [
        "Premium Coffee Beans 1kg",
        "Zero-Sugar Syrup Vanilla 750ml",
        "Spanish Latte Mix 500g",
        "Almond Milk Barista Edition 1L",
        "Paper Cups 12oz (Box 500)",
        "Organic Oat Milk 1L",
        "Espresso Cleaning Tablets",
    ]

    inventory_df = pd.DataFrame(
        {
            "SKU": [f"MRG-SKU-{100+i}" for i in range(len(products))],
            "Product Name": products,
            "Category": [
                "Coffee",
                "Syrups",
                "Mixes",
                "Dairy/Alt",
                "Packaging",
                "Dairy/Alt",
                "Supplies",
            ],
            "Stock Level": [140, 45, 210, 18, 550, 90, 12],
            "Reorder Point": [50, 30, 60, 25, 100, 30, 15],
            "Unit Price ($)": [22.50, 12.00, 18.50, 4.20, 35.00, 4.50, 15.00],
        }
    )

    # Orders / Dispatch Data
    statuses = [
        "Delivered",
        "Out for Delivery",
        "Processing",
        "Pending Dispatch",
    ]
    zones = ["Central Cairo", "Maadi", "New Cairo", "Giza", "6th of October"]
    drivers = [
        "Ahmed Hassan",
        "Karim Zaki",
        "Omar Mahmoud",
        "Youssef Ali",
        "Unassigned",
    ]

    orders = []
    base_date = datetime.now() - timedelta(days=7)

    for i in range(1, 46):
        order_date = base_date + timedelta(
            days=np.random.randint(0, 7), hours=np.random.randint(8, 18)
        )
        status = np.random.choice(statuses, p=[0.5, 0.2, 0.2, 0.1])
        orders.append(
            {
                "Order ID": f"ORD-{202600 + i}",
                "Customer / Branch": f"Branch #{np.random.randint(101, 115)}",
                "Zone": np.random.choice(zones),
                "Items Count": np.random.randint(5, 50),
                "Total Value ($)": round(np.random.uniform(150, 1800), 2),
                "Status": status,
                "Driver": (
                    "Unassigned"
                    if status == "Pending Dispatch"
                    else np.random.choice(drivers[:-1])
                ),
                "Order Date": order_date.strftime("%Y-%m-%d %H:%M"),
            }
        )

    orders_df = pd.DataFrame(orders)
    return inventory_df, orders_df


if "inventory_df" not in st.session_state or "orders_df" not in st.session_state:
    st.session_state.inventory_df, st.session_state.orders_df = (
        load_initial_data()
    )


# ==========================================
# 3. SIDEBAR NAVIGATION & FILTERS
# ==========================================
st.sidebar.title("📦 Mirage Logistics")
st.sidebar.caption("Distribution & Inventory Command Center")

page = st.sidebar.radio(
    "Navigation",
    [
        "🚀 Executive Dashboard",
        "📊 Stock & Inventory",
        "🚚 Orders & Dispatch",
        "📈 Analytics & Reports",
    ],
)

st.sidebar.divider()
st.sidebar.subheader("Quick Actions")
if st.sidebar.button("🔄 Refresh Data State"):
    st.cache_data.clear()
    st.session_state.inventory_df, st.session_state.orders_df = (
        load_initial_data()
    )
    st.rerun()


# ==========================================
# 4. PAGE 1: EXECUTIVE DASHBOARD
# ==========================================
if page == "🚀 Executive Dashboard":
    st.title("Executive Control Panel")
    st.markdown("Real-time summary of Mirage distribution network operations.")

    orders_df = st.session_state.orders_df
    inventory_df = st.session_state.inventory_df

    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Total Orders (7 Days)",
        len(orders_df),
        delta=f"+{len(orders_df[orders_df['Status'] == 'Processing'])} processing",
    )
    c2.metric(
        "Active Deliveries",
        len(orders_df[orders_df["Status"] == "Out for Delivery"]),
        delta="Live Tracking",
    )
    c3.metric(
        "Total Revenue",
        f"${orders_df['Total Value ($)'].sum():,.2f}",
        delta="+12.4% vs last week",
    )

    low_stock_count = len(
        inventory_df[
            inventory_df["Stock Level"] <= inventory_df["Reorder Point"]
        ]
    )
    c4.metric(
        "Low Stock Alerts",
        low_stock_count,
        delta="-Attention Needed" if low_stock_count > 0 else "Optimal",
        delta_color="inverse" if low_stock_count > 0 else "normal",
    )

    st.divider()

    # Active Orders Pipeline & Quick Status Breakdown
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("⚡ Live Dispatch Stream")
        status_filter = st.multiselect(
            "Filter by Status",
            options=orders_df["Status"].unique(),
            default=["Out for Delivery", "Pending Dispatch"],
        )
        filtered_orders = orders_df[orders_df["Status"].isin(status_filter)]
        st.dataframe(
            filtered_orders,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=[
                        "Delivered",
                        "Out for Delivery",
                        "Processing",
                        "Pending Dispatch",
                    ],
                )
            },
        )

    with col_right:
        st.subheader("📌 Orders Breakdown")
        status_counts = orders_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        st.bar_chart(data=status_counts, x="Status", y="Count", color="Status")


# ==========================================
# 5. PAGE 2: STOCK & INVENTORY
# ==========================================
elif page == "📊 Stock & Inventory":
    st.title("Stock & Inventory Management")

    inventory_df = st.session_state.inventory_df

    # Quick Add Item / Reorder Panel
    with st.expander("➕ Add New Inventory Item"):
        with st.form("add_item_form"):
            f1, f2, f3 = st.columns(3)
            p_name = f1.text_input("Product Name")
            p_cat = f2.selectbox(
                "Category",
                ["Coffee", "Syrups", "Mixes", "Dairy/Alt", "Packaging", "Supplies"],
            )
            p_sku = f3.text_input("SKU", value=f"MRG-SKU-{len(inventory_df)+100}")

            f4, f5, f6 = st.columns(3)
            p_stock = f4.number_input("Initial Stock Level", min_value=0, value=50)
            p_reorder = f5.number_input("Reorder Threshold", min_value=0, value=20)
            p_price = f6.number_input(
                "Unit Price ($)", min_value=0.0, value=10.0, step=0.5
            )

            if st.form_submit_button("Add Item to Database"):
                if p_name:
                    new_row = pd.DataFrame(
                        [
                            {
                                "SKU": p_sku,
                                "Product Name": p_name,
                                "Category": p_cat,
                                "Stock Level": p_stock,
                                "Reorder Point": p_reorder,
                                "Unit Price ($)": p_price,
                            }
                        ]
                    )
                    st.session_state.inventory_df = pd.concat(
                        [st.session_state.inventory_df, new_row], ignore_index=True
                    )
                    st.success(f"Added '{p_name}' successfully!")
                    st.rerun()

    st.divider()

    # Inventory Table with Highlights for Low Stock
    st.subheader("Current Warehouse Stock Levels")

    search_query = st.text_input("🔍 Search product or SKU...", "")
    filtered_inv = inventory_df[
        inventory_df["Product Name"]
        .str.contains(search_query, case=False)
        | inventory_df["SKU"].str.contains(search_query, case=False)
    ]

    # Editable dataframe to update stock levels on the fly
    edited_inv = st.data_editor(
        filtered_inv,
        use_container_width=True,
        hide_index=True,
        key="inventory_editor",
    )

    # Save changes back to session state
    if st.button("💾 Save Inventory Changes"):
        st.session_state.inventory_df.update(edited_inv)
        st.success("Inventory updated successfully!")


# ==========================================
# 6. PAGE 3: ORDERS & DISPATCH
# ==========================================
elif page == "🚚 Orders & Dispatch":
    st.title("Orders & Delivery Routing")

    orders_df = st.session_state.orders_df

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Create New Shipment")
        with st.form("new_order_form"):
            branch = st.text_input("Customer / Branch Name")
            zone = st.selectbox(
                "Delivery Zone",
                ["Central Cairo", "Maadi", "New Cairo", "Giza", "6th of October"],
            )
            item_count = st.number_input("Items Quantity", min_value=1, value=10)
            val = st.number_input(
                "Order Total Value ($)", min_value=1.0, value=250.0
            )
            driver = st.selectbox(
                "Assign Driver",
                [
                    "Unassigned",
                    "Ahmed Hassan",
                    "Karim Zaki",
                    "Omar Mahmoud",
                    "Youssef Ali",
                ],
            )

            if st.form_submit_button("Create Dispatch Order"):
                if branch:
                    new_order = {
                        "Order ID": f"ORD-{202600 + len(orders_df) + 1}",
                        "Customer / Branch": branch,
                        "Zone": zone,
                        "Items Count": item_count,
                        "Total Value ($)": val,
                        "Status": (
                            "Pending Dispatch"
                            if driver == "Unassigned"
                            else "Out for Delivery"
                        ),
                        "Driver": driver,
                        "Order Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                    st.session_state.orders_df = pd.concat(
                        [
                            pd.DataFrame([new_order]),
                            st.session_state.orders_df,
                        ],
                        ignore_index=True,
                    )
                    st.success("Shipment created and dispatched to queue!")
                    st.rerun()

    with col2:
        st.subheader("Zone Workload Distribution")
        zone_summary = (
            orders_df.groupby("Zone")
            .agg(Total_Orders=("Order ID", "count"), Total_Value=("Total Value ($)", "sum"))
            .reset_index()
        )
        st.dataframe(zone_summary, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("All Orders Management")
    st.dataframe(orders_df, use_container_width=True, hide_index=True)


# ==========================================
# 7. PAGE 4: ANALYTICS & REPORTS
# ==========================================
elif page == "📈 Analytics & Reports":
    st.title("Analytics & Export Center")

    orders_df = st.session_state.orders_df
    inventory_df = st.session_state.inventory_df

    m1, m2 = st.columns(2)

    with m1:
        st.subheader("Revenue by Delivery Zone")
        zone_revenue = orders_df.groupby("Zone")["Total Value ($)"].sum().reset_index()
        st.bar_chart(zone_revenue, x="Zone", y="Total Value ($)")

    with m2:
        st.subheader("Driver Fulfillment Distribution")
        driver_perf = orders_df["Driver"].value_counts().reset_index()
        driver_perf.columns = ["Driver", "Shipments Handled"]
        st.bar_chart(driver_perf, x="Driver", y="Shipments Handled")

    st.divider()

    st.subheader("📥 Export Financial & Logistics Reports")
    ex1, ex2 = st.columns(2)

    with ex1:
        csv_inventory = inventory_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Inventory Report (CSV)",
            data=csv_inventory,
            file_name=f"mirage_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    with ex2:
        csv_orders = orders_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Dispatch & Orders Log (CSV)",
            data=csv_orders,
            file_name=f"mirage_orders_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
