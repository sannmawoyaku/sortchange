"""Streamlit web UI for the sortchange tube-sorting puzzle game."""

from __future__ import annotations

import streamlit as st

from sortchange import Color, GameBoard, Move, create_board, solve

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

# Hex colour for each block colour.
_COLOR_HEX: dict[Color, str] = {
    Color.RED:    "#e74c3c",
    Color.BLUE:   "#3498db",
    Color.GREEN:  "#27ae60",
    Color.YELLOW: "#f1c40f",
    Color.ORANGE: "#e67e22",
    Color.PURPLE: "#9b59b6",
    Color.PINK:   "#ff69b4",
    Color.CYAN:   "#1abc9c",
    Color.BROWN:  "#8b4513",
    Color.GRAY:   "#95a5a6",
}

# Short Japanese label shown inside each block.
_COLOR_NAMES: dict[Color, str] = {
    Color.RED:    "赤",
    Color.BLUE:   "青",
    Color.GREEN:  "緑",
    Color.YELLOW: "黄",
    Color.ORANGE: "橙",
    Color.PURPLE: "紫",
    Color.PINK:   "桃",
    Color.CYAN:   "水",
    Color.BROWN:  "茶",
    Color.GRAY:   "灰",
}

# Colours where white text would be hard to read → use black text instead.
_DARK_TEXT: frozenset[Color] = frozenset({Color.YELLOW, Color.CYAN, Color.GRAY})

_BLOCK_H = 44   # block height in px
_TUBE_W  = 68   # tube width in px


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------

def _block_html(color: Color) -> str:
    """Return an HTML div for one filled block."""
    bg    = _COLOR_HEX[color]
    label = _COLOR_NAMES[color]
    text  = "#111" if color in _DARK_TEXT else "#fff"
    return (
        f'<div style="height:{_BLOCK_H}px;background:{bg};'
        f'display:flex;align-items:center;justify-content:center;'
        f'font-size:13px;font-weight:700;color:{text};'
        f'text-shadow:none;border-bottom:1px solid rgba(0,0,0,0.15);">'
        f'{label}</div>'
    )


def _empty_block_html() -> str:
    """Return an HTML div for one empty slot."""
    return (
        f'<div style="height:{_BLOCK_H}px;background:#1e1e2e;'
        f'border-bottom:1px solid #2e2e3e;"></div>'
    )


def _tube_html(index: int, tube, capacity: int, highlight: bool) -> str:
    """Return HTML for a single tube column."""
    border_color = "#f39c12" if highlight else "#444"
    border_w     = 3         if highlight else 2
    bg_label     = "#f39c12" if highlight else "#2a2a3e"
    solved_badge = (
        '<div style="font-size:18px;text-align:center;line-height:1;">✓</div>'
        if tube.is_complete and not tube.is_empty else ""
    )

    # Slots rendered top-to-bottom: empty slots first, then blocks in reverse
    slots_html = "".join(
        _empty_block_html() if slot is None else _block_html(slot)
        for slot in ([None] * (capacity - tube.size) + list(reversed(tube.blocks)))
    )

    return (
        f'<div style="display:inline-flex;flex-direction:column;'
        f'align-items:center;margin:0 5px 12px 5px;">'
        # tube body
        f'<div style="width:{_TUBE_W}px;'
        f'border:{border_w}px solid {border_color};'
        f'border-top:none;border-radius:0 0 10px 10px;overflow:hidden;">'
        f'{slots_html}'
        f'</div>'
        # label bar below the tube
        f'<div style="width:{_TUBE_W}px;margin-top:4px;'
        f'background:{bg_label};border-radius:4px;padding:2px 0;'
        f'text-align:center;font-size:13px;font-weight:600;color:#eee;">'
        f'{index}{solved_badge}'
        f'</div>'
        f'</div>'
    )


def _board_html(board: GameBoard, highlighted: frozenset[int]) -> str:
    """Return HTML for the full board."""
    capacity = board.tube_capacity
    tubes_html = "".join(
        _tube_html(i, tube, capacity, highlight=(i in highlighted))
        for i, tube in enumerate(board.tubes)
    )
    return (
        '<div style="display:flex;flex-wrap:wrap;gap:0;'
        'background:#12121f;padding:20px;border-radius:14px;'
        'justify-content:flex-start;">'
        f'{tubes_html}'
        '</div>'
    )


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------

def _init_state() -> None:
    """Initialise session state on the very first run."""
    if "board" not in st.session_state:
        st.session_state.board      = create_board(num_colors=4, tube_capacity=4, empty_tubes=1)
        st.session_state.move_count = 0
        st.session_state.hint_move  = None
        st.session_state.game_won   = False  # prevents balloons from replaying every rerun
        st.session_state.error_msg  = ""


