import csv
import os
import re
import threading
import time
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkinter import Menu
from datetime import datetime
import cv2
import numpy as np
import pandas as pd
from model.classification_model import FacialRecognitionModel
from module import config, find, utils
import tkinter as tk

# Global variables for face processing
embedding_result = None
processing = False
face_bb = None
real_face = False
anti_face_conf = 0
face_model = None
embedding_model = None
model_loaded = False

def load_models_async():
    global face_model, embedding_model, model_loaded
    message3.configure(text="Đang tải model nhận diện khuôn mặt, vui lòng chờ...")
    face_model = FacialRecognitionModel()
    embedding_model = face_model.get_embedding_model()
    model_loaded = True
    message3.configure(text="Face Recognition Based Attendance System")
    # Enable buttons
    takeImg.configure(state="normal")
    trainImg.configure(state="normal")
    trackImg.configure(state="normal")

def clear():
    """Clear the input fields for ID and Name, and reset the instruction message."""
    txt.delete(0, 'end')
    txt2.delete(0, 'end')
    res = "1)Take Images  ===> 2)Save Profile"
    message1.configure(text=res)

def validate_input(entry_id, entry_name):
    """
    Validate ID and Name inputs using regex patterns.

    Args:
        entry_id (str): Employee ID input
        entry_name (str): Employee name input

    Returns:
        bool: True if inputs are valid, False otherwise
    """
    id_pattern = r'^\d{1,3}$'
    name_pattern = r'^[a-zA-Z\s-]{1,50}$'

    id_value = entry_id.strip()
    name_value = entry_name.strip()

    # Validate ID
    if not id_value:
        messagebox.showerror("Error", "ID cannot be empty")
        return False
    if not re.match(id_pattern, id_value):
        messagebox.showerror("Error", "ID must contain only numbers and be 1-3 digits long")
        return False

    # Validate Name
    if not name_value:
        messagebox.showerror("Error", "Name cannot be empty")
        return False
    if not re.match(name_pattern, name_value):
        messagebox.showerror("Error", "Name must contain only letters, spaces, or hyphens (max 50 characters)")
        return False

    return True

