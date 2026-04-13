import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Mother Amadea HR System", page_icon="🏥", layout="wide")

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    .card {background: white; padding: 20px; border-radius: 16px; box-shadow: 0 6px 16px rgba(0,0,0,0.08); margin: 10px 0;}
    .profile-card {background: white; padding: 30px; border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.1); margin: 10px 0;}
    h1, h2, h3 {color: #1e3a8a;}
    .stMetric {background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);}
    .badge-active {background:#10b981;color:white;padding:4px 12px;border-radius:20px;font-size:13px;}
    .badge-inactive {background:#ef4444;color:white;padding:4px 12px;border-radius:20px;font-size:13px;}
    .badge-pending {background:#f59e0b;color:white;padding:4px 12px;border-radius:20px;font-size:13px;}
    .dept-card {background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 20px; border-radius: 16px; margin: 8px 0; cursor: pointer;}
    .kpi-bar {background: #e5e7eb; border-radius: 10px; height: 10px; margin: 6px 0;}
    .kpi-fill {background: #1e3a8a; border-radius: 10px; height: 10px;}
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE ====================
def get_conn():
    return sqlite3.connect("hospital_hr.db", check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            department TEXT NOT NULL,
            salary REAL NOT NULL,
            hire_date TEXT NOT NULL,
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            national_id TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            dob TEXT DEFAULT '',
            employment_type TEXT DEFAULT 'Full Time',
            status TEXT DEFAULT 'Active',
            emergency_contact TEXT DEFAULT '',
            address TEXT DEFAULT '',
            nhif TEXT DEFAULT '',
            nssf TEXT DEFAULT '',
            kra_pin TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS departments (
            dept_name TEXT PRIMARY KEY,
            description TEXT,
            head TEXT DEFAULT '',
            status TEXT DEFAULT 'Active'
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            clock_in TEXT DEFAULT '',
            clock_out TEXT DEFAULT '',
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            month TEXT NOT NULL,
            basic_salary REAL DEFAULT 0,
            house_allowance REAL DEFAULT 0,
            transport REAL DEFAULT 0,
            medical REAL DEFAULT 0,
            other_allowances REAL DEFAULT 0,
            paye REAL DEFAULT 0,
            nssf REAL DEFAULT 0,
            nhif REAL DEFAULT 0,
            loan_deduction REAL DEFAULT 0,
            other_deductions REAL DEFAULT 0,
            gross REAL DEFAULT 0,
            total_deductions REAL DEFAULT 0,
            net REAL DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            leave_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            days INTEGER DEFAULT 0,
            reason TEXT DEFAULT '',
            status TEXT DEFAULT 'Pending',
            approved_by TEXT DEFAULT '',
            applied_on TEXT DEFAULT '',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS kpi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            month TEXT NOT NULL,
            attendance_score REAL DEFAULT 0,
            punctuality_score REAL DEFAULT 0,
            patient_satisfaction REAL DEFAULT 0,
            task_completion REAL DEFAULT 0,
            teamwork REAL DEFAULT 0,
            overall_score REAL DEFAULT 0,
            remarks TEXT DEFAULT '',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS training (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            training_name TEXT NOT NULL,
            provider TEXT DEFAULT '',
            start_date TEXT DEFAULT '',
            end_date TEXT DEFAULT '',
            status TEXT DEFAULT 'Scheduled',
            certificate TEXT DEFAULT '',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            posted_by TEXT DEFAULT 'HR',
            posted_on TEXT DEFAULT '',
            priority TEXT DEFAULT 'Normal'
        );
        CREATE TABLE IF NOT EXISTS recruitment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            department TEXT NOT NULL,
            positions INTEGER DEFAULT 1,
            deadline TEXT DEFAULT '',
            status TEXT DEFAULT 'Open',
            applicants INTEGER DEFAULT 0,
            posted_on TEXT DEFAULT ''
        );
    ''')
    conn.commit()

    # Seed departments if empty
    c.execute("SELECT COUNT(*) FROM departments")
    if c.fetchone()[0] == 0:
        depts = [
            ("ANC", "Antenatal Clinic", "Sr. Nurse", "Active"),
            ("Administration", "Hospital Administration", "Admin Officer", "Active"),
            ("CWC", "Child Welfare Clinic", "Nurse In-Charge", "Active"),
            ("Lab", "Laboratory Services", "Lab Manager", "Active"),
            ("OPD", "Outpatient Department", "Dr. Grace Mwangi", "Active"),
            ("Pharmacy", "Pharmacy Department", "Pharmacist", "Active"),
            ("Radiology", "Radiology & Imaging", "Radiologist", "Active"),
            ("Theatre 1", "Operating Theatre 1", "Theatre Nurse", "Active"),
            ("Theatre 2", "Operating Theatre 2", "Theatre Nurse", "Active"),
        ]
        c.executemany("INSERT OR IGNORE INTO departments VALUES (?,?,?,?)", depts)

    # Seed sample employees if empty
    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0] == 0:
        employees = [
            ("MAMH-001","Dr. Grace Mwangi","Medical Officer","OPD",211553,"2020-01-15","0712345001","grace@amadea.co.ke","12345001","Female","1985-03-10","Full Time","Active","John Mwangi: 0712000001","Mombasa","NH001","NS001","A001234567B"),
            ("MAMH-002","Dr. James Okonkwo","Medical Officer","OPD",217963,"2019-06-01","0712345002","james@amadea.co.ke","12345002","Male","1982-07-22","Full Time","Active","Mary Okonkwo: 0712000002","Mombasa","NH002","NS002","A002234567B"),
            ("MAMH-003","Jane Atieno","Registered Nurse","Maternity",52719,"2021-03-01","0712345003","jane@amadea.co.ke","12345003","Female","1990-11-05","Full Time","Active","Peter Atieno: 0712000003","Mombasa","NH003","NS003","A003234567B"),
            ("MAMH-004","Peter Kamau","Enrolled Nurse","CWC",50592,"2021-07-15","0712345004","peter@amadea.co.ke","12345004","Male","1992-02-14","Full Time","Active","Grace Kamau: 0712000004","Mombasa","NH004","NS004","A004234567B"),
            ("MAMH-005","Mary Njeri","Enrolled Nurse","ANC",51945,"2022-01-10","0712345005","mary@amadea.co.ke","12345005","Female","1993-08-30","Full Time","Active","James Njeri: 0712000005","Mombasa","NH005","NS005","A005234567B"),
        ]
        c.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", employees)

    # Seed payroll if empty
    c.execute("SELECT COUNT(*) FROM payroll")
    if c.fetchone()[0] == 0:
        month = "2026-04"
        payroll_data = [
            ("MAMH-001", month, 150000, 30000, 15000, 10000, 6553, 35000, 1080, 1700, 0, 2220, 211553, 40000, 171553, "Paid"),
            ("MAMH-002", month, 155000, 31000, 15000, 10000, 6963, 36000, 1080, 1700, 0, 1220, 217963, 40000, 177963, "Paid"),
            ("MAMH-003", month, 38000, 7000, 4000, 2000, 1719, 4500, 720, 1700, 0, 80, 52719, 7000, 45719, "Paid"),
            ("MAMH-004", month, 36000, 7000, 4000, 2000, 1592, 4200, 720, 1700, 0, 380, 50592, 7000, 43592, "Paid"),
            ("MAMH-005", month, 37000, 7000, 4000, 2000, 1945, 4300, 720, 1700, 0, 280, 51945, 7000, 44945, "Paid"),
        ]
        c.executemany("INSERT OR IGNORE INTO payroll (emp_id,month,basic_salary,house_allowance,transport,medical,other_allowances,paye,nssf,nhif,loan_deduction,other_deductions,gross,total_deductions,net,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", payroll_data)

    conn.commit()
    conn.close()

init_db()

# ==================== HELPERS ====================
def get_employees():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM employees ORDER BY department, name", conn)
    conn.close()
    return df

def get_departments():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM departments ORDER BY dept_name", conn)
    conn.close()
    return df

def get_payroll(month=None):
    conn = get_conn()
    if month:
        df = pd.read_sql(f"SELECT p.*, e.name, e.department, e.position FROM payroll p JOIN employees e ON p.emp_id=e.emp_id WHERE p.month='{month}' ORDER BY e.name", conn)
    else:
        df = pd.read_sql("SELECT p.*, e.name, e.department, e.position FROM payroll p JOIN employees e ON p.emp_id=e.emp_id ORDER BY p.month DESC, e.name", conn)
    conn.close()
    return df

def get_leaves():
    conn = get_conn()
    df = pd.read_sql("SELECT l.*, e.name, e.department FROM leaves l JOIN employees e ON l.emp_id=e.emp_id ORDER BY l.id DESC", conn)
    conn.close()
    return df

def get_kpi(month=None):
    conn = get_conn()
    if month:
        df = pd.read_sql(f"SELECT k.*, e.name, e.department FROM kpi k JOIN employees e ON k.emp_id=e.emp_id WHERE k.month='{month}' ORDER BY k.overall_score DESC", conn)
    else:
        df = pd.read_sql("SELECT k.*, e.name, e.department FROM kpi k JOIN employees e ON k.emp_id=e.emp_id ORDER BY k.month DESC, k.overall_score DESC", conn)
    conn.close()
    return df

def generate_payslip_text(emp, pay):
    return f"""
================================================================================
                    MOTHER AMADEA MISSION HOSPITAL
                      EMPLOYEE PAY SLIP — {pay.get('month','')
}
================================================================================
Employee Name   : {emp['name']}
Employee ID     : {emp['emp_id']}
Position        : {emp['position']}
Department      : {emp['department']}
NHIF No         : {emp.get('nhif','')}
NSSF No         : {emp.get('nssf','')}
KRA PIN         : {emp.get('kra_pin','')}
================================================================================
EARNINGS
--------------------------------------------------------------------------------
Basic Salary                        KES {pay.get('basic_salary',0):>12,.2f}
House Allowance                     KES {pay.get('house_allowance',0):>12,.2f}
Transport Allowance                 KES {pay.get('transport',0):>12,.2f}
Medical Allowance                   KES {pay.get('medical',0):>12,.2f}
Other Allowances                    KES {pay.get('other_allowances',0):>12,.2f}
--------------------------------------------------------------------------------
GROSS PAY                           KES {pay.get('gross',0):>12,.2f}
================================================================================
DEDUCTIONS
--------------------------------------------------------------------------------
PAYE (Tax)                          KES {pay.get('paye',0):>12,.2f}
NSSF                                KES {pay.get('nssf',0):>12,.2f}
NHIF                                KES {pay.get('nhif',0):>12,.2f}
Loan Deduction                      KES {pay.get('loan_deduction',0):>12,.2f}
Other Deductions                    KES {pay.get('other_deductions',0):>12,.2f}
--------------------------------------------------------------------------------
TOTAL DEDUCTIONS                    KES {pay.get('total_deductions',0):>12,.2f}
================================================================================
NET PAY                             KES {pay.get('net',0):>12,.2f}
================================================================================
Generated on: {datetime.now().strftime('%d %B %Y %H:%M')}
This is a computer-generated payslip — no signature required.
================================================================================
"""

def generate_leave_letter(emp, leave):
    return f"""
================================================================================
                    MOTHER AMADEA MISSION HOSPITAL
                         LEAVE APPROVAL LETTER
================================================================================
Date: {datetime.now().strftime('%d %B %Y')}

To: {emp['name']}
    {emp['position']}
    {emp['department']} Department

Dear {emp['name'].split()[0]},

RE: APPROVAL OF {leave.get('leave_type','').upper()} LEAVE

This is to confirm that your application for {leave.get('leave_type','')} Leave
has been reviewed and {leave.get('status','Approved').upper()}.

Leave Details:
  Leave Type    : {leave.get('leave_type','')}
  Start Date    : {leave.get('start_date','')}
  End Date      : {leave.get('end_date','')}
  Total Days    : {leave.get('days','')} days
  Reason        : {leave.get('reason','')}

You are expected to report back to duty on {leave.get('end_date','')}.

Please ensure proper handover before proceeding on leave.

Yours sincerely,

_______________________
HR Manager
Mother Amadea Mission Hospital
Mombasa

================================================================================
"""

# ==================== LOGIN ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected_staff" not in st.session_state:
    st.session_state.selected_staff = None
if "selected_dept" not in st.session_state:
    st.session_state.selected_dept = None

if not st.session_state.logged_in:
    st.title("🏥 Mother Amadea Mission Hospital")
    st.subheader("Human Resource Management System")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("amadea_logo.png", width=240)
        except:
            st.markdown("### 🏥 Mother Amadea")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary", use_container_width=True):
            if username == "admin" and password == "12345":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    st.stop()

# ==================== SIDEBAR ====================
try:
    st.sidebar.image("amadea_logo.png", width=150)
except:
    pass
st.sidebar.title("Mother Amadea")
st.sidebar.subheader("Mission Hospital")
st.sidebar.success(f"Welcome — {datetime.now().strftime('%B %Y')}")

menu = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "👥 Staff Directory",
    "🏢 Departments",
    "💰 Payroll",
    "📅 Shift Scheduling",
    "⏰ Attendance",
    "🌴 Leave Management",
    "📈 KPI Dashboard",
    "🎓 Training",
    "📢 Announcements",
    "🧑‍💼 Recruitment",
    "📋 Reports"
])

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

# ====================== DASHBOARD ======================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption(f"Welcome back — {datetime.now().strftime('%A, %d %B %Y')}")

    emp_df = get_employees()
    total = len(emp_df)
    depts = len(get_departments())

    conn = get_conn()
    leaves_pending = pd.read_sql("SELECT COUNT(*) as c FROM leaves WHERE status='Pending'", conn).iloc[0]['c']
    pay_df = get_payroll("2026-04")
    net_payroll = pay_df['net'].sum() if len(pay_df) > 0 else 3515002
    conn.close()

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Staff", total, f"{total} active")
    with c2: st.metric("Departments", depts)
    with c3: st.metric("Monthly Payroll", f"KSH {net_payroll:,.0f}")
    with c4: st.metric("Avg KPI Score", "90.8%")

    col_a, col_b = st.columns(2)
    with col_a: st.info(f"📅 **{leaves_pending} Leave Requests** Awaiting approval")
    with col_b: st.info("🔄 **0 Shift Swap Requests** Pending review")

    st.subheader("Performance Overview")
    st.progress(0.917, text="Attendance Rate — 91.7%")
    st.progress(0.893, text="Punctuality — 89.3%")
    st.progress(0.905, text="Patient Satisfaction — 90.5%")
    st.progress(0.919, text="Task Completion — 91.9%")

    st.subheader("Staff by Department")
    if len(emp_df) > 0:
        dept_counts = emp_df.groupby('department').size().reset_index(name='Count')
        st.bar_chart(dept_counts.set_index('department'))

    conn2 = get_conn()
    announcements = pd.read_sql("SELECT * FROM announcements ORDER BY id DESC LIMIT 3", conn2)
    conn2.close()
    if len(announcements) > 0:
        st.subheader("📢 Latest Announcements")
        for _, ann in announcements.iterrows():
            st.info(f"**{ann['title']}** — {ann['message']}")

# ====================== STAFF DIRECTORY ======================
elif menu == "👥 Staff Directory":
    st.title("👥 Staff Directory")

    if st.session_state.selected_staff:
        # Full staff profile view
        emp_id = st.session_state.selected_staff
        conn = get_conn()
        emp = pd.read_sql(f"SELECT * FROM employees WHERE emp_id='{emp_id}'", conn).iloc[0]
        pay = pd.read_sql(f"SELECT * FROM payroll WHERE emp_id='{emp_id}' ORDER BY month DESC LIMIT 1", conn)
        att = pd.read_sql(f"SELECT * FROM attendance WHERE emp_id='{emp_id}' ORDER BY attendance_date DESC LIMIT 10", conn)
        leaves = pd.read_sql(f"SELECT * FROM leaves WHERE emp_id='{emp_id}' ORDER BY id DESC", conn)
        kpis = pd.read_sql(f"SELECT * FROM kpi WHERE emp_id='{emp_id}' ORDER BY month DESC LIMIT 1", conn)
        conn.close()

        if st.button("← Back to Staff Directory"):
            st.session_state.selected_staff = None
            st.rerun()

        st.markdown(f"""
        <div class="profile-card">
            <h2>👤 {emp['name']}</h2>
            <p style="color:#6b7280;font-size:16px;">{emp['position']} — {emp['department']}</p>
            <span class="badge-{'active' if emp['status']=='Active' else 'inactive'}">{emp['status']}</span>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Personal Info", "💰 Payroll", "⏰ Attendance", "🌴 Leaves", "📈 KPI"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Personal Details")
                st.write(f"**Employee ID:** {emp['emp_id']}")
                st.write(f"**Full Name:** {emp['name']}")
                st.write(f"**Gender:** {emp['gender']}")
                st.write(f"**Date of Birth:** {emp['dob']}")
                st.write(f"**National ID:** {emp['national_id']}")
                st.write(f"**Address:** {emp['address']}")
                st.write(f"**Emergency Contact:** {emp['emergency_contact']}")
            with col2:
                st.markdown("#### Employment Details")
                st.write(f"**Position:** {emp['position']}")
                st.write(f"**Department:** {emp['department']}")
                st.write(f"**Hire Date:** {emp['hire_date']}")
                st.write(f"**Employment Type:** {emp['employment_type']}")
                st.write(f"**Phone:** {emp['phone']}")
                st.write(f"**Email:** {emp['email']}")
                st.write(f"**NHIF No:** {emp['nhif']}")
                st.write(f"**NSSF No:** {emp['nssf']}")
                st.write(f"**KRA PIN:** {emp['kra_pin']}")

            st.markdown("---")
            st.markdown("#### ✏️ Edit Profile")
            with st.form("edit_profile"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    new_phone = st.text_input("Phone", emp['phone'])
                    new_email = st.text_input("Email", emp['email'])
                    new_address = st.text_input("Address", emp['address'])
                    new_emergency = st.text_input("Emergency Contact", emp['emergency_contact'])
                with ec2:
                    new_nhif = st.text_input("NHIF No", emp['nhif'])
                    new_nssf = st.text_input("NSSF No", emp['nssf'])
                    new_kra = st.text_input("KRA PIN", emp['kra_pin'])
                    new_status = st.selectbox("Status", ["Active", "Inactive", "On Leave"], index=["Active","Inactive","On Leave"].index(emp['status']) if emp['status'] in ["Active","Inactive","On Leave"] else 0)
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    conn = get_conn()
                    conn.execute("UPDATE employees SET phone=?,email=?,address=?,emergency_contact=?,nhif=?,nssf=?,kra_pin=?,status=? WHERE emp_id=?",
                        (new_phone, new_email, new_address, new_emergency, new_nhif, new_nssf, new_kra, new_status, emp_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Profile updated!")
                    st.rerun()

        with tab2:
            if len(pay) > 0:
                p = pay.iloc[0]
                st.metric("Gross Pay", f"KSH {p['gross']:,.0f}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Basic Salary:** KSH {p['basic_salary']:,.0f}")
                    st.write(f"**House Allowance:** KSH {p['house_allowance']:,.0f}")
                    st.write(f"**Transport:** KSH {p['transport']:,.0f}")
                    st.write(f"**Medical:** KSH {p['medical']:,.0f}")
                with col2:
                    st.write(f"**PAYE:** KSH {p['paye']:,.0f}")
                    st.write(f"**NSSF:** KSH {p['nssf']:,.0f}")
                    st.write(f"**NHIF:** KSH {p['nhif']:,.0f}")
                    st.write(f"**Net Pay:** KSH {p['net']:,.0f}")

                payslip = generate_payslip_text(emp, p)
                st.download_button("📥 Download Payslip", payslip, file_name=f"Payslip_{emp['emp_id']}_{p['month']}.txt", mime="text/plain")
            else:
                st.info("No payroll record found for this employee.")

        with tab3:
            if len(att) > 0:
                st.dataframe(att[['attendance_date','clock_in','clock_out','status','notes']], use_container_width=True, hide_index=True)
            else:
                st.info("No attendance records yet.")

        with tab4:
            if len(leaves) > 0:
                st.dataframe(leaves[['leave_type','start_date','end_date','days','status']], use_container_width=True, hide_index=True)
            else:
                st.info("No leave records yet.")

        with tab5:
            if len(kpis) > 0:
                k = kpis.iloc[0]
                st.metric("Overall KPI Score", f"{k['overall_score']:.1f}%")
                st.progress(k['attendance_score']/100, text=f"Attendance — {k['attendance_score']}%")
                st.progress(k['punctuality_score']/100, text=f"Punctuality — {k['punctuality_score']}%")
                st.progress(k['patient_satisfaction']/100, text=f"Patient Satisfaction — {k['patient_satisfaction']}%")
                st.progress(k['task_completion']/100, text=f"Task Completion — {k['task_completion']}%")
                st.progress(k['teamwork']/100, text=f"Teamwork — {k['teamwork']}%")
                if k['remarks']:
                    st.info(f"**Remarks:** {k['remarks']}")
            else:
                st.info("No KPI records yet.")

    else:
        emp_df = get_employees()
        st.caption(f"{len(emp_df)} employees")

        col_search, col_dept, col_status = st.columns(3)
        with col_search:
            search = st.text_input("🔍 Search by name or ID", "")
        with col_dept:
            depts = ["All"] + sorted(emp_df['department'].unique().tolist())
            dept_filter = st.selectbox("Department", depts)
        with col_status:
            status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])

        filtered = emp_df.copy()
        if search:
            filtered = filtered[filtered['name'].str.contains(search, case=False) | filtered['emp_id'].str.contains(search, case=False)]
        if dept_filter != "All":
            filtered = filtered[filtered['department'] == dept_filter]
        if status_filter != "All":
            filtered = filtered[filtered['status'] == status_filter]

        st.markdown("---")
        # Add new employee
        with st.expander("➕ Add New Staff Member"):
            with st.form("add_staff"):
                fc1, fc2 = st.columns(2)
                with fc1:
                    new_id = st.text_input("Employee ID (e.g. MAMH-075)")
                    new_name = st.text_input("Full Name")
                    new_pos = st.text_input("Position")
                    new_dept = st.selectbox("Department", sorted(emp_df['department'].unique().tolist()))
                    new_salary = st.number_input("Basic Salary (KES)", min_value=0.0)
                    new_hire = st.date_input("Hire Date")
                with fc2:
                    new_phone = st.text_input("Phone")
                    new_email = st.text_input("Email")
                    new_gender = st.selectbox("Gender", ["Female", "Male", "Other"])
                    new_dob = st.date_input("Date of Birth")
                    new_type = st.selectbox("Employment Type", ["Full Time", "Part Time", "Contract", "Locum"])
                    new_nid = st.text_input("National ID")
                if st.form_submit_button("✅ Add Staff", type="primary"):
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO employees (emp_id,name,position,department,salary,hire_date,phone,email,national_id,gender,dob,employment_type,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'Active')",
                            (new_id.upper(), new_name.title(), new_pos, new_dept, new_salary, str(new_hire), new_phone, new_email, new_nid, new_gender, str(new_dob), new_type))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ {new_name} added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

        cols = st.columns(4)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 4]:
                st.markdown(f"""
                <div class="card" style="text-align:center;min-height:200px;">
                    <div style="font-size:40px;">👤</div>
                    <h4 style="margin:8px 0;">{row['name']}</h4>
                    <p style="color:#6b7280;margin:4px 0;">{row['emp_id']}</p>
                    <p style="font-weight:600;margin:4px 0;">{row['position']}</p>
                    <p style="color:#6b7280;margin:4px 0;">{row['department']}</p>
                    <span class="badge-{'active' if row['status']=='Active' else 'inactive'}">{row['status']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"View Profile", key=f"view_{row['emp_id']}"):
                    st.session_state.selected_staff = row['emp_id']
                    st.rerun()

# ====================== DEPARTMENTS ======================
elif menu == "🏢 Departments":
    st.title("🏢 Departments")
    dept_df = get_departments()
    emp_df = get_employees()

    if st.session_state.selected_dept:
        dept_name = st.session_state.selected_dept
        dept = dept_df[dept_df['dept_name'] == dept_name].iloc[0]
        dept_staff = emp_df[emp_df['department'] == dept_name]

        if st.button("← Back to Departments"):
            st.session_state.selected_dept = None
            st.rerun()

        st.markdown(f"""
        <div class="profile-card">
            <h2>🏢 {dept['dept_name']}</h2>
            <p style="color:#6b7280;">{dept['description']}</p>
            <p><strong>Head:</strong> {dept['head']}</p>
            <span class="badge-active">{dept['status']}</span>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Total Staff", len(dept_staff))
        st.subheader(f"Staff in {dept_name}")

        if len(dept_staff) > 0:
            cols = st.columns(4)
            for i, (_, row) in enumerate(dept_staff.iterrows()):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="card" style="text-align:center;">
                        <div style="font-size:32px;">👤</div>
                        <h4>{row['name']}</h4>
                        <p>{row['emp_id']}</p>
                        <p><strong>{row['position']}</strong></p>
                        <span class="badge-{'active' if row['status']=='Active' else 'inactive'}">{row['status']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View Profile", key=f"dept_view_{row['emp_id']}"):
                        st.session_state.selected_staff = row['emp_id']
                        st.session_state.selected_dept = None
                        st.rerun()
        else:
            st.info("No staff assigned to this department yet.")

        st.markdown("---")
        st.subheader("✏️ Edit Department")
        with st.form("edit_dept"):
            new_desc = st.text_input("Description", dept['description'])
            new_head = st.text_input("Department Head", dept['head'])
            new_status = st.selectbox("Status", ["Active", "Inactive"], index=0 if dept['status']=="Active" else 1)
            if st.form_submit_button("💾 Save Changes", type="primary"):
                conn = get_conn()
                conn.execute("UPDATE departments SET description=?,head=?,status=? WHERE dept_name=?", (new_desc, new_head, new_status, dept_name))
                conn.commit()
                conn.close()
                st.success("✅ Department updated!")
                st.rerun()

    else:
        st.caption(f"{len(dept_df)} active departments")

        with st.expander("➕ Add New Department"):
            with st.form("add_dept"):
                d1, d2 = st.columns(2)
                with d1:
                    new_dept_name = st.text_input("Department Name")
                    new_dept_desc = st.text_input("Description")
                with d2:
                    new_dept_head = st.text_input("Department Head")
                if st.form_submit_button("✅ Add Department", type="primary"):
                    try:
                        conn = get_conn()
                        conn.execute("INSERT INTO departments VALUES (?,?,?,'Active')", (new_dept_name.title(), new_dept_desc, new_dept_head))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ {new_dept_name} added!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

        cols = st.columns(3)
        for i, (_, dept) in enumerate(dept_df.iterrows()):
            staff_count = len(emp_df[emp_df['department'] == dept['dept_name']])
            with cols[i % 3]:
                st.markdown(f"""
                <div class="dept-card">
                    <h3 style="color:white;margin:0;">{dept['dept_name']}</h3>
                    <p style="color:#bfdbfe;margin:4px 0;">{dept['description']}</p>
                    <p style="color:white;margin:4px 0;"><strong>Head:</strong> {dept['head']}</p>
                    <p style="color:#bfdbfe;margin:4px 0;">👥 {staff_count} staff</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"View Department", key=f"dept_{dept['dept_name']}"):
                    st.session_state.selected_dept = dept['dept_name']
                    st.rerun()

# ====================== PAYROLL ======================
elif menu == "💰 Payroll":
    st.title("💰 Payroll Management")

    months = ["2026-04", "2026-03", "2026-02", "2026-01"]
    selected_month = st.selectbox("Select Month", months)
    pay_df = get_payroll(selected_month)

    if len(pay_df) > 0:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Gross", f"KSH {pay_df['gross'].sum():,.0f}")
        with c2: st.metric("Total Deductions", f"KSH {pay_df['total_deductions'].sum():,.0f}")
        with c3: st.metric("Net Payroll", f"KSH {pay_df['net'].sum():,.0f}")
        with c4: st.metric("Payslips", len(pay_df))

    tab1, tab2, tab3 = st.tabs(["📋 Payroll Records", "➕ Add/Edit Payroll", "📥 Generate Payslips"])

    with tab1:
        if len(pay_df) > 0:
            display_cols = ['name','department','basic_salary','house_allowance','transport','paye','nssf','nhif','gross','total_deductions','net','status']
            available = [c for c in display_cols if c in pay_df.columns]
            st.dataframe(pay_df[available], use_container_width=True, hide_index=True)

            # Export payroll to Excel
            output = io.BytesIO()
            pay_df.to_excel(output, index=False)
            st.download_button("📥 Export Payroll to Excel", output.getvalue(), file_name=f"Payroll_{selected_month}.xlsx", mime="application/vnd.ms-excel")
        else:
            st.info("No payroll records for this month.")

    with tab2:
        emp_df = get_employees()
        st.subheader("Add / Edit Employee Payroll")
        emp_options = {f"{r['emp_id']} - {r['name']}": r['emp_id'] for _, r in emp_df.iterrows()}
        selected_emp_label = st.selectbox("Select Employee", list(emp_options.keys()))
        selected_emp_id = emp_options[selected_emp_label]

        # Load existing payroll if any
        conn = get_conn()
        existing = pd.read_sql(f"SELECT * FROM payroll WHERE emp_id='{selected_emp_id}' AND month='{selected_month}'", conn)
        conn.close()
        ex = existing.iloc[0] if len(existing) > 0 else None

        with st.form("payroll_form"):
            st.markdown("#### Earnings")
            p1, p2, p3 = st.columns(3)
            with p1:
                basic = st.number_input("Basic Salary", value=float(ex['basic_salary']) if ex is not None else 0.0)
                house = st.number_input("House Allowance", value=float(ex['house_allowance']) if ex is not None else 0.0)
            with p2:
                transport = st.number_input("Transport", value=float(ex['transport']) if ex is not None else 0.0)
                medical = st.number_input("Medical Allowance", value=float(ex['medical']) if ex is not None else 0.0)
            with p3:
                other_allow = st.number_input("Other Allowances", value=float(ex['other_allowances']) if ex is not None else 0.0)

            st.markdown("#### Deductions")
            d1, d2, d3 = st.columns(3)
            with d1:
                paye = st.number_input("PAYE (Tax)", value=float(ex['paye']) if ex is not None else 0.0)
                nssf = st.number_input("NSSF", value=float(ex['nssf']) if ex is not None else 720.0)
            with d2:
                nhif = st.number_input("NHIF", value=float(ex['nhif']) if ex is not None else 1700.0)
                loan = st.number_input("Loan Deduction", value=float(ex['loan_deduction']) if ex is not None else 0.0)
            with d3:
                other_deduct = st.number_input("Other Deductions", value=float(ex['other_deductions']) if ex is not None else 0.0)
                pay_status = st.selectbox("Status", ["Pending", "Paid", "On Hold"], index=["Pending","Paid","On Hold"].index(ex['status']) if ex is not None and ex['status'] in ["Pending","Paid","On Hold"] else 0)

            gross = basic + house + transport + medical + other_allow
            total_deduct = paye + nssf + nhif + loan + other_deduct
            net = gross - total_deduct
            st.info(f"**Gross:** KSH {gross:,.0f} | **Deductions:** KSH {total_deduct:,.0f} | **Net:** KSH {net:,.0f}")

            if st.form_submit_button("💾 Save Payroll", type="primary"):
                conn = get_conn()
                if ex is not None:
                    conn.execute("UPDATE payroll SET basic_salary=?,house_allowance=?,transport=?,medical=?,other_allowances=?,paye=?,nssf=?,nhif=?,loan_deduction=?,other_deductions=?,gross=?,total_deductions=?,net=?,status=? WHERE emp_id=? AND month=?",
                        (basic, house, transport, medical, other_allow, paye, nssf, nhif, loan, other_deduct, gross, total_deduct, net, pay_status, selected_emp_id, selected_month))
                else:
                    conn.execute("INSERT INTO payroll (emp_id,month,basic_salary,house_allowance,transport,medical,other_allowances,paye,nssf,nhif,loan_deduction,other_deductions,gross,total_deductions,net,status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (selected_emp_id, selected_month, basic, house, transport, medical, other_allow, paye, nssf, nhif, loan, other_deduct, gross, total_deduct, net, pay_status))
                conn.commit()
                conn.close()
                st.success("✅ Payroll saved!")
                st.rerun()

    with tab3:
        st.subheader("Generate Payslips")
        if len(pay_df) > 0:
            emp_options2 = {f"{r['emp_id']} - {r['name']}": r['emp_id'] for _, r in pay_df.iterrows()}
            selected_for_slip = st.selectbox("Select Employee for Payslip", list(emp_options2.keys()))
            slip_emp_id = emp_options2[selected_for_slip]
            slip_row = pay_df[pay_df['emp_id'] == slip_emp_id].iloc[0]
            conn = get_conn()
            emp_row = pd.read_sql(f"SELECT * FROM employees WHERE emp_id='{slip_emp_id}'", conn).iloc[0]
            conn.close()
            payslip = generate_payslip_text(emp_row, slip_row)
            st.text(payslip)
            st.download_button("📥 Download Payslip", payslip, file_name=f"Payslip_{slip_emp_id}_{selected_month}.txt", mime="text/plain")

            # Bulk all payslips
            all_slips = ""
            for _, prow in pay_df.iterrows():
                try:
                    conn2 = get_conn()
                    erow = pd.read_sql(f"SELECT * FROM employees WHERE emp_id='{prow['emp_id']}'", conn2).iloc[0]
                    conn2.close()
                    all_slips += generate_payslip_text(erow, prow) + "\n\n"
                except:
                    pass
            st.download_button("📥 Download All Payslips", all_slips, file_name=f"All_Payslips_{selected_month}.txt", mime="text/plain")
        else:
            st.info("No payroll records to generate payslips.")

# ====================== ATTENDANCE ======================
elif menu == "⏰ Attendance":
    st.title("⏰ Attendance Tracking")
    st.caption(f"{datetime.now().strftime('%B %Y')}")

    tab1, tab2 = st.tabs(["📋 Records", "➕ Mark Attendance"])

    with tab1:
        conn = get_conn()
        att_df = pd.read_sql("SELECT a.*, e.name, e.department FROM attendance a JOIN employees e ON a.emp_id=e.emp_id ORDER BY a.attendance_date DESC", conn)
        conn.close()

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Present", len(att_df[att_df['status']=='Present']))
        with c2: st.metric("Absent", len(att_df[att_df['status']=='Absent']))
        with c3: st.metric("Late", len(att_df[att_df['status']=='Late']))
        with c4: st.metric("On Leave", len(att_df[att_df['status']=='On Leave']))

        if len(att_df) > 0:
            st.dataframe(att_df[['name','department','attendance_date','clock_in','clock_out','status','notes']], use_container_width=True, hide_index=True)
            output = io.BytesIO()
            att_df.to_excel(output, index=False)
            st.download_button("📥 Export Attendance", output.getvalue(), file_name="Attendance_Report.xlsx", mime="application/vnd.ms-excel")
        else:
            st.info("No attendance records yet.")

    with tab2:
        emp_df = get_employees()
        with st.form("mark_att"):
            emp_options = {f"{r['emp_id']} - {r['name']}": r['emp_id'] for _, r in emp_df.iterrows()}
            sel_emp = st.selectbox("Employee", list(emp_options.keys()))
            att_date = st.date_input("Date", date.today())
            att_status = st.selectbox("Status", ["Present", "Absent", "Late", "On Leave", "Half Day"])
            clock_in = st.text_input("Clock In (e.g. 08:00 AM)")
            clock_out = st.text_input("Clock Out (e.g. 05:00 PM)")
            notes = st.text_area("Notes")
            if st.form_submit_button("✅ Mark Attendance", type="primary"):
                conn = get_conn()
                conn.execute("INSERT INTO attendance (emp_id,attendance_date,clock_in,clock_out,status,notes) VALUES (?,?,?,?,?,?)",
                    (emp_options[sel_emp], str(att_date), clock_in, clock_out, att_status, notes))
                conn.commit()
                conn.close()
                st.success("✅ Attendance marked!")
                st.rerun()

# ====================== LEAVE MANAGEMENT ======================
elif menu == "🌴 Leave Management":
    st.title("🌴 Leave Management")
    emp_df = get_employees()

    tab1, tab2, tab3 = st.tabs(["📋 All Leaves", "➕ New Leave Request", "📄 Generate Leave Letter"])

    with tab1:
        leaves_df = get_leaves()
        if len(leaves_df) > 0:
            status_options = ["All", "Pending", "Approved", "Rejected"]
            status_f = st.selectbox("Filter by Status", status_options)
            if status_f != "All":
                leaves_df = leaves_df[leaves_df['status'] == status_f]

            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Leaves", len(leaves_df))
            with c2: st.metric("Pending", len(leaves_df[leaves_df['status']=='Pending']))
            with c3: st.metric("Approved", len(leaves_df[leaves_df['status']=='Approved']))
            with c4: st.metric("Rejected", len(leaves_df[leaves_df['status']=='Rejected']))

            for _, leave in leaves_df.iterrows():
                with st.expander(f"🌴 {leave['name']} — {leave['leave_type']} ({leave['start_date']} to {leave['end_date']})"):
                    l1, l2, l3 = st.columns(3)
                    with l1:
                        st.write(f"**Employee:** {leave['name']}")
                        st.write(f"**Department:** {leave['department']}")
                        st.write(f"**Leave Type:** {leave['leave_type']}")
                    with l2:
                        st.write(f"**Start:** {leave['start_date']}")
                        st.write(f"**End:** {leave['end_date']}")
                        st.write(f"**Days:** {leave['days']}")
                    with l3:
                        st.write(f"**Status:** {leave['status']}")
                        st.write(f"**Reason:** {leave['reason']}")

                    if leave['status'] == 'Pending':
                        a1, a2 = st.columns(2)
                        with a1:
                            if st.button("✅ Approve", key=f"approve_{leave['id']}"):
                                conn = get_conn()
                                conn.execute("UPDATE leaves SET status='Approved', approved_by='HR Manager' WHERE id=?", (leave['id'],))
                                conn.commit()
                                conn.close()
                                st.success("Approved!")
                                st.rerun()
                        with a2:
                            if st.button("❌ Reject", key=f"reject_{leave['id']}"):
                                conn = get_conn()
                                conn.execute("UPDATE leaves SET status='Rejected' WHERE id=?", (leave['id'],))
                                conn.commit()
                                conn.close()
                                st.warning("Rejected!")
                                st.rerun()
        else:
            st.info("No leave requests yet.")

    with tab2:
        with st.form("leave_form"):
            emp_opts = {f"{r['emp_id']} - {r['name']}": r['emp_id'] for _, r in emp_df.iterrows()}
            sel_emp = st.selectbox("Employee", list(emp_opts.keys()))
            leave_type = st.selectbox("Leave Type", ["Annual", "Sick", "Emergency", "Maternity", "Paternity", "Compassionate", "Study", "Unpaid"])
            lc1, lc2 = st.columns(2)
            with lc1:
                start = st.date_input("Start Date")
            with lc2:
                end = st.date_input("End Date")
            reason = st.text_area("Reason for Leave")
            if st.form_submit_button("📤 Submit Leave Request", type="primary"):
                days = (end - start).days + 1
                conn = get_conn()
                conn.execute("INSERT INTO leaves (emp_id,leave_type,start_date,end_date,days,reason,status,applied_on) VALUES (?,?,?,?,?,?,'Pending',?)",
                    (emp_opts[sel_emp], leave_type, str(start), str(end), days, reason, str(date.today())))
                conn.commit()
                conn.close()
                st.success("✅ Leave request submitted!")
                st.rerun()

    with tab3:
        leaves_df2 = get_leaves()
        approved = leaves_df2[leaves_df2['status'] == 'Approved'] if len(leaves_df2) > 0 else pd.DataFrame()
        if len(approved) > 0:
            leave_opts = {f"{r['name']} — {r['leave_type']} ({r['start_date']})": r['id'] for _, r in approved.iterrows()}
            selected_leave = st.selectbox("Select Leave", list(leave_opts.keys()))
            leave_id = leave_opts[selected_leave]
            leave_row = approved[approved['id'] == leave_id].iloc[0]
            conn = get_conn()
            emp_row = pd.read_sql(f"SELECT * FROM employees WHERE emp_id='{leave_row['emp_id']}'", conn).iloc[0]
            conn.close()
            letter = generate_leave_letter(emp_row, leave_row)
            st.text(letter)
            st.download_button("📥 Download Leave Letter", letter, file_name=f"Leave_Letter_{emp_row['emp_id']}.txt", mime="text/plain")
        else:
            st.info("No approved leaves to generate letters for. Approve a leave request first.")

# ====================== KPI DASHBOARD ======================
elif menu == "📈 KPI Dashboard":
    st.title("📈 KPI Dashboard")

    months = ["2026-04", "2026-03", "2026-02"]
    kpi_month = st.selectbox("Month", months)
    kpi_df = get_kpi(kpi_month)
    emp_df = get_employees()

    if len(kpi_df) > 0:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Avg Attendance", f"{kpi_df['attendance_score'].mean():.1f}%")
        with c2: st.metric("Avg Punctuality", f"{kpi_df['punctuality_score'].mean():.1f}%")
        with c3: st.metric("Avg Satisfaction", f"{kpi_df['patient_satisfaction'].mean():.1f}%")
        with c4: st.metric("Avg Overall", f"{kpi_df['overall_score'].mean():.1f}%")

    tab1, tab2, tab3 = st.tabs(["📊 Team KPI", "👤 Individual KPI", "➕ Add/Edit KPI"])

    with tab1:
        if len(kpi_df) > 0:
            st.subheader("Team KPI Overview")
            st.progress(kpi_df['attendance_score'].mean()/100, text=f"Attendance — {kpi_df['attendance_score'].mean():.1f}%")
            st.progress(kpi_df['punctuality_score'].mean()/100, text=f"Punctuality — {kpi_df['punctuality_score'].mean():.1f}%")
            st.progress(kpi_df['patient_satisfaction'].mean()/100, text=f"Patient Satisfaction — {kpi_df['patient_satisfaction'].mean():.1f}%")
            st.progress(kpi_df['task_completion'].mean()/100, text=f"Task Completion — {kpi_df['task_completion'].mean():.1f}%")
            st.progress(kpi_df['teamwork'].mean()/100, text=f"Teamwork — {kpi_df['teamwork'].mean():.1f}%")

            st.subheader("Staff KPI Table")
            display = kpi_df[['name','department','attendance_score','punctuality_score','patient_satisfaction','task_completion','teamwork','overall_score','remarks']].copy()
            display.columns = ['Name','Department','Attendance%','Punctuality%','Satisfaction%','Task%','Teamwork%','Overall%','Remarks']
            st.dataframe(display, use_container_width=True, hide_index=True)

            output = io.BytesIO()
            display.to_excel(output, index=False)
            st.download_button("📥 Download KPI Report", output.getvalue(), file_name=f"KPI_{kpi_month}.xlsx", mime="application/vnd.ms-excel")
        else:
            st.info("No KPI records for this month.")

    with tab2:
        if len(kpi_df) > 0:
            emp_opts = {f"{r['name']} ({r['department']})": r['emp_id'] for _, r in kpi_df.iterrows()}
            sel = st.selectbox("Select Employee", list(emp_opts.keys()))
            sel_id = emp_opts[sel]
            row = kpi_df[kpi_df['emp_id'] == sel_id].iloc[0]

            st.markdown(f"### 📊 {row['name']} — {row['department']}")
            st.metric("Overall KPI Score", f"{row['overall_score']:.1f}%")
            st.progress(row['attendance_score']/100, text=f"Attendance — {row['attendance_score']}%")
            st.progress(row['punctuality_score']/100, text=f"Punctuality — {row['punctuality_score']}%")
            st.progress(row['patient_satisfaction']/100, text=f"Patient Satisfaction — {row['patient_satisfaction']}%")
            st.progress(row['task_completion']/100, text=f"Task Completion — {row['task_completion']}%")
            st.progress(row['teamwork']/100, text=f"Teamwork — {row['teamwork']}%")
            if row['remarks']:
                st.info(f"**Remarks:** {row['remarks']}")

            # Individual KPI report download
            kpi_text = f"""
MOTHER AMADEA MISSION HOSPITAL — KPI REPORT
============================================
Employee  : {row['name']}
Department: {row['department']}
Month     : {kpi_month}
============================================
Attendance Score    : {row['attendance_score']}%
Punctuality Score   : {row['punctuality_score']}%
Patient Satisfaction: {row['patient_satisfaction']}%
Task Completion     : {row['task_completion']}%
Teamwork            : {row['teamwork']}%
--------------------------------------------
OVERALL SCORE       : {row['overall_score']}%
============================================
Remarks: {row['remarks']}
Generated: {datetime.now().strftime('%d %B %Y')}
"""
            st.download_button("📥 Download Individual KPI", kpi_text, file_name=f"KPI_{sel_id}_{kpi_month}.txt", mime="text/plain")
        else:
            st.info("No KPI records yet.")

    with tab3:
        emp_opts2 = {f"{r['emp_id']} - {r['name']}": r['emp_id'] for _, r in emp_df.iterrows()}
        sel_emp = st.selectbox("Select Employee", list(emp_opts2.keys()), key="kpi_emp")
        sel_id2 = emp_opts2[sel_emp]

        conn = get_conn()
        existing_kpi = pd.read_sql(f"SELECT * FROM kpi WHERE emp_id='{sel_id2}' AND month='{kpi_month}'", conn)
        conn.close()
        ek = existing_kpi.iloc[0] if len(existing_kpi) > 0 else None

        with st.form("kpi_form"):
            k1, k2 = st.columns(2)
            with k1:
                att_s = st.slider("Attendance Score (%)", 0, 100, int(ek['attendance_score']) if ek is not None else 90)
                pun_s = st.slider("Punctuality Score (%)", 0, 100, int(ek['punctuality_score']) if ek is not None else 90)
                pat_s = st.slider("Patient Satisfaction (%)", 0, 100, int(ek['patient_satisfaction']) if ek is not None else 90)
            with k2:
                task_s = st.slider("Task Completion (%)", 0, 100, int(ek['task_completion']) if ek is not None else 90)
                team_s = st.slider("Teamwork (%)", 0, 100, int(ek['teamwork']) if ek is not None else 90)
                remarks = st.text_area("Remarks", value=ek['remarks'] if ek is not None else "")

            overall = round((att_s + pun_s + pat_s + task_s + team_s) / 5, 1)
            st.info(f"**Overall Score: {overall}%**")

            if st.form_submit_button("💾 Save KPI", type="primary"):
                conn = get_conn()
                if ek is not None:
                    conn.execute("UPDATE kpi SET attendance_score=?,punctuality_score=?,patient_satisfaction=?,task_completion=?,teamwork=?,overall_score=?,remarks=? WHERE emp_id=? AND month=?",
                        (att_s, pun_s, pat_s, task_s, team_s, overall, remarks, sel_id2, kpi_month))
                else:
                    conn.execute("INSERT INTO kpi (emp_id,month,attendance_score,punctuality_score,patient_satisfaction,task_completion,teamwork,overall_score,remarks) VALUES (?,?,?,?,?,?,?,?,?)",
                        (sel_id2, kpi_month, att_s, pun_s, pat_s, task_s, team_s, overall, remarks))
                conn.commit()
                conn.close()
                st.success("✅ KPI saved!")
                st.rerun()

# ====================== SHIFT SCHEDULING ======================
elif menu == "📅 Shift Scheduling":
    st.title("📅 Shift Scheduling")
    st.caption("April 2026")
    leg = st.columns(3)
    with leg[0]: st.markdown("**🌅 Morning** (06:00–14:00)")
    with leg[1]: st.markdown("**🌤️ Afternoon** (14:00–22:00)")
    with leg[2]: st.markdown("**🌙 Night** (22:00–06:00)")
    st.markdown("---")
    days = ["SUN","MON","TUE","WED","THU","FRI","SAT"]
    header = st.columns(7)
    for i, d in enumerate(days):
        with header[i]:
            st.markdown(f"<h4 style='text-align:center'>{d}</h4>", unsafe_allow_html=True)
    weeks = [[1,2,3,4,5,6,7],[8,9,10,11,12,13,14],[15,16,17,18,19,20,21],
             [22,23,24,25,26,27,28],[29,30,0,0,0,0,0]]
    for week in weeks:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0: continue
                st.markdown(f"<div style='text-align:center;font-weight:bold;margin-bottom:8px;'>{day}</div>", unsafe_allow_html=True)
                colors = ["#FF9800","#2196F3","#9C27B0"]
                shifts = ["Morning","Afternoon","Night"]
                for j in range(3):
                    st.markdown(f"""<div style="background:{colors[j]};color:white;padding:6px;margin:3px 0;border-radius:8px;text-align:center;font-size:12px;">{shifts[j]}</div>""", unsafe_allow_html=True)

# ====================== TRAINING ======================
elif menu == "🎓 Training":
    st.title("🎓 Training & Development")
    emp_df = get_employees()

    tab1, tab2 = st.tabs(["📋 Training Records", "➕ Add Training"])

    with tab1:
        conn = get_conn()
        train_df = pd.read_sql("SELECT t.*, e.name, e.department FROM training t JOIN employees e ON t.emp_id=e.emp_id ORDER BY t.id DESC", conn)
        conn.close()

        if len(train_df) > 0:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Trainings", len(train_df))
            with c2: st.metric("Completed", len(train_df[train_df['status']=='Completed']))
            with c3: st.metric("Scheduled", len(train_df[train_df['status']=='Scheduled']))
            st.dataframe(train_df[['name','department','training_name','provider','start_date','end_date','status']], use_container_width=True, hide_index=True)
        else:
            st.info("No training records yet.")

    with tab2:
        with st.form("training_form"):
            emp_opts = {f"{r['emp_id']} - {r['name']}": r['emp_id'] for _, r in emp_df.iterrows()}
            sel_emp = st.selectbox("Employee", list(emp_opts.keys()))
            t1, t2 = st.columns(2)
            with t1:
                train_name = st.text_input("Training Name")
                provider = st.text_input("Provider / Institution")
                t_start = st.date_input("Start Date")
            with t2:
                t_end = st.date_input("End Date")
                t_status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed", "Cancelled"])
                certificate = st.text_input("Certificate No (if completed)")
            if st.form_submit_button("✅ Add Training", type="primary"):
                conn = get_conn()
                conn.execute("INSERT INTO training (emp_id,training_name,provider,start_date,end_date,status,certificate) VALUES (?,?,?,?,?,?,?)",
                    (emp_opts[sel_emp], train_name, provider, str(t_start), str(t_end), t_status, certificate))
                conn.commit()
                conn.close()
                st.success("✅ Training record added!")
                st.rerun()

# ====================== ANNOUNCEMENTS ======================
elif menu == "📢 Announcements":
    st.title("📢 HR Announcements")

    tab1, tab2 = st.tabs(["📋 All Announcements", "➕ Post Announcement"])

    with tab1:
        conn = get_conn()
        ann_df = pd.read_sql("SELECT * FROM announcements ORDER BY id DESC", conn)
        conn.close()
        if len(ann_df) > 0:
            for _, ann in ann_df.iterrows():
                priority_colors = {"High": "🔴", "Normal": "🔵", "Low": "🟢"}
                icon = priority_colors.get(ann['priority'], "🔵")
                with st.expander(f"{icon} {ann['title']} — {ann['posted_on']}"):
                    st.write(ann['message'])
                    st.caption(f"Posted by: {ann['posted_by']} | Priority: {ann['priority']}")
                    if st.button("🗑️ Delete", key=f"del_ann_{ann['id']}"):
                        conn = get_conn()
                        conn.execute("DELETE FROM announcements WHERE id=?", (ann['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
        else:
            st.info("No announcements yet.")

    with tab2:
        with st.form("ann_form"):
            title = st.text_input("Title")
            message = st.text_area("Message")
            priority = st.selectbox("Priority", ["Normal", "High", "Low"])
            posted_by = st.text_input("Posted By", "HR Manager")
            if st.form_submit_button("📢 Post Announcement", type="primary"):
                conn = get_conn()
                conn.execute("INSERT INTO announcements (title,message,posted_by,posted_on,priority) VALUES (?,?,?,?,?)",
                    (title, message, posted_by, str(date.today()), priority))
                conn.commit()
                conn.close()
                st.success("✅ Announcement posted!")
                st.rerun()

# ====================== RECRUITMENT ======================
elif menu == "🧑‍💼 Recruitment":
    st.title("🧑‍💼 Recruitment")
    dept_df = get_departments()

    tab1, tab2 = st.tabs(["📋 Job Openings", "➕ Post Job"])

    with tab1:
        conn = get_conn()
        rec_df = pd.read_sql("SELECT * FROM recruitment ORDER BY id DESC", conn)
        conn.close()

        if len(rec_df) > 0:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Open Positions", len(rec_df[rec_df['status']=='Open']))
            with c2: st.metric("Total Applicants", rec_df['applicants'].sum())
            with c3: st.metric("Closed", len(rec_df[rec_df['status']=='Closed']))

            for _, job in rec_df.iterrows():
                with st.expander(f"💼 {job['job_title']} — {job['department']} ({job['status']})"):
                    j1, j2 = st.columns(2)
                    with j1:
                        st.write(f"**Department:** {job['department']}")
                        st.write(f"**Positions:** {job['positions']}")
                        st.write(f"**Deadline:** {job['deadline']}")
                    with j2:
                        st.write(f"**Status:** {job['status']}")
                        st.write(f"**Applicants:** {job['applicants']}")
                        st.write(f"**Posted:** {job['posted_on']}")
                    u1, u2 = st.columns(2)
                    with u1:
                        new_applicants = st.number_input("Update Applicants", value=int(job['applicants']), key=f"app_{job['id']}")
                    with u2:
                        new_job_status = st.selectbox("Update Status", ["Open","Closed","On Hold"], key=f"js_{job['id']}")
                    if st.button("💾 Update", key=f"upd_{job['id']}"):
                        conn = get_conn()
                        conn.execute("UPDATE recruitment SET applicants=?,status=? WHERE id=?", (new_applicants, new_job_status, job['id']))
                        conn.commit()
                        conn.close()
                        st.success("Updated!")
                        st.rerun()
        else:
            st.info("No job openings yet.")

    with tab2:
        with st.form("rec_form"):
            r1, r2 = st.columns(2)
            with r1:
                job_title = st.text_input("Job Title")
                dept = st.selectbox("Department", sorted(dept_df['dept_name'].tolist()))
                positions = st.number_input("Number of Positions", min_value=1, value=1)
            with r2:
                deadline = st.date_input("Application Deadline")
                rec_status = st.selectbox("Status", ["Open", "On Hold"])
            if st.form_submit_button("📢 Post Job", type="primary"):
                conn = get_conn()
                conn.execute("INSERT INTO recruitment (job_title,department,positions,deadline,status,applicants,posted_on) VALUES (?,?,?,?,?,0,?)",
                    (job_title, dept, positions, str(deadline), rec_status, str(date.today())))
                conn.commit()
                conn.close()
                st.success("✅ Job posted!")
                st.rerun()

# ====================== REPORTS ======================
elif menu == "📋 Reports":
    st.title("📋 HR Reports")
    st.caption(f"{datetime.now().strftime('%B %Y')}")

    emp_df = get_employees()
    pay_df = get_payroll("2026-04")
    leaves_df = get_leaves()
    kpi_df = get_kpi("2026-04")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Staff", len(emp_df))
    with c2: st.metric("Departments", len(get_departments()))
    with c3: st.metric("Net Payroll", f"KSH {pay_df['net'].sum():,.0f}" if len(pay_df) > 0 else "N/A")
    with c4: st.metric("Avg KPI", f"{kpi_df['overall_score'].mean():.1f}%" if len(kpi_df) > 0 else "N/A")

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Staff Report", "💰 Payroll Report", "🌴 Leave Report", "📈 KPI Report"])

    with tab1:
        st.subheader("Staff by Department")
        if len(emp_df) > 0:
            dept_counts = emp_df.groupby('department').size().reset_index(name='Count')
            st.bar_chart(dept_counts.set_index('department'))
            st.subheader("Staff by Employment Type")
            type_counts = emp_df.groupby('employment_type').size().reset_index(name='Count')
            st.dataframe(type_counts, use_container_width=True, hide_index=True)
            st.dataframe(emp_df[['emp_id','name','position','department','hire_date','status']], use_container_width=True, hide_index=True)
            output = io.BytesIO()
            emp_df.to_excel(output, index=False)
            st.download_button("📥 Export Staff Report", output.getvalue(), file_name="Staff_Report.xlsx", mime="application/vnd.ms-excel")

    with tab2:
        if len(pay_df) > 0:
            st.subheader("Payroll Summary")
            dept_pay = pay_df.groupby('department')['net'].sum().reset_index()
            st.bar_chart(dept_pay.set_index('department'))
            st.dataframe(pay_df[['name','department','gross','total_deductions','net','status']], use_container_width=True, hide_index=True)
            output2 = io.BytesIO()
            pay_df.to_excel(output2, index=False)
            st.download_button("📥 Export Payroll Report", output2.getvalue(), file_name="Payroll_Report.xlsx", mime="application/vnd.ms-excel")

    with tab3:
        if len(leaves_df) > 0:
            leave_summary = leaves_df.groupby(['leave_type','status']).size().reset_index(name='Count')
            st.dataframe(leave_summary, use_container_width=True, hide_index=True)
            st.dataframe(leaves_df[['name','department','leave_type','start_date','end_date','days','status']], use_container_width=True, hide_index=True)
            output3 = io.BytesIO()
            leaves_df.to_excel(output3, index=False)
            st.download_button("📥 Export Leave Report", output3.getvalue(), file_name="Leave_Report.xlsx", mime="application/vnd.ms-excel")

    with tab4:
        if len(kpi_df) > 0:
            st.subheader("KPI Performance")
            st.progress(kpi_df['attendance_score'].mean()/100, text=f"Attendance — {kpi_df['attendance_score'].mean():.1f}%")
            st.progress(kpi_df['punctuality_score'].mean()/100, text=f"Punctuality — {kpi_df['punctuality_score'].mean():.1f}%")
            st.progress(kpi_df['patient_satisfaction'].mean()/100, text=f"Patient Satisfaction — {kpi_df['patient_satisfaction'].mean():.1f}%")
            st.progress(kpi_df['task_completion'].mean()/100, text=f"Task Completion — {kpi_df['task_completion'].mean():.1f}%")
            st.dataframe(kpi_df[['name','department','attendance_score','punctuality_score','patient_satisfaction','task_completion','overall_score']], use_container_width=True, hide_index=True)
            output4 = io.BytesIO()
            kpi_df.to_excel(output4, index=False)
            st.download_button("📥 Export KPI Report", output4.getvalue(), file_name="KPI_Report.xlsx", mime="application/vnd.ms-excel")