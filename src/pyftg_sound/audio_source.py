from typing import List

from pyftg_sound.openal import al, alc


class AudioSource:
    contexts: List[alc.ALCcontext]
    source_ids: List[int]

    def __init__(self, contexts: List[alc.ALCcontext], source_ids: List[int]) -> None:
        self.contexts = contexts
        self.source_ids = source_ids
    
    def get_source_ids(self) -> List[int]:
        return self.source_ids
    
    def clear_buffer(self) -> None:
        for i, source_id in enumerate(self.source_ids):
            alc.alcMakeContextCurrent(self.contexts[i])
            al.alSourcei(source_id, al.AL_BUFFER, al.AL_NONE)
