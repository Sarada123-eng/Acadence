import dlib
import numpy as np
from app.pipelines.face.models import face_models

def extract_landmarks(image: np.ndarray, face: dlib.rectangle) -> dlib.full_object_detection:
    """
    Extract facial landmarks (shape) for a single detected face bounding box.

    Args:
        image: RGB image as a NumPy array.
        face: dlib.rectangle defining the bounding box of a single face.

    Returns:
        dlib.full_object_detection object containing 68 facial landmarks.
    """
    shape_predictor = face_models.shape_predictor
    return shape_predictor(image, face) # we are passing image alon