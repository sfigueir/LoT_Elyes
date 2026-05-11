from . import config
from .syntax import (
    MOVE_AND_PLAY, PLAY, MOVE, REPEAT, REPEAT_JUMP,
    REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL, REFLECT,
    MIRROR, MIRROR_BOUNCE, SUB, POINTER, REFERENCE, REPEAT_CHUNK, axis, Prog
)
from .semantics import exe
from .program_ops import size, add_pointers_to_program, size_with_pointers


def show(program: Prog, start="", tab=1):
    if config.with_POINTERS:
        show_with_pointers(program, start, tab)
    else:
        show_without_pointers(program, start, tab)


def show_without_pointers(program: Prog, start="", tab=1):
# renders the program in a nicer way 
# (one instruction per line and tabs for nested structures)
# it contemplates the occurrence of pointers (only for rendering, not part of the language)
    if start != "":
        print("\t\t << at",start,">>")
    for instruction in program:
        size_instruction = size([instruction])
        match instruction:
            case MOVE_AND_PLAY(n):
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"move",("+" if (n>0) else "")+str(n),"and play")
            case PLAY(n):
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"play",str(n))
            case MOVE(n):
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"move",("+" if (n>0) else "")+str(n))
            case REFLECT(n):
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"reflect",axis[n])
            case REPEAT(n,P):
                size_instruction -= config.size_REPEAT(n)[1]*size(P)
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"repeat",n,"times:")
                show_without_pointers(P,tab=tab+1)
            case REPEAT_JUMP(n,P,j):
                size_instruction -= config.size_REPEAT_JUMP(n)[1]*size(P)
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"repeat",n,"times:")
                show_without_pointers(P,tab=tab+1)
                match j:
                    case MOVE(n):
                        print("\t"+"    "*(tab+1),"move",("+" if (n>0) else "")+str(n))
            case REPEAT_APPLY_NOTES(n,P,a):
                size_instruction -= config.size_REPEAT_APPLY_NOTES(n)[2]*size(P)
                size_instruction -= config.size_REPEAT_APPLY_NOTES(n)[1]*size([a])
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"repeat",n,"times with application")
                match a:
                    case MOVE_AND_PLAY(n):
                        print("\t"+str('%.2f' % size([a]))+"\t"*tab,"of 'move",("+" if (n>0) else "")+str(n)+" and play' in notes:")
                    case MOVE(n):
                        print("\t"+str('%.2f' % size([a]))+"\t"*tab,"of 'move",("+" if (n>0) else "")+str(n)+"' in notes:")
                    case REFLECT(n):
                         # H=0, V=1, A=2, B=3, 
                        print("\t"+str(size([a]))+"\t"*tab,"of 'reflect "+axis[n]+"' in notes:")
                show_without_pointers(P,tab=tab+1)
            case REPEAT_APPLY_PEVAL(n,P,a):
                size_instruction -= config.size_REPEAT_APPLY_PEVAL(n)[2]*size(P)
                size_instruction -= config.size_REPEAT_APPLY_PEVAL(n)[1]*size([a])
                # print("\t"+str(round(size_instruction,2))+"\t"*tab,"repeat",n,"times with application2")
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"repeat",n,"times with application")
                match a:
                    case MOVE_AND_PLAY(n):
                        print("\t"+str('%.2f' % size([a]))+"\t"*tab,"of 'move",("+" if (n>0) else "")+str(n)+" and play' in peval:")
                    case MOVE(n):
                        print("\t"+str('%.2f' % size([a]))+"\t"*tab,"of 'move",("+" if (n>0) else "")+str(n)+"' in peval:")
                    case REFLECT(n):
                         # H=0, V=1, A=2, B=3, 
                        print("\t"+str(size([a]))+"\t"*tab,"of 'reflect "+axis[n]+"' in notes:")
                show_without_pointers(P,tab=tab+1)
            case MIRROR(P):
                size_instruction -= config.size_MIRROR[1]*size(P)
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"print and mirror:")
                show_without_pointers(P,tab=tab+1)
            case MIRROR_BOUNCE(P):
                size_instruction -= config.size_MIRROR_BOUNCE[1]*size(P)
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"print and mirror with bounce:")
                show_without_pointers(P,tab=tab+1)
            case SUB(start_sub,P):
                size_instruction -= config.size_SUB(start_sub)[1]*size(P)
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"subprogram starting at "+str(start_sub)+":")
                show_without_pointers(P,tab=tab+1)
            case POINTER(points_to):
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"--> P"+str(points_to))
            case REFERENCE(s,w):
                print("\t"+str(w)+"\t"*tab,"reference to "+str(s))
            case REPEAT_CHUNK(n,P):
                size_instruction -= config.size_REPEAT_CHUNK(n)[1]*size(P)
                print("\t"+str('%.2f' % size_instruction)+"\t"*tab,"repeat",n,"times:   (chunk!)")
                show_without_pointers(P,tab=tab+1)
    if start!="":
        print("\t\t << at",str(exe(program,int(start))[1]),">>")
    if tab==1:
        print("Size =",size(program))

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
