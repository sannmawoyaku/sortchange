# Functions

## sortchange.models — メソッド一覧

### `Tube`

| メソッド | 戻り値 | 説明 |
|---------|--------|------|
| `copy()` | `Tube` | 深いコピーを返す |
| `to_tuple()` | `Tuple` | ハッシュ可能な状態表現 |

### `GameBoard`

| メソッド | 戻り値 | 説明 |
|---------|--------|------|
| `is_valid_move(move)` | `bool` | 指定の手が合法かどうかを返す |
| `apply_move(move)` | `GameBoard` | 手を適用した**新しい**ボードを返す（元のボードは変更しない） |
| `get_valid_moves()` | `List[Move]` | 現在の状態から可能な全合法手を返す |
| `to_state()` | `Tuple` | BFS用のハッシュ可能な状態表現 |
| `copy()` | `GameBoard` | 深いコピーを返す |

---

## sortchange.game — ゲームロジックヘルパー

### `is_valid_move(board, move) -> bool`

`board` 上で `move` が合法かどうかを返します。  
`board.is_valid_move(move)` への委譲です。

**合法手の条件：**
1. 両インデックスがチューブ数の範囲内
2. 移動元が空でない
3. 移動元がすでに complete でない
4. 移動先が満杯でない
5. 移動先が空、または移動先の最上部色が移動元の最上部色と一致

---

### `apply_move(board, move) -> GameBoard`

`move` を適用した新しい `GameBoard` を返します。元のボードは変更しません。

---

### `is_solved(board) -> bool`

全てのチューブが complete（空 or 単色満杯）なら `True` を返します。

---

### `get_valid_moves(board) -> List[Move]`

現在の状態から可能な全合法手のリストを返します。

---

## sortchange.solver — BFSソルバー

### `solve(board, max_moves=200) -> Optional[List[Move]]`

幅優先探索（BFS）で最短手順の解を求めます。

| 引数 | 型 | デフォルト | 説明 |
|-----|-----|-----------|------|
| `board` | `GameBoard` | — | 初期ボード状態 |
| `max_moves` | `int` | `200` | 探索の最大手数（安全上限） |

**戻り値：** `List[Move]`（解の手順）、解なしの場合は `None`

**既に解けている場合** は空リスト `[]` を返します。

---

## sortchange.factory — ボード生成ユーティリティ

### `create_board(num_colors, tube_capacity=4, empty_tubes=2, seed=None) -> GameBoard`

ランダムにシャッフルされたパズルボードを生成します。

| 引数 | 型 | デフォルト | 説明 |
|-----|-----|-----------|------|
| `num_colors` | `int` | — | 色の種類数 |
| `tube_capacity` | `int` | `4` | チューブの容量 |
| `empty_tubes` | `int` | `2` | 空チューブの数 |
| `seed` | `Optional[int]` | `None` | 再現性のための乱数シード |

---

### `create_solved_board(num_colors, tube_capacity=4, empty_tubes=0) -> GameBoard`

クリア済み状態のボードを生成します（テスト・リファレンス用）。

---

### `create_board_from_lists(color_lists, tube_capacity=4) -> GameBoard`

リストのリストからボードを生成します。`None` は空スロットとして扱います。

```python
board = create_board_from_lists(
    [[Color.RED, Color.BLUE], [Color.BLUE, Color.RED], []],
    tube_capacity=4,
)
```
