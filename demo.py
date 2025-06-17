import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
from model.classification_model import FacialRecognitionModel
from module import config, utils, find

# Workaround cho lỗi filedialog trên macOS
filedialog_root = tk.Tk()
filedialog_root.withdraw()

ctk.set_appearance_mode("system")  # default mode

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Face Recognition App")
        self.geometry("1280x720")
        self.minsize(800, 500)
        self.resizable(True, True)
        self.configure(bg="#f5f6fa")
        self.sidebar_width = 220
        self.cap = None
        self.camera_running = False
        # Load model nhận diện
        self.face_model = FacialRecognitionModel()
        self.embedding_model = self.face_model.get_embedding_model()
        # Sử dụng grid cho layout chính
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self._create_sidebar()
        self._create_main_frames()
        self._show_frame(1)
        self.bind("<Configure>", self.on_resize)

    def _get_sidebar_color(self):
        mode = ctk.get_appearance_mode().lower()
        if mode == "dark":
            return "#18181b"  # shadcn dark sidebar
        else:
            return "#f5f6fa"  # shadcn light sidebar

    def _get_button_style(self):
        mode = ctk.get_appearance_mode().lower()
        if mode == "dark":
            return {
                "height": 36,
                "font": ("Arial", 15, "bold"),
                "text_color": "#18181b",
                "corner_radius": 6,
                "fg_color": "#fff",
                "hover_color": "#e4e4e7",
                "border_color": "#27272a",
                "border_width": 1,
                "anchor": "center"
            }
        else:
            return {
                "height": 36,
                "font": ("Arial", 15, "bold"),
                "text_color": "#fff",
                "corner_radius": 6,
                "fg_color": "#18181b",
                "hover_color": "#27272a",
                "border_color": "#d1d5db",
                "border_width": 1,
                "anchor": "center"
            }

    def _create_sidebar(self):
        sidebar_color = self._get_sidebar_color()
        self.sidebar = ctk.CTkFrame(
            self,
            width=self.sidebar_width,
            corner_radius=8,
            fg_color=sidebar_color,
            border_width=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(5, weight=1)
        mode = ctk.get_appearance_mode().lower()
        label_color = "#fff" if mode == "dark" else "#18181b"
        ctk.CTkLabel(self.sidebar, text="MENU", text_color=label_color, font=("Arial", 22, "bold"), fg_color=sidebar_color).grid(row=0, column=0, padx=20, pady=(24, 32))
        btn_style = self._get_button_style()
        self.btn_frame1 = ctk.CTkButton(self.sidebar, text="Upload Ảnh", command=lambda: self._show_frame(1), **btn_style, width=180)
        self.btn_frame1.grid(row=1, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.btn_frame2 = ctk.CTkButton(self.sidebar, text="Camera", command=lambda: self._show_frame(2), **btn_style, width=180)
        self.btn_frame2.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.btn_add_person = ctk.CTkButton(self.sidebar, text="Thêm người nhận diện", command=lambda: self._show_frame(3), **btn_style, width=180)
        self.btn_add_person.grid(row=3, column=0, padx=20, pady=(0, 16), sticky="ew")
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode().lower())
        self.theme_switch = ctk.CTkOptionMenu(self.sidebar, values=["dark", "light", "system"], variable=self.theme_var, command=self._change_theme)
        self.theme_switch.grid(row=6, column=0, padx=20, pady=18, sticky="s")
        ctk.CTkLabel(self.sidebar, text="Giao diện", text_color="#a1a1aa" if mode=="dark" else "#27272a", font=("Arial", 13), fg_color=sidebar_color).grid(row=7, column=0, pady=(0, 0), padx=20, sticky="s")

    def _refresh_sidebar(self):
        # Xoá sidebar cũ và tạo lại khi đổi theme
        if hasattr(self, 'sidebar') and self.sidebar.winfo_exists():
            self.sidebar.destroy()
        self._create_sidebar()

    def _change_theme(self, mode):
        # Đổi theme chính xác theo dark, light, system và refresh sidebar
        if mode.lower() == "dark":
            ctk.set_appearance_mode("dark")
        elif mode.lower() == "light":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
        self._refresh_sidebar()

    def _create_main_frames(self):
        self.main_content = ctk.CTkFrame(self, fg_color="white", corner_radius=5, border_width=2, border_color="#d1d5db")
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.frames = {}
        # Frame 1: Upload ảnh
        frame1 = ctk.CTkFrame(self.main_content, fg_color="white")
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)
        container1 = ctk.CTkFrame(frame1, fg_color="white")
        container1.grid(row=0, column=0, sticky="nsew", padx=60, pady=40)
        container1.grid_rowconfigure((0,1,2,3,4), weight=1)
        container1.grid_columnconfigure(0, weight=1)
        container1.configure(width=800, height=600)
        label1 = ctk.CTkLabel(container1, text="Nhận diện từ ảnh upload", font=("Arial", 22, "bold"), text_color="#18181b")
        label1.grid(row=0, column=0, pady=(10, 5), sticky="nsew")
        self.upload_preview_frame = ctk.CTkFrame(container1, fg_color="#f4f4f5", corner_radius=12, border_color="#d1d5db", border_width=2)
        self.upload_preview_frame.grid(row=1, column=0, pady=5, sticky="nsew")
        self.upload_preview_frame.grid_rowconfigure(0, weight=1)
        self.upload_preview_frame.grid_columnconfigure(0, weight=1)
        self.upload_preview_canvas = tk.Canvas(self.upload_preview_frame, width=320, height=220, bg="#e4e4e7", highlightthickness=0)
        self.upload_preview_canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.upload_result_label = ctk.CTkLabel(container1, text="", font=("Arial", 16), text_color="#18181b")
        self.upload_result_label.grid(row=2, column=0, pady=5, sticky="nsew")
        btn_style = self._get_button_style()
        self.upload_btn = ctk.CTkButton(container1, text="Chọn ảnh để nhận diện", command=self.upload_image, **btn_style, width=220)
        self.upload_btn.grid(row=3, column=0, pady=5, sticky="nsew")
        self.save_btn = ctk.CTkButton(container1, text="Lưu ảnh", command=self.save_uploaded_image, **btn_style, width=220)
        self.save_btn.grid(row=4, column=0, pady=(5, 10), sticky="nsew")
        self.frames[1] = frame1
        frame1.grid(row=0, column=0, sticky="nsew")
        frame1.grid_columnconfigure(0, weight=1)
        # Frame 2: Camera
        frame2 = ctk.CTkFrame(self.main_content, fg_color="white")
        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)
        container2 = ctk.CTkFrame(frame2, fg_color="white")
        container2.grid(row=0, column=0, sticky="nsew", padx=60, pady=40)
        container2.grid_rowconfigure((0,1,2,3), weight=1)
        container2.grid_columnconfigure(0, weight=1)
        container2.configure(width=800, height=600)
        label2 = ctk.CTkLabel(container2, text="Nhận diện từ Camera", font=("Arial", 22, "bold"), text_color="#18181b")
        label2.grid(row=0, column=0, pady=(10, 5), sticky="nsew")
        self.camera_canvas = tk.Canvas(container2, width=800, height=500, bg="#e4e4e7", highlightthickness=0)
        self.camera_canvas.grid(row=1, column=0, pady=5, sticky="nsew")
        self.camera_result_label = ctk.CTkLabel(container2, text="", font=("Arial", 16), text_color="#18181b")
        self.camera_result_label.grid(row=2, column=0, pady=5, sticky="nsew")
        btn_frame = ctk.CTkFrame(container2, fg_color="white")
        btn_frame.grid(row=3, column=0, pady=(10, 10), sticky="nsew")
        btn_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(btn_frame, text="Bắt đầu Camera", command=self.start_camera, **btn_style, width=160).grid(row=0, column=0, padx=8, sticky="nsew")
        ctk.CTkButton(btn_frame, text="Dừng Camera", command=self.stop_camera, **btn_style, width=160).grid(row=0, column=1, padx=8, sticky="nsew")
        self.frames[2] = frame2
        frame2.grid(row=0, column=0, sticky="nsew")
        frame2.grid_columnconfigure(0, weight=1)
        # Frame 3: Thêm người nhận diện
        frame3 = ctk.CTkFrame(self.main_content, fg_color="white")
        frame3.grid_rowconfigure(0, weight=1)
        frame3.grid_columnconfigure(0, weight=1)
        container3 = ctk.CTkFrame(frame3, fg_color="white")
        container3.grid(row=0, column=0, sticky="nsew", padx=60, pady=40)
        container3.grid_rowconfigure((0,1,2,3,4,5,6), weight=1)
        container3.grid_columnconfigure(0, weight=1)
        container3.configure(width=800, height=600)
        label3 = ctk.CTkLabel(container3, text="Thêm người nhận diện mới", font=("Arial", 22, "bold"), text_color="#18181b")
        label3.grid(row=0, column=0, pady=(10, 5), sticky="nsew")
        self.add_img_path_var = tk.StringVar()
        self.add_name_var = tk.StringVar()
        self.add_status_var = tk.StringVar()
        ctk.CTkButton(container3, text="Chọn ảnh khuôn mặt", command=self.choose_add_img, **btn_style, width=220).grid(row=1, column=0, pady=5, sticky="nsew")
        ctk.CTkLabel(container3, textvariable=self.add_img_path_var, font=("Arial", 12), text_color="#18181b").grid(row=2, column=0, pady=5, sticky="nsew")
        ctk.CTkLabel(container3, text="Nhập tên người", font=("Arial", 15), text_color="#18181b").grid(row=3, column=0, pady=5, sticky="nsew")
        ctk.CTkEntry(container3, textvariable=self.add_name_var, font=("Arial", 13), width=220).grid(row=4, column=0, pady=5, sticky="nsew")
        ctk.CTkLabel(container3, textvariable=self.add_status_var, font=("Arial", 12), text_color="#ef4444").grid(row=5, column=0, pady=5, sticky="nsew")
        ctk.CTkButton(container3, text="Thêm", command=self.add_person_from_frame, **btn_style, width=220).grid(row=6, column=0, pady=(5, 10), sticky="nsew")
        self.frames[3] = frame3
        frame3.grid(row=0, column=0, sticky="nsew")
        frame3.grid_columnconfigure(0, weight=1)

    def on_resize(self, event):
        # Debounce resize để tránh lặp callback vô hạn
        if hasattr(self, '_resize_after_id'):
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(200, self._do_resize, event)

    def _do_resize(self, event):
        # Chỉ update kích thước canvas hoặc các widget nhỏ, không gọi lại pack/place các frame lớn
        new_width = event.width - self.sidebar_width - 30
        new_height = event.height - 30
        # Cập nhật kích thước canvas preview nếu cần
        if hasattr(self, 'upload_preview_canvas'):
            self.upload_preview_canvas.config(width=300, height=200)
        if hasattr(self, 'camera_canvas'):
            self.camera_canvas.config(width=800, height=500)
        # Gọi update_layout để đảm bảo main_content fill hết phần bên phải
        self.update_layout()

    def update_layout(self):
        # Main content fill toàn bộ phần còn lại bên phải sidebar
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        self.main_content.place_configure(x=self.sidebar_width+10, y=5)
        self.sidebar.lift()
        self.sidebar.update()
        self.main_content.update()

    def _show_frame(self, frame_number):
        # Ẩn tất cả các frame và chỉ hiện frame được chọn
        for frame in self.frames.values():
            frame.grid_remove()
        self.frames[frame_number].grid(row=0, column=0, sticky="nsew")

    def upload_image(self):
        # Hàm xử lý sự kiện khi nhấn nút "Chọn ảnh để nhận diện"
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")], parent=filedialog_root)
        if file_path:
            # Hiển thị ảnh lên giao diện
            img = Image.open(file_path)
            img.thumbnail((300, 200))
            self.uploaded_pil_image = img.copy()  # Lưu lại ảnh PIL để dùng khi lưu
            self.upload_preview_canvas.image = ImageTk.PhotoImage(img)
            self.upload_preview_canvas.create_image(0, 0, anchor="nw", image=self.upload_preview_canvas.image)
            # Nhận diện khuôn mặt trong ảnh
            self.recognize_faces_in_image(file_path)

    def recognize_faces_in_image(self, file_path):
        # Hàm nhận diện khuôn mặt trong ảnh upload
        img = cv2.imread(file_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Giả lập kết quả nhận diện (để demo)
        result_text = "Kết quả nhận diện:\n"
        for i in range(3):  # Giả lập 3 khuôn mặt được nhận diện
            result_text += f"Khuôn mặt {i+1}: Người A\n"
        self.upload_result_label.configure(text=result_text)

    def save_uploaded_image(self):
        # Hàm lưu ảnh đã upload về máy
        if hasattr(self, 'uploaded_pil_image'):
            file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")], parent=filedialog_root)
            if file_path:
                # Lưu ảnh PIL
                ext = file_path.split('.')[-1].lower()
                fmt = 'PNG' if ext == 'png' else 'JPEG'
                self.uploaded_pil_image.save(file_path, format=fmt)
                tk.messagebox.showinfo("Thông báo", "Ảnh đã được lưu thành công!", parent=filedialog_root)
                # Reset preview và label
                self.upload_preview_canvas.delete("all")
                self.upload_result_label.configure(text="")
        else:
            tk.messagebox.showwarning("Cảnh báo", "Không có ảnh nào để lưu!", parent=filedialog_root)

    def choose_add_img(self):
        # Hàm xử lý sự kiện khi nhấn nút "Chọn ảnh khuôn mặt" trong frame thêm người nhận diện
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")], parent=filedialog_root)
        if file_path:
            self.add_img_path_var.set(file_path)
            # Hiển thị ảnh lên giao diện (nếu cần thiết)
            img = Image.open(file_path)
            img.thumbnail((100, 100))
            self.add_img_preview = ImageTk.PhotoImage(img)
            # Cần tạo một label hoặc canvas để hiển thị ảnh preview
            if not hasattr(self, 'add_img_label'):
                self.add_img_label = ctk.CTkLabel(self.frames[3], text="", fg_color="white")
                self.add_img_label.grid(row=1, column=1, padx=10, pady=10)
            self.add_img_label.configure(image=self.add_img_preview)
            self.add_img_label.image = self.add_img_preview  # Giữ tham chiếu đến ảnh

    def add_person_from_frame(self):
        # Hàm thêm người nhận diện mới từ frame thêm người nhận diện
        name = self.add_name_var.get()
        img_path = self.add_img_path_var.get()
        if not name or not img_path:
            self.add_status_var.set("Vui lòng nhập tên và chọn ảnh khuôn mặt.")
            return
        # Lưu thông tin người nhận diện mới vào model
        # self.face_model.add_person(name, img_path)  # Giả sử có hàm này trong model
        self.add_status_var.set(f"Đã thêm người nhận diện: {name}")
        self.add_name_var.set("")
        self.add_img_path_var.set("")
        if hasattr(self, 'add_img_label'):
            self.add_img_label.configure(image="")
            self.add_img_label.image = None

    def start_camera(self):
        # Bắt đầu phát hình ảnh từ camera
        if not self.camera_running:
            self.cap = cv2.VideoCapture(0)
            self.camera_running = True
            self._update_camera_feed()

    def _update_camera_feed(self):
        # Cập nhật hình ảnh từ camera lên giao diện
        if self.camera_running and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Chuyển đổi màu sắc từ BGR sang RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Chuyển đổi định dạng ảnh để hiển thị trên Tkinter
                img = Image.fromarray(frame_rgb)
                img = img.resize((800, 500), Image.ANTIALIAS)
                self.camera_canvas.image = ImageTk.PhotoImage(img)
                self.camera_canvas.create_image(0, 0, anchor="nw", image=self.camera_canvas.image)
            self.after(10, self._update_camera_feed)

    def stop_camera(self):
        # Dừng phát hình ảnh từ camera
        self.camera_running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.camera_canvas.delete("all")

if __name__ == "__main__":
    app = App()
    app.mainloop()
