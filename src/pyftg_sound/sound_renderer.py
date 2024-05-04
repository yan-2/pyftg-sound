import ctypes
from typing import List

import numpy as np

from pyftg_sound.config import SOUND_RENDER_SIZE, SOUND_SAMPLING_RATE
from pyftg_sound.openal import al, alc
from pyftg_sound.openal.constants import (ALC_FLOAT_SOFT,
                                          ALC_FORMAT_CHANNELS_SOFT,
                                          ALC_FORMAT_TYPE_SOFT, ALC_FREQUENCY,
                                          ALC_STEREO_SOFT)


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
        alc.alcMakeContextCurrent(context)
        return SoundRenderer(device, context)

    @staticmethod
    def create_virtual_renderer():
        device = alc.alcLoopbackOpenDeviceSOFT(None)
        attrs = [ALC_FORMAT_TYPE_SOFT, ALC_FLOAT_SOFT, ALC_FORMAT_CHANNELS_SOFT,
                 ALC_STEREO_SOFT, ALC_FREQUENCY, SOUND_SAMPLING_RATE, 0]
        attrs_c = al.ALint * len(attrs)
        attrs_c = attrs_c(*attrs)
        context = alc.alcCreateContext(device, attrs_c)
        return SoundRenderer(device, context)

    def set(self) -> None:
        alc.alcMakeContextCurrent(self.context)

    def set_listener_data(self) -> None:
        self.set()
        al.alListener3f(al.AL_POSITION, 0, 0, 0)
        al.alListener3f(al.AL_VELOCITY, 0, 0, 0)

    def play(self, source_id: int, buffer_id: int) -> None:
        self.set()
        al.alSourcei(source_id, al.AL_BUFFER, buffer_id)
        al.alSourcePlay(source_id)

    def stop(self, source_id: int) -> None:
        self.set()
        if self.is_playing(source_id):
            al.alSourceStop(source_id)
            al.alSourcei(source_id, al.AL_BUFFER, al.AL_NONE)

    def play(self, source_id: int, buffer_id: int, x: int, y: int, loop: bool) -> None:
        self.set()
        if self.is_playing(source_id):
            self.stop(source_id)
        al.alSourcei(source_id, al.AL_BUFFER, buffer_id)
        al.alSource3f(source_id, al.AL_POSITION, x, 0, 4)
        al.alSourcei(source_id, al.AL_LOOPING, int(loop))
        al.alSourcePlay(source_id)

    def get_source_gain(self, source_id: int) -> float:
        self.set()
        return al.alGetSourcef(source_id, al.AL_GAIN)

    def set_source_gain(self, source_id: int, gain: float) -> None:
        self.set()
        al.alSourcef(source_id, al.AL_GAIN, gain)

    def set_source_3f(self, source_id: int, param: int, x: int, y: int, z: int) -> None:
        self.set()
        al.alSource3f(source_id, param, x, y, z)

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

    def is_playing(self, source_id: int) -> bool:
        self.set()
        state = al.ALint(0)
        al.alGetSourcei(source_id, al.AL_SOURCE_STATE, state)
        return state.value == al.AL_PLAYING

    def al_listener_fv(self, param: int, values: List[float]) -> None:
        self.set()
        values_arr = (al.ALfloat * len(values))(*values)
        al.alListenerfv(param, values_arr)

    def sample_audio(self) -> np.ndarray[np.float32]:
        self.set()
        audio_data_type = al.ALfloat * SOUND_RENDER_SIZE * 2
        audio_sample = audio_data_type()
        audio_sample_pointer = ctypes.cast(audio_sample, ctypes.c_void_p)

        alc.alcRenderSamplesSOFT(self.device, audio_sample_pointer, al.ALsizei(SOUND_RENDER_SIZE))
        sampled_audio = ctypes.cast(audio_sample_pointer, ctypes.POINTER(audio_data_type)).contents

        separated_channel_audio = np.zeros((2, SOUND_RENDER_SIZE), dtype=np.float32)
        separated_channel_audio[0, :] = sampled_audio[0]
        separated_channel_audio[1, :] = sampled_audio[1]
        return separated_channel_audio
    
    def playback(self, source_id: int, audio_sample: bytes) -> None:
        self.set()
        
        queuedBuffers = al.ALint(0)
        processedBuffers = al.ALint(0)
        al.alGetSourcei(source_id, al.AL_BUFFERS_QUEUED, queuedBuffers)
        al.alGetSourcei(source_id, al.AL_BUFFERS_PROCESSED, processedBuffers)
        print(f"Queued Buffers: {queuedBuffers.value}")
        print(f"Processed Buffers: {processedBuffers.value}")

        if processedBuffers.value > 0:
            buffer = al.ALuint(0)
            al.alSourceUnqueueBuffers(source_id, 1, buffer)
            print(f"Unqueued Buffer: {buffer.value}")
        else:
            buffer = al.ALuint(0)
            al.alGenBuffers(1, buffer)
            print(f"Generated Buffer: {buffer.value}")

        al.alBufferData(buffer, al.AL_FORMAT_STEREO16, audio_sample, len(audio_sample), SOUND_SAMPLING_RATE)
        al.alSourceQueueBuffers(source_id, 1, buffer)
        print("Queued Buffer: {buffer.value}")
        state = al.ALint(0)
        al.alGetSourcei(source_id, al.AL_SOURCE_STATE, state)
        if state.value != al.AL_PLAYING:
            al.alSourcePlay(source_id)
            print(f"Played Source: {source_id}")

    def stop_playback(self, source_id: int) -> None:
        self.set()

        queuedBuffers = al.ALint(0)
        processedBuffers = al.ALint(0)
        al.alGetSourcei(source_id, al.AL_BUFFERS_QUEUED, queuedBuffers)
        al.alGetSourcei(source_id, al.AL_BUFFERS_PROCESSED, processedBuffers)

        bufferCount = queuedBuffers.value + processedBuffers.value

        buffer = al.ALuint(0)
        for _ in range(bufferCount):
            al.alSourceUnqueueBuffers(source_id, 1, buffer)
            al.alDeleteBuffers(1, buffer)
        
        al.alSourceStop(source_id)
        al.alSourcei(source_id, al.AL_BUFFER, al.AL_NONE)
        print(f"Clear Buffers: {bufferCount}")
