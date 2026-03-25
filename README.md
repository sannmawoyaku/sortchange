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

## デモ

```bash
python main.py
```
