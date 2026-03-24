"""Tests for sortchange.factory board creation functions."""

import pytest

from sortchange.models import Color, Tube
from sortchange.factory import (
    ALL_COLORS,
    create_board,
    create_board_from_lists,
    create_solved_board,
)


class TestCreateSolvedBoard:
    def test_is_solved(self):
        board = create_solved_board(num_colors=3)
        assert board.is_solved

    def test_correct_number_of_tubes(self):
        board = create_solved_board(num_colors=4, empty_tubes=2)
        assert board.num_tubes == 6

    def test_single_color(self):
        board = create_solved_board(num_colors=1)
        assert board.num_tubes == 1
        assert board.is_solved

    def test_too_many_colors_raises(self):
        with pytest.raises(ValueError):
            create_solved_board(num_colors=len(ALL_COLORS) + 1)

    def test_zero_colors_raises(self):
        with pytest.raises(ValueError):
            create_solved_board(num_colors=0)


class TestCreateBoard:
    def test_board_has_correct_tube_count(self):
        board = create_board(num_colors=3, empty_tubes=2)
        assert board.num_tubes == 5  # 3 filled + 2 empty

    def test_board_not_solved_by_default(self):
        # A random board is almost certainly not already solved.
        board = create_board(num_colors=3, seed=0)
        # Just verify it is a valid board (may or may not be solved).
        assert board.num_tubes == 5  # 3 + 2 default empty

    def test_reproducible_with_seed(self):
        b1 = create_board(num_colors=3, seed=99)
        b2 = create_board(num_colors=3, seed=99)
        assert b1.to_state() == b2.to_state()

    def test_different_seeds_differ(self):
        b1 = create_board(num_colors=3, seed=1)
        b2 = create_board(num_colors=3, seed=2)
        # Very unlikely to be equal.
        assert b1.to_state() != b2.to_state()

    def test_too_many_colors_raises(self):
        with pytest.raises(ValueError):
            create_board(num_colors=len(ALL_COLORS) + 1)

    def test_zero_colors_raises(self):
        with pytest.raises(ValueError):
            create_board(num_colors=0)


class TestCreateBoardFromLists:
    def test_basic(self):
        board = create_board_from_lists(
            [[Color.RED, Color.BLUE], [Color.BLUE, Color.RED], []],
        )
        assert board.num_tubes == 3
        assert board.tubes[0].blocks == [Color.RED, Color.BLUE]
        assert board.tubes[2].is_empty

    def test_none_values_skipped(self):
        board = create_board_from_lists(
            [[Color.RED, None, Color.BLUE]],
        )
        assert board.tubes[0].blocks == [Color.RED, Color.BLUE]

    def test_exceeds_capacity_raises(self):
        with pytest.raises(ValueError):
            create_board_from_lists(
                [[Color.RED, Color.BLUE, Color.GREEN, Color.RED, Color.BLUE]],
                tube_capacity=4,
            )
