import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import random
from module import config

CROP_DIR = os.path.join(config.BASE_DIR, 'dataset', 'face_crop')
TRAIN_DIR = os.path.join(config.BASE_DIR, 'dataset', 'train')
VAL_DIR = os.path.join(config.BASE_DIR, 'dataset', 'val')

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR, exist_ok=True)

VAL_RATIO = 0.2  # 20% val, 80% train

for person in os.listdir(CROP_DIR):
    person_dir = os.path.join(CROP_DIR, person)
    if not os.path.isdir(person_dir):
        continue
    imgs = [f for f in os.listdir(person_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(imgs)
    n_val = int(len(imgs) * VAL_RATIO)
    val_imgs = imgs[:n_val]
    train_imgs = imgs[n_val:]
    train_person_dir = os.path.join(TRAIN_DIR, person)
    val_person_dir = os.path.join(VAL_DIR, person)
    os.makedirs(train_person_dir, exist_ok=True)
    os.makedirs(val_person_dir, exist_ok=True)
    for img_name in train_imgs:
        shutil.copy2(os.path.join(person_dir, img_name), os.path.join(train_person_dir, img_name))
    for img_name in val_imgs:
        shutil.copy2(os.path.join(person_dir, img_name), os.path.join(val_person_dir, img_name))
print('Đã tách dữ liệu train/val từ ảnh mặt đã cắt.')
