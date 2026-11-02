import numpy as np

from app.pipelines.voice.models import voice_models
from resemblyzer import preprocess_wav

def generate_embedding(audio: np.ndarray, sr: int) -> np.ndarray:
    """
    Generate a voice embedding from a preprocessed waveform.
    """

    encoder = voice_models.voice_encoder


    wav = preprocess_wav(audio, sr)
    embedding = encoder.embed_utterance(wav)

    return np.asarray(embedding)