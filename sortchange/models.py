"""Data models for the sortchange tube-sorting puzzle game.

Terminology
-----------
* **Tube** (試験管): A test tube with a fixed capacity that holds a stack of
  colored blocks.  Index 0 is the *bottom*; the last element is the *top*.
* **Color** (色): An enumerated color value representing one block.
* **GameBoard** (ゲームボード): The full game state – an ordered collection of
  tubes.
* **Move** (手): A single move from one tube to another.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Color
# ---------------------------------------------------------------------------

class Color(Enum):
    """Colors used for tube blocks.

    Each variant represents one distinct color that can appear in a tube.
    The integer value is used for compact state serialization.
    """

    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    ORANGE = 5
    PURPLE = 6
    PINK = 7
    CYAN = 8
    BROWN = 9
    GRAY = 10
    LIME = 11
    TEAL = 12

    def __repr__(self) -> str:  # pragma: no cover
        return f"Color.{self.name}"


# ---------------------------------------------------------------------------
# Tube
# ---------------------------------------------------------------------------

class Tube:
    """A test tube that holds a stack of colored blocks.

    The tube has a fixed *capacity* (number of block slots).  Blocks are
    stored in a list from *bottom* (index 0) to *top* (index ``len - 1``).

    Args:
        capacity: Maximum number of blocks the tube can hold (default 4).
        blocks: Initial blocks from bottom to top.  Must not exceed
            *capacity* in length.

    Raises:
        ValueError: If the initial blocks exceed the tube capacity.
    """

    def __init__(
        self,
        capacity: int = 4,
        blocks: Optional[List[Color]] = None,
    ) -> None:
        if capacity < 1:
            raise ValueError(f"capacity must be at least 1, got {capacity}")
        self._capacity = capacity
        self._blocks: List[Color] = list(blocks) if blocks else []
        if len(self._blocks) > self._capacity:
            raise ValueError(
                f"Initial blocks ({len(self._blocks)}) exceed capacity ({self._capacity})."
            )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def capacity(self) -> int:
        """Maximum number of blocks this tube can hold."""
        return self._capacity

    @property
    def blocks(self) -> List[Color]:
        """Current blocks from bottom to top (read-only copy)."""
        return list(self._blocks)

    @property
    def top(self) -> Optional[Color]:
        """The color of the topmost block, or ``None`` if the tube is empty."""
        return self._blocks[-1] if self._blocks else None

    @property
    def size(self) -> int:
        """Current number of blocks in the tube."""
        return len(self._blocks)

    @property
    def free_space(self) -> int:
        """Number of empty slots remaining."""
        return self._capacity - self.size

    @property
    def is_empty(self) -> bool:
        """Return ``True`` if the tube has no blocks."""
        return self.size == 0

    @property
    def is_full(self) -> bool:
        """Return ``True`` if the tube has no free slots."""
        return self.size == self._capacity

    @property
    def is_complete(self) -> bool:
        """Return ``True`` when the tube is either empty or completely filled
        with a single color.

        A complete tube counts as "solved" for the win condition.
        """
        if self.is_empty:
            return True
        return self.is_full and len(set(self._blocks)) == 1

    @property
    def top_group_size(self) -> int:
        """Number of consecutive same-colored blocks on top of the tube.

        Returns 0 for an empty tube.

        Example::

            Tube(blocks=[RED, BLUE, BLUE]) → top_group_size == 2
        """
        if self.is_empty:
            return 0
        count = 0
        top_color = self._blocks[-1]
        for color in reversed(self._blocks):
            if color == top_color:
                count += 1
            else:
                break
        return count

    # ------------------------------------------------------------------
    # Mutation helpers (used internally by GameBoard)
    # ------------------------------------------------------------------

    def _push(self, color: Color) -> None:
        """Push a single block onto the top.  Internal use only."""
        if self.is_full:
            raise ValueError("Tube is full.")
        self._blocks.append(color)

    def _pop(self) -> Color:
        """Pop the topmost block.  Internal use only."""
        if self.is_empty:
            raise ValueError("Tube is empty.")
        return self._blocks.pop()

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def to_tuple(self) -> Tuple[Optional[int], ...]:
        """Return a hashable representation of the tube's block stack.

        The representation is padded to *capacity* length with ``None`` values
        so that tubes with the same blocks but different capacities are still
        distinguished.
        """
        raw: List[Optional[int]] = [c.value for c in self._blocks]
        raw += [None] * self.free_space
        return tuple(raw)

    def copy(self) -> "Tube":
        """Return a deep copy of this tube."""
        return Tube(capacity=self._capacity, blocks=list(self._blocks))

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tube):
            return NotImplemented
        return self._capacity == other._capacity and self._blocks == other._blocks

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __repr__(self) -> str:
        names = [c.name for c in self._blocks]
        return f"Tube(capacity={self._capacity}, blocks={names})"


# ---------------------------------------------------------------------------
# Move
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Move:
    """Represents a single game move: pour from *from_tube* into *to_tube*.

    Attributes:
        from_tube: Zero-based index of the source tube.
        to_tube: Zero-based index of the destination tube.
    """

    from_tube: int
    to_tube: int

    def __post_init__(self) -> None:
        if self.from_tube < 0:
            raise ValueError(f"from_tube must be non-negative, got {self.from_tube}")
        if self.to_tube < 0:
            raise ValueError(f"to_tube must be non-negative, got {self.to_tube}")
        if self.from_tube == self.to_tube:
            raise ValueError("from_tube and to_tube must be different.")

    def __repr__(self) -> str:
        return f"Move({self.from_tube} → {self.to_tube})"


# ---------------------------------------------------------------------------
# GameBoard
# ---------------------------------------------------------------------------

class GameBoard:
    """The full state of a sortchange puzzle.

    A board consists of an ordered list of :class:`Tube` objects.  The board
    is considered *solved* when every tube is either empty or completely
    filled with a single color.

    Args:
        tubes: The initial tubes.  Each tube must have the same capacity.

    Raises:
        ValueError: If *tubes* is empty or tubes have different capacities.
    """

    def __init__(self, tubes: List[Tube]) -> None:
        if not tubes:
            raise ValueError("GameBoard must have at least one tube.")
        capacities = {t.capacity for t in tubes}
        if len(capacities) > 1:
            raise ValueError(
                f"All tubes must have the same capacity. Found: {capacities}"
            )
        self._tubes: List[Tube] = [t.copy() for t in tubes]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def tubes(self) -> List[Tube]:
        """Current tubes (read-only copies)."""
        return [t.copy() for t in self._tubes]

    @property
    def num_tubes(self) -> int:
        """Total number of tubes on the board."""
        return len(self._tubes)

    @property
    def tube_capacity(self) -> int:
        """Maximum block capacity shared by all tubes."""
        return self._tubes[0].capacity

    @property
    def is_solved(self) -> bool:
        """Return ``True`` when every tube is complete (empty or single-color full)."""
        return all(t.is_complete for t in self._tubes)

    # ------------------------------------------------------------------
    # Move validation & application
    # ------------------------------------------------------------------

    def is_valid_move(self, move: Move) -> bool:
        """Return ``True`` if *move* is legal on the current board state.

        A move is legal when:

        1. Both tube indices are within range.
        2. The source tube is not empty.
        3. The source tube is not already complete (no need to move it).
        4. The destination tube is not full.
        5. The destination tube is either empty, or its top color matches
           the source tube's top color.

        Args:
            move: The move to validate.

        Returns:
            ``True`` if the move is legal, ``False`` otherwise.
        """
        n = self.num_tubes
        if move.from_tube >= n or move.to_tube >= n:
            return False

        src = self._tubes[move.from_tube]
        dst = self._tubes[move.to_tube]

        if src.is_empty:
            return False
        if src.is_complete:
            return False
        if dst.is_full:
            return False
        if not dst.is_empty and dst.top != src.top:
            return False

        return True

    def apply_move(self, move: Move) -> "GameBoard":
        """Apply *move* and return the resulting new :class:`GameBoard`.

        The current board is **not mutated**; a new board is returned.

        Args:
            move: The move to apply.  Must be a valid move.

        Returns:
            A new :class:`GameBoard` with the move applied.

        Raises:
            ValueError: If the move is not valid.
        """
        if not self.is_valid_move(move):
            raise ValueError(f"Invalid move: {move}")

        new_board = self.copy()
        src = new_board._tubes[move.from_tube]
        dst = new_board._tubes[move.to_tube]

        # Move as many same-colored blocks from src to dst as possible.
        moving_color = src.top
        blocks_to_move = min(src.top_group_size, dst.free_space)

        for _ in range(blocks_to_move):
            dst._push(src._pop())

        return new_board

    def get_valid_moves(self) -> List[Move]:
        """Return all legal moves available from the current board state.

        Returns:
            A list of :class:`Move` objects, possibly empty if the board is
            already solved or no moves are available.
        """
        moves: List[Move] = []
        for i in range(self.num_tubes):
            for j in range(self.num_tubes):
                if i == j:
                    continue
                m = Move(from_tube=i, to_tube=j)
                if self.is_valid_move(m):
                    moves.append(m)
        return moves

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def to_state(self) -> Tuple:
        """Return a hashable representation of the board for use in search.

        The state is a tuple of per-tube tuples, sorted so that boards that
        differ only by tube order are still treated as distinct (tube order
        matters for move indexing).
        """
        return tuple(t.to_tuple() for t in self._tubes)

    def copy(self) -> "GameBoard":
        """Return a deep copy of this board."""
        return GameBoard([t.copy() for t in self._tubes])

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GameBoard):
            return NotImplemented
        return self._tubes == other._tubes

    def __hash__(self) -> int:
        return hash(self.to_state())

    def __repr__(self) -> str:
        lines = ["GameBoard:"]
        for i, tube in enumerate(self._tubes):
            names = " | ".join(c.name for c in tube.blocks) if tube.blocks else "(empty)"
            status = " ✓" if tube.is_complete else ""
            lines.append(f"  [{i}] {names}{status}")
        return "\n".join(lines)
