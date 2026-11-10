import streamlit as st
import pandas as pd

from datetime import datetime

from utils.report_generator import (
    get_inventory_report_data,
    get_sales_report_data,
    generate_pdf_report,
    generate_excel_report
)


def show_reports():

    st.title("📊 Reports and Export")

    st.write(
        "Generate and download inventory and sales reports "
        "in PDF and Excel formats."
    )

    st.divider()

    # INVENTORY REPORT

    st.subheader("📦 Inventory Report")

    try:

        inventory_df = get_inventory_report_data()

        if not inventory_df.empty:

            total_products = len(inventory_df)

            total_stock = inventory_df[
                "Available_Stock"
            ].sum()

            low_stock = len(
                inventory_df[
                    inventory_df["Stock_Status"] == "Low Stock"
                ]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Products",
                total_products
            )

            col2.metric(
                "Total Stock",
                int(total_stock)
            )

            col3.metric(
                "Low Stock Products",
                low_stock
            )

            st.dataframe(
                inventory_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No inventory records available.")

    except Exception as error:

        st.error(f"Inventory report error: {error}")

    st.divider()

    # SALES REPORT

    st.subheader("💰 Sales Report")

    try:

        sales_df = get_sales_report_data()

        if not sales_df.empty:

            total_transactions = len(sales_df)

            total_revenue = sales_df[
                "Total_Amount"
            ].sum()

            total_units = sales_df[
                "Quantity_Sold"
            ].sum()

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Transactions",
                total_transactions
            )

            col2.metric(
                "Total Units Sold",
                int(total_units)
            )

            col3.metric(
                "Total Revenue",
                f"₹{total_revenue:,.2f}"
            )

            st.dataframe(
                sales_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No sales records available.")

    except Exception as error:

        st.error(f"Sales report error: {error}")

    st.divider()

    # DOWNLOAD REPORTS

    st.subheader("⬇️ Download Reports")

    col1, col2 = st.columns(2)

    # PDF DOWNLOAD

    with col1:

        st.markdown("### PDF Reports")

        report_type = st.selectbox(
            "Select PDF Report",
            ["Inventory", "Sales"]
        )

        if st.button("Generate PDF"):

            try:

                pdf_data = generate_pdf_report(report_type)

                filename = (
                    f"{report_type.lower()}_report_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )

                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=filename,
                    mime="application/pdf"
                )

                st.success("PDF report generated successfully!")

            except Exception as error:

                st.error(f"PDF generation failed: {error}")

    # EXCEL DOWNLOAD

    with col2:

        st.markdown("### Excel Report")

        st.write(
            "Download inventory and sales information "
            "together in one Excel workbook."
        )

        if st.button("Generate Excel"):

            try:

                excel_data = generate_excel_report()

                filename = (
                    f"inventory_sales_report_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                )

                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=filename,
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
                )

                st.success("Excel report generated successfully!")

            except Exception as error:

                st.error(f"Excel generation failed: {error}")

    st.divider()

    st.caption(
        "Smart Inventory Management Assistant | "
        "PDF and Excel Report Generation"
    )