"""Tests for sortchange.solver (BFS solver)."""

import pytest

from sortchange.models import Color, GameBoard, Tube
from sortchange.solver import solve


def _apply_solution(board: GameBoard, solution) -> GameBoard:
    for move in solution:
        board = board.apply_move(move)
    return board


class TestSolveAlreadySolved:
    def test_returns_empty_list(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.RED]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.BLUE]),
        ])
        result = solve(board)
        assert result == []


class TestSolveSimplePuzzle:
    def test_two_color_puzzle(self):
        """
        Start:
          [0] RED BLUE
          [1] BLUE RED
          [2] (empty)
          [3] (empty)
        """
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.BLUE]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.RED]),
            Tube(capacity=2),
            Tube(capacity=2),
        ])
        solution = solve(board)
        assert solution is not None
        final_board = _apply_solution(board, solution)
        assert final_board.is_solved

    def test_solution_leads_to_solved_state(self):
        """Each move in the solution must be valid and result in a solved board."""
        board = GameBoard([
            Tube(capacity=4, blocks=[Color.RED, Color.BLUE, Color.RED, Color.BLUE]),
            Tube(capacity=4, blocks=[Color.BLUE, Color.RED, Color.BLUE, Color.RED]),
            Tube(capacity=4),
            Tube(capacity=4),
        ])
        solution = solve(board)
        assert solution is not None

        current = board
        for move in solution:
            assert current.is_valid_move(move), f"Invalid move in solution: {move}"
            current = current.apply_move(move)
        assert current.is_solved

    def test_three_color_puzzle_solvable(self):
        """Three colors mixed across three tubes + two empty tubes."""
        board = GameBoard([
            Tube(capacity=3, blocks=[Color.RED,   Color.BLUE,  Color.GREEN]),
            Tube(capacity=3, blocks=[Color.GREEN, Color.RED,   Color.BLUE]),
            Tube(capacity=3, blocks=[Color.BLUE,  Color.GREEN, Color.RED]),
            Tube(capacity=3),
            Tube(capacity=3),
        ])
        solution = solve(board)
        assert solution is not None
        assert _apply_solution(board, solution).is_solved


class TestSolveUnsolvable:
    def test_no_empty_tube_unsolvable(self):
        """Without any empty tube the puzzle cannot be solved if mixed."""
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.BLUE]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.RED]),
        ])
        # Solver should return None (no solution possible).
        result = solve(board)
        assert result is None


class TestSolveFactory:
    def test_solved_board_from_factory(self):
        from sortchange.factory import create_solved_board
        board = create_solved_board(num_colors=3, tube_capacity=4)
        assert solve(board) == []
