import json
from . import config
from .syntax import (
    REPEAT, REPEAT_APPLY_NOTES, REPEAT_APPLY_PEVAL
)
from .semantics import exe
from .program_ops import size
from .utils import remove_duplicates
from .complexity import complexity


def _all_starts_signature(program):
    return tuple(exe(program, start) for start in range(config.BASE))


def _signature_output_length(sig):
    lengths = {len(out) for (out, _) in sig}
    if len(lengths) != 1:
        raise ValueError(f"Non-uniform output length in signature: {lengths}")
    return next(iter(lengths))


def _store_signature(classes_by_size_and_length, size_value, out_len, sig, program):
    if out_len not in classes_by_size_and_length[size_value]:
        classes_by_size_and_length[size_value][out_len] = {}
    if sig not in classes_by_size_and_length[size_value][out_len]:
        classes_by_size_and_length[size_value][out_len][sig] = program


def _compose_signatures(sig1, sig2):
    composed = []
    for start in range(config.BASE):
        out1, end1 = sig1[start]
        out2, end2 = sig2[end1]
        composed.append((out1 + out2, end2))
    return tuple(composed)


def _repeat_signature(sig, n):
    out = []
    for start in range(config.BASE):
        current = start
        pieces = []
        for _ in range(n):
            block, current = sig[current]
            pieces.append(block)
        out.append(("".join(pieces), current))
    return tuple(out)


def _apply_notes_signature(sig, n, appl):
    if n < 1:
        return None
    if _signature_output_length(sig) == 0:
        return None

    note_map = {}
    for d in range(config.BASE):
        image = exe([appl], d)[0]
        if len(image) != 1:
            return None
        note_map[str(d)] = image

    out = []
    for start in range(config.BASE):
        block = sig[start][0]
        pieces = [block]
        current = block
        for _ in range(n - 1):
            current = "".join(note_map[ch] for ch in current)
            pieces.append(current)
        total = "".join(pieces)
        out.append((total, int(total[-1])))
    return tuple(out)


def _apply_peval_signature(sig, n, jump):
    if n < 1:
        return None
    if _signature_output_length(sig) == 0:
        return None

    jump_map = {start: exe([jump], start)[1] for start in range(config.BASE)}
    out = []
    for start in range(config.BASE):
        current = start
        pieces = []
        for _ in range(n):
            block, _ = sig[current]
            pieces.append(block)
            current = jump_map[current]
        total = "".join(pieces)
        out.append((total, int(total[-1])))
    return tuple(out)


def _top_level_atomic_programs_for_search():
    atoms = [[instr] for instr in config.atomic_instructions]
    atoms += [[instr] for instr in config.possible_jumps]
    return remove_duplicates(atoms)


