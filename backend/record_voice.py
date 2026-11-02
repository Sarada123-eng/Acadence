"""Record a short WAV file for voice enrollment testing."""

import sounddevice as sd
from scipy.io.wavfile import write


SAMPLE_RATE = 16_000
DURATION_SECONDS = 7
OUTPUT_FILE = "voice_enrollment.wav"


def main() -> None:
    print(f"Recording for {DURATION_SECONDS} seconds...")
    recording = sd.rec(
        int(DURATION_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
    )
    sd.wait()

    write(OUTPUT_FILE, SAMPLE_RATE, recording)
    print(f"Saved recording to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
