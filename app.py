import streamlit as st
from pathlib import Path

from database.db import create_tables

from pages.login import show_login
from pages.register import show_register
from pages.dashboard import show_dashboard
from pages.products import show_products
from pages.sales import show_sales
from pages.forecast import show_forecast_page
from pages.assistant import show_assistant
from pages.agent_dashboard import show_agent_dashboard
from pages.reports import show_reports


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Smart Inventory Management",
    page_icon="📦",
    layout="wide"
)


# LOAD CUSTOM CSS

BASE_DIR = Path(__file__).resolve().parent
CSS_FILE = BASE_DIR / "assets" / "style.css"

if CSS_FILE.exists():
    with open(CSS_FILE, "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


# DATABASE

create_tables()


# SESSION STATE

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"


# LOGIN AND REGISTER

if not st.session_state.logged_in:

    st.title("📦 Smart Inventory Management System")

    choice = st.radio(
        "Select an option",
        ["Login", "Register"],
        horizontal=True
    )

    if choice == "Login":
        show_login()

    else:
        show_register()


# MAIN APPLICATION

else:

    # SIDEBAR HEADER

    st.sidebar.markdown(
        """
        <h2 style="color:#E8C77B;">
        📦 Smart Inventory
        </h2>
        """,
        unsafe_allow_html=True
    )

    if st.session_state.user:
        st.sidebar.success(
            f"Welcome, {st.session_state.user['name']}"
        )

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "<h4 style='color:#E8C77B;'>MAIN MENU</h4>",
        unsafe_allow_html=True
    )

    # NAVIGATION BUTTONS

    navigation = {
        "Dashboard": "🏠",
        "Product Management": "📦",
        "Sales Management": "💰",
        "ML Demand Forecasting": "📈",
        "AI Inventory Assistant": "🤖",
        "Agentic AI Dashboard": "🧠",
        "Reports and Export": "📊"
    }

    for page_name, icon in navigation.items():

        is_active = (
            st.session_state.active_page == page_name
        )

        button_label = (
            f"✓ {icon} {page_name}"
            if is_active
            else f"{icon} {page_name}"
        )

        if st.sidebar.button(
            button_label,
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):

            st.session_state.active_page = page_name
            st.rerun()

    st.sidebar.markdown("---")

    # LOGOUT BUTTON

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.active_page = "Dashboard"

        st.rerun()

    # PAGE DISPLAY

    page = st.session_state.active_page

    if page == "Dashboard":

        show_dashboard()

    elif page == "Product Management":

        show_products()

    elif page == "Sales Management":

        show_sales()

    elif page == "ML Demand Forecasting":

        show_forecast_page()

    elif page == "AI Inventory Assistant":

        show_assistant()

    elif page == "Agentic AI Dashboard":

        show_agent_dashboard()

    elif page == "Reports and Export":

        show_reports()