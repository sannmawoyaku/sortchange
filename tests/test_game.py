"""Tests for sortchange.game helper functions."""

import pytest

from sortchange.models import Color, GameBoard, Move, Tube
from sortchange.game import (
    apply_move,
    get_valid_moves,
    is_solved,
    is_valid_move,
)


def _board_2color():
    """Simple 2-color, capacity-2 board with one empty tube."""
    return GameBoard([
        Tube(capacity=2, blocks=[Color.RED, Color.BLUE]),
        Tube(capacity=2, blocks=[Color.BLUE, Color.RED]),
        Tube(capacity=2),
    ])


class TestIsValidMove:
    def test_valid(self):
        board = _board_2color()
        assert is_valid_move(board, Move(0, 2)) is True

    def test_invalid_empty_source(self):
        board = _board_2color()
        assert is_valid_move(board, Move(2, 0)) is False


class TestApplyMove:
    def test_returns_new_board(self):
        board = _board_2color()
        new_board = apply_move(board, Move(0, 2))
        assert new_board is not board

    def test_invalid_move_raises(self):
        board = _board_2color()
        with pytest.raises(ValueError):
            apply_move(board, Move(2, 0))


class TestIsSolved:
    def test_unsolved(self):
        assert is_solved(_board_2color()) is False

    def test_solved(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.RED]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.BLUE]),
        ])
        assert is_solved(board) is True

    def test_solved_with_empty_tube(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.RED]),
            Tube(capacity=2),
        ])
        assert is_solved(board) is True


class TestGetValidMoves:
    def test_returns_list(self):
        board = _board_2color()
        moves = get_valid_moves(board)
        assert isinstance(moves, list)

    def test_all_returned_moves_are_valid(self):
        board = _board_2color()
        for move in get_valid_moves(board):
            assert is_valid_move(board, move)
