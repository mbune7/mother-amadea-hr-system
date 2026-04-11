import streamlit as st
from datetime import datetime

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Mother Amadea HR System",
    page_icon="🏥",
    layout="wide"
)

# ==================== LOGIN ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏥 Mother Amadea Mission Hospital")
    st.subheader("Human Resource Management System")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("amadea_logo.png", width=180)
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="12345")
        
        if st.button("Login", type="primary", use_container_width=True):
            if username == "admin" and password == "12345":
                st.session_state.logged_in = True
                st.success("Login Successful! Welcome back.")
                st.rerun()
            else:
                st.error("Invalid username or password!")
    st.stop()

# ==================== SIDEBAR ====================
st.sidebar.image("amadea_logo.png", width=120)
st.sidebar.title("Mother Amadea")
st.sidebar.subheader("Mission Hospital")
st.sidebar.success(f"Welcome back — {datetime.now().strftime('%B %Y')}")

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Staff Directory", "Departments", "Payroll", 
     "Attendance", "Leave Management", "KPI Dashboard", "Reports"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ==================== DASHBOARD ====================
if menu == "Dashboard":
    st.title("Dashboard")
    st.caption(f"Welcome back — {datetime.now().strftime('%B %Y')}")

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Staff", "74", "74 active • 0 on leave")
    with c2:
        st.metric("Departments", "9")
    with c3:
        st.metric("Monthly Payroll", "KSH 3,515,002")
    with c4:
        st.metric("Avg KPI Score", "90.8%")

    # Pending Actions
    st.subheader("Pending Actions")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("📅 **5 Leave Requests**\nAwaiting approval")
    with col_b:
        st.info("🔄 **0 Shift Swap Requests**\nPending review")

    # Performance Overview - FIXED
    st.subheader("Performance Overview")
    st.progress(0.917, text="Attendance Rate — 91.7%")
    st.progress(0.893, text="Punctuality — 89.3%")
    st.progress(0.905, text="Patient Satisfaction — 90.5%")
    st.progress(0.919, text="Task Completion — 91.9%")

    st.success("**Overall Score: 90.8%**")

# Placeholder for other pages
else:
    st.title(menu)
    st.info(f"The **{menu}** page is under development.\nWe can build full functionality here.")
