import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import csv
from module import config
from module.utils import detect_face_yolo_with_box, resize_and_pad
from model.classification_model import FacialRecognitionModel
from module.find import findPerson

# Khởi tạo model embedding VGGFace
face_model = FacialRecognitionModel()
embedding_model = face_model.get_embedding_model()

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("1280x720")
app.title("Face ID Demo")

# Sidebar
sidebar = ctk.CTkFrame(app, width=180)
sidebar.pack(side="left", fill="y")
ctk.CTkLabel(sidebar, text="MENU", font=("Arial", 18, "bold")).pack(pady=30)

main_content = ctk.CTkFrame(app)
main_content.pack(side="left", fill="both", expand=True)

# --- Frame 1: Camera ---
frame1 = ctk.CTkFrame(main_content)
frame1.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(frame1, text="Camera nhận diện", font=("Arial", 16, "bold")).pack(pady=10)
camera_canvas = ctk.CTkCanvas(frame1, width=960, height=540, bg="#dfe6e9")
camera_canvas.pack(pady=20)
camera_result_label = ctk.CTkLabel(frame1, text="", font=("Arial", 14))
camera_result_label.pack(pady=10)

# --- Frame 2: Upload nhận diện ---
frame2 = ctk.CTkFrame(main_content)
frame2.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(frame2, text="Nhận diện từ ảnh upload", font=("Arial", 16, "bold")).pack(pady=10)
upload_canvas = ctk.CTkCanvas(frame2, width=960, height=540, bg="#dfe6e9")
upload_canvas.pack(pady=20)
upload_result_label = ctk.CTkLabel(frame2, text="", font=("Arial", 14))
upload_result_label.pack(pady=10)

