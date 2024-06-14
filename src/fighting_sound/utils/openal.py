from typing import Any, List

from fighting_sound.openal import al, alc

def set_source_list_attribute(source_id: int, attr: int, values: List):
    if all(isinstance(item, int) for item in values):
        func = al.alSource3i if len(values) == 3 else al.alSourceiv
        value_arr = (al.ALint * len(values))(*values)
        func(source_id, attr, *value_arr if len(values) == 3 else value_arr)
    elif all(isinstance(item, float) for item in values):
        func = al.alSource3f if len(values) == 3 else al.alSourcefv
        value_arr = (al.ALfloat * len(values))(*values)
        func(source_id, attr, *value_arr if len(values) == 3 else value_arr)
    else:
        raise ValueError("List should contain either all integers or all floats")


def set_source_attribute(source_id: int, attr: int, value: Any, context: alc.ALCcontext = None) -> None:
    if context:
        alc.alcMakeContextCurrent(context)
    
    if isinstance(value, int):
        al.alSourcei(source_id, attr, value)
    elif isinstance(value, float):
        al.alSourcef(source_id, attr, value)
    elif isinstance(value, list):
        set_source_list_attribute(source_id, attr, value)
    else:
        raise ValueError(f"Invalid value type: {type(value)}")
