# LoT Sequence Complexity

This project implements a small programming language for describing finite sequences over a cyclic alphabet, together with tools to compute a constrained notion of complexity inspired by Kolmogorov complexity.

## Main idea

A program is executed relative to a **point of evaluation** in a cyclic alphabet of size `BASE`. The language contains atomic instructions such as:

- `MOVE_AND_PLAY`
- `PLAY`
- `MOVE`

and higher-level constructors such as:

- `REPEAT`
- `REPEAT_APPLY_NOTES`
- `REPEAT_APPLY_PEVAL`

Depending on the configuration, other constructors may also be enabled.

The central complexity notion is:

- the **complexity of a sequence** = the minimum size of a program that generates it

where size is determined by the parameter file.

## Main files

- `LoT_optimized.py`: original monolithic implementation
- `config.py`: global runtime configuration
- `para.json`: parameter file controlling the grammar and the size functions

In the modularized version, the same functionality is split into modules such as:

- `parameters`
- `syntax`
- `semantics`
- `complexity`
- `search`

## Main functions

### Configuration
```python
set_parameters("para.json")
