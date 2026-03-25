"""Tests for the interactive-play helpers in main.py."""

import io
import pytest

from main import parse_move_input, interactive_play
from sortchange.models import Move


# ---------------------------------------------------------------------------
# parse_move_input
# ---------------------------------------------------------------------------

class TestParseMoveInput:
    def test_space_separated(self):
        move = parse_move_input("0 2")
        assert move == Move(from_tube=0, to_tube=2)

    def test_comma_separated(self):
        move = parse_move_input("1,3")
        assert move == Move(from_tube=1, to_tube=3)

    def test_arrow_ascii(self):
        move = parse_move_input("2->4")
        assert move == Move(from_tube=2, to_tube=4)

    def test_arrow_unicode(self):
        move = parse_move_input("0→3")
        assert move == Move(from_tube=0, to_tube=3)

    def test_leading_trailing_whitespace(self):
        move = parse_move_input("  1  2  ")
        assert move == Move(from_tube=1, to_tube=2)

    def test_returns_none_for_single_number(self):
        assert parse_move_input("1") is None

    def test_returns_none_for_three_numbers(self):
        assert parse_move_input("1 2 3") is None

    def test_returns_none_for_non_numeric(self):
        assert parse_move_input("a b") is None

    def test_returns_none_for_empty_string(self):
        assert parse_move_input("") is None

    def test_returns_none_for_same_tube(self):
        # Move(1,1) raises ValueError inside parse_move_input.
        assert parse_move_input("1 1") is None

    def test_dash_treated_as_separator(self):
        # The '-' character is a separator (for '0->1' syntax), so '-1 0'
        # is parsed as Move(1, 0).  Negative indices cannot be expressed.
        move = parse_move_input("-1 0")
        assert move == Move(from_tube=1, to_tube=0)


# ---------------------------------------------------------------------------
# interactive_play (automated via stdin simulation)
# ---------------------------------------------------------------------------

class TestInteractivePlay:
    def _run(self, inputs: list[str], **kwargs) -> str:
        """Run interactive_play with *inputs* fed via stdin, return stdout."""
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr("builtins.input", _InputSimulator(inputs))
            captured = io.StringIO()
            import sys
            mp.setattr(sys, "stdout", captured)
            interactive_play(**kwargs)
        return captured.getvalue()

    def test_quit_immediately(self):
        output = self._run(["q"], num_colors=2, seed=0)
        assert "終了" in output

    def test_invalid_input_does_not_crash(self):
        # Feed bad input then quit.
        output = self._run(["xyz", "q"], num_colors=2, seed=0)
        assert "正しくありません" in output
        assert "終了" in output

    def test_hint_command(self, monkeypatch):
        """Hint command should print a suggestion without crashing."""
        inputs = ["h", "q"]
        captured = io.StringIO()
        import sys
        monkeypatch.setattr("builtins.input", _InputSimulator(inputs))
        monkeypatch.setattr(sys, "stdout", captured)
        interactive_play(num_colors=2, seed=0)
        out = captured.getvalue()
        # Should show either a hint move or "no solution" message
        assert ("ヒント" in out) or ("終了" in out)

    def test_invalid_move_feedback(self, monkeypatch):
        """An invalid move should print an error, not crash."""
        # tube 99 does not exist, so the move is invalid.
        inputs = ["0 99", "q"]
        captured = io.StringIO()
        import sys
        monkeypatch.setattr("builtins.input", _InputSimulator(inputs))
        monkeypatch.setattr(sys, "stdout", captured)
        interactive_play(num_colors=2, seed=0)
        out = captured.getvalue()
        assert "無効" in out

    def test_solve_to_completion(self, monkeypatch):
        """Feed the BFS solution moves to reach a solved state."""
        from sortchange import create_board, solve as bfs_solve

        board = create_board(num_colors=2, tube_capacity=4, empty_tubes=2, seed=7)
        solution = bfs_solve(board)
        assert solution is not None, "Seed 7 must be solvable for this test"

        move_inputs = [f"{m.from_tube} {m.to_tube}" for m in solution]
        captured = io.StringIO()
        import sys
        monkeypatch.setattr("builtins.input", _InputSimulator(move_inputs))
        monkeypatch.setattr(sys, "stdout", captured)
        interactive_play(num_colors=2, tube_capacity=4, empty_tubes=2, seed=7)
        out = captured.getvalue()
        assert "クリア" in out

    def test_undo_command(self, monkeypatch):
        """Undo with no history prints a message; undo after a move goes back."""
        from sortchange import create_board, solve as bfs_solve

        board = create_board(num_colors=2, tube_capacity=4, empty_tubes=2, seed=7)
        solution = bfs_solve(board)
        assert solution is not None and len(solution) >= 2

        # Make first move, undo it, then solve normally
        first_move = solution[0]
        move_str = f"{first_move.from_tube} {first_move.to_tube}"
        move_inputs = [move_str, "u"] + [f"{m.from_tube} {m.to_tube}" for m in solution]
        captured = io.StringIO()
        import sys
        monkeypatch.setattr("builtins.input", _InputSimulator(move_inputs))
        monkeypatch.setattr(sys, "stdout", captured)
        interactive_play(num_colors=2, tube_capacity=4, empty_tubes=2, seed=7)
        out = captured.getvalue()
        assert "戻しました" in out
        assert "クリア" in out

    def test_undo_with_no_history(self, monkeypatch):
        """Undo at the start should print a 'nothing to undo' message."""
        inputs = ["u", "q"]
        captured = io.StringIO()
        import sys
        monkeypatch.setattr("builtins.input", _InputSimulator(inputs))
        monkeypatch.setattr(sys, "stdout", captured)
        interactive_play(num_colors=2, seed=0)
        out = captured.getvalue()
        assert "元に戻せる手がありません" in out

    def test_restart_command(self, monkeypatch):
        """Restart resets move count and board; 'リスタート' should appear."""
        inputs = ["r", "q"]
        captured = io.StringIO()
        import sys
        monkeypatch.setattr("builtins.input", _InputSimulator(inputs))
        monkeypatch.setattr(sys, "stdout", captured)
        interactive_play(num_colors=2, seed=0)
        out = captured.getvalue()
        assert "リスタート" in out


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

class _InputSimulator:
    """Simulates user input by returning items from a list one at a time."""

    def __init__(self, responses: list[str]) -> None:
        self._iter = iter(responses)

    def __call__(self, prompt: str = "") -> str:
        return next(self._iter)
