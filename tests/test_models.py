"""Tests for sortchange data models: Color, Tube, GameBoard, Move."""

import pytest

from sortchange.models import Color, GameBoard, Move, Tube


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------

class TestColor:
    def test_all_colors_have_positive_value(self):
        for color in Color:
            assert color.value > 0

    def test_colors_are_unique(self):
        values = [c.value for c in Color]
        assert len(values) == len(set(values))


# ---------------------------------------------------------------------------
# Tube
# ---------------------------------------------------------------------------

class TestTubeCreation:
    def test_empty_tube(self):
        t = Tube()
        assert t.is_empty
        assert t.size == 0
        assert t.top is None

    def test_tube_with_blocks(self):
        t = Tube(blocks=[Color.RED, Color.BLUE])
        assert t.size == 2
        assert t.top == Color.BLUE
        assert not t.is_empty

    def test_invalid_capacity(self):
        with pytest.raises(ValueError):
            Tube(capacity=0)

    def test_exceeds_capacity(self):
        with pytest.raises(ValueError):
            Tube(capacity=2, blocks=[Color.RED, Color.BLUE, Color.GREEN])

    def test_copy_is_independent(self):
        t = Tube(blocks=[Color.RED])
        t2 = t.copy()
        t2._push(Color.BLUE)
        assert t.size == 1  # original unchanged


class TestTubeProperties:
    def test_free_space(self):
        t = Tube(capacity=4, blocks=[Color.RED, Color.BLUE])
        assert t.free_space == 2

    def test_is_full(self):
        t = Tube(capacity=2, blocks=[Color.RED, Color.BLUE])
        assert t.is_full

    def test_is_complete_empty(self):
        t = Tube()
        assert t.is_complete

    def test_is_complete_single_color_full(self):
        t = Tube(capacity=2, blocks=[Color.RED, Color.RED])
        assert t.is_complete

    def test_not_complete_mixed(self):
        t = Tube(blocks=[Color.RED, Color.BLUE])
        assert not t.is_complete

    def test_not_complete_single_color_not_full(self):
        # Partially filled with one color is NOT complete.
        t = Tube(capacity=4, blocks=[Color.RED, Color.RED])
        assert not t.is_complete

    def test_top_group_size_uniform(self):
        t = Tube(blocks=[Color.RED, Color.BLUE, Color.BLUE, Color.BLUE])
        assert t.top_group_size == 3

    def test_top_group_size_single(self):
        t = Tube(blocks=[Color.RED, Color.BLUE])
        assert t.top_group_size == 1

    def test_top_group_size_empty(self):
        t = Tube()
        assert t.top_group_size == 0

    def test_top_group_size_all_same(self):
        t = Tube(capacity=4, blocks=[Color.RED, Color.RED, Color.RED, Color.RED])
        assert t.top_group_size == 4


class TestTubeMutations:
    def test_push_and_pop(self):
        t = Tube(capacity=2)
        t._push(Color.RED)
        assert t.top == Color.RED
        popped = t._pop()
        assert popped == Color.RED
        assert t.is_empty

    def test_push_full_raises(self):
        t = Tube(capacity=1, blocks=[Color.RED])
        with pytest.raises(ValueError):
            t._push(Color.BLUE)

    def test_pop_empty_raises(self):
        t = Tube()
        with pytest.raises(ValueError):
            t._pop()


class TestTubeEquality:
    def test_equal_tubes(self):
        t1 = Tube(capacity=4, blocks=[Color.RED, Color.BLUE])
        t2 = Tube(capacity=4, blocks=[Color.RED, Color.BLUE])
        assert t1 == t2

    def test_different_blocks(self):
        t1 = Tube(blocks=[Color.RED])
        t2 = Tube(blocks=[Color.BLUE])
        assert t1 != t2

    def test_hashable(self):
        t = Tube(blocks=[Color.RED])
        assert isinstance(hash(t), int)


# ---------------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------------

class TestMove:
    def test_valid_move(self):
        m = Move(from_tube=0, to_tube=1)
        assert m.from_tube == 0
        assert m.to_tube == 1

    def test_same_tube_raises(self):
        with pytest.raises(ValueError):
            Move(from_tube=1, to_tube=1)

    def test_negative_from_raises(self):
        with pytest.raises(ValueError):
            Move(from_tube=-1, to_tube=0)

    def test_negative_to_raises(self):
        with pytest.raises(ValueError):
            Move(from_tube=0, to_tube=-1)

    def test_frozen(self):
        m = Move(from_tube=0, to_tube=1)
        with pytest.raises(Exception):
            m.from_tube = 2  # type: ignore[misc]

    def test_hashable(self):
        m = Move(from_tube=0, to_tube=1)
        assert isinstance(hash(m), int)


