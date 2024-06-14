import wave
from pathlib import Path
from typing import Tuple

from fighting_sound.openal import al

formatmap = {
    (1, 8) : al.AL_FORMAT_MONO8,
    (2, 8) : al.AL_FORMAT_STEREO8,
    (1, 16): al.AL_FORMAT_MONO16,
    (2, 16) : al.AL_FORMAT_STEREO16,
}


def load_sound(file_path: Path) -> Tuple[int, bytes, int]:
    with wave.open(str(file_path), 'rb') as wavefp:
        channels = wavefp.getnchannels()
        bitrate = wavefp.getsampwidth() * 8
        samplerate = wavefp.getframerate()
        wavbuf = wavefp.readframes(wavefp.getnframes())
        alformat = formatmap[(channels, bitrate)]
    return alformat, wavbuf, samplerate