def _generate_program_classes_upto_size_and_length(max_size, length_max):
    """
    classes[c][r] is a dictionary mapping signatures to one witness-program,
    where the witness has size exactly c and output length exactly r.
    Signatures are tuples (exe(P,0), ..., exe(P,BASE-1)).
    Only lengths <= length_max are kept.
    """
    classes = {c: {} for c in range(1, max_size + 1)}

    # Atomic programs
    for program in _top_level_atomic_programs_for_search():
        try:
            current_size = size(program)
        except Exception:
            continue
        if not (1 <= current_size <= max_size):
            continue
        sig = _all_starts_signature(program)
        out_len = _signature_output_length(sig)
        if out_len <= length_max:
            _store_signature(classes, current_size, out_len, sig, program)

    for total_size in range(1, max_size + 1):
        # Concatenation
        for left_size in range(1, total_size):
            right_size = total_size - left_size
            for left_len, left_bucket in classes[left_size].items():
                for right_len, right_bucket in classes[right_size].items():
                    if left_len + right_len > length_max:
                        continue
                    out_len = left_len + right_len
                    target_bucket = classes[total_size].setdefault(out_len, {})
                    for sig1, prog1 in left_bucket.items():
                        for sig2, prog2 in right_bucket.items():
                            sig = _compose_signatures(sig1, sig2)
                            if sig not in target_bucket:
                                target_bucket[sig] = prog1 + prog2

        # Unary constructors
        for sub_size in range(1, total_size):
            for sub_len, sub_bucket in classes[sub_size].items():
                if sub_len <= 0:
                    continue

                max_n = length_max // sub_len
                if max_n < 2:
                    continue

                # REPEAT
                if getattr(config, "include_REPEAT", False):
                    for n in range(2, max_n + 1):
                        out_len = n * sub_len
                        for sig_sub, prog_sub in sub_bucket.items():
                            candidate = [REPEAT(n, prog_sub)]
                            try:
                                if size(candidate) != total_size:
                                    continue
                            except Exception:
                                continue
                            sig = _repeat_signature(sig_sub, n)
                            _store_signature(classes, total_size, out_len, sig, candidate)

                # REPEAT_APPLY_NOTES
                if getattr(config, "include_REPEAT_APPLY_NOTES", False):
                    for appl in getattr(config, "possible_appl_notes", []):
                        for n in range(2, max_n + 1):
                            out_len = n * sub_len
                            for sig_sub, prog_sub in sub_bucket.items():
                                candidate = [REPEAT_APPLY_NOTES(n, prog_sub, appl)]
                                try:
                                    if size(candidate) != total_size:
                                        continue
                                except Exception:
                                    continue
                                sig = _apply_notes_signature(sig_sub, n, appl)
                                if sig is not None:
                                    _store_signature(classes, total_size, out_len, sig, candidate)

                # REPEAT_APPLY_PEVAL
                if getattr(config, "include_REPEAT_APPLY_PEVAL", False):
                    for jump in getattr(config, "possible_appl_peval", []):
                        for n in range(2, max_n + 1):
                            out_len = n * sub_len
                            for sig_sub, prog_sub in sub_bucket.items():
                                candidate = [REPEAT_APPLY_PEVAL(n, prog_sub, jump)]
                                try:
                                    if size(candidate) != total_size:
                                        continue
                                except Exception:
                                    continue
                                sig = _apply_peval_signature(sig_sub, n, jump)
                                if sig is not None:
                                    _store_signature(classes, total_size, out_len, sig, candidate)

    return classes




def _jsonable_loaded_config():
    """
    Returns a JSON-friendly copy of config.GLOBAL_CONFIG.
    """
    out = {}
    for key, value in config.GLOBAL_CONFIG.items():
        if isinstance(value, tuple):
            out[key] = list(value)
        else:
            out[key] = value
    return out


###############################

def normalize_string_starting_at_zero(s: str):
    """
    Shifts all symbols of s by subtracting the first one modulo BASE.
    The result always starts with 0.
    Example (BASE=8):
        123456701 -> 012345670
        111111111 -> 000000000
    """
    if s == "":
        return s
    shift = int(s[0])
    return "".join(str((int(ch) - shift) % config.BASE) for ch in s)


def normalize_signature_starting_at_zero(sig):
    """
    Applies normalize_string_starting_at_zero to the output string in each entry
    of the signature, keeping the endpoint unchanged.
    """
    return tuple((normalize_string_starting_at_zero(out), end) for (out, end) in sig)



