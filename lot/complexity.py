import json
from . import config
from .errors import LoTComplexityError
from .syntax import (
    MOVE_AND_PLAY, PLAY, MOVE, REPEAT, REPEAT_JUMP,
    REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL, MIRROR, MIRROR_BOUNCE,
    SUB, REFERENCE, REPEAT_CHUNK
)
from .semantics import exe
from .program_ops import size, size_p, add_pointers_to_program
from .printing import show
from .utils import remove_duplicates, substrings, chunks_in_order, concatenation_of_chunks


def complexities_and_minprog(sequences_with_names):

# It outputs the complexity and a minimal program of the sequences of the 
# experiment, given the parameters for tuning the notion of "size". 
# If f_choice_BASE is set to 0 (auto), then it initializes it as 
# the number of different letters of the string as the base.
# Notice that for the case different from 0 (auto), it creates an empty dictionary
# and then it adds the complexity of substrings of s, successively for each string s of the experiment. This optimization is to avoid repeated calculations.

    if config.BASE != 0:
        d={}
        for seq_name in sequences_with_names.keys():
            s = sequences_with_names[seq_name]
            d = construct_dictionary(d,s)

        complexities = {}
        for seq_name in sequences_with_names.keys():   
            s = sequences_with_names[seq_name]                   
            
            if config.with_POINTERS==False:
                complexity = min([size(prog) for start in range(int(config.BASE)) for (prog,end) in d[s,start]])
                min_programs = [prog for start in range(int(config.BASE)) for (prog,end) in d[s,start] if size(prog)==complexity]
            else:
                complexity = min([size_p(prog) for start in range(int(config.BASE)) for (prog,end) in d[s,start]])
                min_programs2 = [add_pointers_to_program(prog) for start in range(int(config.BASE)) for (prog,end) in d[s,start] if size_p(prog)==complexity]
                min_programs = []
                [min_programs.append(x) for x in min_programs2 if x not in min_programs]

            complexities[seq_name] = (s,complexity,min_programs)
    else:
        complexities = {}
        for seq_name in sequences_with_names.keys():
            s = sequences_with_names[seq_name]
            config.BASE = len(set(s))
            d={}
            d = construct_dictionary(d,s)

            if config.with_POINTERS==False:
                complexity = min([size(prog) for start in range(int(b)) for (prog,end) in d[s,start]])
                min_programs = [(prog,start) for start in range(int(b)) for (prog,end) in d[s,start] if size(prog)==complexity]
            else:
                complexity = min([size_p(prog) for start in range(int(b)) for (prog,end) in d[s,start]])
                min_programs2 = [add_pointers_to_program(prog) for start in range(int(b)) for (prog,end) in d[s,start] if size_p(prog)==complexity]
                min_programs = []
                [min_programs.append(x) for x in min_programs2 if x not in min_programs]

            complexities[seq_name] = (s,complexity,min_programs)

    return(complexities)

