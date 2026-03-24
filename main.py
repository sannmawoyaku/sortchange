"""CLI entry point for the sortchange tube-sorting puzzle demo."""

from __future__ import annotations

from sortchange import (
    Color,
    GameBoard,
    Move,
    Tube,
    create_board_from_lists,
    solve,
)


def print_board(board: GameBoard, step: int) -> None:
    """Pretty-print the board state."""
    print(f"\n── Step {step} ──────────────────────────────")
    for i, tube in enumerate(board.tubes):
        blocks = " | ".join(c.name[:3] for c in tube.blocks) if tube.blocks else "(empty)"
        status = " ✓" if tube.is_complete else ""
        print(f"  [{i}] {blocks}{status}")


def demo_small() -> None:
    """A small 2-color puzzle that can be solved in a few moves."""
    print("=" * 50)
    print("Demo: 2-color puzzle (RED / BLUE)")
    print("=" * 50)

    # Hand-crafted puzzle: two mixed tubes + two empty tubes
    board = create_board_from_lists(
        [
            [Color.RED, Color.BLUE, Color.RED, Color.BLUE],
            [Color.BLUE, Color.RED, Color.BLUE, Color.RED],
            [],
            [],
        ],
        tube_capacity=4,
    )

    print_board(board, 0)
    solution = solve(board)

    if solution is None:
        print("\nNo solution found.")
        return

    print(f"\nSolution found in {len(solution)} move(s):")
    for step, move in enumerate(solution, start=1):
        print(f"  {step}. {move}")
        board = board.apply_move(move)
        print_board(board, step)

    print("\n✓ Puzzle solved!")


def demo_random() -> None:
    """A randomly generated 3-color puzzle."""
    from sortchange import create_board

    print("\n" + "=" * 50)
    print("Demo: random 3-color puzzle (seed=42)")
    print("=" * 50)

    board = create_board(num_colors=3, tube_capacity=4, empty_tubes=2, seed=42)
    print_board(board, 0)

    solution = solve(board)
    if solution is None:
        print("\nNo solution found (puzzle may be unsolvable with this seed).")
        return

    print(f"\nSolution found in {len(solution)} move(s).")
    print("✓ Puzzle is solvable!")


if __name__ == "__main__":
    demo_small()
    demo_random()