def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return
    img = cv2.imread(file_path)
    if img is None:
        upload_result_label.configure(text="Không thể đọc ảnh!")
        return
    # Lưu ảnh gốc vào attendance_face/Upload
    upload_face_dir = os.path.join("dataset", "attendance_face", "Upload")
    os.makedirs(upload_face_dir, exist_ok=True)
    upload_img_name = os.path.basename(file_path)
    upload_img_path = os.path.join(upload_face_dir, upload_img_name)
    cv2.imwrite(upload_img_path, img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces, boxes = detect_face_yolo_with_box(img_rgb)
    names = []
    for i, (x1, y1, x2, y2) in enumerate(boxes):
        face_crop = img_rgb[y1:y2, x1:x2]
        try:
            face_resized = resize_and_pad(face_crop, (224, 224))
            # Lưu crop vào face_crop/Upload (scale đúng tỉ lệ, không vỡ)
            crop_dir = os.path.join("dataset", "face_crop", "Upload")
            os.makedirs(crop_dir, exist_ok=True)
            crop_img_name = f"{os.path.splitext(upload_img_name)[0]}_face{i}.jpg"
            h_fc, w_fc = face_crop.shape[:2]
            crop_canvas_w, crop_canvas_h = 960, 540
            scale_fc = min(crop_canvas_w / w_fc, crop_canvas_h / h_fc)
            new_wfc, new_hfc = int(w_fc * scale_fc), int(h_fc * scale_fc)
            face_crop_resized = resize_and_pad(face_crop, (224, 224))
            crop_img_path = os.path.join(crop_dir, crop_img_name)
            cv2.imwrite(crop_img_path, cv2.cvtColor(face_crop_resized, cv2.COLOR_RGB2BGR))
            # Sinh embedding và lưu vào attendance_embedding/Upload
            emb_dir = os.path.join("dataset", "attendance_embedding", "Upload")
            os.makedirs(emb_dir, exist_ok=True)
            emb_name = f"{os.path.splitext(upload_img_name)[0]}_face{i}.npy"
            emb_path = os.path.join(emb_dir, emb_name)
            embedding = embedding_model.predict(np.expand_dims(face_resized, axis=0))[0]
            np.save(emb_path, embedding)
            # So sánh với toàn bộ embedding ngoài attendance_embedding/Upload
            best_name = "unknown"
            min_dist = float('inf')
            for root, dirs, files in os.walk(os.path.join("dataset", "attendance_embedding")):
                if os.path.basename(root) == "Upload":
                    continue
                for file in files:
                    if not file.endswith('.npy'):
                        continue
                    compare_emb = np.load(os.path.join(root, file))
                    dist = np.linalg.norm(embedding - compare_emb)
                    if dist < min_dist:
                        min_dist = dist
                        person_folder = os.path.basename(os.path.dirname(os.path.join(root, file)))
                        best_name = person_folder
            name = best_name
        except Exception as e:
            name = "error"
        names.append(name)
        cv2.rectangle(img_rgb, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img_rgb, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
    # Scale ảnh vừa canvas, giữ nguyên tỉ lệ
    h_img, w_img = img_rgb.shape[:2]
    canvas_w, canvas_h = 960, 540
    scale = min(canvas_w / w_img, canvas_h / h_img)
    new_w, new_h = int(w_img * scale), int(h_img * scale)
    img_resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
    img_pil = Image.fromarray(img_resized)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    upload_canvas.delete("all")
    upload_canvas.imgtk = imgtk
    upload_canvas.create_image((canvas_w-new_w)//2, (canvas_h-new_h)//2, anchor="nw", image=imgtk)
    if len(boxes) > 0:
        upload_result_label.configure(text=f"Đã phát hiện {len(boxes)} khuôn mặt: {', '.join(names)}")
    else:
        upload_result_label.configure(text="Không phát hiện khuôn mặt")

# Đảm bảo nút upload nhận diện luôn hiển thị sau khi định nghĩa hàm
ctk.CTkButton(frame2, text="Chọn ảnh để nhận diện", command=upload_image).pack(pady=5)

# --- Frame 3: Thêm khuôn mặt mới ---
frame3 = ctk.CTkFrame(main_content)
frame3.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(frame3, text="Thêm khuôn mặt mới", font=("Arial", 16, "bold")).pack(pady=10)

entry_name = ctk.CTkEntry(frame3, placeholder_text="Nhập tên")
entry_name.pack(pady=5)
addface_canvas = ctk.CTkCanvas(frame3, width=960, height=540, bg="#dfe6e9")
addface_canvas.pack(pady=20)
addface_img_path = [None]

def choose_face_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return
    img = cv2.imread(file_path)
    if img is None:
        messagebox.showerror("Lỗi", "Không thể đọc ảnh!")
        return
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # Scale đúng tỉ lệ, không vỡ ảnh
    h_img, w_img = img.shape[:2]
    canvas_w, canvas_h = 960, 540
    scale = min(canvas_w / w_img, canvas_h / h_img)
    new_w, new_h = int(w_img * scale), int(h_img * scale)
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    img_pil = Image.fromarray(img_resized)
    imgtk = ImageTk.PhotoImage(image=img_pil)
    addface_canvas.delete("all")
    addface_canvas.imgtk = imgtk
    addface_canvas.create_image((canvas_w-new_w)//2, (canvas_h-new_h)//2, anchor="nw", image=imgtk)
    addface_img_path[0] = file_path

ctk.CTkButton(frame3, text="Chọn ảnh khuôn mặt", command=choose_face_image).pack(pady=5)

def save_new_face():
    name_val = entry_name.get().strip()
    img_path = addface_img_path[0]
    if not name_val or not img_path:
        messagebox.showerror("Lỗi", "Vui lòng nhập tên và chọn ảnh!")
        return
    # Không sinh id, chỉ dùng tên
    person_dir = os.path.join("dataset", "attendance_face", name_val)
    os.makedirs(person_dir, exist_ok=True)
    # Lưu ảnh gốc vào attendance_face/<tên>/<tên>.jpg
    face_img_path = os.path.join(person_dir, f"{name_val}.jpg")
    img = cv2.imread(img_path)
    if img is None:
        messagebox.showerror("Lỗi", "Không thể đọc ảnh!")
        return
    cv2.imwrite(face_img_path, img)  # Lưu ảnh gốc
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = crop_face_yolo(img_rgb)
    if not faces:
        messagebox.showerror("Lỗi", "Không phát hiện khuôn mặt!")
        return
    face_img = faces[0]
    # Lưu crop vào face_crop/<tên>/<tên>.jpg
    crop_person_dir = os.path.join("dataset", "face_crop", name_val)
    os.makedirs(crop_person_dir, exist_ok=True)
    crop_face_img_path = os.path.join(crop_person_dir, f"{name_val}.jpg")
    cv2.imwrite(crop_face_img_path, cv2.cvtColor(face_img, cv2.COLOR_RGB2BGR))
    # Sinh embedding và lưu vào attendance_embedding/<tên>/<tên>.npy
    emb_person_dir = os.path.join("dataset", "attendance_embedding", name_val)
    os.makedirs(emb_person_dir, exist_ok=True)
    emb_path = os.path.join(emb_person_dir, f"{name_val}.npy")
    embedding = save_face_embedding(face_img, embedding_model, emb_path)
    exists = False
    with open(config.EMPLOYEE_CSV, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[3] == emb_path:
                exists = True
                break
    if not exists:
        with open(config.EMPLOYEE_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name_val, name_val, face_img_path, emb_path])
    messagebox.showinfo("Thành công", f"Đã lưu khuôn mặt mới: {face_img_path}\nĐã sinh embedding và ghi vào csv!")
    entry_name.delete(0, 'end')
    addface_canvas.delete("all")
    addface_img_path[0] = None

ctk.CTkButton(frame3, text="Lưu khuôn mặt mới", command=save_new_face).pack(pady=10)

def crop_face_yolo(img):
    from module.utils import detect_face_yolo, resize_and_pad
    faces = detect_face_yolo(img)
    if not faces:
        return []
    return [resize_and_pad(face, (224, 224)) for face in faces]

def save_face_embedding(face_img, embedding_model, emb_path):
    embedding = embedding_model.predict(face_img.reshape(1, 224, 224, 3))[0]
    np.save(emb_path, embedding)
    return embedding

# --- Frame 4: Danh sách người ---
frame4 = ctk.CTkFrame(main_content)
frame4.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(frame4, text="Danh sách người có thể nhận diện", font=("Arial", 16, "bold")).pack(pady=10)

# Scrollable frame cho bảng danh sách
scrollable = ctk.CTkScrollableFrame(frame4, width=960, height=540)
scrollable.pack(pady=20, fill="both", expand=True)

header = ["Tên", "Tên hiển thị", "Ảnh", "Embedding"]
for i, col in enumerate(header):
    ctk.CTkLabel(scrollable, text=col, font=("Arial", 14, "bold"), width=220, anchor="w").grid(row=0, column=i, padx=2, pady=2)

def show_people_list():
    # Xóa các dòng cũ
    for widget in scrollable.winfo_children():
        if int(widget.grid_info().get('row', 0)) > 0:
            widget.destroy()
    # Đọc data.csv
    try:
        with open(config.EMPLOYEE_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row_idx, row in enumerate(reader, start=1):
                if len(row) >= 4:
                    for col_idx, val in enumerate(row[:4]):
                        ctk.CTkLabel(scrollable, text=val, font=("Arial", 13), width=220, anchor="w").grid(row=row_idx, column=col_idx, padx=2, pady=2)
    except Exception as e:
        ctk.CTkLabel(scrollable, text=f"Lỗi: {e}", font=("Arial", 13), anchor="w").grid(row=1, column=0, columnspan=4)
    frame4.tkraise()

# --- Sidebar button logic ---
def show_camera():
    frame1.tkraise()
def show_upload():
    frame2.tkraise()
def show_addface():
    frame3.tkraise()

def show_people():
    show_people_list()

ctk.CTkButton(sidebar, text="Camera nhận diện", command=show_camera).pack(pady=10, fill="x", padx=20)
ctk.CTkButton(sidebar, text="Upload ảnh nhận diện", command=show_upload).pack(pady=10, fill="x", padx=20)
ctk.CTkButton(sidebar, text="Thêm khuôn mặt mới", command=show_addface).pack(pady=10, fill="x", padx=20)
ctk.CTkButton(sidebar, text="Danh sách người", command=show_people).pack(pady=10, fill="x", padx=20)

# Show camera frame by default
frame1.tkraise()
app.mainloop()