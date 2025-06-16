# Face Recognition Attendance System

## Mô tả
Hệ thống điểm danh sử dụng nhận diện khuôn mặt với giao diện CustomTkinter và mô hình phát hiện khuôn mặt YOLO.

## Yêu cầu
- Python 3.9
- Xem file `requirements.txt` để cài đặt các thư viện cần thiết.

## Cài đặt
```bash
pip install -r requirements.txt
```

## Cấu trúc thư mục
- `app.py`: Giao diện chính
- `model/`: Chứa các mô hình
- `module/`: Chứa các module tiện ích
- `images/`: Lưu ảnh nhân viên
- `checkpoint/`: Lưu checkpoint mô hình
- `data.csv`: Lưu thông tin nhân viên

## Chạy chương trình
```bash
python app.py
```

## Lưu ý
- Đường dẫn dữ liệu, checkpoint, ảnh... đều nằm trong thư mục dự án.
- Nếu chưa có dữ liệu, hệ thống sẽ tự tạo file `data.csv`.
- Để sử dụng YOLO, cần tải trọng số phù hợp (xem tài liệu YOLOv8).
