import os
import pytest
from audio2midi.pitch_extraction import extract_pitch_librosa

def test_extract_pitch_librosa():
    """
    Tests pitch extraction using a short sample WAV file. Ensures that pitch
    extraction properly returns MIDI notes and a voiced/unvoiced flag array
    with matching lengths.
    """
    sample_wav_path = "tests/data/test_audio.wav"
    # Check if the WAV file exists. If not, skip the test.
    if not os.path.exists(sample_wav_path):
        pytest.skip("Skipping test because sample WAV file was not found.")

    # Perform pitch extraction.
    midi_notes, voiced_flags = extract_pitch_librosa(sample_wav_path)

    # Ensure the length of MIDI notes and voiced flags match.
    assert len(midi_notes) == len(voiced_flags), "midi_notes and voiced_flags must be the same length"