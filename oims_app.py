import streamlit as st
import pandas as pd
import plotly.express as px

# Sample data for demonstration purposes
# Normally this would be connected to a database

# Dummy data for inventory
inventory_data = {
    'SKU': ['P001', 'P002', 'P003', 'P004'],
    'Product Name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'Category': ['Electronics', 'Electronics', 'Electronics', 'Electronics'],
    'Stock': [20, 50, 10, 5],
    'Threshold': [10, 20, 5, 10],
    'Price': [800, 20, 30, 150]
}

# Dummy data for suppliers
suppliers_data = {
    'Supplier ID': ['S001', 'S002', 'S003'],
    'Name': ['TechSupplies', 'OfficeGoods', 'HomeOffice'],
    'Contact': ['123-456-7890', '987-654-3210', '555-555-5555'],
    'Product Supplied': ['Laptops, Accessories', 'Mice, Keyboards', 'Monitors']
}

# Dummy data for orders
orders_data = {
    'Order ID': ['O001', 'O002', 'O003'],
    'Product SKU': ['P001', 'P002', 'P003'],
    'Quantity': [2, 5, 3],
    'Status': ['Shipped', 'Pending', 'Delivered']
}

# Dummy sales data for reporting
sales_data = {
    'Product': ['Laptop', 'Mouse', 'Keyboard', 'Monitor'],
    'Units Sold': [150, 300, 200, 100],
    'Profit': [120000, 6000, 6000, 15000]
}

# Helper functions to display various features

def display_inventory():
    df_inventory = pd.DataFrame(inventory_data)
    st.write("### Inventory")
    st.dataframe(df_inventory)
    
    low_stock = df_inventory[df_inventory['Stock'] < df_inventory['Threshold']]
    st.write(f"### Low Stock Alert ({len(low_stock)} items)")
    st.dataframe(low_stock)

def update_inventory():
    st.write("### Update Inventory")
    sku = st.selectbox("Select Product", inventory_data['SKU'])
    action = st.radio("Action", ['Add Stock', 'Remove Stock'])
    quantity = st.number_input("Quantity", min_value=1, step=1)
    
    if st.button('Update Inventory'):
        if action == 'Add Stock':
            inventory_data['Stock'][inventory_data['SKU'].index(sku)] += quantity
        else:
            inventory_data['Stock'][inventory_data['SKU'].index(sku)] -= quantity
        st.success(f"Inventory Updated! {action} {quantity} units of {sku}")

def product_categorization():
    st.write("### Product Categorization")
    category = st.selectbox("Select Category", ['Electronics', 'Furniture', 'Clothing'])
    filtered_products = [prod for prod in inventory_data['Product Name'] if category in prod]
    st.write(f"Products in {category} category:")
    st.write(filtered_products)

def order_tracking():
    st.write("### Track Order")
    order_id = st.text_input("Enter Order ID")
    order = next((order for order in orders_data['Order ID'] if order == order_id), None)
    
    if order:
        status = next(order['Status'] for order in orders_data if order['Order ID'] == order_id)
        st.write(f"Order {order_id} is currently {status}")
    else:
        st.warning("Order not found")

def supplier_database():
    df_suppliers = pd.DataFrame(suppliers_data)
    st.write("### Supplier Database")
    st.dataframe(df_suppliers)

def reporting_and_analytics():
    st.write("### Reporting & Analytics")
    df_sales = pd.DataFrame(sales_data)
    fig = px.bar(df_sales, x='Product', y='Profit', title="Profit by Product")
    st.plotly_chart(fig)

# Main app layout

def main():
    st.set_page_config(page_title="Inventory Management System", layout="wide")
    
    st.title("Online Inventory Management System")
    
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Select Option", menu)
    
    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Login"):
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.sidebar.success("Login Successful")
            else:
                st.sidebar.error("Invalid Credentials")
    
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        dashboard = ["Dashboard", "Inventory", "Orders", "Suppliers", "Reports"]
        selection = st.sidebar.selectbox("Select Option", dashboard)
        
        if selection == "Dashboard":
            st.subheader("Welcome to the Dashboard!")
            st.write("Here you can manage inventory, track orders, view reports, and more.")
        
        if selection == "Inventory":
            display_inventory()
            update_inventory()
        
        if selection == "Orders":
            order_tracking()
        
        if selection == "Suppliers":
            supplier_database()
        
        if selection == "Reports":
            reporting_and_analytics()

if __name__ == '__main__':
    main()
