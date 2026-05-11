from lot.parameters import set_parameters
from lot.syntax import MOVE_AND_PLAY, REPEAT
from lot.semantics import exe
from lot.complexity import complexity, complexities_and_minprog, write_complexities_and_minprog_json
from lot.search import write_strings_with_initial_repetition_json

set_parameters("para.json")

P = [REPEAT(3, [MOVE_AND_PLAY(1)])]
print(exe(P, 0))
print(complexity("01234"))


data = write_strings_with_initial_repetition_json(
    "results.json",
    3,   # k_min
    8,   # k_max
    8,   # length_min
    10   # length_max
)

print("Done.")

l = {
  "my_seq_name": "0000000",
  "Repetition-2": "010101010101"
  }


print(complexities_and_minprog(l))

write_complexities_and_minprog_json("sequences.json", "complexities_output.json")

print("Done.")