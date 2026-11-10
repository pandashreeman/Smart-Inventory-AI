import sqlite3
import pandas as pd

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


DB_NAME = "inventory.db"


# GET INVENTORY DATA

def get_inventory_report_data():

    conn = sqlite3.connect(DB_NAME)

    try:
        query = """
            SELECT
                p.id AS Product_ID,
                p.product_name AS Product_Name,
                p.category AS Category,
                p.price AS Price,
                i.quantity AS Available_Stock,
                i.minimum_stock AS Minimum_Stock
            FROM products p
            LEFT JOIN inventory i
                ON p.id = i.product_id
            ORDER BY p.product_name
        """

        df = pd.read_sql_query(query, conn)

        df["Available_Stock"] = (
            df["Available_Stock"].fillna(0).astype(int)
        )

        df["Minimum_Stock"] = (
            df["Minimum_Stock"].fillna(0).astype(int)
        )

        df["Stock_Status"] = df.apply(
            lambda row: (
                "Low Stock"
                if row["Available_Stock"] <= row["Minimum_Stock"]
                else "Available"
            ),
            axis=1
        )

        return df

    finally:
        conn.close()


# GET SALES DATA

def get_sales_report_data():

    conn = sqlite3.connect(DB_NAME)

    try:
        query = """
            SELECT
                s.id AS Sale_ID,
                p.product_name AS Product_Name,
                s.quantity_sold AS Quantity_Sold,
                s.unit_price AS Unit_Price,
                s.total_amount AS Total_Amount,
                s.sale_date AS Sale_Date
            FROM sales s
            JOIN products p
                ON s.product_id = p.id
            ORDER BY s.sale_date DESC
        """

        df = pd.read_sql_query(query, conn)

        return df

    finally:
        conn.close()


# GENERATE PDF REPORT

def generate_pdf_report(report_type):

    if report_type == "Inventory":

        df = get_inventory_report_data()
        title = "Inventory Report"

    else:

        df = get_sales_report_data()
        title = "Sales Report"

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4)
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Smart Inventory Management Assistant",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(title, styles["Heading2"])
    )

    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    if df.empty:

        elements.append(
            Paragraph("No records available.", styles["Normal"])
        )

    else:

        display_df = df.copy()

        for column in display_df.columns:
            display_df[column] = (
                display_df[column].fillna("").astype(str)
            )

        table_data = [
            list(display_df.columns)
        ] + display_df.values.tolist()

        report_table = Table(
            table_data,
            repeatRows=1
        )

        report_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#B87936")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.white,
                    colors.HexColor("#F5EBDD")
                ]),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ])
        )

        elements.append(report_table)

    document.build(elements)

    buffer.seek(0)

    return buffer.getvalue()


# GENERATE EXCEL REPORT

def generate_excel_report():

    inventory_df = get_inventory_report_data()
    sales_df = get_sales_report_data()

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        inventory_df.to_excel(
            writer,
            sheet_name="Inventory Report",
            index=False
        )

        sales_df.to_excel(
            writer,
            sheet_name="Sales Report",
            index=False
        )

    buffer.seek(0)

    return buffer.getvalue()