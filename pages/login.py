
import streamlit as st

from utils.auth import login_user


def show_login():

    st.title("Welcome Back!")
    st.write("Login to your Smart Inventory Assistant.")

    with st.form("login_form"):

        email = st.text_input("Email Address")

        password = st.text_input(
            "Password",
            type="password"
        )

        submit = st.form_submit_button(
            "Login",
            use_container_width=True
        )

        if submit:

            if not email.strip() or not password:
                st.error("Please enter email and password.")

            else:

                success, result = login_user(
                    email,
                    password
                )

                if success:

                    st.session_state["logged_in"] = True
                    st.session_state["user"] = result

                    st.success("Login successful!")

                    st.rerun()

                else:
                    st.error(result)

