"""迷路自動生成プログラム（穴掘り法 / 再帰的バックトラッキング）"""
import argparse
import os
import random
import struct
import zlib


def generate_maze(width, height, seed=None):
    """width x height セルの迷路を生成し、0=通路 1=壁 のグリッドを返す"""
    rng = random.Random(seed)
    W, H = width * 2 + 1, height * 2 + 1
    grid = [[1] * W for _ in range(H)]
    stack = [(0, 0)]
    grid[1][1] = 0
    while stack:
        cx, cy = stack[-1]
        neighbors = [(cx + dx, cy + dy, dx, dy)
                     for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                     if 0 <= cx + dx < width and 0 <= cy + dy < height
                     and grid[(cy + dy) * 2 + 1][(cx + dx) * 2 + 1] == 1]
        if neighbors:
            nx, ny, dx, dy = rng.choice(neighbors)
            grid[cy * 2 + 1 + dy][cx * 2 + 1 + dx] = 0
            grid[ny * 2 + 1][nx * 2 + 1] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    grid[1][0] = 0            # 入口（左上）
    grid[H - 2][W - 1] = 0    # 出口（右下）
    return grid


def save_maze_png(grid, path, cell_size=10):
    """標準ライブラリのみでPNGを書き出す（入口=緑, 出口=赤）"""
    H, W = len(grid), len(grid[0])
    colors = {0: b"\xff\xff\xff", 1: b"\x00\x00\x00"}
    special = {(1, 0): b"\x00\xb0\x00", (H - 2, W - 1): b"\xe0\x00\x00"}
    raw = bytearray()
    for y in range(H):
        line = b"".join(special.get((y, x), colors[grid[y][x]]) * cell_size for x in range(W))
        for _ in range(cell_size):
            raw += b"\x00" + line

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", W * cell_size, H * cell_size, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main():
    p = argparse.ArgumentParser(description="迷路を自動生成してPNGで保存します")
    p.add_argument("-n", "--count", type=int, default=10, help="生成する迷路の数")
    p.add_argument("--width", type=int, default=20, help="横のセル数")
    p.add_argument("--height", type=int, default=20, help="縦のセル数")
    p.add_argument("--cell", type=int, default=10, help="1マスのピクセル数")
    p.add_argument("-o", "--outdir", default=os.path.dirname(os.path.abspath(__file__)))
    args = p.parse_args()
    for i in range(1, args.count + 1):
        path = os.path.join(args.outdir, f"maze_{i:02d}.png")
        save_maze_png(generate_maze(args.width, args.height), path, args.cell)
        print("saved:", path)


if __name__ == "__main__":
    main()
