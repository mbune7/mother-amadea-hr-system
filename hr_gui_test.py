import PySimpleGUI as sg

sg.theme('DarkBlue2')

layout = [
    [sg.Text("🏥 MOMBASA HOSPITAL HR MANAGEMENT SYSTEM 🏥", font=("Helvetica", 16, "bold"), justification="center")],
    [sg.Text("\nThis is a test window.\nIf you see this, GUI is working!", font=("Helvetica", 12))],
    [sg.Button("Click Me", size=(20, 2))],
    [sg.Button("Close", size=(20, 2), button_color="red")]
]

window = sg.Window("HR System Test", layout, size=(600, 300), element_justification="center")

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Close":
        break
    if event == "Click Me":
        sg.popup("Hello! 🎉\nThe GUI is working perfectly.", title="Success")

window.close()
print("Test window closed.")