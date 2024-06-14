from pathlib import Path
from typing import List

from pyftg_sound.openal import al, alc
from pyftg_sound.utils.wave import load_sound


class AudioBuffer:
    contexts: List[alc.ALCcontext]
    buffers: List[int]

    def __init__(self, contexts: List[alc.ALCcontext], buffers: List[int]) -> None:
        self.contexts = contexts
        self.buffers = buffers

    def get_buffers(self) -> List[int]:
        return self.buffers
    
    def register_sound(self, file_path: Path) -> None:
        for i, buffer_id in enumerate(self.buffers):
            alc.alcMakeContextCurrent(self.contexts[i])
            alformat, wavbuf, samplerate = load_sound(file_path)
            al.alBufferData(buffer_id, alformat, wavbuf, len(wavbuf), samplerate)
