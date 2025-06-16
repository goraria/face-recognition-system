import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Flatten, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from module import config

class FacialRecognitionModel:
    def __init__(self):
        self.class_names = self._get_class_names()
        self.model = self.load_model()

    def _get_class_names(self):
        # Tự động lấy tên class từ thư mục train nếu có, hoặc dùng danh sách mẫu
        train_dir = config.TRAIN_DATASET
        if tf.io.gfile.exists(train_dir):
            return sorted([d for d in tf.io.gfile.listdir(train_dir) if tf.io.gfile.isdir(tf.io.gfile.join(train_dir, d))])
        # fallback
        return [
            "ChauBui", "Erik", "HoaMinzy", "KhoaPub", "LamVlog", "LanAnh", "NguyenVietHoang", "PhuongLy", "SonTung", "TranMinhHieu"
        ]

    def load_model(self):
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        for layer in base_model.layers:
            layer.trainable = False
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(2048, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.5)(x)
        x = Dense(512, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.5)(x)
        x = Dense(len(self.class_names), activation='softmax')(x)
        model = Model(inputs=base_model.input, outputs=x)
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        self.model = model
        return self.model

    def get_embedding_model(self):
        # Trả về model embedding (không có lớp softmax)
        base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        embedding_model = Model(inputs=base_model.input, outputs=x)
        return embedding_model