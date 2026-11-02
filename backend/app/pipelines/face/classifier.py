import numpy as np
from sklearn.svm import SVC

class FaceClassifier:
    def __init__(self):
        self.clf = None  # Placeholder for the classifier
        self.embeddings = []  # List to store embeddings
        self.student_ids = []  # List to store corresponding student IDs

    def train(self, embeddings: list[np.ndarray], student_ids: list[str]):
        """
        Train the SVM classifier with the provided embeddings and student IDs.

        Args:
            embeddings: List of 128D NumPy vectors for each face.
            student_ids: List of corresponding student IDs.
        """
        if not embeddings:
            raise ValueError("No face embeddings available.")

        if len(embeddings) != len(student_ids):
            raise ValueError(
                "Number of embeddings and student IDs must match."
            )

        self.embeddings = embeddings
        self.student_ids = student_ids

        unique_student_ids = set(student_ids)
        if len(unique_student_ids) < 2:
            self.clf = None  # Not enough classes to train a classifier
            return

        self.clf = SVC(kernel="linear", probability=True, class_weight="balanced")
        self.clf.fit(np.array(embeddings), np.array(student_ids))

    def predict(self, embedding: np.ndarray) -> str:
        """
        Predict the student ID for a given face embedding.

        Args:
            embedding: 128D NumPy vector representing a face.
        """
        if self.clf is None:
            raise ValueError("Classifier has not been trained or not enough classes to train.")

        predicted_id = self.clf.predict([embedding])[0] 

        return int(predicted_id)  # Convert to int before returning

    def calculate_distance(
            self,
            embedding_1: np.ndarray,
            embedding_2: np.ndarray
    ):
        """
        Calculate the Euclidean distance between two face embeddings.

        Args:
            embedding_1: First 128D NumPy vector.
            embedding_2: Second 128D NumPy vector.

        Returns:
            Euclidean distance as a float.
        """
        return np.linalg.norm(embedding_1 - embedding_2)

    def is_match(
        self,
        distance: float,
        threshold: float = 0.6
    ) -> bool:
        """
        Determine if two face embeddings are a match based on their distance.

        Args:
            distance: The Euclidean distance between the two embeddings.
            threshold: The threshold for considering a match.

        Returns:
            True if the distance is less than or equal to the threshold, False otherwise.
        """

        return bool(distance <= threshold)


face_classifier = FaceClassifier()  # Singleton instance of the FaceClassifier