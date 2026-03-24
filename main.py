"""CLI entry point for the sortchange tube-sorting puzzle demo."""

from __future__ import annotations

from sortchange import (
    Color,
    GameBoard,
    Move,
    Tube,
    create_board,
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


def parse_move_input(text: str) -> "Move | None":
    """Parse a move from user input string like '0 2' or '0→2'.

    Returns a :class:`Move` on success, or ``None`` if the input cannot be
    parsed.
    """
    import re
    parts = re.split(r"[\s,\->\u2192]+", text.strip())
    parts = [p for p in parts if p]
    if len(parts) != 2:
        return None
    try:
        from_tube = int(parts[0])
        to_tube = int(parts[1])
        return Move(from_tube=from_tube, to_tube=to_tube)
    except Exception:
        return None


def interactive_play(
    num_colors: int = 3,
    tube_capacity: int = 4,
    empty_tubes: int = 2,
    seed: "int | None" = None,
) -> None:
    """Run an interactive game session in the terminal.

    The player is shown the current board state and prompted to enter moves.

    Commands during play:

    * ``<from> <to>``  – move from tube *from* to tube *to* (0-based)
    * ``h``            – show a one-step hint (uses the BFS solver)
    * ``q``            – quit the game

    Args:
        num_colors: Number of distinct colors / filled tubes (default 3).
        tube_capacity: Number of block slots per tube (default 4).
        empty_tubes: Number of empty tubes to add (default 2).
        seed: Optional random seed for reproducibility.
    """
    board = create_board(
        num_colors=num_colors,
        tube_capacity=tube_capacity,
        empty_tubes=empty_tubes,
        seed=seed,
    )

    move_count = 0
    print("\n" + "=" * 50)
    print(f"試験管ソートパズル ({num_colors}色 / チューブ容量 {tube_capacity})")
    print("コマンド: '<移動元> <移動先>' で移動 | 'h' でヒント | 'q' で終了")
    print("=" * 50)

    while not board.is_solved:
        print(f"\n── 手数: {move_count} ──────────────────────")
        for i, tube in enumerate(board.tubes):
            blocks = " | ".join(c.name[:3] for c in tube.blocks) if tube.blocks else "(空)"
            status = " ✓" if tube.is_complete else ""
            print(f"  [{i}] {blocks}{status}")

        raw = input("\n移動 > ").strip().lower()

        if raw in ("q", "quit", "exit"):
            print("\nゲームを終了しました。")
            return

        if raw in ("h", "hint"):
            solution = solve(board)
            if solution is None:
                print("ヒント: このボードに解がありません。")
            elif not solution:
                print("ヒント: すでに解けています！")
            else:
                hint = solution[0]
                print(f"ヒント: チューブ {hint.from_tube} → チューブ {hint.to_tube} に移動してみましょう。")
            continue

        move = parse_move_input(raw)
        if move is None:
            print("  入力形式が正しくありません。例: '0 2' または '0,2'")
            continue

        if not board.is_valid_move(move):
            print(f"  その手は無効です: {move}")
            continue

        board = board.apply_move(move)
        move_count += 1

    print(f"\n── 最終盤面 ──────────────────────")
    for i, tube in enumerate(board.tubes):
        blocks = " | ".join(c.name[:3] for c in tube.blocks) if tube.blocks else "(空)"
        print(f"  [{i}] {blocks} ✓")
    print(f"\n🎉 クリア！ {move_count} 手で完成しました！")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="sortchange: 試験管ソートパズルゲーム",
    )
    parser.add_argument(
        "--play",
        action="store_true",
        help="インタラクティブプレイモードを起動する",
    )
    parser.add_argument(
        "--colors",
        type=int,
        default=3,
        metavar="N",
        help="色の種類数（デフォルト: 3）",
    )
    parser.add_argument(
        "--capacity",
        type=int,
        default=4,
        metavar="N",
        help="チューブの容量（デフォルト: 4）",
    )
    parser.add_argument(
        "--empty",
        type=int,
        default=2,
        metavar="N",
        help="空チューブの数（デフォルト: 2）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="N",
        help="乱数シード（再現性のため）",
    )
    args = parser.parse_args()

    if args.play:
        interactive_play(
            num_colors=args.colors,
            tube_capacity=args.capacity,
            empty_tubes=args.empty,
            seed=args.seed,
        )
    else:
        demo_small()
        demo_random()
