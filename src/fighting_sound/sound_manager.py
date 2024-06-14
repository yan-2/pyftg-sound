from pathlib import Path
from typing import Dict, List

import numpy as np

from fighting_sound.models.audio_buffer import AudioBuffer
from fighting_sound.models.audio_source import AudioSource
from fighting_sound.models.sound_renderer import SoundRenderer
from fighting_sound.openal import al
from fighting_sound.utils.openal import set_source_attribute


class SoundManager:
    sound_renderers: List[SoundRenderer] = []
    audio_sources: List[AudioSource] = []
    audio_buffers: List[AudioBuffer] = []
    sound_buffers: Dict[str, AudioBuffer] = {}
    virtual_renderer: SoundRenderer = None
    default_renderer: SoundRenderer = None
    virtual_renderer_index:int
    default_renderer_index:int

    def __init__(self) -> None:
        pass

    def set_default_renderer(self, sound_renderer: SoundRenderer) -> None:
        self.default_renderer = sound_renderer
        self.default_renderer_index = len(self.sound_renderers)
        self.sound_renderers.append(sound_renderer)

    def set_virtual_renderer(self, virtual_renderer: SoundRenderer) -> None:
        self.virtual_renderer = virtual_renderer
        self.virtual_renderer_index = len(self.sound_renderers)
        self.sound_renderers.append(virtual_renderer)

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
    
    def create_audio_source(self, attrs: dict = {}) -> AudioSource:
        contexts = [sound_renderer.context for sound_renderer in self.sound_renderers]
        source_ids = [0] * len(self.sound_renderers)
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_ids[i] = sound_renderer.create_source(attrs)
        audio_source = AudioSource(contexts, source_ids)
        self.audio_sources.append(audio_source)
        return audio_source

    def create_audio_buffer(self, file_path: Path = None) -> AudioBuffer:
        contexts = [sound_renderer.context for sound_renderer in self.sound_renderers]
        buffer_ids = [0] * len(self.sound_renderers)
        for i, sound_renderer in enumerate(self.sound_renderers):
            buffer_ids[i] = sound_renderer.create_buffer()
        audio_buffer = AudioBuffer(contexts, buffer_ids)
        if file_path is not None:
            audio_buffer.register_sound(file_path)
            self.sound_buffers[file_path.name] = audio_buffer
        self.audio_buffers.append(audio_buffer)
        return audio_buffer

    def is_playing(self, source: AudioSource) -> bool:
        ans = False
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            ans = ans or sound_renderer.is_playing(source_id)
        return ans
    
    def play(self, source: AudioSource, buffer: AudioBuffer, x: float, y: float, loop: bool) -> None:
        self.play3d(source, buffer, x, 0, y, loop)

    def play_default_render(self, source: AudioSource, buffer: AudioBuffer, x: float, y: float, loop: bool) -> None:
        if self.default_renderer:
            i = self.default_renderer_index
            source_id = source.get_source_ids()[i]
            buffer_id = buffer.get_buffers()[i]
            # fixme
            self.default_renderer.play2(source_id, buffer_id, x, 0, y, loop)

    def play3d(self, source: AudioSource, buffer: AudioBuffer, x: float, y: float, z: float, loop: bool) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            buffer_id = buffer.get_buffers()[i]
            sound_renderer.play2(source_id, buffer_id, x, y, z, loop)

    def stop(self, source: AudioSource) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.stop(source_id)

    def set_source_pos(self, source: AudioSource, x: float, y: float) -> None:
        self.set_source_pos3d(source, x, 0, y)

    def set_source_pos3d(self, source: AudioSource, x: float, y: float, z: float) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            set_source_attribute(source_id, al.AL_POSITION, [x, y, z], context=sound_renderer.context)

    def set_source_gain(self, source: AudioSource, gain: float) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            set_source_attribute(source_id, al.AL_GAIN, gain, context=sound_renderer.context)

    def set_source_pitch(self, source: AudioSource, pitch: float) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            set_source_attribute(source_id, al.AL_PITCH, pitch, context=sound_renderer.context)

    def get_sound_buffer(self, sound_name: str) -> AudioBuffer:
        return self.sound_buffers.get(sound_name)

    def sample_audio(self, dtype: type = al.ALfloat, render_size: int = 800, nchannels: int = 2) -> np.ndarray:
        if not self.virtual_renderer:
            raise ValueError("Virtual renderer not set")
        return self.virtual_renderer.sample_audio(dtype, render_size, nchannels)
    
    def remove_source(self, source: AudioSource) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.delete_source(source_id)
        self.audio_sources.remove(source)

    def playback(self, source: AudioSource, format: int, audio_sample: bytes, sample_rate: int) -> None:
        for i, sound_renderer in enumerate(self.sound_renderers):
            source_id = source.get_source_ids()[i]
            sound_renderer.playback(source_id, format, audio_sample, sample_rate)

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
