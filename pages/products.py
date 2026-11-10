import streamlit as st
import pandas as pd
import sqlite3

from database.db import get_connection


def add_product():
    st.subheader("➕ Add New Product")

    with st.form("add_product_form"):

        product_name = st.text_input("Product Name")

        category = st.selectbox(
            "Category",
            [
                "Electronics",
                "Clothing",
                "Food",
                "Grocery",
                "Furniture",
                "Stationery",
                "Other"
            ]
        )

        price = st.number_input(
            "Product Price (₹)",
            min_value=0.0,
            step=10.0
        )

        description = st.text_area("Product Description")

        quantity = st.number_input(
            "Initial Stock Quantity",
            min_value=0,
            step=1
        )

        minimum_stock = st.number_input(
            "Minimum Stock Level",
            min_value=0,
            step=1
        )

        submitted = st.form_submit_button("Add Product")

        if submitted:

            if not product_name.strip():
                st.error("Please enter a product name.")

            elif price <= 0:
                st.error("Product price must be greater than zero.")

            else:
                conn = get_connection()

                try:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO products
                        (product_name, category, price, description)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            product_name.strip(),
                            category,
                            price,
                            description
                        )
                    )

                    product_id = cursor.lastrowid

                    cursor.execute(
                        """
                        INSERT INTO inventory
                        (product_id, quantity, minimum_stock)
                        VALUES (?, ?, ?)
                        """,
                        (
                            product_id,
                            quantity,
                            minimum_stock
                        )
                    )

                    conn.commit()

                    st.success("Product added successfully!")

                except sqlite3.IntegrityError as error:
                    conn.rollback()
                    st.error(f"Database error: {error}")

                except Exception as error:
                    conn.rollback()
                    st.error(f"Something went wrong: {error}")

                finally:
                    conn.close()


def view_products():
    st.subheader("📋 All Products")

    conn = get_connection()

    try:
        query = """
            SELECT
                p.id,
                p.product_name,
                p.category,
                p.price,
                p.description,
                i.quantity,
                i.minimum_stock
            FROM products p
            LEFT JOIN inventory i
            ON p.id = i.product_id
            ORDER BY p.id DESC
        """

        products = pd.read_sql_query(query, conn)

    except Exception as error:
        st.error(f"Unable to load products: {error}")
        return

    finally:
        conn.close()

    if products.empty:
        st.info("No products available. Add your first product.")
    else:
        products = products.rename(columns={
            "id": "Product ID",
            "product_name": "Product Name",
            "category": "Category",
            "price": "Price (₹)",
            "description": "Description",
            "quantity": "Available Stock",
            "minimum_stock": "Minimum Stock"
        })

        st.dataframe(
            products,
            use_container_width=True,
            hide_index=True
        )


def update_product():
    st.subheader("✏️ Update Product")

    conn = get_connection()

    try:
        products = conn.execute(
            """
            SELECT
                p.id,
                p.product_name,
                p.category,
                p.price,
                p.description,
                i.quantity,
                i.minimum_stock
            FROM products p
            LEFT JOIN inventory i
            ON p.id = i.product_id
            ORDER BY p.id
            """
        ).fetchall()

    finally:
        conn.close()

    if not products:
        st.info("No products available to update.")
        return

    product_options = {
        f"{row['product_name']} (ID: {row['id']})": row['id']
        for row in products
    }

    selected_product = st.selectbox(
        "Select Product",
        list(product_options.keys())
    )

    product_id = product_options[selected_product]

    selected_data = next(
        row for row in products if row["id"] == product_id
    )

    with st.form("update_product_form"):

        name = st.text_input(
            "Product Name",
            value=selected_data["product_name"]
        )

        category_options = [
            "Electronics",
            "Clothing",
            "Food",
            "Grocery",
            "Furniture",
            "Stationery",
            "Other"
        ]

        current_category = selected_data["category"]

        if current_category not in category_options:
            category_options.append(current_category)

        category = st.selectbox(
            "Category",
            category_options,
            index=category_options.index(current_category)
        )

        price = st.number_input(
            "Price (₹)",
            min_value=0.0,
            value=float(selected_data["price"]),
            step=10.0
        )

        description = st.text_area(
            "Description",
            value=selected_data["description"] or ""
        )

        quantity = st.number_input(
            "Available Stock",
            min_value=0,
            value=int(selected_data["quantity"] or 0),
            step=1
        )

        minimum_stock = st.number_input(
            "Minimum Stock",
            min_value=0,
            value=int(selected_data["minimum_stock"] or 0),
            step=1
        )

        submitted = st.form_submit_button("Update Product")

        if submitted:

            if not name.strip():
                st.error("Product name cannot be empty.")

            elif price <= 0:
                st.error("Price must be greater than zero.")

            else:
                conn = get_connection()

                try:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        UPDATE products
                        SET product_name = ?,
                            category = ?,
                            price = ?,
                            description = ?
                        WHERE id = ?
                        """,
                        (
                            name.strip(),
                            category,
                            price,
                            description,
                            product_id
                        )
                    )

                    cursor.execute(
                        """
                        UPDATE inventory
                        SET quantity = ?,
                            minimum_stock = ?
                        WHERE product_id = ?
                        """,
                        (
                            quantity,
                            minimum_stock,
                            product_id
                        )
                    )

                    conn.commit()

                    st.success("Product updated successfully!")

                except Exception as error:
                    conn.rollback()
                    st.error(f"Unable to update product: {error}")

                finally:
                    conn.close()


def delete_product():
    st.subheader("🗑️ Delete Product")

    conn = get_connection()

    try:
        products = conn.execute(
            """
            SELECT id, product_name
            FROM products
            ORDER BY product_name
            """
        ).fetchall()

    finally:
        conn.close()

    if not products:
        st.info("No products available to delete.")
        return

    product_options = {
        f"{row['product_name']} (ID: {row['id']})": row['id']
        for row in products
    }

    selected_product = st.selectbox(
        "Select Product to Delete",
        list(product_options.keys())
    )

    product_id = product_options[selected_product]

    st.warning(
        "Deleting a product may be blocked if it has related "
        "sales, purchases or stock movement records."
    )

    confirm = st.checkbox(
        "I confirm that I want to delete this product."
    )

    if st.button("Delete Product"):

        if not confirm:
            st.error("Please confirm before deleting.")

        else:
            conn = get_connection()

            try:
                cursor = conn.cursor()

                cursor.execute(
                    "DELETE FROM inventory WHERE product_id = ?",
                    (product_id,)
                )

                cursor.execute(
                    "DELETE FROM products WHERE id = ?",
                    (product_id,)
                )

                conn.commit()

                st.success("Product deleted successfully!")
                st.rerun()

            except sqlite3.IntegrityError:
                conn.rollback()

                st.error(
                    "This product has related transaction records. "
                    "It cannot be deleted. Keep it in the database "
                    "to preserve transaction history."
                )

            except Exception as error:
                conn.rollback()
                st.error(f"Unable to delete product: {error}")

            finally:
                conn.close()


def show_products():

    st.title("📦 Product Management")

    st.write(
        "Add, view, update and delete products in your inventory."
    )

    st.divider()

    operation = st.radio(
        "Choose an Operation",
        [
            "Add Product",
            "View Products",
            "Update Product",
            "Delete Product"
        ],
        horizontal=True
    )

    st.divider()

    if operation == "Add Product":
        add_product()

    elif operation == "View Products":
        view_products()

    elif operation == "Update Product":
        update_product()

    elif operation == "Delete Product":
        delete_product()