def compute_strings_with_initial_repetition_table(k_min, k_max, length_min, length_max):
    """
    Returns a nested dictionary results[k][l] = [strings], where:
      - len(s) = l
      - complexity(s) = k
      - s has a minimal program whose first instruction is
        REPEAT / REPEAT_APPLY_NOTES / REPEAT_APPLY_PEVAL
      - only one representative per global cyclic shift is kept,
        namely the normalized one starting with 0
    """
    if k_min <= 0 or length_min <= 0 or k_max < k_min or length_max < length_min:
        return {}

    classes = _generate_program_classes_upto_size_and_length(k_max, length_max)

    best_any = {}
    best_rep = {}

    # Smallest size of any program producing s, modulo global shift
    for c in range(1, k_max + 1):
        for out_len, bucket in classes[c].items():
            if not (length_min <= out_len <= length_max):
                continue
            for sig in bucket:
                for (out, _) in sig:
                    if length_min <= len(out) <= length_max:
                        s0 = normalize_string_starting_at_zero(out)
                        if s0 not in best_any or c < best_any[s0]:
                            best_any[s0] = c

    # Smallest size of a top-level repetition program producing s, modulo global shift
    for total_size in range(1, k_max + 1):
        for sub_size in range(1, total_size):
            for sub_len, sub_bucket in classes[sub_size].items():
                if sub_len <= 0:
                    continue

                max_n = length_max // sub_len
                if max_n < 2:
                    continue

                # REPEAT
                if getattr(config, "include_REPEAT", False):
                    for n in range(2, max_n + 1):
                        out_len = n * sub_len
                        if not (length_min <= out_len <= length_max):
                            continue
                        for sig_sub, prog_sub in sub_bucket.items():
                            candidate = [REPEAT(n, prog_sub)]
                            try:
                                if size(candidate) != total_size:
                                    continue
                            except Exception:
                                continue
                            sig = _repeat_signature(sig_sub, n)
                            for (out, _) in sig:
                                if length_min <= len(out) <= length_max:
                                    s0 = normalize_string_starting_at_zero(out)
                                    if s0 not in best_rep or total_size < best_rep[s0]:
                                        best_rep[s0] = total_size

                # REPEAT_APPLY_NOTES
                if getattr(config, "include_REPEAT_APPLY_NOTES", False):
                    for appl in getattr(config, "possible_appl_notes", []):
                        for n in range(2, max_n + 1):
                            out_len = n * sub_len
                            if not (length_min <= out_len <= length_max):
                                continue
                            for sig_sub, prog_sub in sub_bucket.items():
                                candidate = [REPEAT_APPLY_NOTES(n, prog_sub, appl)]
                                try:
                                    if size(candidate) != total_size:
                                        continue
                                except Exception:
                                    continue
                                sig = _apply_notes_signature(sig_sub, n, appl)
                                if sig is None:
                                    continue
                                for (out, _) in sig:
                                    if length_min <= len(out) <= length_max:
                                        s0 = normalize_string_starting_at_zero(out)
                                        if s0 not in best_rep or total_size < best_rep[s0]:
                                            best_rep[s0] = total_size

                # REPEAT_APPLY_PEVAL
                if getattr(config, "include_REPEAT_APPLY_PEVAL", False):
                    for jump in getattr(config, "possible_appl_peval", []):
                        for n in range(2, max_n + 1):
                            out_len = n * sub_len
                            if not (length_min <= out_len <= length_max):
                                continue
                            for sig_sub, prog_sub in sub_bucket.items():
                                candidate = [REPEAT_APPLY_PEVAL(n, prog_sub, jump)]
                                try:
                                    if size(candidate) != total_size:
                                        continue
                                except Exception:
                                    continue
                                sig = _apply_peval_signature(sig_sub, n, jump)
                                if sig is None:
                                    continue
                                for (out, _) in sig:
                                    if length_min <= len(out) <= length_max:
                                        s0 = normalize_string_starting_at_zero(out)
                                        if s0 not in best_rep or total_size < best_rep[s0]:
                                            best_rep[s0] = total_size

    results = {
        str(k): {str(l): [] for l in range(length_min, length_max + 1)}
        for k in range(k_min, k_max + 1)
    }

    for s0, c in best_any.items():
        if k_min <= c <= k_max and best_rep.get(s0) == c:
            results[str(c)][str(len(s0))].append(s0)

    for k in results:
        for l in results[k]:
            results[k][l] = sorted(set(results[k][l]))

    return results





def write_strings_with_initial_repetition_json(file_path, k_min, k_max, length_min, length_max):
    """
    Writes a JSON file with all strings found in the given rectangle:
      k_min <= complexity <= k_max
      length_min <= length <= length_max

    The strings kept are exactly those having a minimal program whose first
    instruction is REPEAT / REPEAT_APPLY_NOTES / REPEAT_APPLY_PEVAL.
    """
    results = compute_strings_with_initial_repetition_table(
        k_min, k_max, length_min, length_max
    )

    counts = {
        k: {l: len(results[k][l]) for l in results[k]}
        for k in results
    }

    data = {
        "interpretation": {
            "meaning": (
                "results[k][l] contains the strings of length l and complexity exactly k "
                "such that there exists a minimal program for the string whose first "
                "instruction is REPEAT, REPEAT_APPLY_NOTES, or REPEAT_APPLY_PEVAL (or a subset of them, depending on the general parameters)."
            ),
            "counts_meaning": (
                "counts[k][l] is the number of strings listed in results[k][l]."
            ),
            "complexity_meaning": (
                "Complexity is computed by the function complexity()."
            )
        },
        "loaded_config": _jsonable_loaded_config(),
        "parameters": {
            "k_min": k_min,
            "k_max": k_max,
            "length_min": length_min,
            "length_max": length_max,
            "base": config.BASE
        },
        "results": results,
        "counts": counts
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data
