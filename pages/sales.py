import streamlit as st
import pandas as pd
from datetime import datetime

from database.db import get_connection


# Get all available products
def get_products():
    conn = get_connection()

    try:
        products = conn.execute("""
            SELECT
                p.id,
                p.product_name,
                p.price,
                i.quantity
            FROM products p
            JOIN inventory i
            ON p.id = i.product_id
            ORDER BY p.product_name
        """).fetchall()

        return products

    finally:
        conn.close()


# Record a new sale
def record_sale():

    st.subheader("Record New Sale")

    products = get_products()

    if not products:
        st.info("Please add products before recording a sale.")
        return

    product_options = {
        f"{p['product_name']} (Available: {p['quantity']})": p['id']
        for p in products
    }

    selected_product = st.selectbox(
        "Select Product",
        list(product_options.keys())
    )

    product_id = product_options[selected_product]

    product = next(
        p for p in products if p["id"] == product_id
    )

    available_stock = int(product["quantity"])
    product_price = float(product["price"])

    st.write(f"Available Stock: **{available_stock}**")
    st.write(f"Product Price: **₹{product_price:,.2f}**")

    with st.form("record_sale_form"):

        quantity = st.number_input(
            "Quantity Sold",
            min_value=1,
            max_value=max(1, available_stock),
            value=1,
            step=1
        )

        sale_price = st.number_input(
            "Selling Price Per Unit (₹)",
            min_value=0.01,
            value=max(0.01, product_price),
            step=10.0
        )

        total_amount = quantity * sale_price

        st.info(f"Total Sale Amount: ₹{total_amount:,.2f}")

        submitted = st.form_submit_button("Record Sale")

        if submitted:

            if available_stock <= 0:
                st.error("This product is out of stock.")

            elif quantity > available_stock:
                st.error("Not enough stock available.")

            elif sale_price <= 0:
                st.error("Selling price must be greater than zero.")

            else:

                conn = get_connection()

                try:
                    cursor = conn.cursor()

                    stock_row = cursor.execute(
                        """
                        SELECT quantity
                        FROM inventory
                        WHERE product_id = ?
                        """,
                        (product_id,)
                    ).fetchone()

                    if stock_row is None:
                        st.error("Inventory record not found.")
                        return

                    current_stock = int(stock_row["quantity"])

                    if quantity > current_stock:
                        st.error(
                            f"Only {current_stock} units are available."
                        )
                        return

                    sale_date = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    cursor.execute(
                        """
                        INSERT INTO sales
                        (
                            product_id,
                            quantity_sold,
                            unit_price,
                            total_amount,
                            sale_date
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            product_id,
                            quantity,
                            sale_price,
                            total_amount,
                            sale_date
                        )
                    )

                    cursor.execute(
                        """
                        UPDATE inventory
                        SET quantity = quantity - ?
                        WHERE product_id = ?
                        """,
                        (quantity, product_id)
                    )

                    conn.commit()

                    st.success("Sale recorded successfully!")

                    st.success(
                        f"Remaining stock: {current_stock - quantity}"
                    )

                except Exception as error:
                    conn.rollback()
                    st.error(f"Unable to record sale: {error}")

                finally:
                    conn.close()


# Display sales history
def sales_history():

    st.subheader("Sales History")

    conn = get_connection()

    try:
        sales = pd.read_sql_query(
            """
            SELECT
                s.id AS Sale_ID,
                p.product_name AS Product,
                s.quantity_sold AS Quantity,
                s.unit_price AS Unit_Price,
                s.total_amount AS Total_Amount,
                s.sale_date AS Sale_Date
            FROM sales s
            JOIN products p
            ON s.product_id = p.id
            ORDER BY s.sale_date DESC, s.id DESC
            """,
            conn
        )

    except Exception as error:
        st.error(f"Unable to load sales history: {error}")
        return

    finally:
        conn.close()

    if sales.empty:
        st.info("No sales transactions available yet.")

    else:
        sales["Unit_Price"] = sales["Unit_Price"].map(
            lambda value: f"₹{value:,.2f}"
        )

        sales["Total_Amount"] = sales["Total_Amount"].map(
            lambda value: f"₹{value:,.2f}"
        )

        st.dataframe(
            sales,
            use_container_width=True,
            hide_index=True
        )


# Display sales summary
def sales_summary():

    st.subheader("Sales Summary")

    conn = get_connection()

    try:
        summary = conn.execute(
            """
            SELECT
                COUNT(*) AS total_transactions,
                COALESCE(SUM(quantity_sold), 0) AS total_quantity,
                COALESCE(SUM(total_amount), 0) AS total_revenue
            FROM sales
            """
        ).fetchone()

        best_selling = pd.read_sql_query(
            """
            SELECT
                p.product_name AS Product,
                SUM(s.quantity_sold) AS Quantity_Sold,
                SUM(s.total_amount) AS Revenue
            FROM sales s
            JOIN products p
            ON s.product_id = p.id
            GROUP BY p.id, p.product_name
            ORDER BY Quantity_Sold DESC
            LIMIT 10
            """,
            conn
        )

    except Exception as error:
        st.error(f"Unable to load sales summary: {error}")
        return

    finally:
        conn.close()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Transactions",
        summary["total_transactions"]
    )

    col2.metric(
        "Total Quantity Sold",
        summary["total_quantity"]
    )

    col3.metric(
        "Total Revenue",
        f"₹{summary['total_revenue']:,.2f}"
    )

    st.divider()

    st.write("Best Selling Products")

    if best_selling.empty:
        st.info("No sales data available yet.")

    else:
        best_selling["Revenue"] = best_selling["Revenue"].map(
            lambda value: f"₹{value:,.2f}"
        )

        st.dataframe(
            best_selling,
            use_container_width=True,
            hide_index=True
        )


# Main sales page
def show_sales():

    st.title("💰 Sales Management")

    st.write(
        "Record sales, monitor revenue and manage sales transactions."
    )

    st.divider()

    option = st.radio(
        "Choose an Operation",
        [
            "Record Sale",
            "Sales History",
            "Sales Summary"
        ],
        horizontal=True
    )

    st.divider()

    if option == "Record Sale":
        record_sale()

    elif option == "Sales History":
        sales_history()

    elif option == "Sales Summary":
        sales_summary()