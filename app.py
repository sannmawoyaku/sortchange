"""Streamlit web UI for the sortchange tube-sorting puzzle game."""

from __future__ import annotations

import streamlit as st

from sortchange import Color, GameBoard, Move, create_board, solve

# ---------------------------------------------------------------------------
# Color constants
# ---------------------------------------------------------------------------

_COLOR_HEX: dict[Color, str] = {
    Color.RED: "#e74c3c",
    Color.BLUE: "#3498db",
    Color.GREEN: "#27ae60",
    Color.YELLOW: "#f1c40f",
    Color.ORANGE: "#e67e22",
    Color.PURPLE: "#9b59b6",
    Color.PINK: "#ff69b4",
    Color.CYAN: "#1abc9c",
    Color.BROWN: "#8b4513",
    Color.GRAY: "#95a5a6",
}

_COLOR_NAMES: dict[Color, str] = {
    Color.RED: "赤",
    Color.BLUE: "青",
    Color.GREEN: "緑",
    Color.YELLOW: "黄",
    Color.ORANGE: "橙",
    Color.PURPLE: "紫",
    Color.PINK: "桃",
    Color.CYAN: "水",
    Color.BROWN: "茶",
    Color.GRAY: "灰",
}

_BLOCK_HEIGHT = 42  # px per block
_TUBE_WIDTH = 56    # px per tube column


# ---------------------------------------------------------------------------
# Helper: render a single tube as HTML
# ---------------------------------------------------------------------------

