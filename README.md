# Lonpos Puzzle

Jupyter notebook simulating the **Lonpos** board puzzle: a 12-piece set on a grid,
with pivot-based placement, clockwise/counter-clockwise rotation, vertical and
horizontal flips, and a board fit-check (`does_fit`).

## Run
```
python -m jupyter notebook Lonpos.ipynb
```

## Pieces
The 12 polygonal pieces are defined as coordinate offsets in `pieces_list`.
`Board` tracks the grid state; `Piece` holds positions + pivot and supports
rotation/flip transforms.
