import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Initialize mock data in session state if not already initialized
if "inventory_data" not in st.session_state:
    st.session_state.inventory_data = {
        "SKU": ["A123", "B456", "C789"],
        "Product": ["Widget A", "Widget B", "Widget C"],
        "Category": ["Widgets", "Gadgets", "Widgets"],
        "Stock Level": [50, 20, 100],
        "Threshold": [10, 15, 30]
    }

if "orders_data" not in st.session_state:
    st.session_state.orders_data = {
        "Order ID": [1, 2, 3],
        "Product": ["Widget A", "Widget B", "Widget C"],
        "Quantity": [5, 10, 20],
        "Status": ["Shipped", "Pending", "Delivered"]
    }

# Convert dictionaries to DataFrames for easy manipulation
inventory_df = pd.DataFrame(st.session_state.inventory_data)
orders_df = pd.DataFrame(st.session_state.orders_data)

# Streamlit app layout
st.title("Online Inventory Management System (OIMS)")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select a page:", ["Inventory", "Orders", "Reports"])

# Inventory Page
if page == "Inventory":
    st.header("Inventory Management")

    # Display inventory data
    st.subheader("Current Inventory")
    st.dataframe(inventory_df)

    # Low Stock Alerts
    st.subheader("Low Stock Alerts")
    low_stock = inventory_df[inventory_df["Stock Level"] < inventory_df["Threshold"]]
    if not low_stock.empty:
        st.warning("The following items are low in stock:")
        st.table(low_stock)
    else:
        st.success("All items are sufficiently stocked.")

    # Stock Adjustment
    st.subheader("Adjust Stock Levels")
    sku = st.selectbox("Select SKU:", inventory_df["SKU"])
    adjustment = st.number_input("Adjustment Quantity:", value=0)
    if st.button("Adjust Stock"):
        index = inventory_df[inventory_df["SKU"] == sku].index[0]
        st.session_state.inventory_data["Stock Level"][index] += adjustment
        st.success(f"Stock level for {sku} updated.")
        inventory_df = pd.DataFrame(st.session_state.inventory_data)
        st.dataframe(inventory_df)

# Orders Page
elif page == "Orders":
    st.header("Order Processing")

    # Display orders data
    st.subheader("Current Orders")
    st.dataframe(orders_df)

    # Order Status Update
    st.subheader("Update Order Status")
    order_id = st.selectbox("Select Order ID:", orders_df["Order ID"])
    new_status = st.selectbox("New Status:", ["Pending", "Shipped", "Delivered"])
    if st.button("Update Status"):
        index = orders_df[orders_df["Order ID"] == order_id].index[0]
        st.session_state.orders_data["Status"][index] = new_status
        st.success(f"Order {order_id} status updated to {new_status}.")
        orders_df = pd.DataFrame(st.session_state.orders_data)
        st.dataframe(orders_df)

# Reports Page
elif page == "Reports":
    st.header("Sales and Inventory Reports")

    # Sales Report
    st.subheader("Sales Trends")
    # Generate some sample sales data
    dates = pd.date_range(start="2023-01-01", periods=12, freq="M")
    sales = np.random.randint(1000, 5000, size=12)
    sales_data = pd.DataFrame({"Date": dates, "Sales": sales})
    st.line_chart(sales_data.set_index("Date"))

    # Inventory Turnover
    st.subheader("Inventory Turnover")
    turnover = np.random.rand(3) * 10
    turnover_data = pd.DataFrame({
        "SKU": inventory_df["SKU"],
        "Product": inventory_df["Product"],
        "Turnover Rate": turnover
    })
    st.bar_chart(turnover_data.set_index("Product")["Turnover Rate"])

    # Product Performance
    st.subheader("Product Performance Metrics")
    performance_data = {
        "Product": ["Widget A", "Widget B", "Widget C"],
        "Sales": [150, 120, 300],
        "Returns": [5, 10, 8],
        "Profit Margin": [0.35, 0.25, 0.45]
    }
    performance_df = pd.DataFrame(performance_data)
    st.table(performance_df)

    st.write("These reports give insights into sales trends, inventory turnover, and individual product performance, helping managers make informed decisions.")
