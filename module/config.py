# config.py
import os
import tensorflow as tf

# Đường dẫn gốc dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# File paths
TRAIN_DATASET = os.path.join(BASE_DIR, 'dataset', 'train')
VAL_DATASET = os.path.join(BASE_DIR, 'dataset', 'val')
CHECK_POINT = os.path.join(BASE_DIR, 'checkpoint', 'model.h5')
# ATTENDANCE_REPORT = os.path.join(BASE_DIR, 'images', 'attendance', 'report')
EMPLOYEE_CSV = os.path.join(BASE_DIR, 'dataset', 'data', 'data.csv') #
EMPLOYEE_DIR = os.path.join(BASE_DIR, 'dataset', 'attendance_face')
EMPLOYEE_EMBEDDING = os.path.join(BASE_DIR, 'dataset', 'attendance_embedding')
# STUDENT_DETAILS_CSV = os.path.join(BASE_DIR, 'images', 'StudentDetails.csv')

# Model input image size
IMAGE_SIZE = (224, 224)

# Batch size and buffer size
BATCH_SIZE = 256
BUFFER_SIZE = BATCH_SIZE * 2

# Define autotune
AUTO = tf.data.AUTOTUNE

# Training parameters
LEARNING_RATE = 0.0001
STEPS_PER_EPOCH = 50
VALIDATION_STEPS = 10
EPOCHS = 10

# Threshold for verification
THRESHOLD = 0.8