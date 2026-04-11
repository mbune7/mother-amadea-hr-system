here is my codes kindly guide:  Hospital HR Management System - Step 10 (Final)
# Features: Full CRUD + Departments + Attendance + Export to Excel + KPI

import sqlite3
from datetime import datetime
import pandas as pd

# ==================== EMPLOYEE CLASS ====================
class Employee:
    def __init__(self, emp_id, name, position, department, salary, hire_date):
        self.emp_id = emp_id.upper().strip()
        self.name = name.strip().title()
        self.position = position.strip().title()
        self.department = department.strip().title()
        self.salary = float(salary)
        self.hire_date = hire_date.strip()

# ==================== HOSPITAL HR SYSTEM ====================
class HospitalHR:
    def __init__(self):
        self.conn = sqlite3.connect("hospital_hr.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date TEXT NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                dept_name TEXT PRIMARY KEY,
                description TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id TEXT NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
            )
        ''')
        self.conn.commit()

    # ====================== STAFF FUNCTIONS ======================
    def add_employee(self):
        print("\n🏥 ── Add New Staff Member ──")
        emp_id = input("Employee ID: ").strip().upper()
        name = input("Full Name: ").strip()
        position = input("Position: ").strip()
        department = input("Department: ").strip().title()
        while True:
            try:
                salary = float(input("Monthly Salary (KES): "))
                if salary <= 0:
                    print("❌ Salary must be positive.")
                    continue
                break
            except ValueError:
                print("❌ Enter a valid number.")
        hire_date = input("Hire Date (YYYY-MM-DD): ").strip()

        try:
            self.cursor.execute('''
                INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)
            ''', (emp_id, name, position, department, salary, hire_date))
            self.conn.commit()
            print(f"✅ {name} added successfully!")
        except sqlite3.IntegrityError:
            print(f"❌ Employee ID {emp_id} already exists!")

    def view_all_staff(self):
        self.cursor.execute("SELECT * FROM employees ORDER BY department, name")
        rows = self.cursor.fetchall()
        if not rows:
            print("No staff found.")
            return
        print("\n" + "═"*115)
        print("🏥 HOSPITAL STAFF DIRECTORY")
        print("═"*115)
        print(f"{'ID':<8} {'Name':<28} {'Position':<22} {'Department':<20} {'Salary (KES)':<18} {'Hire Date':<12}")
        print("═"*115)
        for row in rows:
            print(f"{row[0]:<8} {row[1]:<28} {row[2]:<22} {row[3]:<20} KES {row[4]:<15,.2f} {row[5]:<12}")
        print("═"*115)

    def search_staff(self):
        emp_id = input("\nEnter Employee ID: ").strip().upper()
        self.cursor.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
        row = self.cursor.fetchone()
        if row:
            print(f"\n✅ Found → ID: {row[0]} | Name: {row[1]} | Position: {row[2]} | Dept: {row[3]}")
        else:
            print("❌ Not found.")

    # ====================== ATTENDANCE ======================
    def mark_attendance(self):
        print("\n🏥 ── Mark Attendance ──")
        emp_id = input("Employee ID: ").strip().upper()
        self.cursor.execute("SELECT name FROM employees WHERE emp_id=?", (emp_id,))
        row = self.cursor.fetchone()
        if not row:
            print("❌ Employee not found!")
            return
        name = row[0]

        date = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        print("1. Present   2. Absent   3. On Leave")
        choice = input("Choose (1-3): ").strip()
        status = {"1": "Present", "2": "Absent", "3": "On Leave"}.get(choice, "Present")

        notes = input("Notes (optional): ").strip()

        try:
            self.cursor.execute('''
                INSERT INTO attendance (emp_id, attendance_date, status, notes) 
                VALUES (?, ?, ?, ?)
            ''', (emp_id, date, status, notes))
            self.conn.commit()
            print(f"✅ Attendance marked for {name} on {date} as {status}")
        except Exception:
            print("Attendance already marked for this date.")

    def view_attendance(self):
        emp_id = input("\nEnter Employee ID: ").strip().upper()
        self.cursor.execute("""
            SELECT attendance_date, status, notes 
            FROM attendance WHERE emp_id=? 
            ORDER BY attendance_date DESC
        """, (emp_id,))
        rows = self.cursor.fetchall()
        if not rows:
            print("No attendance records.")
            return
        self.cursor.execute("SELECT name FROM employees WHERE emp_id=?", (emp_id,))
        name = self.cursor.fetchone()[0]
        print(f"\nAttendance for {name} ({emp_id})")
        for row in rows:
            print(f"{row[0]} → {row[1]}  {row[2] if row[2] else ''}")

    # ====================== EXPORT TO EXCEL ======================
    def export_to_excel(self):
        self.cursor.execute("SELECT * FROM employees ORDER BY department, name")
        rows = self.cursor.fetchall()
        if not rows:
            print("No staff to export.")
            return

        data = []
        for row in rows:
            data.append({
                "Employee ID": row[0],
                "Name": row[1],
                "Position": row[2],
                "Department": row[3],
                "Salary (KES)": row[4],
                "Hire Date": row[5]
            })

        df = pd.DataFrame(data)
        filename = f"hospital_staff_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        df.to_excel(filename, index=False)
        print(f"✅ Staff list exported successfully!")
        print(f"📁 File saved as: {filename}")
        print("You can find the file in your project folder.")

    # ====================== KPI MONITORING ======================
    def kpi_monitoring(self):
        print("\n🏥 KPI MONITORING DASHBOARD")
        print("="*50)

        # Total Staff
        self.cursor.execute("SELECT COUNT(*) FROM employees")
        total_staff = self.cursor.fetchone()[0]

        # Attendance Rate (last 30 days - simplified)
        self.cursor.execute("""
            SELECT COUNT(*) FROM attendance 
            WHERE status = 'Present'
        """)
        present = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM attendance")
        total_records = self.cursor.fetchone()[0]

        attendance_rate = (present / total_records * 100) if total_records > 0 else 0

        print(f"Total Staff          : {total_staff}")
        print(f"Attendance Records   : {total_records}")
        print(f"Present Rate         : {attendance_rate:.1f}%")

        # Department-wise staff count
        self.cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM employees GROUP BY department ORDER BY count DESC
        """)
        print("\nStaff per Department:")
        for row in self.cursor.fetchall():
            print(f"• {row[0]:<20} : {row[1]} staff")

    # ====================== DEPARTMENTS ======================
    def add_department(self):
        dept_name = input("\nDepartment Name: ").strip().title()
        desc = input("Description: ").strip()
        try:
            self.cursor.execute("INSERT INTO departments VALUES (?, ?)", (dept_name, desc))
            self.conn.commit()
            print(f"✅ {dept_name} added!")
        except sqlite3.IntegrityError:
            print("Department already exists.")

    def view_departments(self):
        self.cursor.execute("SELECT * FROM departments")
        rows = self.cursor.fetchall()
        if not rows:
            print("No departments yet.")
            return
        print("\nHospital Departments:")
        for row in rows:
            print(f"• {row[0]}")

    def delete_department(self):
        self.view_departments()
        dept = input("\nDepartment to delete: ").strip().title()
        self.cursor.execute("SELECT COUNT(*) FROM employees WHERE department=?", (dept,))
        if self.cursor.fetchone()[0] > 0:
            print("❌ Cannot delete - staff assigned!")
            return
        if input(f"Delete {dept}? (yes/no): ").lower() in ['yes','y']:
            self.cursor.execute("DELETE FROM departments WHERE dept_name=?", (dept,))
            self.conn.commit()
            print("✅ Deleted.")

    def close(self):
        self.conn.close()


# ====================== MAIN MENU ======================
def main():
    print("="*75)
    print("       🏥  MOMBASA HOSPITAL HR MANAGEMENT SYSTEM  🏥")
    print("="*75)

    hr = HospitalHR()

    while True:
        print("\n" + "─"*65)
        print("MAIN MENU")
        print("─"*65)
        print("1. Add New Staff")
        print("2. View All Staff")
        print("3. Search Staff")
        print("4. Mark Attendance")
        print("5. View Attendance History")
        print("6. Export Staff List to Excel")
        print("7. KPI Monitoring")
        print("8. Departments Management")
        print("9. Exit")
        print("─"*65)

        choice = input("Enter choice (1-9): ").strip()

        if choice == "1":
            hr.add_employee()
        elif choice == "2":
            hr.view_all_staff()
        elif choice == "3":
            hr.search_staff()
        elif choice == "4":
            hr.mark_attendance()
        elif choice == "5":
            hr.view_attendance()
        elif choice == "6":
            hr.export_to_excel()
        elif choice == "7":
            hr.kpi_monitoring()
        elif choice == "8":
            print("\nDepartments Menu:")
            print("a. Add Department   b. View Departments   c. Delete Department")
            sub = input("Choose a/b/c: ").strip().lower()
            if sub == "a":
                hr.add_department()
            elif sub == "b":
                hr.view_departments()
            elif sub == "c":
                hr.delete_department()
        elif choice == "9":
            hr.close()
            print("\n👋 Thank you for using Mombasa Hospital HR System!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()