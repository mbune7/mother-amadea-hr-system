import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date
import io

st.set_page_config(page_title="Mother Amadea HR System", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    .card {background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin: 10px 0;}
    .profile-card {background: linear-gradient(135deg, #1e3a8a, #2563eb); color: white; padding: 24px; border-radius: 16px; margin-bottom: 16px;}
    .badge {display:inline-block; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600;}
    .badge-green {background:#d1fae5; color:#065f46;}
    .badge-red {background:#fee2e2; color:#991b1b;}
    .badge-yellow {background:#fef3c7; color:#92400e;}
    .badge-blue {background:#dbeafe; color:#1e40af;}
    h1,h2,h3 {color:#1e3a8a;}
    .stMetric {background:white; padding:15px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.06);}
    .section-header {background:#f0f4ff; padding:12px 16px; border-radius:10px; border-left:4px solid #1e3a8a; margin:16px 0 12px 0;}
</style>
""", unsafe_allow_html=True)

# ==================== DATABASE ====================
def get_conn():
    return sqlite3.connect("hospital_hr.db", check_same_thread=False)


def column_exists(cursor, table, column_name):
    cursor.execute(f"PRAGMA table_info({table})")
    return column_name in [row[1] for row in cursor.fetchall()]


def add_column_if_missing(cursor, table, column_name, column_definition, copy_from=None):
    if not column_exists(cursor, table, column_name):
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_name} {column_definition}")
        if copy_from is not None and column_exists(cursor, table, copy_from):
            cursor.execute(
                f"UPDATE {table} SET {column_name} = {copy_from} WHERE {copy_from} IS NOT NULL"
            )


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
            emergency_contact TEXT DEFAULT '',
            emergency_phone TEXT DEFAULT '',
            gender TEXT DEFAULT '',
            employment_type TEXT DEFAULT 'Full-Time',
            status TEXT DEFAULT 'Active'
        );
        CREATE TABLE IF NOT EXISTS departments (
            dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dept_name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            head TEXT DEFAULT '',
            status TEXT DEFAULT 'Active'
        );
        CREATE TABLE IF NOT EXISTS payroll (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            month TEXT NOT NULL,
            basic_salary REAL DEFAULT 0,
            house_allowance REAL DEFAULT 0,
            transport_allowance REAL DEFAULT 0,
            medical_allowance REAL DEFAULT 0,
            other_allowance REAL DEFAULT 0,
            nssf REAL DEFAULT 0,
            nhif REAL DEFAULT 0,
            paye REAL DEFAULT 0,
            loan_deduction REAL DEFAULT 0,
            other_deduction REAL DEFAULT 0,
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
            days INTEGER NOT NULL,
            reason TEXT DEFAULT '',
            status TEXT DEFAULT 'Pending',
            approved_by TEXT DEFAULT '',
            applied_date TEXT DEFAULT '',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            att_date TEXT NOT NULL,
            clock_in TEXT DEFAULT '',
            clock_out TEXT DEFAULT '',
            status TEXT DEFAULT 'Present',
            notes TEXT DEFAULT '',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS kpi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id TEXT NOT NULL,
            month TEXT NOT NULL,
            attendance_score REAL DEFAULT 0,
            punctuality_score REAL DEFAULT 0,
            satisfaction_score REAL DEFAULT 0,
            task_score REAL DEFAULT 0,
            teamwork_score REAL DEFAULT 0,
            overall_score REAL DEFAULT 0,
            notes TEXT DEFAULT '',
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
            notes TEXT DEFAULT '',
            FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
        );
        CREATE TABLE IF NOT EXISTS recruitment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position TEXT NOT NULL,
            department TEXT NOT NULL,
            posted_date TEXT DEFAULT '',
            deadline TEXT DEFAULT '',
            applicants INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Open',
            notes TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            posted_by TEXT DEFAULT 'HR Admin',
            posted_date TEXT DEFAULT '',
            priority TEXT DEFAULT 'Normal',
            target TEXT DEFAULT 'All Staff'
        );
    ''')

    add_column_if_missing(c, 'employees', 'phone', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'employees', 'email', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'employees', 'national_id', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'employees', 'emergency_contact', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'employees', 'emergency_phone', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'employees', 'gender', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'employees', 'employment_type', "TEXT DEFAULT 'Full-Time'")
    add_column_if_missing(c, 'employees', 'status', "TEXT DEFAULT 'Active'")
    add_column_if_missing(c, 'departments', 'head', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'departments', 'status', "TEXT DEFAULT 'Active'")
    add_column_if_missing(c, 'payroll', 'transport_allowance', 'REAL DEFAULT 0', copy_from='transport')
    add_column_if_missing(c, 'payroll', 'other_allowance', 'REAL DEFAULT 0', copy_from='other_allowances')
    add_column_if_missing(c, 'payroll', 'other_deduction', 'REAL DEFAULT 0', copy_from='other_deductions')
    add_column_if_missing(c, 'leaves', 'applied_date', "TEXT DEFAULT ''", copy_from='applied_on')
    add_column_if_missing(c, 'attendance', 'att_date', "TEXT DEFAULT ''", copy_from='attendance_date')
    add_column_if_missing(c, 'announcements', 'posted_date', "TEXT DEFAULT ''", copy_from='posted_on')
    add_column_if_missing(c, 'announcements', 'target', "TEXT DEFAULT 'All Staff'")
    add_column_if_missing(c, 'recruitment', 'position', "TEXT DEFAULT ''", copy_from='job_title')
    add_column_if_missing(c, 'recruitment', 'posted_date', "TEXT DEFAULT ''", copy_from='posted_on')
    add_column_if_missing(c, 'recruitment', 'deadline', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'recruitment', 'notes', "TEXT DEFAULT ''")
    add_column_if_missing(c, 'kpi', 'satisfaction_score', 'REAL DEFAULT 0', copy_from='patient_satisfaction')
    add_column_if_missing(c, 'kpi', 'task_score', 'REAL DEFAULT 0', copy_from='task_completion')
    add_column_if_missing(c, 'kpi', 'teamwork_score', 'REAL DEFAULT 0', copy_from='teamwork')
    add_column_if_missing(c, 'kpi', 'notes', "TEXT DEFAULT ''", copy_from='remarks')

    c.execute("SELECT COUNT(*) FROM departments")
    if c.fetchone()[0] == 0:
        depts = [
            ("ANC", "Antenatal Clinic", ""),
            ("Administration", "Hospital Administration", ""),
            ("CWC", "Child Welfare Clinic", ""),
            ("Lab", "Laboratory Services", ""),
            ("OPD", "Outpatient Department", ""),
            ("Pharmacy", "Pharmacy Department", ""),
            ("Radiology", "Radiology & Imaging", ""),
            ("Theatre 1", "Operating Theatre 1", ""),
            ("Theatre 2", "Operating Theatre 2", ""),
            ("Maternity", "Maternity Ward", ""),
        ]
        c.executemany("INSERT OR IGNORE INTO departments (dept_name, description, head) VALUES (?,?,?)", depts)
    conn.commit()
    conn.close()

init_db()

# ==================== LOGIN ====================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = "HR Admin"

USERS = {
    "admin": {"password": "amadea2026", "role": "Admin", "name": "HR Admin"},
    "hr": {"password": "hr2026", "role": "HR Manager", "name": "HR Manager"},
    "viewer": {"password": "view2026", "role": "Viewer", "name": "Viewer"},
}

if not st.session_state.logged_in:
    st.title("🏥 Mother Amadea Mission Hospital")
    st.subheader("Human Resource Management System")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("amadea_logo.png", width=220)
        except:
            st.markdown("### 🏥 Mother Amadea")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("🔐 Login", type="primary", use_container_width=True):
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.current_user = USERS[username]["name"]
                st.session_state.role = USERS[username]["role"]
                st.success("✅ Login Successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        st.caption("Default: admin / amadea2026")
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    try:
        st.image("amadea_logo.png", width=140)
    except:
        st.markdown("## 🏥")
    st.markdown(f"**Mother Amadea Mission Hospital**")
    st.caption(f"👤 {st.session_state.current_user} | {datetime.now().strftime('%d %b %Y')}")
    st.markdown("---")

    menu = st.radio("Navigation", [
        "📊 Dashboard",
        "👥 Staff Directory",
        "🏢 Departments",
        "💰 Payroll",
        "🌴 Leave Management",
        "⏰ Attendance",
        "📈 KPI Dashboard",
        "🎓 Training",
        "📢 Recruitment",
        "📣 Announcements",
        "📋 Reports",
    ])
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

conn = get_conn()

# ==================== HELPERS ====================
def get_employees():
    return pd.read_sql("SELECT * FROM employees ORDER BY department, name", conn)

def get_departments():
    return pd.read_sql("SELECT * FROM departments ORDER BY dept_name", conn)

def get_dept_names():
    df = get_departments()
    return df["dept_name"].tolist() if not df.empty else []

def employee_selector(label="Select Employee", key=None):
    emp_df = get_employees()
    if emp_df.empty:
        st.warning("No employees found. Please add employees first.")
        return None, None
    options = [f"{r['emp_id']} — {r['name']}" for _, r in emp_df.iterrows()]
    widget_key = key or f"employee_selector_{label.replace(' ', '_').lower()}"
    sel = st.selectbox(label, options, key=widget_key)
    emp_id = sel.split(" — ")[0]
    return emp_id, emp_df[emp_df["emp_id"] == emp_id].iloc[0]

def generate_payslip_text(emp, pay):
    lines = []
    lines.append("=" * 55)
    lines.append("     MOTHER AMADEA MISSION HOSPITAL")
    lines.append("           PAYSLIP / PAY ADVICE")
    lines.append("=" * 55)
    lines.append(f"Employee Name   : {emp['name']}")
    lines.append(f"Employee ID     : {emp['emp_id']}")
    lines.append(f"Position        : {emp['position']}")
    lines.append(f"Department      : {emp['department']}")
    lines.append(f"Pay Month       : {pay['month']}")
    lines.append(f"Employment Type : {emp.get('employment_type','Full-Time')}")
    lines.append("-" * 55)
    lines.append("EARNINGS")
    lines.append(f"  Basic Salary          : KES {pay['basic_salary']:>12,.2f}")
    lines.append(f"  House Allowance       : KES {pay['house_allowance']:>12,.2f}")
    lines.append(f"  Transport Allowance   : KES {pay['transport_allowance']:>12,.2f}")
    lines.append(f"  Medical Allowance     : KES {pay['medical_allowance']:>12,.2f}")
    lines.append(f"  Other Allowance       : KES {pay['other_allowance']:>12,.2f}")
    lines.append(f"  GROSS SALARY          : KES {pay['gross']:>12,.2f}")
    lines.append("-" * 55)
    lines.append("DEDUCTIONS")
    lines.append(f"  NSSF                  : KES {pay['nssf']:>12,.2f}")
    lines.append(f"  NHIF                  : KES {pay['nhif']:>12,.2f}")
    lines.append(f"  PAYE (Tax)            : KES {pay['paye']:>12,.2f}")
    lines.append(f"  Loan Deduction        : KES {pay['loan_deduction']:>12,.2f}")
    lines.append(f"  Other Deduction       : KES {pay['other_deduction']:>12,.2f}")
    lines.append(f"  TOTAL DEDUCTIONS      : KES {pay['total_deductions']:>12,.2f}")
    lines.append("=" * 55)
    lines.append(f"  NET PAY               : KES {pay['net']:>12,.2f}")
    lines.append("=" * 55)
    lines.append("This is a computer-generated payslip.")
    lines.append(f"Generated on: {datetime.now().strftime('%d %b %Y %H:%M')}")
    return "\n".join(lines)

def generate_leave_letter(emp, leave):
    lines = []
    lines.append("MOTHER AMADEA MISSION HOSPITAL")
    lines.append("P.O. Box — Mombasa, Kenya")
    lines.append("")
    lines.append(f"Date: {datetime.now().strftime('%d %B %Y')}")
    lines.append("")
    lines.append("TO: " + emp['name'])
    lines.append(f"    {emp['position']}, {emp['department']}")
    lines.append(f"    ID: {emp['emp_id']}")
    lines.append("")
    lines.append(f"RE: APPROVAL OF {leave['leave_type'].upper()} LEAVE")
    lines.append("")
    lines.append("Dear " + emp['name'].split()[0] + ",")
    lines.append("")
    lines.append(f"We write to confirm that your application for {leave['leave_type']} Leave")
    lines.append(f"has been reviewed and APPROVED as follows:")
    lines.append("")
    lines.append(f"  Leave Type    : {leave['leave_type']}")
    lines.append(f"  Start Date    : {leave['start_date']}")
    lines.append(f"  End Date      : {leave['end_date']}")
    lines.append(f"  Total Days    : {leave['days']} day(s)")
    lines.append(f"  Reason        : {leave['reason']}")
    lines.append("")
    lines.append("You are expected to resume duty on the next working day after your leave ends.")
    lines.append("Please ensure proper handover of your duties before proceeding on leave.")
    lines.append("")
    lines.append("Yours faithfully,")
    lines.append("")
    lines.append("_________________________")
    lines.append("HR Manager")
    lines.append("Mother Amadea Mission Hospital")
    lines.append(f"Date: {datetime.now().strftime('%d %B %Y')}")
    return "\n".join(lines)

# ====================== DASHBOARD ======================
if menu == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption(f"Welcome, {st.session_state.current_user} — {datetime.now().strftime('%A, %d %B %Y')}")

    emp_df = get_employees()
    total_staff = len(emp_df)
    active_staff = len(emp_df[emp_df["status"] == "Active"]) if not emp_df.empty else 0
    dept_count = len(get_departments())
    pay_df = pd.read_sql(f"SELECT * FROM payroll WHERE month='{datetime.now().strftime('%B %Y')}'", conn)
    net_payroll = pay_df["net"].sum() if not pay_df.empty else 0
    leave_df = pd.read_sql("SELECT * FROM leaves WHERE status='Pending'", conn)
    pending_leaves = len(leave_df)
    kpi_df = pd.read_sql("SELECT AVG(overall_score) as avg FROM kpi", conn)
    avg_kpi = kpi_df["avg"].iloc[0] if not kpi_df.empty and kpi_df["avg"].iloc[0] else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("👥 Total Staff", total_staff)
    with c2: st.metric("✅ Active", active_staff)
    with c3: st.metric("🏢 Departments", dept_count)
    with c4: st.metric("💰 Net Payroll", f"KES {net_payroll:,.0f}" if net_payroll else "Not Set")
    with c5: st.metric("📈 Avg KPI", f"{avg_kpi:.1f}%" if avg_kpi else "N/A")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-header"><strong>⚠️ Pending Actions</strong></div>', unsafe_allow_html=True)
        if pending_leaves > 0:
            st.warning(f"🌴 {pending_leaves} Leave Request(s) awaiting approval")
        else:
            st.success("✅ No pending leave requests")
        ann_df = pd.read_sql("SELECT * FROM announcements ORDER BY id DESC LIMIT 3", conn)
        if not ann_df.empty:
            st.markdown("**📣 Latest Announcements**")
            for _, a in ann_df.iterrows():
                st.info(f"**{a['title']}** — {a['posted_date']}")

    with col_b:
        st.markdown('<div class="section-header"><strong>📊 Staff by Department</strong></div>', unsafe_allow_html=True)
        if not emp_df.empty:
            dept_counts = emp_df.groupby("department").size().reset_index(name="Count")
            st.dataframe(dept_counts, use_container_width=True, hide_index=True)

    if not emp_df.empty:
        st.markdown('<div class="section-header"><strong>👥 Recently Added Staff</strong></div>', unsafe_allow_html=True)
        recent = emp_df.tail(5)[["emp_id", "name", "position", "department", "hire_date", "status"]]
        st.dataframe(recent, use_container_width=True, hide_index=True)

# ====================== STAFF DIRECTORY ======================
elif menu == "👥 Staff Directory":
    st.title("👥 Staff Directory")
    tab1, tab2, tab3 = st.tabs(["📋 View Staff", "➕ Add Staff", "✏️ Edit / Delete"])

    with tab1:
        emp_df = get_employees()
        st.caption(f"{len(emp_df)} employees registered")
        col1, col2, col3 = st.columns(3)
        with col1: search = st.text_input("🔍 Search name or ID")
        with col2: dept_filter = st.selectbox("Filter by Department", ["All"] + get_dept_names())
        with col3: status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "On Leave"])

        filtered = emp_df.copy()
        if search:
            filtered = filtered[filtered["name"].str.contains(search, case=False) | filtered["emp_id"].str.contains(search, case=False)]
        if dept_filter != "All":
            filtered = filtered[filtered["department"] == dept_filter]
        if status_filter != "All":
            filtered = filtered[filtered["status"] == status_filter]

        if filtered.empty:
            st.info("No staff found matching your search.")
        else:
            selected_id = st.selectbox("Select staff to view full profile", ["— Select —"] + filtered["emp_id"].tolist())
            if selected_id != "— Select —":
                emp = filtered[filtered["emp_id"] == selected_id].iloc[0]
                st.markdown(f"""
                <div class="profile-card">
                    <h2 style="color:white;margin:0;">👤 {emp['name']}</h2>
                    <p style="margin:4px 0;opacity:0.85;">{emp['position']} | {emp['department']}</p>
                    <p style="margin:4px 0;opacity:0.75;">ID: {emp['emp_id']}</p>
                </div>
                """, unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**Personal Details**")
                    st.write(f"📞 Phone: {emp.get('phone','N/A')}")
                    st.write(f"📧 Email: {emp.get('email','N/A')}")
                    st.write(f"🪪 National ID: {emp.get('national_id','N/A')}")
                    st.write(f"⚧ Gender: {emp.get('gender','N/A')}")
                with c2:
                    st.markdown("**Employment Details**")
                    st.write(f"📅 Hire Date: {emp['hire_date']}")
                    st.write(f"💼 Type: {emp.get('employment_type','Full-Time')}")
                    st.write(f"💰 Salary: KES {emp['salary']:,.2f}")
                    status_color = "badge-green" if emp['status'] == 'Active' else "badge-red"
                    st.markdown(f"Status: <span class='badge {status_color}'>{emp['status']}</span>", unsafe_allow_html=True)
                with c3:
                    st.markdown("**Emergency Contact**")
                    st.write(f"👤 {emp.get('emergency_contact','N/A')}")
                    st.write(f"📞 {emp.get('emergency_phone','N/A')}")

                att = pd.read_sql(f"SELECT * FROM attendance WHERE emp_id='{selected_id}' ORDER BY att_date DESC LIMIT 10", conn)
                if not att.empty:
                    st.markdown("**Recent Attendance**")
                    st.dataframe(att[["att_date","clock_in","clock_out","status"]], use_container_width=True, hide_index=True)

            st.markdown("---")
            display_cols = ["emp_id","name","position","department","phone","status","hire_date"]
            st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
            csv = filtered.to_csv(index=False).encode()
            st.download_button("📥 Download Staff List (CSV)", csv, "staff_list.csv", "text/csv")

    with tab2:
        st.subheader("➕ Add New Staff Member")
        with st.form("add_staff_form"):
            c1, c2 = st.columns(2)
            with c1:
                emp_id = st.text_input("Employee ID *", placeholder="MAMH-001")
                name = st.text_input("Full Name *")
                position = st.text_input("Position *")
                department = st.selectbox("Department *", get_dept_names())
                salary = st.number_input("Monthly Salary (KES) *", min_value=0.0, step=500.0)
                hire_date = st.date_input("Hire Date *")
                gender = st.selectbox("Gender", ["Male","Female","Other"])
            with c2:
                phone = st.text_input("Phone Number")
                email = st.text_input("Email Address")
                national_id = st.text_input("National ID")
                employment_type = st.selectbox("Employment Type", ["Full-Time","Part-Time","Contract","Intern"])
                emergency_contact = st.text_input("Emergency Contact Name")
                emergency_phone = st.text_input("Emergency Contact Phone")
                status = st.selectbox("Status", ["Active","Inactive"])
            if st.form_submit_button("✅ Add Staff Member", type="primary"):
                if not emp_id or not name or not position:
                    st.error("Please fill in all required fields (*)")
                else:
                    try:
                        conn.execute("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (emp_id.upper().strip(), name.strip(), position.strip(), department,
                             salary, str(hire_date), phone, email, national_id,
                             emergency_contact, emergency_phone, gender, employment_type, status))
                        conn.commit()
                        st.success(f"✅ {name} added successfully!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"❌ Employee ID {emp_id} already exists!")

    with tab3:
        st.subheader("✏️ Edit or Delete Staff")
        emp_id_sel, emp_row = employee_selector("Select Staff to Edit", key="select_staff_to_edit")
        if emp_row is not None:
            with st.form("edit_staff_form"):
                c1, c2 = st.columns(2)
                with c1:
                    new_name = st.text_input("Full Name", emp_row["name"])
                    new_pos = st.text_input("Position", emp_row["position"])
                    dept_list = get_dept_names()
                    dept_idx = dept_list.index(emp_row["department"]) if emp_row["department"] in dept_list else 0
                    new_dept = st.selectbox("Department", dept_list, index=dept_idx)
                    new_salary = st.number_input("Salary (KES)", value=float(emp_row["salary"]), step=500.0)
                    new_phone = st.text_input("Phone", emp_row.get("phone",""))
                    new_email = st.text_input("Email", emp_row.get("email",""))
                with c2:
                    new_national_id = st.text_input("National ID", emp_row.get("national_id",""))
                    gender_opts = ["Male","Female","Other"]
                    new_gender = st.selectbox("Gender", gender_opts,
                        index=gender_opts.index(emp_row.get("gender","Male")) if emp_row.get("gender","Male") in gender_opts else 0)
                    emp_type_opts = ["Full-Time","Part-Time","Contract","Intern"]
                    new_emp_type = st.selectbox("Employment Type", emp_type_opts,
                        index=emp_type_opts.index(emp_row.get("employment_type","Full-Time")) if emp_row.get("employment_type","Full-Time") in emp_type_opts else 0)
                    new_ec = st.text_input("Emergency Contact", emp_row.get("emergency_contact",""))
                    new_ep = st.text_input("Emergency Phone", emp_row.get("emergency_phone",""))
                    status_opts = ["Active","Inactive","On Leave"]
                    new_status = st.selectbox("Status", status_opts,
                        index=status_opts.index(emp_row.get("status","Active")) if emp_row.get("status","Active") in status_opts else 0)
                col_save, col_del = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        conn.execute("""UPDATE employees SET name=?,position=?,department=?,salary=?,
                            phone=?,email=?,national_id=?,gender=?,employment_type=?,
                            emergency_contact=?,emergency_phone=?,status=? WHERE emp_id=?""",
                            (new_name,new_pos,new_dept,new_salary,new_phone,new_email,
                             new_national_id,new_gender,new_emp_type,new_ec,new_ep,new_status,emp_id_sel))
                        conn.commit()
                        st.success("✅ Staff details updated!")
                        st.rerun()
                with col_del:
                    if st.form_submit_button("🗑️ Delete Staff"):
                        conn.execute("DELETE FROM employees WHERE emp_id=?", (emp_id_sel,))
                        conn.commit()
                        st.success("✅ Staff member deleted.")
                        st.rerun()

# ====================== DEPARTMENTS ======================
elif menu == "🏢 Departments":
    st.title("🏢 Departments")
    tab1, tab2, tab3 = st.tabs(["📋 View Departments", "➕ Add Department", "✏️ Edit Department"])

    with tab1:
        dept_df = get_departments()
        emp_df = get_employees()
        st.caption(f"{len(dept_df)} departments registered")
        for _, dept in dept_df.iterrows():
            staff_in_dept = emp_df[emp_df["department"] == dept["dept_name"]] if not emp_df.empty else pd.DataFrame()
            count = len(staff_in_dept)
            with st.expander(f"🏢 {dept['dept_name']} — {dept['description']} ({count} staff)"):
                c1, c2, c3 = st.columns(3)
                with c1: st.write(f"**Description:** {dept['description']}")
                with c2: st.write(f"**Head:** {dept['head'] or 'Not assigned'}")
                with c3:
                    status_class = "badge-green" if dept["status"] == "Active" else "badge-red"
                    st.markdown(f"**Status:** <span class='badge {status_class}'>{dept['status']}</span>", unsafe_allow_html=True)
                if not staff_in_dept.empty:
                    st.markdown(f"**Staff in {dept['dept_name']}:**")
                    show_cols = ["emp_id","name","position","phone","status"]
                    st.dataframe(staff_in_dept[show_cols], use_container_width=True, hide_index=True)
                else:
                    st.info("No staff assigned to this department yet.")

    with tab2:
        st.subheader("➕ Add New Department")
        with st.form("add_dept_form"):
            dept_name = st.text_input("Department Name *")
            description = st.text_input("Description")
            head = st.text_input("Department Head")
            status = st.selectbox("Status", ["Active","Inactive"])
            if st.form_submit_button("✅ Add Department", type="primary"):
                if not dept_name:
                    st.error("Department name is required!")
                else:
                    try:
                        conn.execute("INSERT INTO departments (dept_name,description,head,status) VALUES (?,?,?,?)",
                            (dept_name.strip(), description, head, status))
                        conn.commit()
                        st.success(f"✅ {dept_name} added!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Department already exists!")

    with tab3:
        st.subheader("✏️ Edit Department")
        dept_df = get_departments()
        if not dept_df.empty:
            dept_sel = st.selectbox("Select Department", dept_df["dept_name"].tolist())
            dept_row = dept_df[dept_df["dept_name"] == dept_sel].iloc[0]
            with st.form("edit_dept_form"):
                new_desc = st.text_input("Description", dept_row["description"])
                new_head = st.text_input("Department Head", dept_row["head"])
                new_status = st.selectbox("Status", ["Active","Inactive"], index=0 if dept_row["status"] == "Active" else 1)
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        conn.execute("UPDATE departments SET description=?,head=?,status=? WHERE dept_name=?",
                            (new_desc, new_head, new_status, dept_sel))
                        conn.commit()
                        st.success("✅ Department updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🗑️ Delete Department"):
                        emp_df2 = get_employees()
                        if not emp_df2.empty and dept_sel in emp_df2["department"].values:
                            st.error("❌ Cannot delete — staff are assigned to this department!")
                        else:
                            conn.execute("DELETE FROM departments WHERE dept_name=?", (dept_sel,))
                            conn.commit()
                            st.success("✅ Department deleted!")
                            st.rerun()

# ====================== PAYROLL ======================
elif menu == "💰 Payroll":
    st.title("💰 Payroll Management")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Payroll Records", "➕ Add/Edit Payroll", "📄 Generate Payslip", "📊 Summary"])

    with tab1:
        pay_df = pd.read_sql("SELECT p.*, e.name, e.department FROM payroll p JOIN employees e ON p.emp_id=e.emp_id ORDER BY p.month DESC", conn)
        if pay_df.empty:
            st.info("No payroll records yet. Use 'Add/Edit Payroll' tab to add records.")
        else:
            month_list = pay_df["month"].unique().tolist()
            sel_month = st.selectbox("Select Month", month_list)
            filtered_pay = pay_df[pay_df["month"] == sel_month]
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Gross", f"KES {filtered_pay['gross'].sum():,.0f}")
            with c2: st.metric("Total Deductions", f"KES {filtered_pay['total_deductions'].sum():,.0f}")
            with c3: st.metric("Net Payroll", f"KES {filtered_pay['net'].sum():,.0f}")
            with c4: st.metric("Payslips", len(filtered_pay))
            show = filtered_pay[["emp_id","name","department","gross","total_deductions","net","status"]]
            st.dataframe(show, use_container_width=True, hide_index=True)
            csv = show.to_csv(index=False).encode()
            st.download_button("📥 Download Payroll CSV", csv, f"payroll_{sel_month}.csv", "text/csv")

    with tab2:
        st.subheader("➕ Add / Edit Employee Payroll")
        emp_id_sel, emp_row = employee_selector("Select Employee")
        if emp_row is not None:
            sel_month = st.text_input("Month", datetime.now().strftime("%B %Y"))
            existing = pd.read_sql(f"SELECT * FROM payroll WHERE emp_id='{emp_id_sel}' AND month='{sel_month}'", conn)
            ex = existing.iloc[0] if not existing.empty else None
            st.markdown("**Earnings**")
            c1, c2, c3 = st.columns(3)
            with c1:
                basic = st.number_input("Basic Salary", value=float(ex["basic_salary"]) if ex is not None else float(emp_row["salary"]), step=500.0)
                house = st.number_input("House Allowance", value=float(ex["house_allowance"]) if ex is not None else 0.0, step=100.0)
            with c2:
                transport = st.number_input("Transport Allowance", value=float(ex["transport_allowance"]) if ex is not None else 0.0, step=100.0)
                medical = st.number_input("Medical Allowance", value=float(ex["medical_allowance"]) if ex is not None else 0.0, step=100.0)
            with c3:
                other_allow = st.number_input("Other Allowance", value=float(ex["other_allowance"]) if ex is not None else 0.0, step=100.0)
            st.markdown("**Deductions**")
            c1, c2, c3 = st.columns(3)
            with c1:
                nssf = st.number_input("NSSF", value=float(ex["nssf"]) if ex is not None else 200.0, step=50.0)
                nhif = st.number_input("NHIF", value=float(ex["nhif"]) if ex is not None else 500.0, step=50.0)
            with c2:
                paye = st.number_input("PAYE (Tax)", value=float(ex["paye"]) if ex is not None else 0.0, step=100.0)
                loan = st.number_input("Loan Deduction", value=float(ex["loan_deduction"]) if ex is not None else 0.0, step=100.0)
            with c3:
                other_ded = st.number_input("Other Deduction", value=float(ex["other_deduction"]) if ex is not None else 0.0, step=100.0)
                pay_status = st.selectbox("Status", ["Pending","Paid","On Hold"])
            gross = basic + house + transport + medical + other_allow
            total_ded = nssf + nhif + paye + loan + other_ded
            net = gross - total_ded
            st.markdown(f"**Gross:** KES {gross:,.2f} | **Deductions:** KES {total_ded:,.2f} | **Net:** KES {net:,.2f}")
            if st.button("💾 Save Payroll", type="primary"):
                if ex is not None:
                    conn.execute("""UPDATE payroll SET basic_salary=?,house_allowance=?,transport_allowance=?,
                        medical_allowance=?,other_allowance=?,nssf=?,nhif=?,paye=?,loan_deduction=?,
                        other_deduction=?,gross=?,total_deductions=?,net=?,status=? WHERE emp_id=? AND month=?""",
                        (basic,house,transport,medical,other_allow,nssf,nhif,paye,loan,other_ded,gross,total_ded,net,pay_status,emp_id_sel,sel_month))
                else:
                    conn.execute("""INSERT INTO payroll (emp_id,month,basic_salary,house_allowance,transport_allowance,
                        medical_allowance,other_allowance,nssf,nhif,paye,loan_deduction,other_deduction,gross,total_deductions,net,status)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (emp_id_sel,sel_month,basic,house,transport,medical,other_allow,nssf,nhif,paye,loan,other_ded,gross,total_ded,net,pay_status))
                conn.commit()
                st.success("✅ Payroll saved!")
                st.rerun()

    with tab3:
        st.subheader("📄 Generate Payslip")
        emp_id_sel, emp_row = employee_selector("Select Employee", key="payslip_select_employee")
        if emp_row is not None:
            pay_df2 = pd.read_sql(f"SELECT * FROM payroll WHERE emp_id='{emp_id_sel}' ORDER BY id DESC", conn)
            if pay_df2.empty:
                st.warning("No payroll records for this employee. Please add payroll first.")
            else:
                sel_pay_month = st.selectbox("Select Month", pay_df2["month"].tolist())
                pay_row = pay_df2[pay_df2["month"] == sel_pay_month].iloc[0]
                payslip = generate_payslip_text(emp_row, pay_row)
                st.text(payslip)
                st.download_button("📥 Download Payslip", payslip,
                    f"payslip_{emp_row['emp_id']}_{sel_pay_month.replace(' ','_')}.txt", "text/plain")

    with tab4:
        st.subheader("📊 Payroll Summary by Department")
        pay_all = pd.read_sql("SELECT p.*, e.department FROM payroll p JOIN employees e ON p.emp_id=e.emp_id", conn)
        if not pay_all.empty:
            summary = pay_all.groupby("department").agg(
                Staff=("emp_id","count"), Gross=("gross","sum"),
                Deductions=("total_deductions","sum"), Net=("net","sum")).reset_index()
            st.dataframe(summary, use_container_width=True, hide_index=True)
        else:
            st.info("No payroll data available yet.")

# ====================== LEAVE MANAGEMENT ======================
elif menu == "🌴 Leave Management":
    st.title("🌴 Leave Management")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Leaves", "➕ Request Leave", "✅ Approve/Reject", "📄 Leave Letter"])

    with tab1:
        leave_df = pd.read_sql("SELECT l.*, e.name, e.department FROM leaves l JOIN employees e ON l.emp_id=e.emp_id ORDER BY l.id DESC", conn)
        if leave_df.empty:
            st.info("No leave records yet.")
        else:
            col1, col2 = st.columns(2)
            with col1: status_filter = st.selectbox("Filter by Status", ["All","Pending","Approved","Rejected"])
            with col2: type_filter = st.selectbox("Filter by Type", ["All","Annual","Sick","Emergency","Maternity","Paternity","Study"])
            filtered_leave = leave_df.copy()
            if status_filter != "All": filtered_leave = filtered_leave[filtered_leave["status"] == status_filter]
            if type_filter != "All": filtered_leave = filtered_leave[filtered_leave["leave_type"] == type_filter]
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total", len(leave_df))
            with c2: st.metric("Pending", len(leave_df[leave_df["status"] == "Pending"]))
            with c3: st.metric("Approved", len(leave_df[leave_df["status"] == "Approved"]))
            with c4: st.metric("Rejected", len(leave_df[leave_df["status"] == "Rejected"]))
            show = filtered_leave[["name","department","leave_type","start_date","end_date","days","reason","status"]]
            st.dataframe(show, use_container_width=True, hide_index=True)
            csv = show.to_csv(index=False).encode()
            st.download_button("📥 Download Leave Records", csv, "leave_records.csv", "text/csv")

    with tab2:
        st.subheader("➕ New Leave Request")
        with st.form("leave_form"):
            emp_df2 = get_employees()
            if not emp_df2.empty:
                emp_options = [f"{r['emp_id']} — {r['name']}" for _, r in emp_df2.iterrows()]
                emp_sel = st.selectbox("Employee", emp_options)
                emp_id_leave = emp_sel.split(" — ")[0]
            leave_type = st.selectbox("Leave Type", ["Annual","Sick","Emergency","Maternity","Paternity","Study","Compassionate"])
            c1, c2 = st.columns(2)
            with c1: start_date = st.date_input("Start Date")
            with c2: end_date = st.date_input("End Date")
            reason = st.text_area("Reason for Leave")
            days = (end_date - start_date).days + 1
            st.info(f"Total days: {days}")
            if st.form_submit_button("✅ Submit Leave Request", type="primary"):
                if days < 1:
                    st.error("End date must be after start date!")
                else:
                    conn.execute("INSERT INTO leaves (emp_id,leave_type,start_date,end_date,days,reason,applied_date) VALUES (?,?,?,?,?,?,?)",
                        (emp_id_leave, leave_type, str(start_date), str(end_date), days, reason, str(date.today())))
                    conn.commit()
                    st.success("✅ Leave request submitted!")
                    st.rerun()

    with tab3:
        st.subheader("✅ Approve or Reject Leave Requests")
        pending = pd.read_sql("SELECT l.*, e.name FROM leaves l JOIN employees e ON l.emp_id=e.emp_id WHERE l.status='Pending'", conn)
        if pending.empty:
            st.success("✅ No pending leave requests!")
        else:
            for _, row in pending.iterrows():
                with st.expander(f"🌴 {row['name']} — {row['leave_type']} ({row['start_date']} to {row['end_date']}, {row['days']} days)"):
                    st.write(f"**Reason:** {row['reason']}")
                    st.write(f"**Applied:** {row['applied_date']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Approve", key=f"app_{row['id']}"):
                            conn.execute("UPDATE leaves SET status='Approved', approved_by=? WHERE id=?",
                                (st.session_state.current_user, row["id"]))
                            conn.commit()
                            st.success("✅ Approved!")
                            st.rerun()
                    with c2:
                        if st.button("❌ Reject", key=f"rej_{row['id']}"):
                            conn.execute("UPDATE leaves SET status='Rejected', approved_by=? WHERE id=?",
                                (st.session_state.current_user, row["id"]))
                            conn.commit()
                            st.warning("❌ Rejected.")
                            st.rerun()

    with tab4:
        st.subheader("📄 Generate Leave Letter")
        emp_id_sel, emp_row = employee_selector("Select Employee", key="leave_letter_select_employee")
        if emp_row is not None:
            leave_records = pd.read_sql(f"SELECT * FROM leaves WHERE emp_id='{emp_id_sel}' AND status='Approved' ORDER BY id DESC", conn)
            if leave_records.empty:
                st.warning("No approved leaves found for this employee.")
            else:
                leave_options = [f"{r['leave_type']} ({r['start_date']} to {r['end_date']})" for _, r in leave_records.iterrows()]
                sel_leave_idx = st.selectbox("Select Leave", range(len(leave_options)), format_func=lambda x: leave_options[x])
                leave_row = leave_records.iloc[sel_leave_idx]
                letter = generate_leave_letter(emp_row, leave_row)
                st.text(letter)
                st.download_button("📥 Download Leave Letter", letter,
                    f"leave_letter_{emp_row['emp_id']}_{leave_row['start_date']}.txt", "text/plain")

# ====================== ATTENDANCE ======================
elif menu == "⏰ Attendance":
    st.title("⏰ Attendance Tracking")
    tab1, tab2, tab3 = st.tabs(["📋 View Attendance", "➕ Mark Attendance", "📊 Summary"])

    with tab1:
        att_df = pd.read_sql("SELECT a.*, e.name, e.department FROM attendance a JOIN employees e ON a.emp_id=e.emp_id ORDER BY a.att_date DESC", conn)
        if att_df.empty:
            st.info("No attendance records yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: date_filter = st.date_input("Filter by Date", date.today())
            with c2: dept_filter = st.selectbox("Filter by Department", ["All"] + get_dept_names())
            with c3: status_filter = st.selectbox("Filter by Status", ["All","Present","Absent","Late","On Leave"])
            filtered_att = att_df[att_df["att_date"] == str(date_filter)]
            if dept_filter != "All": filtered_att = filtered_att[filtered_att["department"] == dept_filter]
            if status_filter != "All": filtered_att = filtered_att[filtered_att["status"] == status_filter]
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Present", len(att_df[att_df["status"] == "Present"]))
            with c2: st.metric("Absent", len(att_df[att_df["status"] == "Absent"]))
            with c3: st.metric("Late", len(att_df[att_df["status"] == "Late"]))
            with c4: st.metric("On Leave", len(att_df[att_df["status"] == "On Leave"]))
            show = filtered_att[["name","department","att_date","clock_in","clock_out","status","notes"]]
            st.dataframe(show, use_container_width=True, hide_index=True)
            csv = show.to_csv(index=False).encode()
            st.download_button("📥 Download", csv, "attendance.csv", "text/csv")

    with tab2:
        st.subheader("➕ Mark Attendance")
        with st.form("att_form"):
            emp_df2 = get_employees()
            if not emp_df2.empty:
                emp_options = [f"{r['emp_id']} — {r['name']}" for _, r in emp_df2.iterrows()]
                emp_sel = st.selectbox("Employee", emp_options)
                emp_id_att = emp_sel.split(" — ")[0]
            att_date_val = st.date_input("Date", date.today())
            c1, c2 = st.columns(2)
            with c1:
                clock_in = st.text_input("Clock In Time", "08:00 AM")
                att_status = st.selectbox("Status", ["Present","Absent","Late","On Leave"])
            with c2:
                clock_out = st.text_input("Clock Out Time", "05:00 PM")
                notes = st.text_input("Notes (optional)")
            if st.form_submit_button("✅ Mark Attendance", type="primary"):
                existing_att = pd.read_sql(f"SELECT id FROM attendance WHERE emp_id='{emp_id_att}' AND att_date='{att_date_val}'", conn)
                if not existing_att.empty:
                    conn.execute("UPDATE attendance SET clock_in=?,clock_out=?,status=?,notes=? WHERE emp_id=? AND att_date=?",
                        (clock_in, clock_out, att_status, notes, emp_id_att, str(att_date_val)))
                    st.success("✅ Attendance updated!")
                else:
                    conn.execute("INSERT INTO attendance (emp_id,att_date,clock_in,clock_out,status,notes) VALUES (?,?,?,?,?,?)",
                        (emp_id_att, str(att_date_val), clock_in, clock_out, att_status, notes))
                    st.success("✅ Attendance marked!")
                conn.commit()
                st.rerun()

    with tab3:
        st.subheader("📊 Attendance Summary by Employee")
        att_all = pd.read_sql("SELECT a.emp_id, e.name, e.department, a.status, COUNT(*) as count FROM attendance a JOIN employees e ON a.emp_id=e.emp_id GROUP BY a.emp_id, a.status", conn)
        if not att_all.empty:
            pivot = att_all.pivot_table(index=["emp_id","name","department"], columns="status", values="count", fill_value=0).reset_index()
            st.dataframe(pivot, use_container_width=True, hide_index=True)
        else:
            st.info("No attendance data yet.")

# ====================== KPI DASHBOARD ======================
elif menu == "📈 KPI Dashboard":
    st.title("📈 KPI Dashboard")
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "➕ Add/Edit KPI", "👤 Individual KPI"])

    with tab1:
        kpi_df = pd.read_sql("SELECT k.*, e.name, e.department FROM kpi k JOIN employees e ON k.emp_id=e.emp_id ORDER BY k.overall_score DESC", conn)
        if kpi_df.empty:
            st.info("No KPI records yet. Add KPI scores in the 'Add/Edit KPI' tab.")
        else:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("Avg Attendance", f"{kpi_df['attendance_score'].mean():.1f}%")
            with c2: st.metric("Avg Punctuality", f"{kpi_df['punctuality_score'].mean():.1f}%")
            with c3: st.metric("Avg Satisfaction", f"{kpi_df['satisfaction_score'].mean():.1f}%")
            with c4: st.metric("Avg Task Score", f"{kpi_df['task_score'].mean():.1f}%")
            with c5: st.metric("Avg Overall", f"{kpi_df['overall_score'].mean():.1f}%")
            st.markdown("**Top Performers**")
            top = kpi_df.nlargest(10, "overall_score")[["name","department","attendance_score","punctuality_score","satisfaction_score","task_score","teamwork_score","overall_score"]]
            st.dataframe(top, use_container_width=True, hide_index=True)
            csv = kpi_df.to_csv(index=False).encode()
            st.download_button("📥 Download KPI Report (CSV)", csv, "kpi_report.csv", "text/csv")

    with tab2:
        st.subheader("➕ Add / Edit KPI Scores")
        emp_id_sel, emp_row = employee_selector("Select Employee", key="kpi_add_edit_select_employee")
        if emp_row is not None:
            kpi_month = st.text_input("Month", datetime.now().strftime("%B %Y"))
            existing_kpi = pd.read_sql(f"SELECT * FROM kpi WHERE emp_id='{emp_id_sel}' AND month='{kpi_month}'", conn)
            ex = existing_kpi.iloc[0] if not existing_kpi.empty else None
            c1, c2, c3 = st.columns(3)
            with c1:
                att_score = st.slider("Attendance Score (%)", 0, 100, int(ex["attendance_score"]) if ex is not None else 90)
                punct_score = st.slider("Punctuality Score (%)", 0, 100, int(ex["punctuality_score"]) if ex is not None else 90)
            with c2:
                sat_score = st.slider("Patient Satisfaction (%)", 0, 100, int(ex["satisfaction_score"]) if ex is not None else 90)
                task_score = st.slider("Task Completion (%)", 0, 100, int(ex["task_score"]) if ex is not None else 90)
            with c3:
                team_score = st.slider("Teamwork Score (%)", 0, 100, int(ex["teamwork_score"]) if ex is not None else 90)
                kpi_notes = st.text_area("Notes", ex["notes"] if ex is not None else "")
            overall = (att_score + punct_score + sat_score + task_score + team_score) / 5
            st.metric("Overall KPI Score", f"{overall:.1f}%")
            if st.button("💾 Save KPI", type="primary"):
                if ex is not None:
                    conn.execute("""UPDATE kpi SET attendance_score=?,punctuality_score=?,satisfaction_score=?,
                        task_score=?,teamwork_score=?,overall_score=?,notes=? WHERE emp_id=? AND month=?""",
                        (att_score,punct_score,sat_score,task_score,team_score,overall,kpi_notes,emp_id_sel,kpi_month))
                else:
                    conn.execute("""INSERT INTO kpi (emp_id,month,attendance_score,punctuality_score,satisfaction_score,
                        task_score,teamwork_score,overall_score,notes) VALUES (?,?,?,?,?,?,?,?,?)""",
                        (emp_id_sel,kpi_month,att_score,punct_score,sat_score,task_score,team_score,overall,kpi_notes))
                conn.commit()
                st.success("✅ KPI saved!")
                st.rerun()

    with tab3:
        st.subheader("👤 Individual Employee KPI Tracker")
        emp_id_sel, emp_row = employee_selector("Select Employee", key="kpi_individual_select_employee")
        if emp_row is not None:
            emp_kpi = pd.read_sql(f"SELECT * FROM kpi WHERE emp_id='{emp_id_sel}' ORDER BY id DESC", conn)
            if emp_kpi.empty:
                st.info("No KPI records for this employee yet.")
            else:
                st.markdown(f"**KPI History for {emp_row['name']}**")
                st.dataframe(emp_kpi[["month","attendance_score","punctuality_score","satisfaction_score","task_score","teamwork_score","overall_score","notes"]], use_container_width=True, hide_index=True)
                avg = emp_kpi["overall_score"].mean()
                st.metric("Average Overall Score", f"{avg:.1f}%")
                kpi_text = f"KPI REPORT — {emp_row['name']} ({emp_id_sel})\n" + "=" * 50 + "\n"
                for _, r in emp_kpi.iterrows():
                    kpi_text += f"\nMonth: {r['month']}\n  Attendance: {r['attendance_score']}%  Punctuality: {r['punctuality_score']}%\n  Satisfaction: {r['satisfaction_score']}%  Task: {r['task_score']}%  Teamwork: {r['teamwork_score']}%\n  Overall: {r['overall_score']:.1f}%\n"
                st.download_button("📥 Download Individual KPI Report", kpi_text, f"kpi_{emp_id_sel}.txt", "text/plain")

# ====================== TRAINING ======================
elif menu == "🎓 Training":
    st.title("🎓 Training & Development")
    tab1, tab2 = st.tabs(["📋 Training Records", "➕ Add Training"])

    with tab1:
        train_df = pd.read_sql("SELECT t.*, e.name, e.department FROM training t JOIN employees e ON t.emp_id=e.emp_id ORDER BY t.id DESC", conn)
        if train_df.empty:
            st.info("No training records yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Trainings", len(train_df))
            with c2: st.metric("Completed", len(train_df[train_df["status"] == "Completed"]))
            with c3: st.metric("Scheduled", len(train_df[train_df["status"] == "Scheduled"]))
            show = train_df[["name","department","training_name","provider","start_date","end_date","status","certificate"]]
            st.dataframe(show, use_container_width=True, hide_index=True)
            csv = show.to_csv(index=False).encode()
            st.download_button("📥 Download Training Records", csv, "training_records.csv", "text/csv")

    with tab2:
        st.subheader("➕ Add Training Record")
        with st.form("training_form"):
            emp_df2 = get_employees()
            if not emp_df2.empty:
                emp_options = [f"{r['emp_id']} — {r['name']}" for _, r in emp_df2.iterrows()]
                emp_sel = st.selectbox("Employee", emp_options)
                emp_id_train = emp_sel.split(" — ")[0]
            c1, c2 = st.columns(2)
            with c1:
                training_name = st.text_input("Training Name *")
                provider = st.text_input("Training Provider")
                start_date = st.date_input("Start Date")
            with c2:
                end_date = st.date_input("End Date")
                status = st.selectbox("Status", ["Scheduled","In Progress","Completed","Cancelled"])
                certificate = st.text_input("Certificate Number (if any)")
            notes = st.text_area("Notes")
            if st.form_submit_button("✅ Add Training", type="primary"):
                if not training_name:
                    st.error("Training name is required!")
                else:
                    conn.execute("INSERT INTO training (emp_id,training_name,provider,start_date,end_date,status,certificate,notes) VALUES (?,?,?,?,?,?,?,?)",
                        (emp_id_train, training_name, provider, str(start_date), str(end_date), status, certificate, notes))
                    conn.commit()
                    st.success("✅ Training record added!")
                    st.rerun()

# ====================== RECRUITMENT ======================
elif menu == "📢 Recruitment":
    st.title("📢 Recruitment Management")
    tab1, tab2 = st.tabs(["📋 Job Postings", "➕ Add Job Posting"])

    with tab1:
        rec_df = pd.read_sql("SELECT * FROM recruitment ORDER BY id DESC", conn)
        if rec_df.empty:
            st.info("No job postings yet.")
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Total Postings", len(rec_df))
            with c2: st.metric("Open", len(rec_df[rec_df["status"] == "Open"]))
            with c3: st.metric("Total Applicants", int(rec_df["applicants"].sum()))
            st.dataframe(rec_df[["position","department","posted_date","deadline","applicants","status","notes"]], use_container_width=True, hide_index=True)
            sel_job = st.selectbox("Select Job to Update", rec_df["id"].tolist(),
                format_func=lambda x: rec_df[rec_df["id"] == x]["position"].values[0])
            c1, c2 = st.columns(2)
            with c1: new_status = st.selectbox("New Status", ["Open","Closed","On Hold","Filled"])
            with c2: new_applicants = st.number_input("Applicant Count", min_value=0)
            if st.button("💾 Update Job Posting"):
                conn.execute("UPDATE recruitment SET status=?, applicants=? WHERE id=?", (new_status, new_applicants, sel_job))
                conn.commit()
                st.success("✅ Job posting updated!")
                st.rerun()

    with tab2:
        st.subheader("➕ Post New Job")
        with st.form("rec_form"):
            c1, c2 = st.columns(2)
            with c1:
                position = st.text_input("Position Title *")
                department = st.selectbox("Department", get_dept_names())
                posted_date = st.date_input("Posted Date", date.today())
            with c2:
                deadline = st.date_input("Application Deadline")
                status = st.selectbox("Status", ["Open","Closed","On Hold"])
            notes = st.text_area("Job Description / Notes")
            if st.form_submit_button("✅ Post Job", type="primary"):
                if not position:
                    st.error("Position title is required!")
                else:
                    conn.execute("INSERT INTO recruitment (position,department,posted_date,deadline,status,notes) VALUES (?,?,?,?,?,?)",
                        (position, department, str(posted_date), str(deadline), status, notes))
                    conn.commit()
                    st.success("✅ Job posted!")
                    st.rerun()

# ====================== ANNOUNCEMENTS ======================
elif menu == "📣 Announcements":
    st.title("📣 HR Announcements")
    tab1, tab2 = st.tabs(["📋 View Announcements", "➕ Post Announcement"])

    with tab1:
        ann_df = pd.read_sql("SELECT * FROM announcements ORDER BY id DESC", conn)
        if ann_df.empty:
            st.info("No announcements yet.")
        else:
            for _, ann in ann_df.iterrows():
                priority_color = {"High": "🔴", "Normal": "🔵", "Low": "⚪"}.get(ann["priority"], "🔵")
                with st.expander(f"{priority_color} {ann['title']} — {ann['posted_date']} | To: {ann['target']}"):
                    st.write(ann["message"])
                    st.caption(f"Posted by: {ann['posted_by']} | Priority: {ann['priority']}")
                    if st.button(f"🗑️ Delete", key=f"del_ann_{ann['id']}"):
                        conn.execute("DELETE FROM announcements WHERE id=?", (ann["id"],))
                        conn.commit()
                        st.rerun()

    with tab2:
        st.subheader("➕ Post New Announcement")
        with st.form("ann_form"):
            title = st.text_input("Title *")
            message = st.text_area("Message *")
            c1, c2, c3 = st.columns(3)
            with c1: priority = st.selectbox("Priority", ["Normal","High","Low"])
            with c2: target = st.selectbox("Target Audience", ["All Staff","Doctors","Nurses","Administration","Department Heads"])
            with c3: posted_by = st.text_input("Posted By", st.session_state.current_user)
            if st.form_submit_button("📢 Post Announcement", type="primary"):
                if not title or not message:
                    st.error("Title and message are required!")
                else:
                    conn.execute("INSERT INTO announcements (title,message,posted_by,posted_date,priority,target) VALUES (?,?,?,?,?,?)",
                        (title, message, posted_by, str(date.today()), priority, target))
                    conn.commit()
                    st.success("✅ Announcement posted!")
                    st.rerun()

# ====================== REPORTS ======================
elif menu == "📋 Reports":
    st.title("📋 HR Reports & Analytics")
    emp_df = get_employees()
    dept_df = get_departments()
    pay_df = pd.read_sql("SELECT * FROM payroll", conn)
    leave_df = pd.read_sql("SELECT * FROM leaves", conn)
    kpi_df = pd.read_sql("SELECT * FROM kpi", conn)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Staff Report", "💰 Payroll Report", "📈 KPI Report"])

    with tab1:
        st.subheader("Facility Overview")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        with c1: st.metric("Total Staff", len(emp_df))
        with c2: st.metric("Active Staff", len(emp_df[emp_df["status"] == "Active"]) if not emp_df.empty else 0)
        with c3: st.metric("Departments", len(dept_df))
        with c4: st.metric("Net Payroll", f"KES {pay_df['net'].sum():,.0f}" if not pay_df.empty else "N/A")
        with c5: st.metric("Total Leaves", len(leave_df))
        with c6: st.metric("Avg KPI", f"{kpi_df['overall_score'].mean():.1f}%" if not kpi_df.empty else "N/A")
        if not emp_df.empty:
            st.markdown("**Staff Distribution by Department**")
            dept_counts = emp_df.groupby("department").size().reset_index(name="Staff Count")
            st.dataframe(dept_counts, use_container_width=True, hide_index=True)
            st.markdown("**Employment Type Breakdown**")
            emp_type = emp_df.groupby("employment_type").size().reset_index(name="Count")
            st.dataframe(emp_type, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Staff Report")
        if emp_df.empty:
            st.info("No staff records.")
        else:
            st.dataframe(emp_df, use_container_width=True, hide_index=True)
            csv = emp_df.to_csv(index=False).encode()
            st.download_button("📥 Download Full Staff Report", csv, "full_staff_report.csv", "text/csv")

    with tab3:
        st.subheader("Payroll Report")
        if pay_df.empty:
            st.info("No payroll records.")
        else:
            pay_full = pd.read_sql("SELECT p.*, e.name, e.department FROM payroll p JOIN employees e ON p.emp_id=e.emp_id", conn)
            st.dataframe(pay_full, use_container_width=True, hide_index=True)
            csv = pay_full.to_csv(index=False).encode()
            st.download_button("📥 Download Payroll Report", csv, "payroll_report.csv", "text/csv")

    with tab4:
        st.subheader("KPI Report")
        if kpi_df.empty:
            st.info("No KPI records.")
        else:
            kpi_full = pd.read_sql("SELECT k.*, e.name, e.department FROM kpi k JOIN employees e ON k.emp_id=e.emp_id ORDER BY k.overall_score DESC", conn)
            st.dataframe(kpi_full, use_container_width=True, hide_index=True)
            csv = kpi_full.to_csv(index=False).encode()
            st.download_button("📥 Download KPI Report", csv, "kpi_report.csv", "text/csv")

        report_text = f"MOTHER AMADEA MISSION HOSPITAL\nFULL HR REPORT\nGenerated: {datetime.now().strftime('%d %B %Y %H:%M')}\n"
        report_text += "=" * 50 + "\n"
        report_text += f"Total Staff     : {len(emp_df)}\nDepartments     : {len(dept_df)}\n"
        report_text += f"Net Payroll     : KES {pay_df['net'].sum():,.2f}\n" if not pay_df.empty else "Net Payroll     : N/A\n"
        report_text += f"Avg KPI Score   : {kpi_df['overall_score'].mean():.1f}%\n" if not kpi_df.empty else "Avg KPI Score   : N/A\n"
        st.download_button("📥 Download Full Facility Report (TXT)", report_text, "facility_report.txt", "text/plain")