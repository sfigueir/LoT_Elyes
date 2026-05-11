from __future__ import annotations
from dataclasses import dataclass
from . import config


@dataclass
class MOVE_AND_PLAY: 
    n: int

# PLAY: Play constant n (and don't move)
@dataclass
class PLAY: 
    n: int

# MOVE: Move the peval n positions (and don't play)
@dataclass
class MOVE: 
    n: int

# REPEAT: Repeat n times the program P (keeping track of pevals)
@dataclass
class REPEAT: 
    n: int
    P: Prog

# REPEAT_JUMP: Execute P in peval. Suppose the output is o_1 and the peval n_1 
# Then, it applies instruction 'appl' to n_1, and executes P in n1 obtaining output o_2 and peval n_2
# Then, it applies instruction 'appl' to n_2, and executes P in n2 obtaining output o_3 and peval n_3
# And so on
# At the end, it outputs o_1 o_2 ... o_n. 
# The peval after the execution is the last peval in this process, namely n_n
# FORGET ABOUT THIS ONE
@dataclass
class REPEAT_JUMP: 
    n: int
    P: Prog
    jump: config.possible_jumps

# REPEAT_APPLY_NOTES: Execute P in peval. Suppose the output is o_1. 
# Then, it applies instruction 'appl' to each note of o_1, obtaining say o_2
# Then, it applies instruction 'appl' to each note of o_2, obtaining say o_3... and so on
# At the end, it outputs o_1 o_2 ... o_n
# The peval after the execution is the last note played in this process, namely on
# This instruction is analogous to the repeat with <appl> in the language of geometry 
@dataclass
class REPEAT_APPLY_NOTES: 
    n: int
    p: Prog
    appl: config.possible_appl_notes

# REPEAT_APPLY_PEVAL: Execute P in peval, say m_1. Suppose the output is o_1 
# Then, it applies instruction 'appl' to m_1, obtaining a new point, say m_2, and executes P in m_2 obtaining output o_2 
# Then, it applies instruction 'appl' to m_2, obtaining a new point, say m_3, and executes P in m_3 obtaining output o_3 
# And so on
# At the end, it outputs o_1 o_2 ... o_n
# The peval after the execution is the last note played in this process, namely o_n
# This instruction is analogous to the repeat with {appl} in the language of geometry 
@dataclass
class REPEAT_APPLY_PEVAL: 
    n: int
    P: Prog
    jump: config.possible_apply_peval

# REFLECT: Reflect on an axes and play note. 
# This is as in the language of geometry. 
# Probably not used for music. Added for completeness... Legacy
# It only works for BASE=8. 
# Axes are: H=0, V=1, A=2, B=3, as in the Language of Geometry
@dataclass 
class REFLECT: 
    n: int

# MIRROR: obvious
@dataclass
class MIRROR: 
    P: Prog

# MIRROR_BOUNCE: does not mirror the last symbol, eg, MIRROR_BOUNCE of "012" is "01210"
@dataclass
class MIRROR_BOUNCE: 
    P: Prog

# SUB: execute P from 'start'. 
# No changes in the current peval after the execution
@dataclass
class SUB: 
    start: int
    P: Prog

# Not an instruction. Just a marker to refer to a program. 
# Only used for representing differently a program. 
# Formally, it is not part of the grammar - but it was easier to include it here
# FORGET ABOUT THIS
@dataclass
class POINTER: 
    points_to: int

# This is used for the Relative complexity of x given y. 
# It hardwires the string 'refers_to', of weight 'weight'.
# Typically, 'refers_to' will be a substring of y of length >1 and 'weight' is constant or
# smaller than the complexity of 'refers_to'. This depends on the semantics to be given.
# FORGET ABOUT THIS
@dataclass
class REFERENCE: 
    refers_to: str
    weight: int

# REPEAT: Repeat n times the program P (keeping track of pevals)
# Exactly equal to the REPEAT. Used only for marking applications in the context of chunks. Not really needed.@dataclass
@dataclass
class REPEAT_CHUNK: 
    n: int
    P: Prog


Instr = PLAY | REPEAT | REPEAT_JUMP | MOVE_AND_PLAY | REPEAT_APPLY_NOTES | REPEAT_APPLY_PEVAL | MOVE | MIRROR | MIRROR_BOUNCE | SUB | REFERENCE | REPEAT_CHUNK
Prog  = [Instr]

possible_refl       = [0,1,2,3] 
# only for BASE=8. 
# H=0 (horizontal), 
# V=1 (vertical), 
# A=2, 
# B=3
axis = ["H","V","A","B"]
