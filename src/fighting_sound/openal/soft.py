import ctypes

from . import dll
from .alc import ALCchar, ALCdevice, ALCenum, ALCint, ALCsizei, ALCvoid
from .log import logger

__all__ = []

_bind = dll.bind_function

ALC_BYTE_SOFT = 0x1400
ALC_UNSIGNED_BYTE_SOFT = 0x1401
ALC_SHORT_SOFT = 0x1402
ALC_UNSIGNED_SHORT_SOFT = 0x1403
ALC_INT_SOFT = 0x1404
ALC_UNSIGNED_INT_SOFT = 0x1405
ALC_FLOAT_SOFT = 0x1406

ALC_MONO_SOFT = 0x1500
ALC_STEREO_SOFT = 0x1501
ALC_QUAD_SOFT = 0x1503
ALC_5POINT1_SOFT = 0x1504
ALC_6POINT1_SOFT = 0x1505
ALC_7POINT1_SOFT = 0x1506

ALC_FORMAT_CHANNELS_SOFT = 0x1990
ALC_FORMAT_TYPE_SOFT = 0x1991

try:
    alcLoopbackOpenDeviceSOFT = _bind("alcLoopbackOpenDeviceSOFT", [ctypes.POINTER(ALCchar)], ctypes.POINTER(ALCdevice))
    alcGetStringiSOFT = _bind("alcGetStringiSOFT", [ctypes.POINTER(ALCdevice),
                                                      ctypes.POINTER(ALCenum),
                                                      ctypes.POINTER(ALCsizei)])
    alcResetDeviceSOFT = _bind("alcResetDeviceSOFT", [ctypes.POINTER(ALCdevice),
                                                      ctypes.POINTER(ALCint)])
    alcRenderSamplesSOFT = _bind("alcRenderSamplesSOFT", [ctypes.POINTER(ALCdevice), ctypes.POINTER(ALCvoid), ALCsizei])
except AttributeError:
    logger.warning("OpenAL-Soft functions could not be bound")
else:
    __all__.extend(("alcLoopbackOpenDeviceSOFT", "alcGetStringiSOFT", "alcResetDeviceSOFT", "alcRenderSamplesSOFT"))
