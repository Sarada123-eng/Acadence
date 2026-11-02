import numpy as np
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.biometric_repository import get_classroom_biometric_embeddings
from app.pipelines.face.face_pipeline import extract_face_embeddings
from app.pipelines.face.classifier import FaceClassifier


def enroll_student_face_embedding(
    db: Session,
    student_id: int,
    image: np.ndarray,
) -> None:
    """
    Generate and store a student's face embedding.

    Enrollment expects exactly one face in the image.
    """

    student = db.get(Student, student_id)

    if student is None:
        raise ValueError(
            f"Student with ID {student_id} does not exist."
        )


    embeddings = extract_face_embeddings(image)

    if not embeddings:
        raise ValueError(
            "No face detected in the provided image."
        )

    if len(embeddings) > 1:
        raise ValueError(
            "Multiple faces detected in the provided image. "
            "Please provide an image with a single face."
        )

    face_embedding = embeddings[0]


    student.face_embedding = face_embedding.tolist()

    db.commit()


def verify_student_face_embedding(
    db: Session,
    student_id: int,
    image: np.ndarray,
) -> bool:
    """
    Verify whether the face in the provided image belongs
    to the specified student.

    This is a 1-to-1 verification.
    """


    student = db.get(Student, student_id)

    if student is None:
        raise ValueError(
            f"Student with ID {student_id} does not exist."
        )

    if student.face_embedding is None:
        raise ValueError(
            "Student has not enrolled a face."
        )


    embeddings = extract_face_embeddings(image)

    if not embeddings:
        raise ValueError(
            "No face detected in the provided image."
        )

    if len(embeddings) > 1:
        raise ValueError(
            "Multiple faces detected in the provided image. "
            "Please provide an image with a single face."
        )

    detected_embedding = embeddings[0]


    stored_embedding = np.asarray(
        student.face_embedding,
        dtype=np.float64,
    )

    classifier = FaceClassifier()

    distance = classifier.calculate_distance(
        detected_embedding,
        stored_embedding,
    )

    return classifier.is_match(distance)


def identify_students_in_classroom(
    db: Session,
    classroom_id: int,
    image: np.ndarray,
) -> list[int]:
    """
    Identify students present in a classroom photograph.

    Flow:

        Classroom students
                ↓
        Train classroom SVM
                ↓
        Classroom image
                ↓
        DLIB embeddings
                ↓
        SVM prediction
                ↓
        Euclidean distance verification
                ↓
        Matched student IDs
    """



    candidates = get_classroom_biometric_embeddings(
        db,
        classroom_id,
    )

    if not candidates:
        return []

    # candidates should look like:
    #
    # [
    #     (student_id, embedding),
    #     (student_id, embedding),
    #     ...
    # ]

    # --------------------------------------------------
    # 2. Prepare SVM training data
    # --------------------------------------------------

    training_embeddings = []
    training_student_ids = []

    for student_id, embedding, _ in candidates:

        if embedding is None:
            continue

        training_embeddings.append(
            np.asarray(embedding, dtype=np.float64)
        )

        training_student_ids.append(student_id)

    if not training_embeddings:
        return []

    # --------------------------------------------------
    # 3. Train SVM for this classroom
    # --------------------------------------------------

    classifier = FaceClassifier()

    classifier.train(
        embeddings=training_embeddings,
        student_ids=training_student_ids,
    )

    # --------------------------------------------------
    # 4. Extract faces from classroom image
    # --------------------------------------------------

    detected_embeddings = extract_face_embeddings(image)

    if not detected_embeddings:
        return []

    # --------------------------------------------------
    # 5. Identify each detected face
    # --------------------------------------------------

    matched_student_ids: set[int] = set()

    for detected_embedding in detected_embeddings:

        # ----------------------------------------------
        # Case: classroom contains only one enrolled
        # student.
        #
        # SVM cannot train with only one class.
        # ----------------------------------------------

        if classifier.clf is None:

            predicted_student_id = training_student_ids[0]

        else:

            # ------------------------------------------
            # SVM prediction
            # ------------------------------------------

            predicted_student_id = classifier.predict(
                detected_embedding
            )

        # ----------------------------------------------
        # Find the stored embedding of the student
        # predicted by the SVM
        # ----------------------------------------------

        predicted_embedding = None

        for student_id, embedding, _ in candidates:

            if student_id == predicted_student_id:
                predicted_embedding = np.asarray(
                    embedding,
                    dtype=np.float64,
                )
                break

        if predicted_embedding is None:
            continue

        # ----------------------------------------------
        # Distance verification
        # ----------------------------------------------

        distance = classifier.calculate_distance(
            detected_embedding,
            predicted_embedding,
        )

        # ----------------------------------------------
        # Final acceptance
        # ----------------------------------------------

        if classifier.is_match(distance):
            matched_student_ids.add(
                predicted_student_id
            )

    return list(matched_student_ids)