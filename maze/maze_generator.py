"""迷路自動生成プログラム

穴掘り法（再帰的バックトラック法）で迷路を生成し、PNG 画像として保存します。
外部ライブラリ不要（Python 標準ライブラリのみで PNG を書き出します）。

使い方:
    python3 maze_generator.py                 # 迷路を10個生成（maze_01.png 〜 maze_10.png）
    python3 maze_generator.py -n 5 -W 30 -H 20 --cell 12 --seed 42
"""

import argparse
import os
import random
import struct
import zlib

WALL = (30, 30, 30)
PATH = (255, 255, 255)
START = (46, 204, 113)
GOAL = (231, 76, 60)


def generate_maze(width, height, rng):
    """width x height マスの迷路を生成し、壁(True)/通路(False)のグリッドを返す。

    グリッドのサイズは (2*height+1) x (2*width+1)。
    """
    rows, cols = 2 * height + 1, 2 * width + 1
    grid = [[True] * cols for _ in range(rows)]

    start = (0, 0)
    grid[1][1] = False
    visited = {start}
    stack = [start]

    while stack:
        cx, cy = stack[-1]
        neighbors = [
            (nx, ny)
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1))
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited
        ]
        if not neighbors:
            stack.pop()
            continue
        nx, ny = rng.choice(neighbors)
        # 現在のマスと次のマスの間の壁を壊す
        grid[cy + ny + 1][cx + nx + 1] = False
        grid[2 * ny + 1][2 * nx + 1] = False
        visited.add((nx, ny))
        stack.append((nx, ny))

    # 入口（左上）と出口（右下）を開ける
    grid[1][0] = False
    grid[rows - 2][cols - 1] = False
    return grid


def write_png(path, pixels):
    """RGB タプルの2次元リストを PNG ファイルとして保存する。"""
    height = len(pixels)
    width = len(pixels[0])
    raw = bytearray()
    for row in pixels:
        raw.append(0)  # フィルタタイプ: None
        for r, g, b in row:
            raw += bytes((r, g, b))

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


def render(grid, cell):
    """グリッドを cell ピクセル四方のブロックで描画したピクセル配列を返す。"""
    rows, cols = len(grid), len(grid[0])
    start_pos = (1, 0)
    goal_pos = (rows - 2, cols - 1)
    pixels = []
    for y in range(rows):
        line = []
        for x in range(cols):
            if (y, x) == start_pos:
                color = START
            elif (y, x) == goal_pos:
                color = GOAL
            else:
                color = WALL if grid[y][x] else PATH
            line.extend([color] * cell)
        for _ in range(cell):
            pixels.append(line)
    return pixels


def main():
    parser = argparse.ArgumentParser(description="迷路を自動生成して PNG で保存します")
    parser.add_argument("-n", "--count", type=int, default=10, help="生成する迷路の数（既定: 10）")
    parser.add_argument("-W", "--width", type=int, default=25, help="横のマス数（既定: 25）")
    parser.add_argument("-H", "--height", type=int, default=25, help="縦のマス数（既定: 25）")
    parser.add_argument("--cell", type=int, default=10, help="1ブロックのピクセル数（既定: 10）")
    parser.add_argument("--seed", type=int, default=None, help="乱数シード（再現用）")
    parser.add_argument(
        "-o", "--outdir", default=os.path.dirname(os.path.abspath(__file__)),
        help="出力先フォルダ（既定: このスクリプトと同じフォルダ）",
    )
    args = parser.parse_args()

    rng = random.Random(args.seed)
    os.makedirs(args.outdir, exist_ok=True)
    for i in range(1, args.count + 1):
        grid = generate_maze(args.width, args.height, rng)
        path = os.path.join(args.outdir, f"maze_{i:02d}.png")
        write_png(path, render(grid, args.cell))
        print(f"保存しました: {path}")


if __name__ == "__main__":
    main()
