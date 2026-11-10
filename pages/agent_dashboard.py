import streamlit as st
import pandas as pd

from agents.reorder_recommendation import (
    get_reorder_recommendations,
    get_reorder_summary
)

from agents.forecast_tools import (
    get_ml_demand_analysis,
    get_ml_forecast_summary
)

from agents.inventory_workflow import run_inventory_analysis


def show_agent_dashboard():

    st.title("🤖 Agentic AI Dashboard")
    st.write(
        "Automated inventory analysis, smart reorder recommendations "
        "and machine learning demand forecasting."
    )

    st.divider()

    # RUN AUTOMATED ANALYSIS

    st.subheader("Automated Inventory Analysis")

    if st.button("Run Complete Inventory Analysis"):

        with st.spinner("AI is analyzing your inventory..."):

            try:
                report = run_inventory_analysis()

                st.success("Inventory analysis completed!")

                st.markdown("### AI Analysis Report")
                st.write(report)

            except Exception as error:
                st.error(f"Analysis failed: {error}")

    st.divider()

    # REORDER SUMMARY

    st.subheader("📦 Smart Reorder Summary")

    try:
        reorder_summary = get_reorder_summary()

        if isinstance(reorder_summary, dict):

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Total Products",
                reorder_summary.get("total_products", 0)
            )

            col2.metric(
                "Products to Reorder",
                reorder_summary.get("products_to_reorder", 0)
            )

            col3.metric(
                "Critical Products",
                reorder_summary.get("critical_products", 0)
            )

            col4.metric(
                "Estimated Reorder Cost",
                f"₹{reorder_summary.get('total_estimated_cost', 0):,.2f}"
            )

        else:
            st.info(str(reorder_summary))

    except Exception as error:
        st.error(f"Could not load reorder summary: {error}")

    # REORDER DETAILS

    st.subheader("Smart Reorder Recommendations")

    try:
        reorder_data = get_reorder_recommendations()

        if reorder_data:

            reorder_df = pd.DataFrame(reorder_data)

            if "recommended_quantity" in reorder_df.columns:

                reorder_df = reorder_df[
                    reorder_df["recommended_quantity"] > 0
                ]

            if not reorder_df.empty:

                st.dataframe(
                    reorder_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.success("No products currently require reordering.")

        else:
            st.info("No reorder recommendations available.")

    except Exception as error:
        st.error(f"Could not load reorder recommendations: {error}")

    st.divider()

    # ML FORECAST SUMMARY

    st.subheader("📈 ML Demand Forecast Summary")

    try:
        forecast_summary = get_ml_forecast_summary(days=7)

        if isinstance(forecast_summary, dict):

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Products",
                forecast_summary.get("total_products", 0)
            )

            col2.metric(
                "Successful Forecasts",
                forecast_summary.get("successful_forecasts", 0)
            )

            col3.metric(
                "Unavailable Forecasts",
                forecast_summary.get("unavailable_forecasts", 0)
            )

            col4, col5 = st.columns(2)

            col4.metric(
                "Predicted Demand",
                forecast_summary.get("total_predicted_demand", 0)
            )

            col5.metric(
                "Suggested Reorder",
                forecast_summary.get("total_suggested_reorder", 0)
            )

        else:
            st.info(str(forecast_summary))

    except Exception as error:
        st.error(f"Could not load forecast summary: {error}")

    # ML FORECAST DETAILS

    st.subheader("ML Demand Forecast Details")

    try:
        forecast_data = get_ml_demand_analysis(days=7)

        if isinstance(forecast_data, list) and forecast_data:

            forecast_df = pd.DataFrame(forecast_data)

            st.dataframe(
                forecast_df,
                use_container_width=True,
                hide_index=True
            )

            unavailable = [
                item for item in forecast_data
                if item.get("status") != "Success"
            ]

            if unavailable:
                st.warning(
                    "Some forecasts are unavailable. "
                    "Train the required product models from the "
                    "ML Demand Forecasting page."
                )

        elif isinstance(forecast_data, str):
            st.info(forecast_data)

        else:
            st.info("No forecast information is available.")

    except Exception as error:
        st.error(f"Could not load ML forecast details: {error}")

    st.divider()

    st.caption(
        "Smart Inventory Management Assistant | "
        "Agentic AI + Machine Learning + LLM"
    )