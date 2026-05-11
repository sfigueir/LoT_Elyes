from . import config
from .syntax import (
    MOVE_AND_PLAY, PLAY, MOVE, REPEAT, REPEAT_JUMP,
    REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL, REFLECT,
    MIRROR, MIRROR_BOUNCE, SUB, POINTER, REFERENCE,
    REPEAT_CHUNK, Prog
)


def size(program: Prog):
# the size of a program is the sum of the size of its instructions.
# each instruction's size is defined as follows:
    output = 0
    for instruction in program:
        match instruction:
            case MOVE_AND_PLAY(n):
                output += config.size_MOVE_AND_PLAY(n)
            case PLAY(n):
                output += config.size_PLAY(n)
            case MOVE(n):
                output += config.size_MOVE(n)
            case REPEAT(n,p):
                output += config.size_REPEAT(n)[0] + config.size_REPEAT(n)[1]*size(p)
                # output += len(str(n)) + size(p)
            case REPEAT_JUMP(n,p,j):
                output += config.size_REPEAT_JUMP(n)[0] + config.size_REPEAT_JUMP(n)[1]*size([j]) + config.size_REPEAT_JUMP(n)[2]*size(p)
                # output += len(str(n)) + size([j]) + size(p) 
            case REPEAT_APPLY_NOTES(n,p,a):
                output += config.size_REPEAT_APPLY_NOTES(n)[0] + config.size_REPEAT_APPLY_NOTES(n)[1]*size([a]) + config.size_REPEAT_APPLY_NOTES(n)[2]*size(p)
                # output += len(str(n)) + size([a]) + size(p)
            case REPEAT_APPLY_PEVAL(n,p,a):
                output += config.size_REPEAT_APPLY_PEVAL(n)[0] + config.size_REPEAT_APPLY_PEVAL(n)[1]*size([a]) + config.size_REPEAT_APPLY_PEVAL(n)[2]*size(p)
                # output += len(str(n)) + size([a]) + size(p)
            case REFLECT(n): #only for BASE=8
                output += config.size_REFLECT(n) 
            case MIRROR(P): 
                output += config.size_MIRROR[0] + config.size_MIRROR[1]*size(P)
            case MIRROR_BOUNCE(P): 
                output += config.size_MIRROR_BOUNCE[0] + config.size_MIRROR_BOUNCE[1]*size(P)
            case SUB(start,P): 
                output += config.size_SUB(start)[0] + config.size_SUB(start)[1]*size(P)
            case POINTER(n): 
                output += config.size_POINTERS
            case REFERENCE(_,w): 
                output += w
            case REPEAT_CHUNK(n,p):
                output += config.size_REPEAT_CHUNK(n)[0] + config.size_REPEAT_CHUNK(n)[1]*size(p)
    return(output)


def size_with_pointers(program,list_of_references):
    return(size(program) + sum([size([p]) for p in list_of_references]))

def size_p (prog):
# returns the size of the program after factorizing with pointers
  return size_with_pointers(add_pointers_to_program(prog)[0],add_pointers_to_program(prog)[1])

def first_instruction_is_a_repetition(program: Prog):
    output = True
    first_instruction = program[0]
    match first_instruction:
        case MOVE_AND_PLAY(n):
            output = False
        case PLAY(n):
            output = False
        case MOVE(n):
            output = False
    return output

def all_programs_start_with_repetitions(d:[Prog]):
    output = True
    for P in d:
        if not first_instruction_is_a_repetition(P):
            output = False
    return output

def is_a_repetition(program):
    if len(program)>1:
        return(False)
    else:
        match program[0]:
            case REPEAT(n,P):
                return(True)
            case REPEAT_JUMP(n,P,x): 
                return(True)
            case REPEAT_APPLY_NOTES(n,P,x): 
                return(True)
            case REPEAT_APPLY_PEVAL(n,P,x): 
                return(True)
            case REPEAT_CHUNK(n,P):
                return(True)
            case other:
                return(False)

def set_parameter_of_repetition(program,m):
# used in occam_razor
    match program[0]:
        case REPEAT(n,P):
            return([REPEAT(m,P)])
        case REPEAT_JUMP(n,P,x): 
            return([REPEAT_JUMP(m,P,x)])
        case REPEAT_APPLY_NOTES(n,P,x): 
            return([REPEAT_APPLY_NOTES(m,P,x)])
        case REPEAT_APPLY_PEVAL(n,P,x): 
            return([REPEAT_APPLY_PEVAL(m,P,x)])
        case REPEAT_CHUNK(n,P):
            return([REPEAT_CHUNK(m,P)])


