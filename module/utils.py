import cv2
import numpy as np
from module import config
import os

# Khởi tạo YOLOv8-face cho phát hiện khuôn mặt
try:
    from ultralytics import YOLO
    YOLO_FACE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', 'yolov8n-face.pt')
    yolo_face = YOLO(YOLO_FACE_PATH)
    YOLO_FACE_OK = True
except Exception as e:
    print('Không load được YOLOv8-face:', e)
    YOLO_FACE_OK = False


def detect_face_yolo(img):
    import numpy as np
    import cv2
    if not YOLO_FACE_OK:
        print('Model YOLOv8-face chưa sẵn sàng!')
        return []
    # Nếu là path, đọc ảnh
    if isinstance(img, str):
        img = cv2.imread(img)
    if img is None:
        return []
    orig_img = img.copy()
    h0, w0 = img.shape[:2]
    # Dùng model ultralytics YOLOv8-face
    results = yolo_face.predict(img, conf=0.3, verbose=False)
    faces = []
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy() if hasattr(r.boxes, 'xyxy') else []
        for box in boxes:
            x1, y1, x2, y2 = map(int, box[:4])
            x1 = max(0, x1)
            x2 = min(w0, x2)
            y1 = max(0, y1)
            y2 = min(h0, y2)
            if x2 > x1 and y2 > y1:
                face_img = orig_img[y1:y2, x1:x2]
                if face_img.size > 0:
                    faces.append(face_img)
    return faces


def detect_face_yolo_with_box(img):
    """
    Trả về (faces, boxes) với boxes là list [x1, y1, x2, y2] của từng khuôn mặt.
    """
    if not YOLO_FACE_OK:
        print('Model YOLOv8-face chưa sẵn sàng!')
        return [], []
    if isinstance(img, str):
        img = cv2.imread(img)
    if img is None:
        return [], []
    orig_img = img.copy()
    h0, w0 = img.shape[:2]
    results = yolo_face.predict(img, conf=0.3, verbose=False)
    faces = []
    boxes = []
    for r in results:
        box_arr = r.boxes.xyxy.cpu().numpy() if hasattr(r.boxes, 'xyxy') else []
        for box in box_arr:
            x1, y1, x2, y2 = map(int, box[:4])
            x1 = max(0, x1)
            x2 = min(w0, x2)
            y1 = max(0, y1)
            y2 = min(h0, y2)
            if x2 > x1 and y2 > y1:
                face_img = orig_img[y1:y2, x1:x2]
                if face_img.size > 0:
                    faces.append(face_img)
                    boxes.append([x1, y1, x2, y2])
    return faces, boxes


def distance_to_similarity(distance, min_d=0.2, max_d=0.8):
    if distance > max_d:
        return 0
    elif distance < min_d:
        return 100
    else:
        return round(100 * (1 - (distance - min_d) / (max_d - min_d)), 2)


def preprocess(path, embedding_model):
    if isinstance(path, str):
        img = cv2.imread(path)
    else:
        img = path

    faces = detect_face_yolo(img)
    if not faces:
        return None, None

    face_img = faces[0]
    face_img = cv2.resize(face_img, (224, 224))
    embedding_img = embedding_model.predict(face_img)[0]
    return embedding_img, None


def check_face(path, embedding_model):
    if isinstance(path, str):
        img = cv2.imread(path)
    else:
        img = path

    faces = detect_face_yolo(img)
    if not faces:
        return None, None

    face_img = faces[0]
    face_img = cv2.resize(face_img, (224, 224))
    embedding_img = embedding_model.predict(face_img)[0]
    return embedding_img, None


def get_face_embedding(img, embedding_model):
    """
    Cắt khuôn mặt đầu tiên trong ảnh và sinh embedding.
    Trả về (embedding, face_img) hoặc (None, None) nếu không phát hiện khuôn mặt.
    """
    faces = detect_face_yolo(img)
    if not faces:
        return None, None
    face_img = cv2.resize(faces[0], (224, 224))
    embedding = embedding_model.predict(np.expand_dims(face_img, axis=0))[0]
    return embedding, face_img


def resize_and_pad(img, size=(224, 224)):
    h, w = img.shape[:2]
    target_w, target_h = size
    scale = min(target_w / w, target_h / h)
    new_w, new_h = int(w * scale), int(h * scale)
    img_resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    pad_top, pad_bottom, pad_left, pad_right = 0, 0, 0, 0
    if new_w < target_w:
        pad_left = (target_w - new_w) // 2
        pad_right = target_w - new_w - pad_left
    if new_h < target_h:
        pad_top = (target_h - new_h) // 2
        pad_bottom = target_h - new_h - pad_top
    img_padded = cv2.copyMakeBorder(img_resized, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0,0,0])
    return img_padded