def construct_dictionary(d, sequence: str, references={}):
# Constructs a dictionary that has as keys a pair (s,i) and as values
# a set of (p,e), where s is a sequence, i is a starting point (a number in 0..BASE-1)
# p is a minimal program describing s when starting in i and e is the last position of p
# Optionally, it may receive a dictionary of references for using in the REFERENCE instructions
# (this is for the relative complexity)
    sequence = sequence.replace(" ", "")
    if [x for x in sequence if int(x) not in range(config.BASE)] != []:
        raise LoTComplexityError("Invalid character in sequence. Check base setting.")
    # d = {}

    # The addition of chunks changed the code more than I wanted. Now there are two codes: 
    # one for the absence of chunks (this one was the original) and one for the presence of chunks
    # The two codes are very similar, but I could not factorize them
    if config.with_CHUNKS:
        # in case we want to work with chunks, the base case are not the single symbols
        # of the sequence, but the chunks. The shortest descriptions are different for
        # chunks of length 1 and for chunks of length > 1
        chunks = chunks_in_order(sequence)
        concat_of_chunks = concatenation_of_chunks(sequence)
        # print(concat_of_chunks)

        for s in concat_of_chunks:
            if s in chunks:
                if (s,0) not in d.keys():
                    for start in range(config.BASE):
                        if len(s)==1:
                            d[s,start] = [ 
                                            ([P],exe([P],start)[1]) for 
                                            P in config.atomic_instructions if exe([P],start)[0] == s
                                         ]
                        else:
                            candidates = []
                            if config.include_PLAY:
                                candidates += [ ([REPEAT_CHUNK(n=len(s), P=[PLAY(n=int(s[0]))])],start)  ]
                            if config.include_MOVE_AND_PLAY and int(s[0])==start:
                                candidates += [ ([REPEAT_CHUNK(n=len(s), P=[MOVE_AND_PLAY(n=0)])],start) ]
                            min_size = min([size(X[0]) for X in candidates])
                            d[s,start] = remove_duplicates([X for X in candidates if size(X[0]) == min_size])


            else:
                if (s,0) not in d.keys():
                    split = [
                                (s[0:i+1],s[i+1:]) for 
                                i in range(len(s)-1) 
                                if (s[0:i+1],0) in d.keys() and (s[i+1:],0) in d.keys()
                            ]
                    for start in range(config.BASE):
                        candidates = []
                        # concatenation
                        for (a,b) in split:
                            candidates += [(min_a + min_b , end_b) 
                                for (min_a,end_a) in d[a,start] for (min_b,end_b) in d[b,end_a]]            
                        

                        # SUB
                        # In a concatenation, SUB can be applied to the former, the latter or both.
                        # Adding SUB to the language makes all calculations much much slower!
                        if config.include_SUB:
                            for start_sub in range(config.BASE):
                                for (a,b) in split:
                                    candidates += [(min_a + [SUB(start_sub,min_b)] , end_a) 
                                        for (min_a,end_a) in d[a,start] for (min_b,_) in d[b,start_sub]]            
                                    candidates += [([SUB(start_sub,min_a)] + min_b , end_b) 
                                        for (min_a,_) in d[a,start_sub] for (min_b,end_b) in d[b,start]]            
                            for start_sub1 in range(config.BASE):
                                for start_sub2 in range(config.BASE):
                                    for (a,b) in split:
                                        candidates += [([SUB(start_sub1,min_a)] + [SUB(start_sub2,min_b)] , start) 
                                            for (min_a,_) in d[a,start_sub1] for (min_b,_) in d[b,start_sub2]]            
                        # MIRROR
                        if config.include_MIRROR:
                            if len(s)%2==0:
                                prefix = s[0:len(s)//2]
                                # if prefix in concat_of_chunks: 
                                # ATTENTION: Observe that MIRROR does not get well
                                # with CHUNKS: 
                                # for "000111222 222111000", the chunk "222 222" will
                                # make "000111222" be absent in concat_of_chunks
                                # and hence the dictionary will never discover
                                # the prefix "000111222" 
                                if (prefix,0) in d.keys():                       
                                    for (P,e) in d[prefix,start]:
                                        candidate = [MIRROR(P)]
                                        (description,end) = exe(candidate,start)
                                        if description == s:
                                            candidates += [(candidate,end)]

                        # MIRROR_BOUNCE
                        if config.include_MIRROR_BOUNCE:
                            # not implemented because of the above explanation
                            pass
                        # rest of cases...
                        for j in range(1,1+len(s)//2):
                            if len(s)%j == 0:                        
                                # There is just one attempt in case SUB is not included. 
                                # Otherwise more attempts have to be considered 
                                # (see, eg case 12301231 starting at 0) 
                                # This action makes all calculations much much slower!
                                if not config.include_SUB:
                                    # if s[0:j] in concat_of_chunks:
                                    if (s[0:j],0) in d.keys():
                                        attempts = [(s[0:j],start)]
                                    else:
                                        attempts = []
                                else:
                                    attempts = [ 
                                                (s[j*h:j*h+j],start2) 
                                                    for h      in range(len(s)//j) 
                                                    for start2 in range(config.BASE) 
                                                    # if s[j*h:j*h+j] in concat_of_chunks
                                                    if (s[j*h:j*h+j],0) in d.keys()
                                               ]

                                for (prefix,start2) in attempts:
                                    for (P,e) in d[prefix,start2]:                            
                                        # REPEAT
                                        if config.include_REPEAT:
                                            candidate = [REPEAT(len(s)//j,P)]
                                            (description,end) = exe(candidate,start)
                                            if description == s and s[j-1] != s[j]:
                                              # condition s[j-1] != s[j] avoids
                                                # breaking a chunk. See, e.g. with input "01101"
                                                candidates += [(candidate,end)] 
                                        # REPEAT_JUMP
                                        if config.include_REPEAT_JUMP:
                                            for jump in config.possible_jumps:
                                                candidate = [REPEAT_JUMP(len(s)//j,P,jump)]
                                                (description,end) = exe(candidate,start)
                                                if description == s and s[j-1] != s[j]:
                                                    candidates += [(candidate,end)] 
                                        # REPEAT_APPLY_NOTES
                                        if config.include_REPEAT_APPLY_NOTES:
                                            for jump in config.possible_appl_notes:
                                                candidate = [REPEAT_APPLY_NOTES(len(s)//j,P,jump)]
                                                (description,end) = exe(candidate,start)
                                                if description == s and s[j-1] != s[j]:
                                                    candidates += [(candidate,end)] 
                                        # REPEAT_APPLY_PEVAL
                                        if config.include_REPEAT_APPLY_PEVAL:
                                            for jump in config.possible_appl_peval:
                                                candidate = [REPEAT_APPLY_PEVAL(len(s)//j,P,jump)]
                                                (description,end) = exe(candidate,start)
                                                if description == s and s[j-1] != s[j]:
                                                    candidates += [(candidate,end)] 
                        
                        # If there is a reference to s then add new candidate
                        if s in references:
                            candidate = [REFERENCE(s,references[s])]
                            candidates += [(candidate,start)]

                        if candidates == []:
                            raise LoTComplexityError("No way to build the string with the actual parameters of the grammar.")

                        min_size = min([size(X[0]) for X in candidates])
                        d[s,start] = remove_duplicates([X for X in candidates if size(X[0]) == min_size])



    else:
        # VERSION WITHOUT CHUNKS
        # Any substring has a set of minimal programs (this is not true with chunks)
        # The base case is for single symbols, and the dictionary is filled for
        # strings in order of length
        for s in substrings(sequence):
            if len(s) == 1:
                if (s,0) not in d.keys():
                    for start in range(config.BASE):
                        d[s,start] = [ 
                                        ([P],exe([P],start)[1]) for 
                                        P in config.atomic_instructions if exe([P],start)[0] == s
                                     ]
            else:
                if (s,0) not in d.keys():
                    split = [(s[0:i+1],s[i+1:]) for i in range(len(s)-1)]
                    for start in range(config.BASE):
                        candidates = []
                        # concatenation
                        for (a,b) in split:
                            candidates += [(min_a + min_b , end_b) 
                                for (min_a,end_a) in d[a,start] for (min_b,end_b) in d[b,end_a]]            
                        

                        # SUB
                        # In a concatenation, SUB can be applied to the former, the latter or both.
                        # Adding SUB to the language makes all calculations much much slower!
                        if config.include_SUB:
                            for start_sub in range(config.BASE):
                                for (a,b) in split:
                                    candidates += [(min_a + [SUB(start_sub,min_b)] , end_a) 
                                        for (min_a,end_a) in d[a,start] for (min_b,_) in d[b,start_sub]]            
                                    candidates += [([SUB(start_sub,min_a)] + min_b , end_b) 
                                        for (min_a,_) in d[a,start_sub] for (min_b,end_b) in d[b,start]]            
                            for start_sub1 in range(config.BASE):
                                for start_sub2 in range(config.BASE):
                                    for (a,b) in split:
                                        candidates += [([SUB(start_sub1,min_a)] + [SUB(start_sub2,min_b)] , start) 
                                            for (min_a,_) in d[a,start_sub1] for (min_b,_) in d[b,start_sub2]]            
                        # MIRROR
                        if config.include_MIRROR:
                            if len(s)%2==0:
                                prefix = s[0:len(s)//2]
                                for (P,e) in d[prefix,start]:
                                    candidate = [MIRROR(P)]
                                    (description,end) = exe(candidate,start)
                                    if description == s:
                                        candidates += [(candidate,end)]

                        # MIRROR_BOUNCE
                        if config.include_MIRROR_BOUNCE:
                            if len(s)%2==1:
                                prefix = s[0:(1+len(s))//2]
                                for (P,e) in d[prefix,start]:
                                    candidate = [MIRROR_BOUNCE(P)]
                                    (description,end) = exe(candidate,start)
                                    if description == s:
                                        candidates += [(candidate,end)]
                        
                        # rest of cases...
                        for j in range(1,1+len(s)//2):
                            if len(s)%j == 0:                        
                                # There is just one attempt in case SUB is not included. 
                                # Otherwise more attempts have to be considered 
                                # (see, eg case 12301231 starting at 0) 
                                # This action makes all calculations much much slower!
                                if not config.include_SUB:
                                    attempts = [(s[0:j],start)]
                                else:
                                    attempts = [ 
                                                (s[j*h:j*h+j],start2) 
                                                    for h      in range(len(s)//j) 
                                                    for start2 in range(config.BASE) 
                                               ]
                                
                                for (prefix,start2) in attempts:
                                    # prefix = s[0:j]
                                    for (P,e) in d[prefix,start2]:                            
                                        # REPEAT
                                        if config.include_REPEAT:
                                            candidate = [REPEAT(len(s)//j,P)]
                                            (description,end) = exe(candidate,start)
                                            if description == s:
                                                candidates += [(candidate,end)] 
                                        # REPEAT_JUMP
                                        if config.include_REPEAT_JUMP:
                                            for jump in config.possible_jumps:
                                                candidate = [REPEAT_JUMP(len(s)//j,P,jump)]
                                                (description,end) = exe(candidate,start)
                                                if description == s:
                                                    candidates += [(candidate,end)] 
                                        # REPEAT_APPLY_NOTES
                                        if config.include_REPEAT_APPLY_NOTES:
                                            for jump in config.possible_appl_notes:
                                                candidate = [REPEAT_APPLY_NOTES(len(s)//j,P,jump)]
                                                (description,end) = exe(candidate,start)
                                                if description == s:
                                                    candidates += [(candidate,end)] 
                                        # REPEAT_APPLY_PEVAL
                                        if config.include_REPEAT_APPLY_PEVAL:
                                            for jump in config.possible_appl_peval:
                                                candidate = [REPEAT_APPLY_PEVAL(len(s)//j,P,jump)]
                                                (description,end) = exe(candidate,start)
                                                if description == s:
                                                    candidates += [(candidate,end)] 
                        
                        # If there is a reference to s then add new candidate
                        if s in references:
                            candidate = [REFERENCE(s,references[s])]
                            candidates += [(candidate,start)]

                        min_size = min([size(X[0]) for X in candidates])
                        d[s,start] = remove_duplicates([X for X in candidates if size(X[0]) == min_size])

    return d

def print_dictionary(sequence):
    d = construct_dictionary(sequence)
    # complexity = min([size(prog) for (prog,end) in d[sequence,start]])
    for key in d.keys():
        print(key)
        for value in d[key]:
            print("   ",value)


def complexity_starting(sequence: str, start: int):
    sequence = sequence.replace(" ", "")
    # sequence = convertToBase(sequence)
    d = construct_dictionary(sequence)
    complexity = min([size(prog) for (prog,end) in d[sequence,start]])
    return complexity    


def complexity(sequence: str):
    sequence = sequence.replace(" ", "")
    # sequence = convertToBase(sequence)
    d={}
    d = construct_dictionary(d,sequence)
    complexity = min([size(prog) for start in range(config.BASE) for (prog,end) in d[sequence,start]])
    count_min_programs = len([prog for start in range(config.BASE) for (prog,end) in d[sequence,start] if size(prog)==complexity])
    return (complexity,count_min_programs)    


def complexity_starting_with_pointers(sequence: str, start: int):
    sequence = sequence.replace(" ", "")
    # sequence = convertToBase(sequence)
    d = construct_dictionary(sequence)
    complexity = min([size_with_pointers(add_pointers_to_program(prog)[0],add_pointers_to_program(prog)[1]) for (prog,end) in d[sequence,start]])
    return complexity    

# def list_by_complexity(LENGTH: int, M: int):
# # enumerates all strings of complexity 1,2,..., M of length 'LENGTH'
# # It's unfeasible, so use small values of 'LENGTH' and 'M'
#     d = {}
#     d[1] = [[a] for a in atomic_instructions]
#     strings_by_complexity = []
#     for i in range(2,M+1):
#         d[i] = []  
#         for a in atomic_instructions:
#             for P in d[i-1]:
#                 d[i] += [[a]+P]
#         for n in range(2,LENGTH+1):
#             for P in d[i-1]:
#                 d[i] += [[REPEAT(n,P)]]
#         if i>=3:
#             for j in possible_jumps:
#                 for n in range(2,LENGTH+1):
#                     for P in d[i-2]:
#                         d[i] += [[REPEAT_JUMP(n,P,j)]]
#         for P in d[i]: 
#             for start in range(BASE):
#                 (described,last) = exe(P,start)
#                 if len(described)==LENGTH and not (described in strings_by_complexity):
#                     strings_by_complexity += [described]
#                     print(i,described)



############################################################################
# Print all minimal programs
############################################################################


def min_progs(sequence: str, start: int = -1, relative_to = ""):
# Lists the complexity and all minimal programs of 'sequence' 
# optional parameters: 
#       start -> a number in 0..BASE-1 fixes the starting point
#       relative_to -> a string whose substrings will be used as references as in the relative complexity

    sequence = sequence.replace(" ", "")
    relative_to = relative_to.replace(" ", "")

    references = {x:1 for x in substrings(relative_to) if len(x)>1}

    print("Base :",config.BASE)
    print("Target :",sequence)

    if references != {}:
        print("References created by",relative_to,":")
        for x in references:
            print("\t",x,"has weight",references[x]) 

    d = {}
    d = construct_dictionary(d,sequence,references)
    if start != -1:
        complexity = size(d[sequence,start][0][0])
        possible_starting = [start]
        if references == {}:
            print("Complexity of",sequence,"starting at",start,"is",complexity)
        else:
            print("Complexity of",sequence,"relative to",relative_to,"starting at",start,"is",complexity)
    else:
        complexity = min([size(prog) for start in range(config.BASE) for (prog,end) in d[sequence,start]])
        possible_starting = range(config.BASE)
        if references == {}:
            print("Complexity of",sequence,"is",complexity)
        else:
            print("Complexity of",sequence,"relative to",relative_to,"is",complexity)            
    print("Minimal program(s) :")
    print()
    count = 1
    for start in possible_starting:
        for (prog,end) in d[sequence,start]:
            if size(prog) == complexity:
                if count < config.MAX_SHOWN+1:
                    print(str(count)+")")
                count += 1
                if count <= config.MAX_SHOWN+1:
                    show(prog,str(start))
                    print()
                    print("   In Python this is written as:")
                    print("     ",prog)
                    print()
                if count == config.MAX_SHOWN+2:
                    print(str(config.MAX_SHOWN+1)+") ...")
    print("Total minimal programs:",count-1)



def printSequence_starting(sequence: str, start: int):    
    sequence = sequence.replace(" ", "")
    for i in range(config.BASE-1,-1,-1):
        line = ""
        for note in sequence:
            if note == str(i):
                line+="- O -"
            else:
                line+="-----"
        print(i, line)
    print()
    min_progs_starting(sequence,start)
    print()
    print()


def write_complexities_and_minprog_json(input_json_file: str, output_json_file: str):
    """
    Reads a JSON file of the form
        { "name1": "sequence1", "name2": "sequence2", ... }
    computes complexities_and_minprog on it, and writes the result as JSON.

    Minimal programs are stored as strings, not decomposed.
    Assumes set_parameters(...) was already called.
    """
    with open(input_json_file, "r", encoding="utf-8") as f:
        sequences_with_names = json.load(f)

    raw_output = complexities_and_minprog(sequences_with_names)

    json_output = {}
    for name, value in raw_output.items():
        seq, comp, min_programs = value
        json_output[name] = {
            "sequence": seq,
            "complexity": comp,
            "minimal_programs": [str(p) for p in min_programs]
        }

    with open(output_json_file, "w", encoding="utf-8") as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)

    return json_output