# sortchange

**試験管ソートパズルゲーム** のPythonライブラリです。

複数の試験管（チューブ）に異なる色のブロックが混在した状態からスタートし、  
各チューブを単一の色で揃えるとゲームクリアとなります。

## クイックスタート

```python
from sortchange import Color, create_board_from_lists, solve

board = create_board_from_lists([
    [Color.RED, Color.BLUE, Color.RED, Color.BLUE],
    [Color.BLUE, Color.RED, Color.BLUE, Color.RED],
    [],
    [],
], tube_capacity=4)

solution = solve(board)
for move in solution:
    board = board.apply_move(move)

assert board.is_solved
```

## テスト

```bash
pip install pytest
python -m pytest tests/ -v
```

## インタラクティブプレイ

```bash
# デフォルト設定（3色）でプレイ
python main.py

# 難易度をカスタマイズしてプレイ
python main.py --colors 4 --seed 42

# オプション一覧
python main.py --help
```

## 自動デモ（ソルバー検証用）

```bash
python main.py --demo
```

プレイ中のコマンド:

| コマンド | 説明 |
|---------|------|
| `<移動元> <移動先>` | チューブ間でブロックを移動（例: `0 2`） |
| `h` | ヒントを表示（BFSソルバーが次の最善手を提案） |
| `q` | ゲームを終了 |
