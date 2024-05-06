import ctypes
from typing import List

import numpy as np

from pyftg_sound.openal import al, alc, soft
from pyftg_sound.utils.dtype import dtype_map
from pyftg_sound.utils.openal import set_source_attribute


class SoundRenderer:
    device = None
    context = None

    def __init__(self, device, context) -> None:
        self.device = device
        self.context = context

    @staticmethod
    def create_default_renderer():
        device = alc.alcOpenDevice(None)
        context = alc.alcCreateContext(device, None)
        return SoundRenderer(device, context)

    @staticmethod
    def create_virtual_renderer(format: int = soft.ALC_FLOAT_SOFT, channel: int = soft.ALC_STEREO_SOFT, sample_rate: int = 48000):
        device = soft.alcLoopbackOpenDeviceSOFT(None)
        attrs = [
            soft.ALC_FORMAT_TYPE_SOFT, format, soft.ALC_FORMAT_CHANNELS_SOFT,
            channel, alc.ALC_FREQUENCY, sample_rate, 0
        ]
        attrs_c = (al.ALint * len(attrs))(*attrs)
        context = alc.alcCreateContext(device, attrs_c)
        return SoundRenderer(device, context)

    def set(self) -> None:
        alc.alcMakeContextCurrent(self.context)

    def create_source(self, attrs: dict) -> int:
        self.set()
        source = al.ALuint(0)
        al.alGenSources(1, source)
        for attr, value in attrs.items():
            set_source_attribute(source, attr, value)
        return source.value
        
    def create_buffer(self) -> int:
        self.set()
        buffer = al.ALuint(0)
        al.alGenBuffers(1, buffer)
        return buffer.value

    def al_listener_fv(self, param: int, values: List[float]) -> None:
        self.set()
        values_arr = (al.ALfloat * len(values))(*values)
        al.alListenerfv(param, values_arr)

    def play(self, source_id: int) -> None:
        self.set()
        al.alSourcePlay(source_id)

    def is_playing(self, source_id: int) -> bool:
        self.set()
        state = al.ALint(0)
        al.alGetSourcei(source_id, al.AL_SOURCE_STATE, state)
        return state.value == al.AL_PLAYING

    def stop(self, source_id: int) -> None:
        self.set()
        if self.is_playing(source_id):
            al.alSourceStop(source_id)

    def play2(self, source_id: int, buffer_id: int, x: float, y: float, z: float, loop: bool) -> None:
        self.set()
        if self.is_playing(source_id):
            self.stop(source_id)
        set_source_attribute(source_id, al.AL_BUFFER, buffer_id)
        set_source_attribute(source_id, al.AL_POSITION, [x, y, z])
        set_source_attribute(source_id, al.AL_LOOPING, al.AL_TRUE if loop else al.AL_FALSE)
        self.play(source_id)

    def delete_source(self, source_id: int) -> None:
        self.set()
        al.alDeleteSources(1, al.ALuint(source_id))

    def delete_buffer(self, buffer_id: int) -> None:
        self.set()
        al.alDeleteBuffers(1, al.ALuint(buffer_id))

    def close(self) -> None:
        self.set()
        alc.alcDestroyContext(self.context)
        alc.alcCloseDevice(self.device)

    def sample_audio(self, dtype: type, render_size: int, nchannels: int) -> np.ndarray:
        self.set()
        audio_sample_type = dtype * render_size * nchannels
        audio_sample_ptr = ctypes.cast(audio_sample_type(), ctypes.c_void_p)
        soft.alcRenderSamplesSOFT(self.device, audio_sample_ptr, al.ALsizei(render_size))
        separated_channel_audio = np.zeros((nchannels, render_size), dtype=dtype_map[dtype])
        separated_channel_audio[:, :] = ctypes.cast(audio_sample_ptr, ctypes.POINTER(audio_sample_type)).contents
        return separated_channel_audio
    
    def get_processed_buffers(self, source_id: int) -> int:
        self.set()
        processed_buffers = al.ALint(0)
        al.alGetSourcei(source_id, al.AL_BUFFERS_PROCESSED, processed_buffers)
        return processed_buffers.value
    
    def playback(self, source_id: int, format: int, audio_sample: bytes, sample_rate: int) -> None:
        self.set()
        buffer = al.ALuint(0)
        if self.get_processed_buffers(source_id) > 0:
            al.alSourceUnqueueBuffers(source_id, 1, buffer)
        else:
            al.alGenBuffers(1, buffer)
        al.alBufferData(buffer, format, audio_sample, len(audio_sample), sample_rate)
        al.alSourceQueueBuffers(source_id, 1, buffer)
        if not self.is_playing(source_id):
            self.play(source_id)

    def stop_playback(self, source_id: int) -> None:
        self.set()
        buffer = al.ALuint(0)
        for _ in range(self.get_processed_buffers(source_id)):
            al.alSourceUnqueueBuffers(source_id, 1, buffer)
            al.alDeleteBuffers(1, buffer)
        self.stop(source_id)
        self.al_source_i(source_id, al.AL_BUFFER, al.AL_NONE)
