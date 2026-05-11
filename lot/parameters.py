import json
import math
from . import config
from .syntax import MOVE_AND_PLAY, PLAY, MOVE, REFLECT, possible_refl
from .errors import LoTConfigError


def set_parameters(file_path: str):
    config.GLOBAL_CONFIG = {
        "BASE": "8",
        "MOVE_AND_PLAY":      ("True", "lambda n: 1"),
        "PLAY":               ("True", "lambda n: 1"),
        "MOVE":               ("True", "lambda n: 1"),
        "REPEAT":             ("True", "lambda n: (int(math.log2(n)),1)"),
        "REPEAT_JUMP":        ("False", "None"),
        "REPEAT_APPLY_NOTES": ("True", "lambda n: (int(math.log2(n)),1,1)"),
        "REPEAT_APPLY_PEVAL": ("True", "lambda n: (int(math.log2(n)),1,1)"),
        "REFLECT":            ("True",  "lambda n: 1"),
        "MIRROR":             ("False", "None"),
        "MIRROR_BOUNCE":      ("False", "None"),
        "SUB":                ("False", "None"),
        "REPEAT_CHUNKS":      ("False", "None"),
        "POINTERS":           ("False", "None")
    }

    """
    Reads parameters from a JSON file and sets them globally.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Map JSON list/array to Python Tuples for the existing logic
        # We assume the JSON has keys matching the internal names
        for key in config.GLOBAL_CONFIG.keys():
            if key in data:
                val = data[key]
                if isinstance(val, list):
                    config.GLOBAL_CONFIG[key] = tuple(val)
                else:
                    config.GLOBAL_CONFIG[key] = val
        
        print(f"Parameters successfully loaded from {file_path}")
        
    except FileNotFoundError as e:
        raise LoTConfigError(f"Configuration file not found: {file_path}") from e
    except json.JSONDecodeError as e:
        raise LoTConfigError(f"Failed to decode JSON from {file_path}") from e

    config.BASE                        = eval ( config.GLOBAL_CONFIG["BASE"] )
    config.include_MOVE_AND_PLAY       = eval ( config.GLOBAL_CONFIG["MOVE_AND_PLAY"][0] )
    config.include_PLAY                = eval ( config.GLOBAL_CONFIG["PLAY"][0] )
    config.include_REPEAT              = eval ( config.GLOBAL_CONFIG["REPEAT"][0] )
    config.include_REPEAT_JUMP         = eval ( "False" )
    config.include_REPEAT_APPLY_NOTES  = eval ( config.GLOBAL_CONFIG["REPEAT_APPLY_NOTES"][0] )
    config.include_REPEAT_APPLY_PEVAL  = eval ( config.GLOBAL_CONFIG["REPEAT_APPLY_PEVAL"][0] )
    config.include_REFLECT             = eval ( config.GLOBAL_CONFIG["REFLECT"][0] )
    config.include_MIRROR              = eval ( config.GLOBAL_CONFIG["MIRROR"][0] )
    config.include_MIRROR_BOUNCE       = eval ( config.GLOBAL_CONFIG["MIRROR_BOUNCE"][0] )
    config.include_SUB                 = eval ( config.GLOBAL_CONFIG["SUB"][0] )
    config.with_POINTERS               = eval ( config.GLOBAL_CONFIG["POINTERS"][0] )
    config.with_CHUNKS                 = eval ( config.GLOBAL_CONFIG["REPEAT_CHUNKS"][0] )
    config.size_MOVE_AND_PLAY          = eval ( config.GLOBAL_CONFIG["MOVE_AND_PLAY"][1] )
    config.size_PLAY                   = eval ( config.GLOBAL_CONFIG["PLAY"][1] )
    config.size_MOVE                   = eval ( config.GLOBAL_CONFIG["MOVE"][1] )
    config.size_REPEAT                 = eval ( config.GLOBAL_CONFIG["REPEAT"][1] )
    config.size_REPEAT_JUMP            = eval ( "None" )
    config.size_REPEAT_APPLY_NOTES     = eval ( config.GLOBAL_CONFIG["REPEAT_APPLY_NOTES"][1] )
    config.size_REPEAT_APPLY_PEVAL     = eval ( config.GLOBAL_CONFIG["REPEAT_APPLY_PEVAL"][1] )
    config.size_REFLECT                = eval ( config.GLOBAL_CONFIG["REFLECT"][1] )
    config.size_MIRROR                 = eval ( config.GLOBAL_CONFIG["MIRROR"][1] )
    config.size_MIRROR_BOUNCE          = eval ( config.GLOBAL_CONFIG["MIRROR_BOUNCE"][1] )
    config.size_SUB                    = eval ( config.GLOBAL_CONFIG["SUB"][1] )
    config.size_REPEAT_CHUNK           = eval ( config.GLOBAL_CONFIG["REPEAT_CHUNKS"][1] )
    config.size_POINTERS               = eval ( config.GLOBAL_CONFIG["POINTERS"][1] )
    config.atomic_instructions = ( 
                            ([MOVE_AND_PLAY(i)  for i in range(1+config.BASE//2)]         if config.include_MOVE_AND_PLAY    else []) +  
                            ([MOVE_AND_PLAY(-i) for i in range(1,(1+(config.BASE-1)//2))] if config.include_MOVE_AND_PLAY    else []) + 
                            ([PLAY(i)           for i in range(0,config.BASE)]            if config.include_PLAY             else []) +
                            ([REFLECT(i)        for i in possible_refl]            if config.include_REFLECT          else [])
                            )
    if config.atomic_instructions==[]:
        raise LoTConfigError("No atomic instructions! Check settings.")

    config.possible_jumps = ( 
                            [MOVE(i)  for i in range(0,1+config.BASE//2)] + 
                            [MOVE(-i) for i in range(1,(1+(config.BASE-1)//2))]
                            )

    config.possible_appl_notes = ( 
                            [MOVE_AND_PLAY(i)  for i in range(0,1+config.BASE//2)]       + 
                            [MOVE_AND_PLAY(-i) for i in range(1,(1+(config.BASE-1)//2))] +
                            ([REFLECT(i)       for i in range(3)] if config.include_REFLECT else [])
                            )

    config.possible_appl_peval = (
                            [MOVE(i)     for i in range(0,1+config.BASE//2)]       + 
                            [MOVE(-i)    for i in range(1,(1+(config.BASE-1)//2))] +
                            ([REFLECT(i) for i in range(3)] if config.include_REFLECT else [])
                            )