def _start_new_game(num_colors: int, tube_capacity: int, empty_tubes: int, seed: int | None) -> None:
    """Reset all state and generate a new puzzle."""
    st.session_state.board      = create_board(num_colors=num_colors, tube_capacity=tube_capacity,
                                               empty_tubes=empty_tubes, seed=seed)
    st.session_state.move_count = 0
    st.session_state.hint_move  = None
    st.session_state.game_won   = False
    st.session_state.error_msg  = ""


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="試験管ソートパズル",
        page_icon="🧪",
        layout="wide",
    )

    _init_state()

    st.title("🧪 試験管ソートパズル")
    st.caption("同じ色のブロックを同じ試験管に揃えるとクリア！")

    # ------------------------------------------------------------------
    # Sidebar ― new-game settings
    # ------------------------------------------------------------------
    with st.sidebar:
        st.header("⚙️ ゲーム設定")
        num_colors    = st.slider("色の数",          min_value=2, max_value=10, value=4)
        empty_tubes   = st.slider("空の試験管の数",   min_value=1, max_value=3,  value=1)
        tube_capacity = st.slider("試験管の容量",     min_value=3, max_value=6,  value=4)

        seed_raw = st.text_input("シード（空欄でランダム）", value="", placeholder="例: 42")
        seed: int | None = None
        if seed_raw.strip():
            try:
                seed = int(seed_raw.strip())
            except ValueError:
                st.warning("シードは整数で入力してください")

        if st.button("🎮 新しいゲームを開始", use_container_width=True):
            _start_new_game(num_colors, tube_capacity, empty_tubes, seed)
            st.rerun()

        st.divider()
        st.metric("手数", st.session_state.move_count)

    # ------------------------------------------------------------------
    # Snapshot current state
    # ------------------------------------------------------------------
    board: GameBoard       = st.session_state.board
    hint_move: Move | None = st.session_state.hint_move
    highlighted = frozenset(
        {hint_move.from_tube, hint_move.to_tube} if hint_move else set()
    )

    # ------------------------------------------------------------------
    # Board rendering
    # ------------------------------------------------------------------
    st.markdown(_board_html(board, highlighted), unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Win detection (balloons fire only once per game)
    # ------------------------------------------------------------------
    if board.is_solved:
        if not st.session_state.game_won:
            st.session_state.game_won = True
            st.balloons()
        st.success(f"🎉 クリア！ **{st.session_state.move_count}** 手で完成しました！おめでとうございます！")
        st.info("サイドバーの「新しいゲームを開始」から次の問題に挑戦できます。")
        return  # hide move controls after winning

    # ------------------------------------------------------------------
    # Hint banner
    # ------------------------------------------------------------------
    if hint_move is not None:
        st.info(
            f"💡 ヒント：試験管 **{hint_move.from_tube}** → 試験管 **{hint_move.to_tube}** に移動してみましょう"
        )

    # ------------------------------------------------------------------
    # Error banner (cleared after one render)
    # ------------------------------------------------------------------
    if st.session_state.error_msg:
        st.error(st.session_state.error_msg)
        st.session_state.error_msg = ""

    # ------------------------------------------------------------------
    # Move controls
    # ------------------------------------------------------------------
    st.subheader("移動")

    tube_labels = [
        f"{i}番 ― {' | '.join(_COLOR_NAMES[c] for c in t.blocks) or '（空）'}"
        for i, t in enumerate(board.tubes)
    ]

    col_from, col_to, col_btn = st.columns([3, 3, 2])
    with col_from:
        from_idx: int = st.selectbox(
            "移動元（from）", range(board.num_tubes),
            format_func=lambda i: tube_labels[i], key="from_sel",
        )
    with col_to:
        to_idx: int = st.selectbox(
            "移動先（to）", range(board.num_tubes),
            format_func=lambda i: tube_labels[i], key="to_sel",
        )
    with col_btn:
        st.markdown('<div style="height:29px"></div>', unsafe_allow_html=True)
        move_clicked = st.button("➡️ 移動する", use_container_width=True, type="primary")

    # Hint / dismiss hint buttons on the same row
    col_hint, col_dismiss = st.columns(2)
    with col_hint:
        if st.button("💡 ヒントを表示", use_container_width=True):
            solution = solve(board)
            if solution is None:
                st.session_state.hint_move = None
                st.session_state.error_msg = "このボードには解がありません。"
            elif not solution:
                st.session_state.hint_move = None
            else:
                st.session_state.hint_move = solution[0]
            st.rerun()
    with col_dismiss:
        if hint_move is not None:
            if st.button("✖ ヒントを消す", use_container_width=True):
                st.session_state.hint_move = None
                st.rerun()

    # ------------------------------------------------------------------
    # Apply move
    # ------------------------------------------------------------------
    if move_clicked:
        if from_idx == to_idx:
            st.session_state.error_msg = "移動元と移動先が同じです。"
            st.rerun()
        else:
            move = Move(from_tube=from_idx, to_tube=to_idx)
            if not board.is_valid_move(move):
                st.session_state.error_msg = (
                    f"無効な手です（{from_idx}番 → {to_idx}番）。"
                    " 色が合わないか、移動先が満杯です。"
                )
                st.rerun()
            else:
                st.session_state.board      = board.apply_move(move)
                st.session_state.move_count += 1
                st.session_state.hint_move  = None
                st.rerun()


if __name__ == "__main__":
    main()
