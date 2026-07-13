import os
import numpy as np
from functools import lru_cache
from PIL import Image

# This model was trained on 64x64 images (confirmed via model.input_shape)
IMG_SIZE = (64, 64)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "multi_crop_disease_model.h5")
CLASS_NAMES_PATH = os.path.join(BASE_DIR, "class_names.txt")


@lru_cache(maxsize=1)
def load_disease_model():
    # Imported here so Django doesn't need TensorFlow loaded at startup
    from tensorflow.keras.models import load_model
    model = load_model(MODEL_PATH)
    return model


@lru_cache(maxsize=1)
def load_class_names():
    with open(CLASS_NAMES_PATH, "r") as f:
        return [line.strip() for line in f if line.strip()]


def preprocess_image(image_file):
    """image_file: a Django UploadedFile / InMemoryUploadedFile object"""
    img = Image.open(image_file).convert("RGB")
    img = img.resize(IMG_SIZE)
    # No manual /255.0 here — the model has its own internal Rescaling layer
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)  # shape: (1, 64, 64, 3)
    return arr


def predict_disease(image_file):
    model = load_disease_model()
    class_names = load_class_names()

    x = preprocess_image(image_file)
    preds = model.predict(x)[0]  # shape: (num_classes,)

    top_idx = int(np.argmax(preds))
    confidence = float(preds[top_idx])
    label = class_names[top_idx]

    # top-3 for extra context
    top3_idx = preds.argsort()[::-1][:3]
    top3 = [(class_names[i], round(float(preds[i]) * 100, 2)) for i in top3_idx]

    return {
        "label": label,
        "confidence": round(confidence * 100, 2),
        "top3": top3,
    }