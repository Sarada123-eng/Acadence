import numpy as np


def calculate_similarity(
    embedding_1: np.ndarray,
    embedding_2: np.ndarray,
) -> float:

    return float(
        np.dot(
            embedding_1,
            embedding_2,
        )
    )


def is_match(
    similarity: float,
    threshold: float = 0.65,
) -> bool:

    return similarity >= threshold