# Hướng dẫn pipeline xử lý dữ liệu gốc cho nhận diện khuôn mặt

1. Chạy cắt mặt từ ảnh gốc:
```bash
python process/process_crop_face.py
```
- Ảnh mặt sẽ được lưu vào `dataset/face_crop/<người>/`

2. Chia dữ liệu train/val từ ảnh mặt đã cắt:
```bash
python process/process_split_train_val.py
```
- Ảnh train/val sẽ nằm ở `dataset/train/<người>/` và `dataset/val/<người>/`

3. Sinh embedding cho toàn bộ ảnh mặt:
```bash
python process/process_embedding.py
```
- Embedding sẽ được lưu vào `images/attendance_embedding/<người>/`

---

- Đảm bảo các module YOLO, VGGFace, config đã hoạt động đúng.
- Nếu cần mã hóa lại cho ảnh mới, chỉ cần chạy lại các script trên.
- Có thể mở rộng để sinh file csv, hoặc tích hợp vào pipeline train/test.
