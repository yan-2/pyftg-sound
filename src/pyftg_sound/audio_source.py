from typing import List

from pyftg_sound.openal import al


class AudioSource:
    source_ids: List[int]

    def __init__(self, source_ids: List[int]) -> None:
        self.source_ids = source_ids
    
    def get_source_ids(self) -> List[int]:
        return self.source_ids
    
    def clear_buffer(self) -> None:
        for i, source_id in enumerate(self.source_ids):
            al.alSourcei(source_id, al.AL_BUFFER, al.AL_NONE)