def get_program_parameter(instruction):
    match instruction:
        case REPEAT(n,P):
            return(P)
        case REPEAT_JUMP(n,P,x): 
            return(P)
        case REPEAT_APPLY_NOTES(n,P,x): 
            return(P)
        case REPEAT_APPLY_PEVAL(n,P,x): 
            return(P)
        case MIRROR(P): 
            return(P)
        case MIRROR_BOUNCE(P): 
            return(P)
        case SUB(n,P):
            return(P)
        case REPEAT_CHUNK(n,P):
            return(P)
        case other:
            return([])

def subprograms(program):
    if program == []:
        return([])
    else:
        list_of_subprograms = []
        for instruction in program:
            P = get_program_parameter(instruction)
            if P != []:
            # match instruction:
            #     case REPEAT(n,P) | REPEAT_JUMP(n,P,x) | REPEAT_APPLY_NOTES(n,P,x) | REPEAT_APPLY_PEVAL(n,P,x) | MIRROR(P) | SUB(n,P):
                
                list_of_subprograms += [instruction]
                list_of_subprograms += subprograms(P)
        return(list_of_subprograms)


def depth(program):
    if program == []:
        return(0)
    else:
        list_of_depths = []
        for instruction in program:
            P = get_program_parameter(instruction)
            if P != []:
            # match instruction:
            #     case REPEAT(n,P):
                list_of_depths += [1+depth(P)]
        if list_of_depths==[]:
            return(0)
        else:
            return(max(list_of_depths))

def subprograms_sorted(program):
    l = sorted(subprograms(program),key=lambda x: depth([x]), reverse=True)
    return(l)

def repeated_subprograms(program):
    l2 = []
    l = subprograms_sorted(program)
    for x in l:
        if l.count(x)>1 and x not in l2:
            l2 += [x]
    # Now remove Q from l2 if there is P in l2 such that Q is a subprogram of P
    # We need a list of subprograms l2 which is an antichain under subprogram inclusion
    # l3 = []
    # for x in l2:
    #     add_it = True
    #     for y in l2:
    #         if x != y and x in subprograms([y]):
    #             add_it = False
    #     if add_it == True:
    #         l3 += [x]
    return(l2)

def replace_subprograms_by_pointer(program,subprogram,points_to):
    if program == []:
        return([])
    else:
        new_program = []
        for instruction in program:
            if [instruction] == subprogram:
                new_program += [POINTER(points_to)]
            else:
                match instruction:
                    case REPEAT(n,P):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [REPEAT(n,Q)]
                    case REPEAT_JUMP(n,P):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [REPEAT_JUMP(n,Q)]
                    case REPEAT_APPLY_NOTES(n,P,x):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [REPEAT_APPLY_NOTES(n,Q,x)]
                    case REPEAT_APPLY_PEVAL(n,P,x):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [REPEAT_APPLY_PEVAL(n,Q,x)]
                    case MIRROR(P):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [MIRROR(Q)]
                    case MIRROR_BOUNCE(P):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [MIRROR_BOUNCE(Q)]
                    case SUB(n,P):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [SUB(n,Q)]
                    case REPEAT_CHUNK(n,P):
                        Q = replace_subprograms_by_pointer(P,subprogram,points_to)
                        new_program += [REPEAT_CHUNK(n,Q)]
                    case other:
                        new_program += [instruction]       
        return(new_program)    


def add_pointers_to_program(program):
# returns the program with references and the list of list_of_references in order
    repeated = repeated_subprograms(program)
    unused_pointers = []
    for i in range(len(repeated)):
        program_before = program
        program_after = replace_subprograms_by_pointer(program_before,[repeated[i]],i)
        if program_before == program_after:
            # There was no replacement. 
            # This can happen because of the order in which we replace subprograms by pointers
            unused_pointers += [i]
        program = program_after
    repeated_used = [repeated[j] for j in range(len(repeated)) if j not in unused_pointers]
    return(program,repeated_used)



def show_with_pointers2(x, start="", tab=1):
    (P,list_of_references) = x
    show_without_pointers(P, start)
    if list_of_references != []:
        print("\nwhere")
        for x in list_of_references:
            print("\nP"+str(list_of_references.index(x))+":")
            show([x])
        print("\nTotal size (with pointers) =",size_with_pointers(P,list_of_references),"\n")


def show_with_pointers(program, start="", tab=1):
    (P,list_of_references) = add_pointers_to_program(program)
    show_without_pointers(P, start)
    if list_of_references != []:
        print("\nwhere")
        for x in list_of_references:
            print("\nP"+str(list_of_references.index(x))+":")
            show([x])
        print("\nTotal size (with pointers) =",size_with_pointers(P,list_of_references),"\n")
