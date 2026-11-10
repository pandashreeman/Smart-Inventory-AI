import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database.db import get_connection

from models.demand_forecasting import (
    load_sales_data,
    train_model,
    forecast_demand,
    prepare_product_data
)


# -----------------------------------------
# Get products from database
# -----------------------------------------

def get_products():

    conn = get_connection()

    try:

        products = conn.execute("""
            SELECT id, product_name
            FROM products
            ORDER BY product_name
        """).fetchall()

        return products

    finally:
        conn.close()


# -----------------------------------------
# Machine Learning forecasting page
# -----------------------------------------

def show_forecast():

    st.title("🤖 ML Demand Forecasting")

    st.write(
        "Predict future product demand using "
        "Machine Learning and historical sales."
    )

    st.divider()

    products = get_products()

    if not products:

        st.warning(
            "Please add products before using demand forecasting."
        )

        return

    product_options = {
        f"{p['product_name']} (ID: {p['id']})": p["id"]
        for p in products
    }

    selected_product = st.selectbox(
        "Select Product",
        list(product_options.keys())
    )

    product_id = product_options[selected_product]

    st.divider()

    # -----------------------------------------
    # Historical sales information
    # -----------------------------------------

    st.subheader("Historical Sales Data")

    all_sales = load_sales_data()

    product_data = prepare_product_data(
        all_sales,
        product_id
    )

    if product_data.empty:

        st.warning(
            "No sales history is available for this product."
        )

        return

    col1, col2 = st.columns(2)

    col1.metric(
        "Historical Days",
        len(product_data)
    )

    col2.metric(
        "Total Units Sold",
        int(product_data["quantity_sold"].sum())
    )

    st.line_chart(
        product_data["quantity_sold"]
    )

    st.divider()

    # -----------------------------------------
    # Train Machine Learning model
    # -----------------------------------------

    st.subheader("Train Machine Learning Model")

    if st.button("Train Random Forest Model"):

        with st.spinner("Training model..."):

            result, message = train_model(product_id)

        if result is None:

            st.warning(message)

        else:

            st.success(message)

            st.metric(
                "Training Mean Absolute Error",
                f"{result['mae']:.2f} units"
            )

            st.caption(
                "This training error is measured on the training "
                "data, so it is not an independent test score."
            )

            st.success(
                "Model saved successfully in the saved_models folder."
            )

    st.divider()

    # -----------------------------------------
    # Generate future predictions
    # -----------------------------------------

    st.subheader("Predict Future Demand")

    days = st.selectbox(
        "Select Forecast Period",
        [7],
        format_func=lambda x: f"Next {x} Days"
    )

    if st.button("Generate Demand Forecast"):

        with st.spinner("Generating predictions..."):

            results, message = forecast_demand(
                product_id,
                days
            )

        if results is None:

            st.warning(message)

        else:

            st.success(message)

            st.write("### Predicted Product Demand")

            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

            total_demand = results[
                "Predicted Demand"
            ].sum()

            st.metric(
                "Expected Demand for Next 7 Days",
                f"{total_demand:.2f} units"
            )

            st.subheader("Demand Forecast Chart")

            fig, ax = plt.subplots(figsize=(10, 5))

            ax.plot(
                results["Date"],
                results["Predicted Demand"],
                marker="o"
            )

            ax.set_xlabel("Date")
            ax.set_ylabel("Predicted Quantity")
            ax.set_title("Next 7 Days Demand Forecast")

            plt.xticks(rotation=45)
            fig.tight_layout()

            st.pyplot(fig)

            plt.close(fig)


# -----------------------------------------
# Main page
# -----------------------------------------

def show_forecast_page():

    show_forecast()