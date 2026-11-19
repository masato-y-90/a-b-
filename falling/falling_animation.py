"""物体（ボール）が重力で落下し、地面で跳ね返るアニメーション"""
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

G = 9.8            # 重力加速度 [m/s^2]
DT = 0.02          # 1フレームの時間 [s]
RESTITUTION = 0.8  # 反発係数
RADIUS = 0.3       # ボールの半径 [m]

y = 10.0   # 初期高さ [m]
v = 0.0    # 初期速度 [m/s]

fig, ax = plt.subplots(figsize=(4, 6))
ax.set_xlim(-2, 2)
ax.set_ylim(0, 11)
ax.set_aspect("equal")
ax.axhline(0, color="saddlebrown", linewidth=4)
ax.set_title("Falling Ball")
ball = plt.Circle((0, y), RADIUS, color="tab:red")
ax.add_patch(ball)
text = ax.text(-1.9, 10.5, "", fontsize=9)


def update(frame):
    global y, v
    v -= G * DT
    y += v * DT
    if y - RADIUS <= 0:          # 地面に衝突したら跳ね返る
        y = RADIUS
        v = -v * RESTITUTION
    ball.center = (0, y)
    text.set_text(f"t={frame * DT:.2f}s  h={y:.2f}m  v={v:.2f}m/s")
    return ball, text


anim = FuncAnimation(fig, update, frames=500, interval=DT * 1000, blit=True)

if __name__ == "__main__":
    plt.show()
    # GIFで保存したい場合:
    # anim.save("falling.gif", writer="pillow", fps=50)
