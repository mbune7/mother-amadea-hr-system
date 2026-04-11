import PySimpleGUI as sg
from hr_system import HospitalHR
import pandas as pd
import os
import io

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

# 🎨 Beautiful Theme & Styling
sg.theme('LightBlue2')  # Soft blue theme
DEFAULT_FONT = ('Arial', 10)
HEADER_FONT = ('Arial', 14, 'bold')
BUTTON_FONT = ('Arial', 10, 'bold')

class HR_GUI:
    def __init__(self):
        self.hr = HospitalHR()
        self.layout = self.create_layout()
        self.window = sg.Window(
            "🏥 Mother Amadea HR System",
            self.layout,
            size=(1100, 750),
            resizable=True,
            icon=None,  # Add icon if you have one
            finalize=True
        )

    def create_layout(self):
        # 🖼️ Header with Logo/Image
        logo_element = self.create_logo_element()
        header_layout = [
            [logo_element,
             sg.Text("Mother Amadea", font=('Arial', 24, 'bold'), text_color='navy'),
             sg.Text("HR System", font=('Arial', 16), text_color='darkblue')]
        ]

        # Employee Tab with Frames
        employee_layout = [
            [sg.Frame("Add New Employee", [
                [sg.Text("ID:", font=DEFAULT_FONT), sg.Input(key="-EMP_ID-", size=(10,1), font=DEFAULT_FONT),
                 sg.Text("Name:", font=DEFAULT_FONT), sg.Input(key="-EMP_NAME-", size=(20,1), font=DEFAULT_FONT)],
                [sg.Text("Position:", font=DEFAULT_FONT), sg.Input(key="-EMP_POS-", size=(15,1), font=DEFAULT_FONT),
                 sg.Text("Department:", font=DEFAULT_FONT), sg.Input(key="-EMP_DEPT-", size=(15,1), font=DEFAULT_FONT)],
                [sg.Text("Salary (KES):", font=DEFAULT_FONT), sg.Input(key="-EMP_SAL-", size=(10,1), font=DEFAULT_FONT),
                 sg.Text("Hire Date (YYYY-MM-DD):", font=DEFAULT_FONT), sg.Input(key="-EMP_DATE-", size=(12,1), font=DEFAULT_FONT)],
                [sg.Button("Add Employee", key="-ADD_EMP-", font=BUTTON_FONT, button_color=('white', 'green'), size=(15,1)),
                 sg.Button("Clear Form", key="-CLEAR_EMP-", font=BUTTON_FONT, button_color=('white', 'orange'), size=(15,1))]
            ], font=HEADER_FONT, title_color='darkgreen')],
            [sg.HorizontalSeparator()],
            [sg.Frame("Search Employee", [
                [sg.Text("Employee ID:", font=DEFAULT_FONT), sg.Input(key="-SEARCH_ID-", size=(10,1), font=DEFAULT_FONT),
                 sg.Button("Search", key="-SEARCH_EMP-", font=BUTTON_FONT, button_color=('white', 'blue'))],
                [sg.Text("", key="-SEARCH_RESULT-", size=(60,2), font=DEFAULT_FONT, text_color='red')]
            ], font=HEADER_FONT, title_color='darkblue')],
            [sg.HorizontalSeparator()],
            [sg.Frame("Employee Directory", [
                [sg.Button("View All Employees", key="-VIEW_ALL-", font=BUTTON_FONT, button_color=('white', 'purple'), size=(20,1))],
                [sg.Table(values=[], headings=["ID", "Name", "Position", "Department", "Salary", "Hire Date"],
                          key="-EMP_TABLE-", size=(90,15), justification="left", enable_events=True,
                          font=DEFAULT_FONT, header_font=HEADER_FONT, header_background_color='lightblue')],
                [sg.Button("Edit Selected", key="-EDIT_EMP-", font=BUTTON_FONT, button_color=('white', 'teal'), size=(15,1)),
                 sg.Button("Delete Selected", key="-DEL_EMP-", font=BUTTON_FONT, button_color=('white', 'red'), size=(15,1))]
            ], font=HEADER_FONT, title_color='purple')]
        ]

        # Attendance Tab
        attendance_layout = [
            [sg.Frame("Mark Attendance", [
                [sg.Text("Employee ID:", font=DEFAULT_FONT), sg.Input(key="-ATT_ID-", size=(10,1), font=DEFAULT_FONT),
                 sg.Text("Date (YYYY-MM-DD):", font=DEFAULT_FONT), sg.Input(key="-ATT_DATE-", size=(12,1), font=DEFAULT_FONT)],
                [sg.Text("Status:", font=DEFAULT_FONT), sg.Combo(["Present", "Absent", "On Leave"], key="-ATT_STATUS-", default_value="Present", font=DEFAULT_FONT)],
                [sg.Text("Notes:", font=DEFAULT_FONT), sg.Input(key="-ATT_NOTES-", size=(40,1), font=DEFAULT_FONT)],
                [sg.Button("Mark Attendance", key="-MARK_ATT-", font=BUTTON_FONT, button_color=('white', 'green'), size=(20,1))]
            ], font=HEADER_FONT, title_color='darkgreen')],
            [sg.HorizontalSeparator()],
            [sg.Frame("View Attendance History", [
                [sg.Text("Employee ID:", font=DEFAULT_FONT), sg.Input(key="-VIEW_ATT_ID-", size=(10,1), font=DEFAULT_FONT),
                 sg.Button("View History", key="-VIEW_ATT-", font=BUTTON_FONT, button_color=('white', 'blue'))],
                [sg.Multiline("", key="-ATT_HISTORY-", size=(90,15), font=DEFAULT_FONT, disabled=True, background_color='lightcyan')]
            ], font=HEADER_FONT, title_color='darkblue')]
        ]

        # Departments Tab
        dept_layout = [
            [sg.Frame("Add Department", [
                [sg.Text("Name:", font=DEFAULT_FONT), sg.Input(key="-DEPT_NAME-", size=(20,1), font=DEFAULT_FONT),
                 sg.Text("Description:", font=DEFAULT_FONT), sg.Input(key="-DEPT_DESC-", size=(40,1), font=DEFAULT_FONT)],
                [sg.Button("Add Department", key="-ADD_DEPT-", font=BUTTON_FONT, button_color=('white', 'green'), size=(20,1))]
            ], font=HEADER_FONT, title_color='darkgreen')],
            [sg.HorizontalSeparator()],
            [sg.Frame("Department List", [
                [sg.Button("View Departments", key="-VIEW_DEPT-", font=BUTTON_FONT, button_color=('white', 'purple'), size=(20,1))],
                [sg.Listbox(values=[], key="-DEPT_LIST-", size=(60,10), font=DEFAULT_FONT, background_color='lightyellow')],
                [sg.Button("Delete Selected", key="-DEL_DEPT-", font=BUTTON_FONT, button_color=('white', 'red'), size=(20,1))]
            ], font=HEADER_FONT, title_color='purple')]
        ]

        # Reports Tab
        reports_layout = [
            [sg.Frame("Reports & KPIs", [
                [sg.Button("Export Staff to Excel", key="-EXPORT_EXCEL-", font=BUTTON_FONT, button_color=('white', 'blue'), size=(25,1)),
                 sg.Button("Show KPI Dashboard", key="-SHOW_KPI-", font=BUTTON_FONT, button_color=('white', 'purple'), size=(25,1))],
                [sg.Multiline("", key="-KPI_OUTPUT-", size=(90,20), font=DEFAULT_FONT, disabled=True, background_color='lightgreen')]
            ], font=HEADER_FONT, title_color='darkblue')]
        ]

        tab_group = sg.TabGroup([
            [sg.Tab("👥 Employees", employee_layout, background_color='lightblue'),
             sg.Tab("📅 Attendance", attendance_layout, background_color='lightcyan'),
             sg.Tab("🏢 Departments", dept_layout, background_color='lightyellow'),
             sg.Tab("📊 Reports", reports_layout, background_color='lightgreen')]
        ], font=BUTTON_FONT, tab_background_color='white', selected_background_color='lightgrey')

        layout = [
            header_layout,
            [tab_group],
            [sg.Button("Exit", button_color=('white', 'red'), font=BUTTON_FONT, size=(10,1))]
        ]
        return layout

    def create_logo_element(self):
        logo_path = 'amadea_logo.png'
        if os.path.exists(logo_path):
            if Image is not None and ImageDraw is not None:
                try:
                    with Image.open(logo_path).convert('RGBA') as img:
                        img = img.resize((64, 64), Image.LANCZOS)
                        circle = Image.new('RGBA', (80, 80), (255, 255, 255, 0))
                        mask = Image.new('L', (64, 64), 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, 64, 64), fill=255)
                        img_circle = Image.new('RGBA', (64, 64), (255, 255, 255, 0))
                        img_circle.paste(img, (0, 0), mask=mask)
                        circle.paste(img_circle, (8, 8), mask=img_circle)
                        draw_circle = ImageDraw.Draw(circle)
                        draw_circle.ellipse((4, 4, 76, 76), outline=(0, 85, 150), width=3)
                        bio = io.BytesIO()
                        circle.save(bio, format='PNG')
                        return sg.Image(data=bio.getvalue(), size=(80, 80), key='-LOGO-')
                except Exception:
                    pass
            return sg.Image(logo_path, size=(80, 80), key='-LOGO-')
        return sg.Text('🏥', font=('Arial', 32), text_color='navy')

    def run(self):
        selected_emp = None
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                break

            # Add Employee
            if event == "-ADD_EMP-":
                try:
                    emp_id = values["-EMP_ID-"].strip().upper()
                    name = values["-EMP_NAME-"].strip()
                    pos = values["-EMP_POS-"].strip()
                    dept = values["-EMP_DEPT-"].strip()
                    sal = float(values["-EMP_SAL-"])
                    date = values["-EMP_DATE-"].strip()
                    if not all([emp_id, name, pos, dept, date]):
                        sg.popup_error("All fields required!")
                        continue
                    self.hr.cursor.execute("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", (emp_id, name, pos, dept, sal, date))
                    self.hr.conn.commit()
                    sg.popup("Employee added successfully!")
                    self.clear_emp_form()
                except ValueError:
                    sg.popup_error("Invalid salary!")
                except Exception as e:
                    sg.popup_error(f"Error: {str(e)}")

            # Clear Employee Form
            if event == "-CLEAR_EMP-":
                self.clear_emp_form()

            # Search Employee
            if event == "-SEARCH_EMP-":
                emp_id = values["-SEARCH_ID-"].strip().upper()
                self.hr.cursor.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
                row = self.hr.cursor.fetchone()
                if row:
                    result = f"ID: {row[0]} | Name: {row[1]} | Position: {row[2]} | Dept: {row[3]} | Salary: {row[4]} | Hire: {row[5]}"
                else:
                    result = "Employee not found."
                self.window["-SEARCH_RESULT-"].update(result)

            # View All Employees
            if event == "-VIEW_ALL-":
                self.load_employee_table()

            # Table Selection
            if event == "-EMP_TABLE-":
                selected = values["-EMP_TABLE-"]
                if selected:
                    selected_emp = self.window["-EMP_TABLE-"].get()[selected[0]][0]  # Get ID

            # Edit Employee (placeholder)
            if event == "-EDIT_EMP-":
                if selected_emp:
                    sg.popup("Edit feature coming soon!")
                else:
                    sg.popup_error("Select an employee first!")

            # Delete Employee (placeholder)
            if event == "-DEL_EMP-":
                if selected_emp:
                    confirm = sg.popup_yes_no(f"Delete employee {selected_emp}?")
                    if confirm == "Yes":
                        self.hr.cursor.execute("DELETE FROM employees WHERE emp_id=?", (selected_emp,))
                        self.hr.conn.commit()
                        sg.popup("Employee deleted!")
                        self.load_employee_table()
                else:
                    sg.popup_error("Select an employee first!")

            # Mark Attendance
            if event == "-MARK_ATT-":
                emp_id = values["-ATT_ID-"].strip().upper()
                date = values["-ATT_DATE-"].strip()
                status = values["-ATT_STATUS-"]
                notes = values["-ATT_NOTES-"].strip()
                try:
                    self.hr.cursor.execute("INSERT INTO attendance (emp_id, attendance_date, status, notes) VALUES (?, ?, ?, ?)", (emp_id, date, status, notes))
                    self.hr.conn.commit()
                    sg.popup("Attendance marked!")
                except Exception as e:
                    sg.popup_error(f"Error: {str(e)}")

            # View Attendance
            if event == "-VIEW_ATT-":
                emp_id = values["-VIEW_ATT_ID-"].strip().upper()
                self.hr.cursor.execute("SELECT attendance_date, status, notes FROM attendance WHERE emp_id=? ORDER BY attendance_date DESC", (emp_id,))
                rows = self.hr.cursor.fetchall()
                history = "\n".join([f"{r[0]}: {r[1]} {r[2] if r[2] else ''}" for r in rows]) if rows else "No records."
                self.window["-ATT_HISTORY-"].update(history)

            # Add Department
            if event == "-ADD_DEPT-":
                name = values["-DEPT_NAME-"].strip()
                desc = values["-DEPT_DESC-"].strip()
                try:
                    self.hr.cursor.execute("INSERT INTO departments VALUES (?, ?)", (name, desc))
                    self.hr.conn.commit()
                    sg.popup("Department added!")
                except Exception as e:
                    sg.popup_error(f"Error: {str(e)}")

            # View Departments
            if event == "-VIEW_DEPT-":
                self.hr.cursor.execute("SELECT dept_name FROM departments")
                depts = [r[0] for r in self.hr.cursor.fetchall()]
                self.window["-DEPT_LIST-"].update(depts)

            # Delete Department
            if event == "-DEL_DEPT-":
                selected = values["-DEPT_LIST-"]
                if selected:
                    dept = selected[0]
                    self.hr.cursor.execute("SELECT COUNT(*) FROM employees WHERE department=?", (dept,))
                    if self.hr.cursor.fetchone()[0] > 0:
                        sg.popup_error("Cannot delete - employees assigned!")
                    else:
                        confirm = sg.popup_yes_no(f"Delete {dept}?")
                        if confirm == "Yes":
                            self.hr.cursor.execute("DELETE FROM departments WHERE dept_name=?", (dept,))
                            self.hr.conn.commit()
                            sg.popup("Deleted!")
                            self.window["-VIEW_DEPT-"].click()  # Refresh

            # Export to Excel
            if event == "-EXPORT_EXCEL-":
                self.hr.export_to_excel()
                sg.popup("Exported to Excel!")

            # Show KPI
            if event == "-SHOW_KPI-":
                # Call KPI method and display
                kpi_text = self.get_kpi_text()
                self.window["-KPI_OUTPUT-"].update(kpi_text)

        self.window.close()
        self.hr.close()

    def clear_emp_form(self):
        for key in ["-EMP_ID-", "-EMP_NAME-", "-EMP_POS-", "-EMP_DEPT-", "-EMP_SAL-", "-EMP_DATE-"]:
            self.window[key].update("")

    def load_employee_table(self):
        self.hr.cursor.execute("SELECT emp_id, name, position, department, salary, hire_date FROM employees ORDER BY department, name")
        rows = self.hr.cursor.fetchall()
        table_data = [[r[0], r[1], r[2], r[3], f"{r[4]:,.2f}", r[5]] for r in rows]
        self.window["-EMP_TABLE-"].update(values=table_data)

    def get_kpi_text(self):
        self.hr.cursor.execute("SELECT COUNT(*) FROM employees")
        total_staff = self.hr.cursor.fetchone()[0]
        self.hr.cursor.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
        present = self.hr.cursor.fetchone()[0]
        self.hr.cursor.execute("SELECT COUNT(*) FROM attendance")
        total_att = self.hr.cursor.fetchone()[0]
        rate = (present / total_att * 100) if total_att > 0 else 0
        self.hr.cursor.execute("SELECT department, COUNT(*) FROM employees GROUP BY department ORDER BY COUNT(*) DESC")
        dept_counts = self.hr.cursor.fetchall()
        dept_text = "\n".join([f"{d[0]}: {d[1]}" for d in dept_counts])
        return f"Total Staff: {total_staff}\nAttendance Records: {total_att}\nPresent Rate: {rate:.1f}%\n\nStaff per Department:\n{dept_text}"

if __name__ == "__main__":
    gui = HR_GUI()
    gui.run()