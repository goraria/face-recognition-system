import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from module import config, utils

# Đường dẫn dữ liệu gốc (ảnh chưa cắt mặt)
RAW_DIR = os.path.join(config.BASE_DIR, 'dataset', 'pretrain')
CROP_DIR = os.path.join(config.BASE_DIR, 'dataset', 'face_crop')
os.makedirs(CROP_DIR, exist_ok=True)

def resize_and_pad(img, size=(224, 224)):
    h, w = img.shape[:2]
    target_w, target_h = size
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    pad_top, pad_bottom, pad_left, pad_right = 0, 0, 0, 0
    if new_w < target_w:
        # Ảnh dọc, pad trái phải
        pad_left = (target_w - new_w) // 2
        pad_right = target_w - new_w - pad_left
    if new_h < target_h:
        # Ảnh ngang, pad trên dưới
        pad_top = (target_h - new_h) // 2
        pad_bottom = target_h - new_h - pad_top
    img_padded = cv2.copyMakeBorder(img_resized, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0,0,0])
    return img_padded

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
        face_img = resize_and_pad(face_img, (224, 224))
        save_path = os.path.join(crop_person_dir, img_name)
        cv2.imwrite(save_path, face_img)
print('Đã cắt xong mặt, lưu vào', CROP_DIR)
