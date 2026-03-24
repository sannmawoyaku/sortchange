# Implementation

## 概要

`sortchange` は**試験管ソートパズルゲーム**のPythonライブラリです。

複数の試験管（チューブ）に異なる色のブロックが混在した状態からスタートし、  
各チューブを単一の色で揃えるとゲームクリアとなります。

---

## ゲームルール

| ルール | 内容 |
|--------|------|
| 移動操作 | チューブの最上部にある**同色連続ブロック**をまとめて別のチューブへ注ぐ |
| 移動条件 | 移動先が**空**、または移動先の最上部色が移動元と**同じ** |
| 移動制限 | 移動先に**空きスロット**が必要 |
| クリア条件 | 全てのチューブが**空**または**1色で満杯** |

---

## プロジェクト構成

```
sortchange/
├── sortchange/
│   ├── __init__.py          # 公開APIの再エクスポート
│   ├── models.py            # Color, Tube, GameBoard, Move データ構造
│   ├── game.py              # ゲームロジックヘルパー関数
│   ├── solver.py            # BFS自動ソルバー
│   └── factory.py           # ボード生成ユーティリティ
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # データ構造テスト（54テスト）
│   ├── test_game.py          # ゲームロジックテスト（10テスト）
│   ├── test_solver.py        # ソルバーテスト（7テスト）
│   └── test_factory.py       # ファクトリテスト（12テスト）
├── main.py                   # CLIデモ
├── requirements.txt
└── README.md
```

---

## アーキテクチャ設計

### 不変性（Immutability）

`GameBoard.apply_move()` は元のボードを変更せず、新しいボードオブジェクトを返します。  
これによりBFS探索での状態管理が安全かつシンプルになります。

### 状態のハッシュ化

`GameBoard.to_state()` は全チューブの内容をタプルで表現し、  
BFS探索の `visited` 集合でのO(1)重複チェックを可能にします。

---

## ソルバーアルゴリズム

BFS（幅優先探索）を使用して**最短手数**の解を求めます。

```
queue = [(initial_board, [])]
visited = {initial_state}

while queue:
    current, path = queue.popleft()
    for each valid_move:
        next_board = current.apply_move(move)
        if next_board.state not in visited:
            visited.add(next_board.state)
            if next_board.is_solved:
                return path + [move]   # 最短解を返す
            queue.append((next_board, path + [move]))
```

- **計算量**: O(S × M)  S=訪問済み状態数、M=1状態あたりの合法手数
- **空間量**: O(S)

---

## 使用例

```python
from sortchange import Color, Tube, GameBoard, create_board_from_lists, solve

# ボードを手動で定義
board = create_board_from_lists([
    [Color.RED, Color.BLUE, Color.RED, Color.BLUE],
    [Color.BLUE, Color.RED, Color.BLUE, Color.RED],
    [],  # 空チューブ
    [],  # 空チューブ
], tube_capacity=4)

# 自動で解く
solution = solve(board)
print(f"解: {len(solution)} 手")

for move in solution:
    board = board.apply_move(move)

assert board.is_solved  # クリア確認
```

---

## テスト実行

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## 新しい色の追加方法

1. `sortchange/models.py` の `Color` 列挙型に新しい色を追加する
2. `sortchange/factory.py` の `ALL_COLORS` リストに含まれる（自動）
3. テストを追加する
