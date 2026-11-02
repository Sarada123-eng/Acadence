import numpy as np
import io
import librosa
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.biometric_repository import get_classroom_biometric_embeddings
from app.pipelines.voice.pipeline import process_audio_segment
from app.pipelines.voice.similarity import (
    calculate_similarity,
    is_match,
)
from app.pipelines.voice.embedder import generate_embedding

def enroll_student_voice_embedding(
    db: Session,
    student_id: int,
    audio_bytes: bytes,
) -> None:
    """
    Generate and store a student's voice embedding.

    Enrollment expects a valid audio file containing the student's voice.
    """

    student = db.get(Student, student_id)

    if student is None:
        raise ValueError(
            f"Student with ID {student_id} does not exist."
        )

    # Load the audio from bytes
    audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

    # Generate the voice embedding
    voice_embedding = generate_embedding(audio, sr)

    student.voice_embedding = voice_embedding.tolist()

    db.commit()


def verify_student_voice_embedding(
    db: Session,
    student_id: int,
    audio_bytes: bytes,
) -> bool:
    """
    Verify whether the provided voice belongs
    to the specified student.
    """

    student = db.get(Student, student_id)

    if student is None:
        raise ValueError(
            f"Student with ID {student_id} does not exist."
        )

    if student.voice_embedding is None:
        raise ValueError(
            "Student has not enrolled a voice."
        )

    audio, sr = librosa.load(
        io.BytesIO(audio_bytes),
        sr=16000,
    )

    detected_embedding = generate_embedding(
        audio,
        sr,
    )

    stored_embedding = np.asarray(
        student.voice_embedding,
        dtype=np.float64,
    )

    similarity = calculate_similarity(
        detected_embedding,
        stored_embedding,
    )

    return is_match(similarity)



def identify_students_in_classroom_by_voice(
    db: Session,
    classroom_id: int,
    audio_bytes: bytes,
) -> dict[int, float] | None:
    """
    Identify speakers in a classroom recording.

    The repository supplies the enrolled biometric records. This service
    extracts only the voice candidates and delegates audio processing and
    speaker identification to the voice pipeline.
    """

    biometric_records = get_classroom_biometric_embeddings(
        db,
        classroom_id,
    )

    voice_candidates = {
        student_id: voice_embedding
        for student_id, _, voice_embedding in biometric_records
        if voice_embedding is not None
    }

    return process_audio_segment(
        audio_bytes,
        voice_candidates,
    )


