import cv2
import numpy as np
from module import config
import torch
import os

# Khởi tạo YOLOv5 model bằng torch.hub, sau đó load weights từ model/yolov5s.pt
YOLOV5_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'model', 'yolov5s.pt')
yolo = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=False)
yolo.load_state_dict(torch.load(YOLOV5_PATH, map_location='cpu')['model'].state_dict())

# Tích hợp ultralytics YOLOv8-face cho phát hiện khuôn mặt
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