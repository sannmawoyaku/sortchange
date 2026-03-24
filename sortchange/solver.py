"""BFS solver for the sortchange tube-sorting puzzle.

The solver finds the **shortest** sequence of moves (in terms of move count)
that takes a :class:`~sortchange.models.GameBoard` from its initial state to a
solved state.  It uses breadth-first search with visited-state de-duplication.

Example::

    from sortchange import GameBoard, Tube, Color, solve

    board = GameBoard([
        Tube(blocks=[Color.RED, Color.BLUE]),
        Tube(blocks=[Color.BLUE, Color.RED]),
        Tube(),  # empty tube
    ])
    solution = solve(board)
    # solution is a list of Move objects, or None if unsolvable
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

from .models import GameBoard, Move


def solve(board: GameBoard, max_moves: int = 200) -> Optional[List[Move]]:
    """Find the shortest solution for *board* using breadth-first search.

    Args:
        board: The initial board state.
        max_moves: Safety limit on solution length to prevent infinite search
            on very complex or unsolvable puzzles (default 200).

    Returns:
        A list of :class:`Move` objects representing the solution path, or
        ``None`` if no solution exists within *max_moves*.
    """
    if board.is_solved:
        return []

    # Each entry in the queue: (current_board, path_of_moves_taken)
    queue: deque[Tuple[GameBoard, List[Move]]] = deque()
    queue.append((board, []))

    visited: Dict[tuple, bool] = {board.to_state(): True}

    while queue:
        current, path = queue.popleft()

        if len(path) >= max_moves:
            continue

        for move in current.get_valid_moves():
            next_board = current.apply_move(move)
            state = next_board.to_state()

            if state in visited:
                continue
            visited[state] = True

            next_path = path + [move]

            if next_board.is_solved:
                return next_path

            queue.append((next_board, next_path))

    return None
