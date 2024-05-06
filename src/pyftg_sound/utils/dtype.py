import numpy as np

from pyftg_sound.openal import al

dtype_map = {
    al.ALbyte: np.int8,
    al.ALubyte: np.uint8,
    al.ALshort: np.int16,
    al.ALushort: np.uint16,
    al.ALint: np.int32,
    al.ALuint: np.uint32,
    al.ALfloat: np.float32,
    al.ALdouble: np.float64,
}
