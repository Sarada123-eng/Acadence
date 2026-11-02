import io

import librosa
import numpy as np

from app.pipelines.voice.embedder import generate_embedding
from app.pipelines.voice.similarity import calculate_similarity, is_match

def _identify_speaker(
    embedding: np.ndarray,#here audio segment is already converted to embedding
    candidates: dict[int, np.ndarray],
    threshold: float = 0.65,
) -> tuple[int | None, float]:
    """
    Identify the speaker from a voice embedding.

    Args:
        embedding: The voice embedding to identify.
        candidates: A dictionary mapping student IDs to their stored embeddings.
        threshold: Similarity threshold for a match.
    
    Returns:
        The identified student ID and similarity when a match is found.
        Otherwise, ``(None, best_similarity)``.
    """

    if embedding is None or len(candidates) == 0:
        return None, -1.0

    best_student_id = None
    best_similarity = -1.0

    for sid , stored_embedding in candidates.items():
        if stored_embedding is None:
            continue

        similarity = calculate_similarity(
            embedding,
            np.asarray(stored_embedding, dtype=np.float64),
        )

        if similarity > best_similarity:
            best_similarity = similarity
            best_student_id = sid

    if best_student_id is not None and is_match(best_similarity, threshold):
        return best_student_id, best_similarity

    return None, best_similarity

def process_audio_segment(
    audio_bytes: bytes,
    candidates: dict[int, np.ndarray],
    threshold: float = 0.65,
) -> dict[int, float] | None:
    """
    Process an audio segment to identify the speaker.

    Args:
        audio_bytes: The audio segment in bytes.
        candidates: A dictionary mapping student IDs to their stored embeddings.
        threshold: Similarity threshold for a match.

    Returns:
        A dictionary with the identified student ID and similarity score, or None if no match is found.
    """

    if not audio_bytes or len(candidates) == 0:
        return None

    audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

    segments = librosa.effects.split(audio, top_db=30)
    identified_students: dict[int, float] = {}

    for start, end in segments:
        if (end - start) < sr * 0.5:  # Skip segments shorter than 0.5 seconds
            continue
        segment_audio = audio[start:end]

        embedding = generate_embedding(segment_audio, sr)

        student_id, similarity = _identify_speaker(
            embedding,
            candidates,
            threshold,
        )
        if student_id is not None:

            # Keep the strongest score if the same
            # speaker appears in multiple segments.
            if (
                student_id not in identified_students
                or similarity > identified_students[student_id]
            ):
                identified_students[student_id] = similarity

    return identified_students