def _tube_html(tube_index: int, tube, capacity: int, highlight: bool = False) -> str:
    """Return HTML for one tube rendered as a vertical test-tube shape."""
    border_color = "#f39c12" if highlight else "#555"
    border_width = 3 if highlight else 2

    # Build blocks top-to-bottom: first pad empty slots, then reversed blocks
    slots = [None] * (capacity - tube.size) + list(reversed(tube.blocks))

    rows_html = ""
    for slot in slots:
        if slot is None:
            cell = (
                '<div style="'
                f"height:{_BLOCK_HEIGHT}px;"
                "background:#1e1e2e;"
                "border-bottom:1px solid #333;"
                '"></div>'
            )
        else:
            hex_color = _COLOR_HEX[slot]
            label = _COLOR_NAMES[slot]
            cell = (
                '<div style="'
                f"height:{_BLOCK_HEIGHT}px;"
                f"background:{hex_color};"
                "display:flex;align-items:center;justify-content:center;"
                "font-size:12px;font-weight:bold;color:#fff;"
                f"text-shadow:0 0 3px #000;"
                "border-bottom:1px solid rgba(0,0,0,0.2);"
                f'">{label}</div>'
            )
        rows_html += cell

    complete_mark = " ✓" if tube.is_complete else ""
    label_style = (
        "text-align:center;font-size:13px;color:#aaa;margin-top:4px;"
    )

    return (
        f'<div style="display:inline-block;margin:0 4px;vertical-align:top;">'
        f'<div style="'
        f"width:{_TUBE_WIDTH}px;"
        f"border:{border_width}px solid {border_color};"
        "border-top:none;"
        "border-radius:0 0 8px 8px;"
        "overflow:hidden;"
        f'">'
        f"{rows_html}"
        f"</div>"
        f'<div style="{label_style}">[{tube_index}]{complete_mark}</div>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Helper: render the full board
# ---------------------------------------------------------------------------

def _board_html(board: GameBoard, highlighted: set[int] | None = None) -> str:
    highlighted = highlighted or set()
    capacity = board.tube_capacity
    inner = "".join(
        _tube_html(i, tube, capacity, highlight=(i in highlighted))
        for i, tube in enumerate(board.tubes)
    )
    return (
        '<div style="'
        "display:flex;flex-wrap:wrap;gap:4px;"
        "background:#12121f;padding:16px;border-radius:12px;"
        f'">{inner}</div>'
    )


# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------

def _init_state() -> None:
    if "board" not in st.session_state:
        st.session_state.board = create_board(num_colors=4, tube_capacity=4, empty_tubes=1, seed=None)
        st.session_state.move_count = 0
        st.session_state.hint_move = None
        st.session_state.message = ""


def _new_game(num_colors: int, tube_capacity: int, empty_tubes: int, seed: int | None) -> None:
    st.session_state.board = create_board(
        num_colors=num_colors,
        tube_capacity=tube_capacity,
        empty_tubes=empty_tubes,
        seed=seed,
    )
    st.session_state.move_count = 0
    st.session_state.hint_move = None
    st.session_state.message = "新しいゲームを開始しました！"


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
    st.caption("同じ色のブロックを同じ試験管にまとめるとクリアです")

    # ------------------------------------------------------------------
    # Sidebar: new game settings
    # ------------------------------------------------------------------
    with st.sidebar:
        st.header("⚙️ 新しいゲーム設定")
        num_colors = st.slider("色の数", min_value=2, max_value=10, value=4)
        empty_tubes = st.slider("空の試験管の数", min_value=1, max_value=3, value=1)
        tube_capacity = st.slider("試験管の容量", min_value=3, max_value=6, value=4)
        seed_input = st.text_input("シード（空欄でランダム）", value="", placeholder="例: 42")
        try:
            seed = int(seed_input.strip()) if seed_input.strip() else None
        except ValueError:
            seed = None
            st.warning("シードは整数で入力してください")

        if st.button("🎮 新しいゲームを開始", use_container_width=True):
            _new_game(num_colors, tube_capacity, empty_tubes, seed)
            st.rerun()

        st.divider()
        st.markdown(f"**現在の手数:** {st.session_state.move_count}")

    # ------------------------------------------------------------------
    # Board display
    # ------------------------------------------------------------------
    board: GameBoard = st.session_state.board

    # Highlight hint move tubes if hint is active
    highlighted: set[int] = set()
    hint_move: Move | None = st.session_state.hint_move
    if hint_move is not None:
        highlighted = {hint_move.from_tube, hint_move.to_tube}

    st.markdown(_board_html(board, highlighted), unsafe_allow_html=True)

    if hint_move is not None:
        st.info(
            f"💡 ヒント: 試験管 **{hint_move.from_tube}** → 試験管 **{hint_move.to_tube}** に移動してみましょう"
        )

    # ------------------------------------------------------------------
    # Message banner
    # ------------------------------------------------------------------
    if st.session_state.message:
        st.success(st.session_state.message)
        st.session_state.message = ""

    # ------------------------------------------------------------------
    # Win detection
    # ------------------------------------------------------------------
    if board.is_solved:
        st.balloons()
        st.success(f"🎉 クリア！ {st.session_state.move_count} 手で完成しました！")
        return

    # ------------------------------------------------------------------
    # Move controls
    # ------------------------------------------------------------------
    st.subheader("移動")

    tube_labels = [
        f"[{i}] {' | '.join(_COLOR_NAMES[c] for c in t.blocks) or '(空)'}"
        for i, t in enumerate(board.tubes)
    ]

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        from_idx = st.selectbox("移動元", range(board.num_tubes), format_func=lambda i: tube_labels[i], key="from_select")
    with col2:
        to_idx = st.selectbox("移動先", range(board.num_tubes), format_func=lambda i: tube_labels[i], key="to_select")
    with col3:
        st.markdown('<div style="height:28px"></div>', unsafe_allow_html=True)
        move_clicked = st.button("➡️ 移動", use_container_width=True)

    col_hint, col_undo = st.columns(2)
    with col_hint:
        if st.button("💡 ヒントを表示", use_container_width=True):
            solution = solve(board)
            if solution is None:
                st.session_state.hint_move = None
                st.warning("このボードには解がありません。")
            elif not solution:
                st.session_state.hint_move = None
                st.success("すでに解けています！")
            else:
                st.session_state.hint_move = solution[0]
            st.rerun()

    with col_undo:
        # Show hint clear button when hint is shown
        if hint_move is not None:
            if st.button("✖️ ヒントを消す", use_container_width=True):
                st.session_state.hint_move = None
                st.rerun()

    # ------------------------------------------------------------------
    # Apply move
    # ------------------------------------------------------------------
    if move_clicked:
        if from_idx == to_idx:
            st.error("移動元と移動先が同じです。")
        else:
            move = Move(from_tube=from_idx, to_tube=to_idx)
            if not board.is_valid_move(move):
                st.error(f"無効な手です: [{from_idx}] → [{to_idx}]")
            else:
                st.session_state.board = board.apply_move(move)
                st.session_state.move_count += 1
                st.session_state.hint_move = None
                st.rerun()


if __name__ == "__main__":
    main()
