import os
import shutil
import cv2
from module import config, utils

# Đường dẫn dữ liệu
PRETRAIN_DIR = os.path.join(config.BASE_DIR, 'dataset', 'pretrain')
TRAIN_DIR = os.path.join(config.BASE_DIR, 'dataset', 'train')
VAL_DIR = os.path.join(config.BASE_DIR, 'dataset', 'val')
EMPLOYEE_DIR = config.EMPLOYEE_DIR
EMBEDDING_DIR = config.EMPLOYEE_EMBEDDING

os.makedirs(TRAIN_DIR, exist_ok=True)
os.makedirs(VAL_DIR, exist_ok=True)
os.makedirs(EMPLOYEE_DIR, exist_ok=True)
os.makedirs(EMBEDDING_DIR, exist_ok=True)

# Tỉ lệ train/val (vd: 80% train, 20% val)
VAL_RATIO = 0.2

embedding_model = None
try:
    from model.classification_model import FacialRecognitionModel
    embedding_model = FacialRecognitionModel().get_embedding_model()
except Exception as e:
    print('Lỗi load embedding model:', e)

def process_images():
    for person in os.listdir(PRETRAIN_DIR):
        person_dir = os.path.join(PRETRAIN_DIR, person)
        if not os.path.isdir(person_dir):
            continue
        train_person_dir = os.path.join(TRAIN_DIR, person)
        val_person_dir = os.path.join(VAL_DIR, person)
        emp_person_dir = os.path.join(EMPLOYEE_DIR, person)
        emb_person_dir = os.path.join(EMBEDDING_DIR, person)
        os.makedirs(train_person_dir, exist_ok=True)
        os.makedirs(val_person_dir, exist_ok=True)
        os.makedirs(emp_person_dir, exist_ok=True)
        os.makedirs(emb_person_dir, exist_ok=True)

        images = [f for f in os.listdir(person_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        n_val = int(len(images) * VAL_RATIO)
        val_imgs = set(images[:n_val])
        for img_name in images:
            img_path = os.path.join(person_dir, img_name)
            img = cv2.imread(img_path)
            if img is None:
                continue
            faces = utils.detect_face_yolo(img)
            if not faces:
                continue
            face_img = faces[0]
            face_img = cv2.resize(face_img, (224, 224))
            # Lưu ảnh gốc vào EMPLOYEE_DIR
            emp_save_path = os.path.join(emp_person_dir, img_name)
            cv2.imwrite(emp_save_path, img)
            # Lưu ảnh mặt vào train/val
            if img_name in val_imgs:
                save_path = os.path.join(val_person_dir, img_name)
            else:
                save_path = os.path.join(train_person_dir, img_name)
            cv2.imwrite(save_path, face_img)
            # Sinh embedding và lưu
            if embedding_model is not None:
                embedding = embedding_model.predict(face_img.reshape(1, 224, 224, 3))[0]
                emb_save_path = os.path.join(emb_person_dir, img_name + '.npy')
                import numpy as np
                np.save(emb_save_path, embedding)

if __name__ == '__main__':
    process_images()
    print('Đã xử lý xong ảnh: cắt mặt, lưu train/val, employee, embedding.')
