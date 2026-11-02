import dlib
import numpy as np
from app.pipelines.face.models import face_models

def detect_faces(image: np.ndarray) -> list[dlib.rectangle]:
    """
    Detect face bounding boxes in an image.

    Args:
        image: RGB image as a NumPy array.

    Returns:
        List of dlib.rectangle bounding boxes.
    """
    detector = face_models.face_detector
    return detector(image, 1) # Here 1 represent the number of image pyramid layers to apply when upscaling the image. A higher number can help detect smaller faces but will increase processing time.
                              # this function is returning a list of dlib.rectangle objects, which represent the bounding boxes of detected faces in the image.