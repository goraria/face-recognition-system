import os
import cv2
from module import config, utils

# Đường dẫn dữ liệu gốc (ảnh chưa cắt mặt)
RAW_DIR = os.path.join(config.BASE_DIR, 'dataset', 'pretrain')
CROP_DIR = os.path.join(config.BASE_DIR, 'dataset', 'face_crop')
os.makedirs(CROP_DIR, exist_ok=True)

# Cắt mặt từ ảnh gốc, lưu vào CROP_DIR theo class
for person in os.listdir(RAW_DIR):
    person_dir = os.path.join(RAW_DIR, person)
    if not os.path.isdir(person_dir):
        continue
    crop_person_dir = os.path.join(CROP_DIR, person)
    os.makedirs(crop_person_dir, exist_ok=True)
    for img_name in os.listdir(person_dir):
        if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        img_path = os.path.join(person_dir, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue
        faces = utils.detect_face_yolo(img)
        if not faces:
            continue
        face_img = faces[0]
        face_img = cv2.resize(face_img, (224, 224))
        save_path = os.path.join(crop_person_dir, img_name)
        cv2.imwrite(save_path, face_img)
print('Đã cắt xong mặt, lưu vào', CROP_DIR)
