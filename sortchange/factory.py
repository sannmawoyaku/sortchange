"""Factory functions for creating sortchange game boards.

These helpers make it easy to build standard puzzles and random puzzles for
testing or gameplay.
"""

from __future__ import annotations

import random
from typing import List, Optional

from .models import Color, GameBoard, Tube


# All colors available for puzzle generation.
ALL_COLORS: List[Color] = list(Color)


def create_board(
    num_colors: int,
    tube_capacity: int = 4,
    empty_tubes: int = 2,
    seed: Optional[int] = None,
) -> GameBoard:
    """Create a randomized solvable-layout game board.

    The board is constructed by:

    1. Creating ``num_colors`` filled tubes, each containing
       ``tube_capacity`` blocks of a single color.
    2. Shuffling all blocks together.
    3. Distributing them randomly across ``num_colors`` tubes.
    4. Appending ``empty_tubes`` empty tubes (required for legal moves).

    .. note::
        The randomized distribution does **not** guarantee solvability in all
        cases.  Use the :func:`~sortchange.solver.solve` function to check
        whether the generated board has a solution before presenting it to a
        player.  Re-generate with a different *seed* if no solution is found.

    Args:
        num_colors: Number of distinct colors / filled tubes.
        tube_capacity: Number of block slots per tube (default 4).
        empty_tubes: Number of empty tubes to add (default 2).
        seed: Optional random seed for reproducibility.

    Returns:
        A new :class:`GameBoard` ready to play.

    Raises:
        ValueError: If *num_colors* exceeds the number of available colors, or
            if *num_colors* is less than 1.
    """
    if num_colors < 1:
        raise ValueError(f"num_colors must be at least 1, got {num_colors}")
    if num_colors > len(ALL_COLORS):
        raise ValueError(
            f"num_colors ({num_colors}) exceeds the number of available "
            f"colors ({len(ALL_COLORS)})."
        )

    rng = random.Random(seed)

    colors = ALL_COLORS[:num_colors]
    # Create a pool: each color repeated `tube_capacity` times.
    pool: List[Color] = [color for color in colors for _ in range(tube_capacity)]
    rng.shuffle(pool)

    # Distribute into `num_colors` tubes of `tube_capacity` each.
    tubes: List[Tube] = []
    for i in range(num_colors):
        chunk = pool[i * tube_capacity : (i + 1) * tube_capacity]
        tubes.append(Tube(capacity=tube_capacity, blocks=chunk))

    # Add empty tubes.
    for _ in range(empty_tubes):
        tubes.append(Tube(capacity=tube_capacity))

    return GameBoard(tubes)


def create_solved_board(
    num_colors: int,
    tube_capacity: int = 4,
    empty_tubes: int = 0,
) -> GameBoard:
    """Create a board that is already in the solved state.

    Useful as a reference or as the starting point for generating shuffled
    puzzles.

    Args:
        num_colors: Number of distinct colors / filled tubes.
        tube_capacity: Number of block slots per tube (default 4).
        empty_tubes: Number of empty tubes to append (default 0).

    Returns:
        A solved :class:`GameBoard`.

    Raises:
        ValueError: If *num_colors* exceeds the number of available colors.
    """
    if num_colors < 1:
        raise ValueError(f"num_colors must be at least 1, got {num_colors}")
    if num_colors > len(ALL_COLORS):
        raise ValueError(
            f"num_colors ({num_colors}) exceeds available colors ({len(ALL_COLORS)})."
        )

    colors = ALL_COLORS[:num_colors]
    tubes: List[Tube] = [
        Tube(capacity=tube_capacity, blocks=[color] * tube_capacity)
        for color in colors
    ]
    for _ in range(empty_tubes):
        tubes.append(Tube(capacity=tube_capacity))
    return GameBoard(tubes)


def create_board_from_lists(
    color_lists: List[List[Optional[Color]]],
    tube_capacity: int = 4,
) -> GameBoard:
    """Create a board from a list-of-lists specification.

    Each inner list represents one tube's blocks from *bottom* to *top*.
    ``None`` values are ignored (they represent empty slots).

    Args:
        color_lists: E.g. ``[[Color.RED, Color.BLUE], [Color.BLUE, Color.RED], []]``
        tube_capacity: Capacity of each tube.

    Returns:
        A :class:`GameBoard`.

    Raises:
        ValueError: If any inner list exceeds *tube_capacity*.
    """
    tubes: List[Tube] = []
    for blocks in color_lists:
        filled = [b for b in blocks if b is not None]
        tubes.append(Tube(capacity=tube_capacity, blocks=filled))
    return GameBoard(tubes)
