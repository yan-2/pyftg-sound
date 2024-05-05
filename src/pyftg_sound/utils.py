import wave
from pathlib import Path
from typing import Tuple

import numpy as np

from pyftg_sound.openal import al

formatmap = {
    (1, 8) : al.AL_FORMAT_MONO8,
    (2, 8) : al.AL_FORMAT_STEREO8,
    (1, 16): al.AL_FORMAT_MONO16,
    (2, 16) : al.AL_FORMAT_STEREO16,
}

dtypemap = {
    al.ALbyte: np.int8,
    al.ALubyte: np.uint8,
    al.ALshort: np.int16,
    al.ALushort: np.uint16,
    al.ALint: np.int32,
    al.ALuint: np.uint32,
    al.ALfloat: np.float32,
    al.ALdouble: np.float64,
}


def load_sound(file_path: Path) -> Tuple[int, bytes, int]:
    with wave.open(str(file_path), 'rb') as wavefp:
        channels = wavefp.getnchannels()
        bitrate = wavefp.getsampwidth() * 8
        samplerate = wavefp.getframerate()
        wavbuf = wavefp.readframes(wavefp.getnframes())
        alformat = formatmap[(channels, bitrate)]
    return alformat, wavbuf, samplerate
