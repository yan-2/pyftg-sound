from pathlib import Path
from typing import List

from pyftg_sound.openal import al
from pyftg_sound.utils import load_sound


class AudioBuffer:
    buffers: List[int]

    def __init__(self, buffers: List[int]) -> None:
        self.buffers = buffers

    def get_buffers(self) -> List[int]:
        return self.buffers
    
    def register_sound(self, file_path: Path) -> None:
        for i, buffer_id in enumerate(self.buffers):
            alformat, wavbuf, samplerate = load_sound(file_path)
            al.alBufferData(buffer_id, alformat, wavbuf, len(wavbuf), samplerate)
