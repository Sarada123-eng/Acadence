import numpy as np
from app.pipelines.face.detector import detect_faces
from app.pipelines.face.landmarks import extract_landmarks
from app.pipelines.face.embedder import generate_embedding

def extract_face_embeddings(image: np.ndarray) -> list[np.ndarray]:
    """
    Coordinates the face recognition pipeline:
    Image -> Detector -> Landmarks -> Embeddings

    Args:
        image: RGB image as a NumPy array.

    Returns:
        List of 128D NumPy vectors for each face found in the image.
    """
    faces = detect_faces(image)
    if not faces:
        return []

    embeddings = []
    for face in faces:
        shape = extract_landmarks(image, face)
        embedding = generate_embedding(image, shape)
        embeddings.append(embedding)

    return embeddings