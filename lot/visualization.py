from graphviz import Digraph
from .syntax import (
    MOVE_AND_PLAY, PLAY, MOVE, REPEAT, REPEAT_JUMP,
    REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL, REFLECT,
    MIRROR, MIRROR_BOUNCE, SUB, POINTER, REFERENCE, REPEAT_CHUNK
)
from .semantics import exe_with_parenthesis


def program_to_tree(lst, graph=None, parent=None, node_id=[0]):
#Recursively builds a syntactic tree representation of a program using Graphviz
    if graph is None:
        graph = Digraph(format="png")  

    current_id = node_id[0]
    node_id[0] += 1
    
    if isinstance(lst, list):  
        label = "Prog"
    else:  
        label = str(lst)
        match lst:
            case MOVE_AND_PLAY(n):
                label = "MV&PL "+str(n)
            case PLAY(n):
                label = "PLAY "+str(n)
            case MOVE(n):
                label = "MOVE "+str(n)
            case REPEAT(n,p):
                label = "REP "+str(n)
                program_to_tree(p, graph, current_id, node_id)
            case REPEAT_JUMP(n,p,j):
                label = "REP JMP "+str(n)+"\n"+instr_name(j)
                program_to_tree(p, graph, current_id, node_id)
            case REPEAT_APPLY_NOTES(n,p,a):
                label = "REP AN " +str(n)+"\n"+instr_name(a)
                program_to_tree(p, graph, current_id, node_id)
            case REPEAT_APPLY_PEVAL(n,p,a):
                label = "REP AP " + str(n)+"\n"+instr_name(a)
                program_to_tree(p, graph, current_id, node_id)
            case REFLECT(n): #only for BASE=8
                label = "REFL" + str(n)
                program_to_tree(p, graph, current_id, node_id)
            case MIRROR(P): 
                label = "MIR" + str(n)
                program_to_tree(p, graph, current_id, node_id)
            case MIRROR_BOUNCE(P): 
                label = "MIR B\n" +str(n)
                program_to_tree(p, graph, current_id, node_id)
            case SUB(start,P): 
                label = "SUB" +str(start)
                program_to_tree(p, graph, current_id, node_id)
            case POINTER(n): 
                label = "PTR\n" + str(n)
                program_to_tree(p, graph, current_id, node_id)
            case REFERENCE(_,w): 
                label = "REF" + str(w)
                program_to_tree(p, graph, current_id, node_id)
            case REPEAT_CHUNK(n,p):
                label = "REP CHK" + str(n)
                program_to_tree(p, graph, current_id, node_id)

    graph.node(str(current_id), label)

    if parent is not None:
        graph.edge(str(parent), str(current_id))

    if isinstance(lst, list):
        if len(lst) == 1:
            program_to_tree(lst[0], graph, current_id, node_id)
        else:
            for item in lst:
                program_to_tree(item, graph, current_id, node_id)

    return graph

def instr_name(instr):    
    match instr:
        case MOVE_AND_PLAY(n):
            label = "MV&PL "+str(n)
        case MOVE(n):
            label = "MOVE "+str(n)
        case REFLECT(n):
            label = "REFL "+str(n)
    return label 

def plot_syntactic_tree(nested_list, name='tree'):
    dot = Digraph(name, format='png')
    
    def format_label(sublist):
        label = str(sublist).replace('[', '(').replace(']', ')').replace(',', '').replace(' ', '')
        # if label.startswith('(') and label.endswith(')'):
        #     label = label[1:-1]
        return label
    
    def add_nodes_edges(sublist, parent_id=None, node_id=[0]):
        current_id = node_id[0]
        node_label = format_label(sublist)
        dot.node(str(current_id), node_label)
        
        if parent_id is not None:
            dot.edge(str(parent_id), str(current_id))
        
        node_id[0] += 1
        
        if isinstance(sublist, list):
            for item in sublist:
                add_nodes_edges(item, current_id, node_id)
    
    add_nodes_edges(nested_list)
    dot.render("Parsed sequence",view=True)


def parse_parentheses(s, index=0):
    def helper():
        lst = []
        while index[0] < len(s):
            char = s[index[0]]
            if char.isdigit():
                lst.append(int(char))
            elif char == '(':
                index[0] += 1  # Move past '('
                lst.append(helper())  # Recurse
            elif char == ')':
                return lst
            index[0] += 1
        if len(lst)==1:
            return lst[0]
        else:
            return lst
    return helper()

def parsing_trees(P,start):
    # input: a program and a starting point
    string_with_parenthesis=exe_with_parenthesis(P,start)[0]
    t = parse_parentheses(string_with_parenthesis, [0])
    plot_syntactic_tree(t)
    tree = program_to_tree(P)
    tree.render("Program Tree", view=True)  # Save and open the tree visualization
