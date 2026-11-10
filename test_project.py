import os
import sqlite3
import importlib
import urllib.request


print("\n======================================")
print(" SMART INVENTORY PROJECT TESTING")
print("======================================\n")


# 1. CHECK PROJECT MODULES

modules = [
    "database.db",
    "utils.auth",
    "utils.report_generator",
    "pages.login",
    "pages.register",
    "pages.dashboard",
    "pages.products",
    "pages.sales",
    "pages.forecast",
    "pages.assistant",
    "pages.agent_dashboard",
    "pages.reports",
    "models.demand_forecasting",
    "agents.inventory_tools",
    "agents.ai_assistant",
    "agents.reorder_recommendation",
    "agents.inventory_workflow",
    "agents.forecast_tools"
]

print("1. MODULE TESTING")

for module in modules:

    try:
        importlib.import_module(module)
        print(f"[PASS] {module}")

    except Exception as error:
        print(f"[FAIL] {module}: {error}")


# 2. DATABASE TESTING

print("\n2. DATABASE TESTING")

if os.path.exists("inventory.db"):

    try:
        conn = sqlite3.connect("inventory.db")

        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table'
        """).fetchall()

        table_names = [table[0] for table in tables]

        required_tables = [
            "users",
            "suppliers",
            "products",
            "inventory",
            "sales",
            "purchases",
            "stock_movements",
            "predictions",
            "ai_history",
            "stock_alerts"
        ]

        for table in required_tables:

            if table in table_names:
                print(f"[PASS] {table} table exists")

            else:
                print(f"[FAIL] {table} table missing")

        conn.close()

    except Exception as error:
        print("[FAIL] Database error:", error)

else:

    print("[FAIL] inventory.db not found")


# 3. REPORT GENERATION TESTING

print("\n3. REPORT TESTING")

try:

    from utils.report_generator import (
        generate_pdf_report,
        generate_excel_report
    )

    pdf_data = generate_pdf_report("Inventory")

    if pdf_data.startswith(b"%PDF"):
        print("[PASS] PDF generation")
    else:
        print("[FAIL] PDF format is invalid")

    excel_data = generate_excel_report()

    if excel_data.startswith(b"PK"):
        print("[PASS] Excel generation")
    else:
        print("[FAIL] Excel format is invalid")

except Exception as error:

    print("[FAIL] Report testing:", error)


# 4. OLLAMA CONNECTION TESTING

print("\n4. OLLAMA CONNECTION TESTING")

try:

    url = "http://localhost:11434/api/tags"

    request = urllib.request.Request(url)

    with urllib.request.urlopen(
        request,
        timeout=5
    ) as response:

        print("[PASS] Ollama server is running")

except Exception as error:

    print("[WARNING] Ollama is not responding:", error)


# 5. ML MODEL FILE TESTING

print("\n5. MACHINE LEARNING MODEL TESTING")

model_folder = "saved_models"

if os.path.exists(model_folder):

    model_files = [
        file for file in os.listdir(model_folder)
        if file.endswith(".joblib")
    ]

    if model_files:

        for model in model_files:
            print(f"[PASS] {model}")

    else:

        print("[WARNING] No trained ML models found")

else:

    print("[WARNING] saved_models folder not found")


print("\n======================================")
print(" PROJECT TESTING COMPLETED")
print("======================================")