# ---------------------------------------------------------------------------
# GameBoard
# ---------------------------------------------------------------------------

class TestGameBoardCreation:
    def test_basic_board(self):
        board = GameBoard([Tube(), Tube()])
        assert board.num_tubes == 2

    def test_empty_tubes_raises(self):
        with pytest.raises(ValueError):
            GameBoard([])

    def test_mixed_capacity_raises(self):
        with pytest.raises(ValueError):
            GameBoard([Tube(capacity=4), Tube(capacity=3)])

    def test_copy_is_independent(self):
        board = GameBoard([Tube(blocks=[Color.RED]), Tube()])
        board2 = board.copy()
        board2._tubes[0]._push(Color.BLUE)
        assert board._tubes[0].size == 1  # original unchanged


class TestGameBoardSolvedState:
    def test_empty_board_is_solved(self):
        board = GameBoard([Tube(), Tube()])
        assert board.is_solved

    def test_complete_tubes_is_solved(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.RED]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.BLUE]),
        ])
        assert board.is_solved

    def test_mixed_board_not_solved(self):
        board = GameBoard([
            Tube(blocks=[Color.RED, Color.BLUE]),
            Tube(),
        ])
        assert not board.is_solved


class TestGameBoardMoves:
    def _simple_board(self):
        """Two mixed tubes + one empty tube (capacity 2)."""
        return GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.BLUE]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.RED]),
            Tube(capacity=2),
        ])

    def test_valid_move_to_empty(self):
        board = self._simple_board()
        # Move top of tube 0 (BLUE) to empty tube 2
        assert board.is_valid_move(Move(0, 2))

    def test_invalid_move_out_of_range(self):
        board = self._simple_board()
        assert not board.is_valid_move(Move(0, 10))

    def test_invalid_move_from_empty(self):
        board = self._simple_board()
        assert not board.is_valid_move(Move(2, 0))

    def test_invalid_move_color_mismatch(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.BLUE]),
            Tube(capacity=2, blocks=[Color.RED, Color.RED]),
        ])
        # Top of 0 is BLUE, top of 1 is RED → mismatch
        assert not board.is_valid_move(Move(0, 1))

    def test_invalid_move_full_destination(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.BLUE, Color.BLUE]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.BLUE]),
        ])
        assert not board.is_valid_move(Move(0, 1))

    def test_apply_move_returns_new_board(self):
        board = self._simple_board()
        move = Move(0, 2)
        new_board = board.apply_move(move)
        assert new_board is not board

    def test_apply_move_does_not_mutate(self):
        board = self._simple_board()
        original_state = board.to_state()
        board.apply_move(Move(0, 2))
        assert board.to_state() == original_state

    def test_apply_invalid_move_raises(self):
        board = self._simple_board()
        with pytest.raises(ValueError):
            board.apply_move(Move(2, 0))  # tube 2 is empty

    def test_get_valid_moves_not_empty(self):
        board = self._simple_board()
        moves = board.get_valid_moves()
        assert len(moves) > 0

    def test_get_valid_moves_solved_board(self):
        board = GameBoard([
            Tube(capacity=2, blocks=[Color.RED, Color.RED]),
            Tube(capacity=2, blocks=[Color.BLUE, Color.BLUE]),
        ])
        # All tubes are complete, so no moves should be generated.
        moves = board.get_valid_moves()
        assert moves == []

    def test_move_group_transfer(self):
        """Multiple same-colored blocks on top should all move at once."""
        board = GameBoard([
            Tube(capacity=4, blocks=[Color.RED, Color.BLUE, Color.BLUE]),
            Tube(capacity=4),
        ])
        new_board = board.apply_move(Move(0, 1))
        # Both BLUE blocks should have moved to tube 1.
        assert new_board.tubes[1].size == 2
        assert new_board.tubes[1].top == Color.BLUE
        assert new_board.tubes[0].size == 1  # only RED remains


class TestGameBoardState:
    def test_to_state_is_tuple(self):
        board = GameBoard([Tube(blocks=[Color.RED]), Tube()])
        assert isinstance(board.to_state(), tuple)

    def test_equal_boards_same_state(self):
        board1 = GameBoard([Tube(blocks=[Color.RED]), Tube()])
        board2 = GameBoard([Tube(blocks=[Color.RED]), Tube()])
        assert board1.to_state() == board2.to_state()

    def test_hashable(self):
        board = GameBoard([Tube(blocks=[Color.RED]), Tube()])
        assert isinstance(hash(board), int)
