"""Game-logic helpers for the sortchange tube-sorting puzzle.

These functions operate on :class:`~sortchange.models.GameBoard` objects and
provide the high-level interface used by player code, the solver, and the CLI.
"""

from __future__ import annotations

from typing import List

from .models import GameBoard, Move


def is_valid_move(board: GameBoard, move: Move) -> bool:
    """Return ``True`` if *move* is legal on *board*.

    Delegates to :meth:`GameBoard.is_valid_move`.

    Args:
        board: Current board state.
        move: The move to check.

    Returns:
        ``True`` if the move is legal.
    """
    return board.is_valid_move(move)


def apply_move(board: GameBoard, move: Move) -> GameBoard:
    """Apply *move* to *board* and return the new board state.

    The original *board* is not mutated.  Delegates to
    :meth:`GameBoard.apply_move`.

    Args:
        board: Current board state.
        move: A valid move to apply.

    Returns:
        New :class:`GameBoard` after the move.

    Raises:
        ValueError: If the move is invalid.
    """
    return board.apply_move(move)


def is_solved(board: GameBoard) -> bool:
    """Return ``True`` if *board* is in a solved (win) state.

    A board is solved when every tube is either empty or completely filled
    with a single color.

    Args:
        board: Board state to check.

    Returns:
        ``True`` if the puzzle is solved.
    """
    return board.is_solved


def get_valid_moves(board: GameBoard) -> List[Move]:
    """Return all legal moves available from *board*.

    Args:
        board: Current board state.

    Returns:
        List of valid :class:`Move` objects (may be empty).
    """
    return board.get_valid_moves()