def load_attendance_to_table():
    """
    Load today's attendance data from CSV and display in the attendance table.

    Displays error if the CSV file for the current date does not exist.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    csv_filepath = os.path.join(config.ATTENDANCE_REPORT, f"{today}.csv")

    if not os.path.exists(csv_filepath):
        messagebox.showerror("Error", f"Attendance file {today}.csv not found")
        return

    with open(csv_filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) == 4:
                tb.insert('', 'end', text=row[0], values=(row[1], row[2], row[3]))

def async_preprocess(frame, embedding_model):
    """
    Preprocess a frame asynchronously to extract face embeddings and detect spoofing.

    Args:
        frame: Video frame to process
        embedding_model: Model for generating face embeddings
    """
    global embedding_result, processing, face_bb, real_face, anti_face_conf
    processing = True
    embedding_result, face_bb = utils.preprocess(frame, embedding_model)
    processing = False

def check_id_exists(id_value):
    """
    Check if an employee ID already exists in the employee CSV file.

    Args:
        id_value (str): Employee ID to check

    Returns:
        bool: True if ID exists, False otherwise
    """
    if not os.path.exists(config.EMPLOYEE_CSV):
        return False
    with open(config.EMPLOYEE_CSV, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if row and row[0] == id_value:
                return True
    return False

def SaveProfile():
    """
    Save employee profile (ID, name, image path, and embedding) after admin verification.

    Validates inputs, checks for duplicate IDs, and saves data to CSV after admin authentication.
    """
    id_value = txt.get()
    name_value = txt2.get()
    img_path = os.path.join(config.EMPLOYEE_DIR, f"{id_value}.jpg")
    embedding_path = os.path.join(config.EMPLOYEE_EMBEDDING, f"{id_value}.npy")

    if check_id_exists(id_value):
        messagebox.showerror("Error", f"ID {id_value} already exists in the system")
        return

    def verify_admin():
        """Verify admin credentials and save employee data if valid."""
        username = entry_username.get().strip()
        password = entry_password.get().strip()

        if username == "admin" and password == "admin123":
            with open(config.EMPLOYEE_CSV, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([id_value, name_value, img_path, embedding_path])
            messagebox.showinfo("Success", f"Saved profile for ID: {id_value}, Name: {name_value}")
            admin_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    admin_window.verify_button.config(command=verify_admin)
    admin_window.deiconify()
    admin_window.grab_set()

def TakeImages():
    """
    Capture an employee's face image using webcam and save it with embeddings.

    Validates inputs, checks for duplicate IDs, captures image on 's' key press,
    and saves both the image and its embedding.
    """
    os.makedirs(config.EMPLOYEE_DIR, exist_ok=True)

    # Initialize employee CSV if it doesn't exist
    if not os.path.exists(config.EMPLOYEE_CSV):
        with open(config.EMPLOYEE_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'img_path', 'embedding'])
        print(f"Created CSV file: {config.EMPLOYEE_CSV}")

    id_value = txt.get()
    name_value = txt2.get()

    if validate_input(id_value, name_value) and not check_id_exists(id_value):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error capturing frame")
                break
            cv2.imshow("Webcam", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                img_path = os.path.join(config.EMPLOYEE_DIR, f"{id_value}.jpg")
                cv2.imwrite(img_path, frame)
                print(f"Saved image: {img_path}")
                messagebox.showinfo("Success", f"Stored image path: {img_path}")

                embedding_img, _ = utils.preprocess(img_path, embedding_model)
                np.save(os.path.join(config.EMPLOYEE_EMBEDDING, f"{id_value}.npy"), embedding_img)
                break
            elif key == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()
    elif not validate_input(id_value, name_value):
        messagebox.showerror("Error", "Invalid ID or Name")
    else:
        messagebox.showerror("Error", "ID already exists in database")

def TrackImages():
    """
    Track and record employee attendance using face recognition.

    Captures video, processes frames for face recognition, verifies identity,
    and logs attendance in a CSV file. Displays results in the attendance table.
    """
    today = datetime.now()
    threshold = config.THRESHOLD
    os.makedirs(config.ATTENDANCE_REPORT, exist_ok=True)

    # Clear attendance table
    for item in tb.get_children():
        tb.delete(item)

    # Initialize today's attendance CSV
    csv_filename = today.strftime("%Y-%m-%d") + ".csv"
    csv_filepath = os.path.join(config.ATTENDANCE_REPORT, csv_filename)
    if not os.path.exists(csv_filepath):
        with open(csv_filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'date', 'time'])
        print(f"Created CSV file: {csv_filepath}")

    # Start video capture
    cap = cv2.VideoCapture(0)
    frame_id = 0
    frame_interval = 30
    people = set()
    next_id = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print(f"Error with frame {frame_id}")
            break
        frame_id += 1

        # Process frame periodically
        if frame_id % frame_interval == 0 and not processing:
            threading.Thread(target=async_preprocess, args=(frame.copy(), embedding_model)).start()

        # Verify and log attendance
        if embedding_result is not None and real_face:
            identity, distant = find.findPerson(embedding_result)
            scale = utils.distance_to_similarity(distant)
            if distant <= threshold and identity not in people:
                people.add(identity)
                checkin_date = today.strftime("%d-%m-%Y")
                checkin_time = today.strftime("%H:%M:%S")
                attendance = [str(next_id), identity, checkin_date, checkin_time]
                with open(csv_filepath, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(attendance)
                next_id += 1

            # Visualize results
            color = (0, 255, 0) if distant <= threshold else (0, 0, 255)
            cv2.putText(frame, f"Hello: {identity}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Match: {scale:.1f}%", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            if face_bb:
                cv2.rectangle(frame, (face_bb.x, face_bb.y), (face_bb.x + face_bb.w, face_bb.y + face_bb.h), color, 2)
        else:
            color = (0, 0, 255)
            cv2.putText(frame, "Fake Face", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.putText(frame, f"Match: {anti_face_conf:.1f}%", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            if face_bb:
                cv2.rectangle(frame, (face_bb.x, face_bb.y), (face_bb.x + face_bb.w, face_bb.y + face_bb.h), color, 2)

        cv2.imshow("img", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    load_attendance_to_table()
    cap.release()
    cv2.destroyAllWindows()

# Front End
window = ctk.CTk()
window.title("Face Recognition Based Attendance System")
window.geometry("1280x720")
window.resizable(True, True)
window.configure(background='#ffb8c6')

# Admin Window
admin_window = ctk.CTkToplevel(window)
admin_window.title("Đăng nhập Admin")
admin_window.geometry("300x500")
admin_window.withdraw()

ctk.CTkLabel(admin_window, text="Username:", width=20, height=1, text_color="black", bg_color="white", font=('times', 17, 'bold')).pack(pady=10)
entry_username = ctk.CTkEntry(admin_window, width=32, text_color="black", bg_color="#e1f2f2", font=('times', 15, 'bold'))
entry_username.pack()

ctk.CTkLabel(admin_window, text="Password:", width=20, height=1, text_color="black", bg_color="white", font=('times', 17, 'bold')).pack(pady=10)
entry_password = ctk.CTkEntry(admin_window, width=32, text_color="black", bg_color="#e1f2f2", font=('times', 15, 'bold'))
entry_password.pack()

# Create verify button without assigning command immediately
admin_window.verify_button = ctk.CTkButton(admin_window, text="Xác nhận")
admin_window.verify_button.pack(pady=20)

# Help menubar
menubar = tk.Menu(window)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Change Password!")
help_menu.add_command(label="Contact Us")
help_menu.add_separator()
help_menu.add_command(label="Exit")
menubar.add_cascade(label="Help", menu=help_menu)

# Add ABOUT label to menubar
def show_about():
    messagebox.showinfo("About", "Face Recognition Attendance System\nPowered by YOLO & VGGFace")
menubar.add_command(label="About", command=show_about)

# Attach menu to window
window.config(menu=menubar)

# Main window
message3 = ctk.CTkLabel(window, text="Face Recognition Based Attendance System", text_color="white", bg_color="#355454", width=60, height=1, font=('times', 29, 'bold'))
message3.place(x=10, y=10, relwidth=1)

# Frames
frame1 = ctk.CTkFrame(window, bg_color="white")
frame1.place(relx=0.11, rely=0.15, relwidth=0.39, relheight=0.80)

frame2 = ctk.CTkFrame(window, bg_color="white")
frame2.place(relx=0.51, rely=0.15, relwidth=0.39, relheight=0.80)

# Frame headers
fr_head1 = ctk.CTkLabel(frame1, text="Register New Employee", text_color="white", bg_color="black", font=('times', 17, 'bold'))
fr_head1.place(x=0, y=0, relwidth=1)

fr_head2 = ctk.CTkLabel(frame2, text="Mark Employee's attendance", text_color="white", bg_color="black", font=('times', 17, 'bold'))
fr_head2.place(x=0, y=0, relwidth=1)

# Registration frame
lbl = ctk.CTkLabel(frame1, text="Enter ID", width=20, height=1, text_color="black", bg_color="white", font=('times', 17, 'bold'))
lbl.place(x=0, y=55)

txt = ctk.CTkEntry(frame1, width=32, text_color="black", bg_color="#e1f2f2", font=('times', 15, 'bold'))
txt.place(x=55, y=88, relwidth=0.75)

lbl2 = ctk.CTkLabel(frame1, text="Enter Name", width=20, text_color="black", bg_color="white", font=('times', 17, 'bold'))
lbl2.place(x=0, y=140)

txt2 = ctk.CTkEntry(frame1, width=32, text_color="black", bg_color="#e1f2f2", font=('times', 15, 'bold'))
txt2.place(x=55, y=173, relwidth=0.75)

message0 = ctk.CTkLabel(frame1, text="Follow the steps...", bg_color="white", text_color="black", width=39, height=1, font=('times', 16, 'bold'))
message0.place(x=7, y=275)

message1 = ctk.CTkLabel(frame1, text="1)Take Images  ===> 2)Save Profile", bg_color="white", text_color="black", width=39, height=1, font=('times', 15, 'bold'))
message1.place(x=7, y=300)

message = ctk.CTkLabel(frame1, text="", bg_color="white", text_color="black", width=39, height=1, font=('times', 16, 'bold'))
message.place(x=7, y=500)

# Attendance frame
lbl3 = ctk.CTkLabel(frame2, text="Attendance Table", width=20, text_color="black", bg_color="white", height=1, font=('times', 17, 'bold'))
lbl3.place(x=100, y=115)

# Display total registrations
res = 0
if os.path.isfile(config.STUDENT_DETAILS_CSV):
    with open(config.STUDENT_DETAILS_CSV, 'r') as csvFile1:
        reader1 = csv.reader(csvFile1)
        for l in reader1:
            res = res + 1
    res = (res // 2) - 1
message.configure(text='Total Registrations : ' + str(res))

# Buttons
clearButton = ctk.CTkButton(frame1, text="Clear", command=clear, text_color="white", bg_color="#13059c", width=11, font=('times', 12, 'bold'))
clearButton.place(x=55, y=230, relwidth=0.29)

takeImg = ctk.CTkButton(frame1, text="Take Images", command=TakeImages, text_color="black", bg_color="#00aeff", width=34, height=1, font=('times', 16, 'bold'), state="disabled")
takeImg.place(x=30, y=350, relwidth=0.89)

trainImg = ctk.CTkButton(frame1, text="Save Profile", text_color="black", command=SaveProfile, bg_color="#00aeff", width=34, height=1, font=('times', 16, 'bold'), state="disabled")
trainImg.place(x=30, y=430, relwidth=0.89)

trackImg = ctk.CTkButton(frame2, text="Take Attendance", command=TrackImages, text_color="black", bg_color="#00aeff", height=1, font=('times', 16, 'bold'), state="disabled")
trackImg.place(x=30, y=60, relwidth=0.89)

quitWindow = ctk.CTkButton(frame2, text="Quit", command=window.destroy, text_color="white", bg_color="#13059c", width=35, height=1, font=('times', 16, 'bold'))
quitWindow.place(x=30, y=450, relwidth=0.89)

# Attendance table
style = ttk.Style()
style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))  # Modify the font of the body
style.configure("mystyle.Treeview.Heading", font=('times', 13, 'bold'))  # Modify the font of the headings
style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders
tb = ttk.Treeview(frame2, height=13, columns=('name', 'date', 'time'), style="mystyle.Treeview")
tb.column('#0', width=82)
tb.column('name', width=130)
tb.column('date', width=133)
tb.column('time', width=133)
tb.grid(row=2, column=0, padx=(0, 0), pady=(150, 0), columnspan=4)
tb.heading('#0', text='ID')
tb.heading('name', text='NAME')
tb.heading('date', text='DATE')
tb.heading('time', text='TIME')

# Scrollbar
scroll = ttk.Scrollbar(frame2, orient='vertical', command=tb.yview)
scroll.grid(row=2, column=4, padx=(0, 100), pady=(150, 0), sticky='ns')
tb.configure(yscrollcommand=scroll.set)

# Closing lines
window.protocol("WM_DELETE_WINDOW")
threading.Thread(target=load_models_async, daemon=True).start()
window.mainloop()