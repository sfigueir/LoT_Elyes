from lot.parameters import set_parameters
from lot.syntax import MOVE_AND_PLAY, REPEAT
from lot.semantics import exe
from lot.complexity import complexity, complexities_and_minprog, write_complexities_and_minprog_json
from lot.search import write_strings_with_initial_repetition_json


# Loads the parameters
set_parameters("para.json")


# A program and its execution
P = [REPEAT(3, [MOVE_AND_PLAY(1)])]
print(exe(P, 0))
print(complexity("01234"))


# All strings of a given complexity
data = write_strings_with_initial_repetition_json(
    "results.json",
    3,   # k_min
    8,   # k_max
    8,   # length_min
    10   # length_max
)



# A list l of strings
l = {
  "my_seq_name": "0000000",
  "Repetition-2": "010101010101"
  }

# Outputs the complexities of list l
print(complexities_and_minprog(l))

# Outputs complexities of all strings in file sequences.json 
write_complexities_and_minprog_json("sequences.json", "complexities_output.json")

