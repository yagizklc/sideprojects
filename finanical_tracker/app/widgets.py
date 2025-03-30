import streamlit as st


# Custom CSS for notifications


def load_widgets() -> None:
    notification_container()


def notification_container() -> None:
    st.markdown(
        """
<style>
.notification-container {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 9999;
    width: 300px;
    padding: 15px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.5s, fadeOut 0.5s 2.5s;
    opacity: 0.95;
}

.success-notification {
    background-color: #4CAF50;
}

.error-notification {
    background-color: #f44336;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 0.95;}
}

@keyframes fadeOut {
    from {opacity: 0.95;}
    to {opacity: 0;}
}
</style>
""",
        unsafe_allow_html=True,
    )


# Function to display notification
def show_notification():
    if st.session_state.notification["show"]:
        notification_type = st.session_state.notification["type"]
        css_class = (
            "success-notification"
            if notification_type == "success"
            else "error-notification"
        )

        st.markdown(
            f"""
        <div class="notification-container {css_class}" id="notification">
            {st.session_state.notification["message"]}
        </div>
        <script>
            setTimeout(function() {{
                document.getElementById('notification').style.display = 'none';
            }}, 3000);
        </script>
        """,
            unsafe_allow_html=True,
        )

        # Reset notification after displaying
        st.session_state.notification = {"show": False, "message": "", "type": ""}
