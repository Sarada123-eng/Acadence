import dlib
import numpy as np
from app.pipelines.face.models import face_models

def generate_embedding(image: np.ndarray, shape: dlib.full_object_detection) -> np.ndarray:
    """
    Generate a 128D embedding vector for a single face shape.

    Args:
        image: RGB image as a NumPy array.
        shape: dlib.full_object_detection containing facial landmarks.

    Returns:
        NumPy array of shape (128,) representing the 128-dimensional embedding.
    """
    facerec = face_models.face_recognition_model
    descriptor = facerec.compute_face_descriptor(image, shape, 1)
    return np.array(descriptor)