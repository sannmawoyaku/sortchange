# Data Structures

## Color (Enum)

Represents a single block color in a tube.

| Name     | Value | 説明 |
|----------|-------|------|
| `RED`    | 1     | 赤   |
| `BLUE`   | 2     | 青   |
| `GREEN`  | 3     | 緑   |
| `YELLOW` | 4     | 黄   |
| `ORANGE` | 5     | オレンジ |
| `PURPLE` | 6     | 紫   |
| `PINK`   | 7     | ピンク |
| `CYAN`   | 8     | シアン |
| `BROWN`  | 9     | 茶   |
| `GRAY`   | 10    | 灰   |

---

## Tube (試験管)

一本の試験管を表すクラス。ブロックをスタック構造で管理します。

- インデックス `0` = **底（bottom）**
- インデックス `-1` = **上部（top）**
- 全てのチューブは同じ固定の `capacity`（最大ブロック数）を持ちます。

### プロパティ

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `capacity` | `int` | チューブの最大容量（デフォルト 4） |
| `blocks` | `List[Color]` | 底から上へのブロックリスト（読み取り専用コピー） |
| `top` | `Optional[Color]` | 最上部のブロック色。空の場合は `None` |
| `size` | `int` | 現在のブロック数 |
| `free_space` | `int` | 残り空きスロット数 |
| `is_empty` | `bool` | ブロックが0個かどうか |
| `is_full` | `bool` | 空きスロットが0個かどうか |
| `is_complete` | `bool` | 空、または1色で満杯かどうか（クリア条件） |
| `top_group_size` | `int` | 最上部に連続する同色ブロックの数 |

---

## Move (手)

一手の移動操作を表す不変データクラス（`frozen=True`）。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `from_tube` | `int` | 移動元チューブのインデックス（0始まり） |
| `to_tube` | `int` | 移動先チューブのインデックス（0始まり） |

- `from_tube == to_tube` の場合は `ValueError` を発生させます。
- ハッシュ可能（集合・辞書のキーに使用可能）。

---

## GameBoard (ゲームボード)

ゲーム全体の状態を保持するクラス。`Tube` の順序付きリストで構成されます。

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `tubes` | `List[Tube]` | 全チューブの読み取り専用コピー |
| `num_tubes` | `int` | チューブの総数 |
| `tube_capacity` | `int` | 各チューブの容量（全て同じ） |
| `is_solved` | `bool` | 全チューブが complete な場合 `True` |

ハッシュ可能（BFS探索の訪問済み状態管理に使用）。
