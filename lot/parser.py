import re
from .syntax import MOVE_AND_PLAY, MOVE, PLAY, REPEAT, REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL
from .semantics import exe

#########################################################
# Utility: get indentation level
#########################################################
def indent_level(line):
    return len(line) - len(line.lstrip(" "))

#########################################################
# Parse one instruction line (not containing nested block)
#########################################################
def parse_single_instruction(line):
    line = line.strip()

    # move +1 and play
    m = re.match(r"move\s*([+-]?\d+)\s*and play", line)
    if m:
        return MOVE_AND_PLAY(n=int(m.group(1)))

    # move +1
    m = re.match(r"move\s*([+-]?\d+)$", line)
    if m:
        return MOVE(n=int(m.group(1)))

    # play 3
    m = re.match(r"play\s*(\d+)$", line)
    if m:
        return PLAY(n=int(m.group(1)))

    raise ValueError("Unknown instruction: " + line)

#########################################################
# Parse apply='xxx' clause → return instruction object
#########################################################
def parse_apply_clause(clause):
    clause = clause.strip()

    # formats:
    #   'move +1 and play'
    #   'move +1'
    if clause.startswith("move") and "and play" in clause:
        m = re.match(r"move\s*([+-]?\d+)\s*and play", clause)
        return MOVE_AND_PLAY(n=int(m.group(1)))

    if clause.startswith("move"):
        m = re.match(r"move\s*([+-]?\d+)", clause)
        return MOVE(n=int(m.group(1)))

    raise ValueError("Unknown apply clause: " + clause)

#########################################################
# Recursive parser for block of instructions
#########################################################
def parse_block(lines, start_index=0, base_indent=0):
    """
    Returns: (program_list, next_index)
    """
    program = []
    i = start_index

    while i < len(lines):
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue

        current_indent = indent_level(line)
        if current_indent < base_indent:
            break   # block ends

        # strip outer indent
        line = line.strip()

        ###############################################
        # Case 1: repeat with apply
        ###############################################
        m = re.match(r"repeat\s*(\d+)\s*\(apply='([^']+)'\):", line)
        if m:
            n = int(m.group(1))
            apply_instruction = parse_apply_clause(m.group(2))

            # parse the inner block
            inner_block, next_i = parse_block(lines, i+1, base_indent + 4)

            # Determine if notes or peval type:
            # very simple rule: MOVE_AND_PLAY → apply-to-notes
            if isinstance(apply_instruction, MOVE_AND_PLAY):
                instr = REPEAT_APPLY_NOTES(n=n, p=inner_block, appl=apply_instruction)
            else:
                instr = REPEAT_APPLY_PEVAL(n=n, P=inner_block, jump=apply_instruction)

            program.append(instr)
            i = next_i
            continue

        ###############################################
        # Case 2: repeat N:
        ###############################################
        m = re.match(r"repeat\s*(\d+)\s*:", line)
        if m:
            n = int(m.group(1))

            inner_block, next_i = parse_block(lines, i+1, base_indent + 4)
            instr = REPEAT(n=n, P=inner_block)

            program.append(instr)
            i = next_i
            continue

        ###############################################
        # Case 3: atomic instruction
        ###############################################
        instr = parse_single_instruction(line)
        program.append(instr)

        i += 1

    return program, i

#########################################################
# Top-level parser
#########################################################
def parser(text_or_path):
    if "\n" in text_or_path or "repeat" in text_or_path:
        text = text_or_path
    else:
        with open(text_or_path, "r") as f:
            text = f.read()

    lines = text.split("\n")
    program, _ = parse_block(lines, 0, 0)
    return program

#########################################################
# exe2 = exe(parser(...))
#########################################################
def exe2(text, start=0):
    P = parser(text)
    return exe(P, start)


