from pathlib import Path
from typing import Dict, List

import numpy as np

from pyftg_sound.audio_buffer import AudioBuffer
from pyftg_sound.audio_source import AudioSource
from pyftg_sound.openal import al
from pyftg_sound.sound_renderer import SoundRenderer


class SoundManager:
    sound_renderers: List[SoundRenderer] = []
    audio_sources: List[AudioSource] = []
    audio_buffers: List[AudioBuffer] = []
    sound_buffers: Dict[str, AudioBuffer] = {}
    virtual_renderer: SoundRenderer = None

    def __init__(self) -> None:
        self.virtual_renderer = SoundRenderer.create_virtual_renderer()
        self.sound_renderers.append(SoundRenderer.create_default_renderer())
        self.sound_renderers.append(self.virtual_renderer)
        if len(self.sound_renderers) == 0:
            raise ValueError("No audio renderer has been created.")

    def set_listener_position(self, x: float, y: float, z: float) -> None:
        listener_pos = [x, y, z]
        for sound_renderer in self.sound_renderers:
            sound_renderer.al_listener_fv(al.AL_POSITION, listener_pos)

    def set_listener_velocity(self, x: float, y: float, z: float) -> None:
        listener_vel = [x, y, z]
        for sound_renderer in self.sound_renderers:
            sound_renderer.al_listener_fv(al.AL_VELOCITY, listener_vel)

    def set_listener_orientation(self, x: float, y: float, z: float, x_up: float, y_up: float, z_up: float) -> None:
        listener_ori = [x, y, z, x_up, y_up, z_up]
        for sound_renderer in self.sound_renderers:
            sound_renderer.al_listener_fv(al.AL_ORIENTATION, listener_ori)
    
    def create_source(self) -> int:
        source = al.ALuint(0)
        al.alGenSources(1, source)
        al.alSourcef(source, al.AL_ROLLOFF_FACTOR, 0.01)
        return source.value
        
    def create_buffer(self) -> int:
        buffer = al.ALuint(0)
        al.alGenBuffers(1, buffer)
        return buffer.value
    
    def create_audio_source(self) -> AudioSource:
        source_ids = [0] * len(self.sound_renderers)
        for i, sound_renderer in enumerate(self.sound_renderers):
            sound_renderer.set()
            source_ids[i] = self.create_source()
        audio_source = AudioSource(source_ids)
        self.audio_sources.append(audio_source)
        return audio_source

    def create_audio_buffer(self, file_path: Path = None) -> AudioBuffer:
        buffer_ids = [0] * len(self.sound_renderers)
        for i, sound_renderer in enumerate(self.sound_renderers):
            sound_renderer.set()
            buffer_ids[i] = self.create_buffer()
        audio_buffer = AudioBuffer(buffer_ids)
        if file_path is not None:
            audio_buffer.register_sound(file_path)
            self.sound_buffers[file_path.name] = audio_buffer
        self.audio_buffers.append(audio_buffer)
        return audio_buffer

    def play(self, source: AudioSource, buffer: AudioBuffer, x: int, y: int, loop: bool) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            buffer_id = buffer.get_buffers()[i]
            sound_renderer.play(source_id, buffer_id, x, y, loop)

    def get_sound_buffer(self, sound_name: str) -> AudioBuffer:
        return self.sound_buffers.get(sound_name)

    def is_playing(self, source: AudioSource) -> bool:
        ans = False
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            ans = ans or sound_renderer.is_playing(source_id)
        return ans

    def stop(self, source: AudioSource) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.stop(source_id)

    def set_source_pos(self, source: AudioSource, x: int, y: int) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.set_source_3f(source_id, al.AL_POSITION, x, 0, 4)

    def set_source_gain(self, source: AudioSource, gain: float) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.set_source_gain(source_id, min(1.0, max(0.0, gain)))

    def sample_audio(self) -> np.ndarray[np.float32]:
        return self.virtual_renderer.sample_audio()
    
    def remove_source(self, source: AudioSource) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.delete_source(source_id)
        self.audio_sources.remove(source)

    def playback(self, source: AudioSource, audio_sample: bytes) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.playback(source_id, audio_sample)

    def stop_playback(self, source: AudioSource) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.stop_playback(source_id)

    def stop_all(self) -> None:
        for audio_source in self.audio_sources:
            self.stop(audio_source)

    def close(self) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            for audio_buffer in self.audio_buffers:
                sound_renderer.delete_buffer(audio_buffer.get_buffers()[i])
            for audio_source in self.audio_sources:
                sound_renderer.delete_source(audio_source.get_source_ids()[i])
            sound_renderer.close()
