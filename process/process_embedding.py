import os
import numpy as np
from module import config

from model.classification_model import FacialRecognitionModel

CROP_DIR = os.path.join(config.BASE_DIR, 'dataset', 'face_crop')
EMBEDDING_DIR = os.path.join(config.BASE_DIR, 'images', 'attendance_embedding')
os.makedirs(EMBEDDING_DIR, exist_ok=True)

embedding_model = FacialRecognitionModel().get_embedding_model()

for person in os.listdir(CROP_DIR):
    person_dir = os.path.join(CROP_DIR, person)
    if not os.path.isdir(person_dir):
        continue
    emb_person_dir = os.path.join(EMBEDDING_DIR, person)
    os.makedirs(emb_person_dir, exist_ok=True)
    for img_name in os.listdir(person_dir):
        if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        img_path = os.path.join(person_dir, img_name)
        import cv2
        img = cv2.imread(img_path)
        if img is None:
            continue
        img = cv2.resize(img, (224, 224))
        embedding = embedding_model.predict(img.reshape(1, 224, 224, 3))[0]
        emb_save_path = os.path.join(emb_person_dir, img_name + '.npy')
        np.save(emb_save_path, embedding)
print('Đã sinh embedding cho toàn bộ ảnh mặt, lưu vào', EMBEDDING_DIR)
