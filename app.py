import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import threading
import time
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageTk
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

# === NEW: Sidebar and Main Layout ===
window = ctk.CTk()
window.title("Face Recognition System")
window.geometry("1280x720")
window.resizable(True, True)  # Cho phép phóng to/thu nhỏ
window.configure(bg="#f5f6fa")

# === Center window on screen ===
def center_window(win, width=1280, height=720):
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

center_window(window, 1280, 720)
window.lift()
window.focus_force()
window.attributes('-topmost', True)
window.after(100, lambda: window.attributes('-topmost', False))

# Sidebar
sidebar = ctk.CTkFrame(window, width=200, fg_color="#222f3e")
sidebar.pack(side="left", fill="y")
ctk.CTkLabel(sidebar, text="MENU", text_color="white", font=("Arial", 20, "bold"), fg_color="#222f3e").pack(pady=30)

# Camera Button
def show_camera():
    frame1.tkraise()

def show_upload():
    frame2.tkraise()

btn_camera = ctk.CTkButton(sidebar, text="Camera nhận diện", command=show_camera, font=("Arial", 16), fg_color="#10ac84", text_color="white")
btn_camera.pack(pady=20, fill="x", padx=20)

btn_upload = ctk.CTkButton(sidebar, text="Upload ảnh nhận diện", command=show_upload, font=("Arial", 16), fg_color="#576574", text_color="white")
btn_upload.pack(pady=20, fill="x", padx=20)

# Main content area
main_content = ctk.CTkFrame(window, fg_color="#f5f6fa")
main_content.pack(side="left", fill="both", expand=True)

# Frame 1: Camera nhận diện
frame1 = ctk.CTkFrame(main_content, fg_color="white")
frame1.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(frame1, text="Camera nhận diện khuôn mặt", font=("Arial", 18, "bold"), text_color="#222f3e").pack(pady=10)

camera_canvas = tk.Canvas(frame1, width=800, height=500, bg="#dfe6e9")
camera_canvas.pack(pady=20)

camera_result_label = ctk.CTkLabel(frame1, text="", font=("Arial", 16), text_color="#222f3e")
camera_result_label.pack(pady=10)

# Frame 2: Upload ảnh nhận diện
frame2 = ctk.CTkFrame(main_content, fg_color="white")
frame2.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(frame2, text="Nhận diện từ ảnh upload", font=("Arial", 18, "bold"), text_color="#222f3e").pack(pady=10)

upload_canvas = tk.Canvas(frame2, width=800, height=500, bg="#dfe6e9")
upload_canvas.pack(pady=20)

upload_result_label = ctk.CTkLabel(frame2, text="", font=("Arial", 16), text_color="#222f3e")
upload_result_label.pack(pady=10)

# === Camera logic ===
face_model = FacialRecognitionModel()
embedding_model = face_model.get_embedding_model()

cap = None
camera_running = False

def start_camera():
    global cap, camera_running
    if cap is None:
        cap = cv2.VideoCapture(0)
    camera_running = True
    update_camera()

def stop_camera():
    global cap, camera_running
    camera_running = False
    if cap:
        cap.release()
        cap = None
    camera_canvas.delete("all")
    camera_result_label.configure(text="")

def update_camera():
    if not camera_running or cap is None:
        return
    ret, frame = cap.read()
    if not ret:
        stop_camera()
        return
    # Detect face
    faces = utils.detect_face_yolo(frame)
    name = "Unknown"
    if faces:
        face_img = cv2.resize(faces[0], (224, 224))
        embedding_img = embedding_model.predict(np.expand_dims(face_img, axis=0))[0]
        identity, dist = find.findPerson(embedding_img)
        name = identity if dist < config.THRESHOLD else "Unknown"
        # Draw bounding box
        for f in faces:
            h, w = frame.shape[:2]
            x, y, x2, y2 = 0, 0, w, h
            if hasattr(f, 'shape') and len(f.shape) == 3:
                # Find where this face is in the frame
                res = cv2.matchTemplate(frame, f, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                x, y = max_loc
                x2, y2 = x + f.shape[1], y + f.shape[0]
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    # Show frame
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    imgtk = ImageTk.PhotoImage(image=img)
    camera_canvas.imgtk = imgtk
    camera_canvas.create_image(0, 0, anchor="nw", image=imgtk)
    camera_result_label.configure(text=f"Kết quả: {name}")
    if camera_running:
        camera_canvas.after(30, update_camera)

ctk.CTkButton(frame1, text="Bắt đầu Camera", command=start_camera, fg_color="#10ac84", text_color="white").pack(side="left", padx=40, pady=10)
ctk.CTkButton(frame1, text="Dừng Camera", command=stop_camera, fg_color="#ee5253", text_color="white").pack(side="left", padx=40, pady=10)

# === Upload logic ===
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return
    img = cv2.imread(file_path)
    if img is None:
        upload_result_label.configure(text="Không thể đọc ảnh!")
        return
    faces = utils.detect_face_yolo(img)
    name = "Unknown"
    if faces:
        face_img = cv2.resize(faces[0], (224, 224))
        embedding_img = embedding_model.predict(np.expand_dims(face_img, axis=0))[0]
        identity, dist = find.findPerson(embedding_img)
        name = identity if dist < config.THRESHOLD else "Unknown"
        # Draw bounding box
        for f in faces:
            h, w = img.shape[:2]
            x, y, x2, y2 = 0, 0, w, h
            if hasattr(f, 'shape') and len(f.shape) == 3:
                res = cv2.matchTemplate(img, f, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                x, y = max_loc
                x2, y2 = x + f.shape[1], y + f.shape[0]
            cv2.rectangle(img, (x, y), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(rgb)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    upload_canvas.imgtk = imgtk
    upload_canvas.create_image(0, 0, anchor="nw", image=imgtk)
    upload_result_label.configure(text=f"Kết quả: {name}")

ctk.CTkButton(frame2, text="Chọn ảnh để nhận diện", command=upload_image, fg_color="#10ac84", text_color="white").pack(pady=10)

# Show camera frame by default
frame1.tkraise()
window.lift()
window.focus_force()
window.mainloop()