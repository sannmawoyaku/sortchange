"""sortchange: A tube-sorting puzzle game library.

The puzzle
----------
You have a set of test tubes (試験管), each containing a stack of coloured
blocks.  To solve the puzzle you must sort the blocks so that every tube
contains blocks of only one colour (or is empty).  You can only pour the
top block(s) of one tube into another tube when:

* The destination tube is **not full**.
* The destination tube is **empty**, *or* its topmost block has the **same
  colour** as the block(s) you are moving.

Quick start::

    from sortchange import Color, Tube, GameBoard, Move, solve

    board = GameBoard([
        Tube(blocks=[Color.RED, Color.BLUE, Color.RED, Color.BLUE]),
        Tube(blocks=[Color.BLUE, Color.RED, Color.BLUE, Color.RED]),
        Tube(),   # empty tube
        Tube(),   # empty tube
    ])

    solution = solve(board)
    for move in solution:
        board = board.apply_move(move)
    assert board.is_solved
"""

from .models import Color, Tube, GameBoard, Move
from .game import is_valid_move, apply_move, is_solved, get_valid_moves
from .solver import solve
from .factory import create_board, create_solved_board, create_board_from_lists

__all__ = [
    # models
    "Color",
    "Tube",
    "GameBoard",
    "Move",
    # game helpers
    "is_valid_move",
    "apply_move",
    "is_solved",
    "get_valid_moves",
    # solver
    "solve",
    # factory
    "create_board",
    "create_solved_board",
    "create_board_from_lists",
]
