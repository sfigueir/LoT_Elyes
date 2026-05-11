from . import config
from .errors import LoTSemanticsError
from .syntax import (
    MOVE_AND_PLAY, PLAY, MOVE, REPEAT, REPEAT_JUMP,
    REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL, REFLECT,
    MIRROR, MIRROR_BOUNCE, SUB, REFERENCE, REPEAT_CHUNK, Prog
)


def exe(program: Prog, start: int):
# Given a program 'program' and a peval 'start' (= number in 0..BASE-1), 
# return the pair (output,current_point) where
# 'output' is the sequence described when executing 'program' in peval='start'
# and 'current_point' is the peval after such execution
    output = ""
    current_point = start
    for instruction in program:
        match instruction:
            case MOVE_AND_PLAY(n):
                current_point = (current_point + n) % config.BASE
                output += str(current_point)
            case PLAY(n):
                output += str(n)
            case MOVE(n):
                current_point = (current_point + n) % config.BASE
            case REPEAT(n,P):
                for i in range(n):
                    (s,ending_point) = exe(P,current_point)
                    output += s
                    current_point = ending_point
            case REPEAT_JUMP(n,P,jump):
                for i in range(n):
                    (s,ending_point) = exe(P,current_point)
                    output += s
                    current_point = exe([jump],ending_point)[1]
            case REPEAT_APPLY_NOTES(n,P,appl):
                for i in range(n):
                    if i == 0:
                        (s,ending_point) = exe(P,current_point)
                        t = s
                    else:
                        t = "".join([exe([appl],int(s[j]))[0] for j in range(len(s))])
                        s = t
                    output += t
                    current_point = ending_point
                current_point = int(output[-1]) # this is the semantics in the lang. Geom.
            case REPEAT_APPLY_PEVAL(n,P,jump):
                for i in range(n):
                    (s,ending_point) = exe(P,current_point)
                    output += s
                    current_point = exe([jump],current_point)[1]
                current_point = int(output[-1]) # this is the semantics in the lang. Geom.
            case REFLECT(n): #only for BASE=8
                if config.BASE!=8:
                    raise LoTSemanticsError("For using REFLECT, the value of BASE should be 8")
                if n==0:
                    current_point = (3-current_point) % 8
                elif n==1:
                    current_point = (7-current_point) % 8
                elif n==2:
                    current_point = (5-current_point) % 8
                else: # n==3
                    current_point = (1-current_point) % 8
                output += str(current_point)
            case MIRROR(P):
                (t,_) = exe(P,current_point)
                output += t + t[::-1]  
                current_point = int(output[-1])
            case MIRROR_BOUNCE(P):
                (t,_) = exe(P,current_point)
                output += t + t[::-1][1:]  
                current_point = int(output[-1])
            case SUB(start,P):
                (t,_) = exe(P,start)
                output += t   
                current_point = current_point #no change in current point
            case REFERENCE(s,_):
                output = s
                current_point = current_point #no change in current point
            case REPEAT_CHUNK(n,P): # exactly equal to the REPEAT. Used only for marking applications in the context of chunks. Not really needed.
                for i in range(n):
                    (s,ending_point) = exe(P,current_point)
                    output += s
                    current_point = ending_point
            case REPEAT_CHUNK(n,P):
                for i in range(n):
                    (s,ending_point) = exe(P,current_point)
                    output += s
                    current_point = ending_point
    return((output,current_point))

def exe_with_parenthesis(program: Prog, start: int):
    output = ""
    current_point = start
    for instruction in program:
        match instruction:
            case MOVE_AND_PLAY(n):
                current_point = (current_point + n) % config.BASE
                output += str(current_point)
            case PLAY(n):
                output += str(n)
            case MOVE(n):
                current_point = (current_point + n) % config.BASE
            case REPEAT(n,P):
                output += "("
                for i in range(n):
                    (s,ending_point) = exe_with_parenthesis(P,current_point)
                    # output += "(" + s + ")"
                    output += s
                    current_point = ending_point
                # output = "(" + output + ")"
                output += ")"
            case REPEAT_JUMP(n,P,jump):
                output += "("
                for i in range(n):
                    (s,ending_point) = exe_with_parenthesis(P,current_point)
                    # output += "(" + s + ")"
                    output += s
                    current_point = exe_with_parenthesis([jump],ending_point)[1]
                output += ")"
                # output = "(" + output + ")"
            case REPEAT_APPLY_NOTES(n,P,appl):
                output += "("
                for i in range(n):
                    if i == 0:
                        (s,ending_point) = exe_with_parenthesis(P,current_point)
                        t = s
                    else:
                        t = "".join([exe_with_parenthesis([appl],int(s[j]))[0] if s[j].isdigit() else s[j] for j in range(len(s))])
                        s = t
                    # output += "(" + t + ")"
                    output += t
                    current_point = ending_point
                # current_point = int(output[-1]) # this is the semantics in the lang. Geom.
                # output = "(" + output + ")"
                output += ")"
                current_point = rightmost_digit(output)
            case REPEAT_APPLY_PEVAL(n,P,jump):
                for i in range(n):
                    (s,ending_point) = exe_with_parenthesis(P,current_point)
                    output += "(" + s + ")"
                    current_point = exe_with_parenthesis([jump],current_point)[1]
                # current_point = int(output[-1]) # this is the semantics in the lang. Geom.
                current_point = rightmost_digit(output)
            # case REFLECT(n): #only for BASE=8
            #     if BASE!=8:
            #         print("For using REFLECT, the value of BASE should be 8")
            #         exit()
            #     if n==0:
            #         current_point = (3-current_point) % 8
            #     elif n==1:
            #         current_point = (7-current_point) % 8
            #     elif n==2:
            #         current_point = (5-current_point) % 8
            #     else: # n==3
            #         current_point = (1-current_point) % 8
            #     output += str(current_point)
            # case MIRROR(P):
            #     (t,_) = exe_with_parenthesis(P,current_point)
            #     output += t + t[::-1]  
            #     current_point = int(output[-1])
            # case MIRROR_BOUNCE(P):
            #     (t,_) = exe_with_parenthesis(P,current_point)
            #     output += t + t[::-1][1:]  
            #     current_point = int(output[-1])
            # case SUB(start,P):
            #     (t,_) = exe_with_parenthesis(P,start)
            #     output += t   
            #     current_point = current_point #no change in current point
            # case REFERENCE(s,_):
            #     output = s
            #     current_point = current_point #no change in current point
            # case REPEAT_CHUNK(n,P): # exactly equal to the REPEAT. Used only for marking applications in the context of chunks. Not really needed.
            #     for i in range(n):
            #         (s,ending_point) = exe_with_parenthesis(P,current_point)
            #         output += s
            #         current_point = ending_point
            # case REPEAT_CHUNK(n,P):
            #     for i in range(n):
            #         (s,ending_point) = exe_with_parenthesis(P,current_point)
            #         output += s
            #         current_point = ending_point
    # if len(output)==3 and output[0]=='(' and output[2]==')':
    #     output = output[1]
    return((output,current_point))


def rightmost_digit(s):
    for c in reversed(s):
        if c.isdigit():
            return c
    return None  
