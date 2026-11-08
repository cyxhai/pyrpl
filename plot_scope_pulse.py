# 新加的绘图脚本

import numpy as np
import matplotlib.pyplot as plt
from pyrpl import Pyrpl

# ==========================================
# 1. 参数设置
# ==========================================

CONFIG = "myconfig"

INPUT_CHANNEL = "in1"

# 根据你目前的波形设置
TRIGGER_THRESHOLD = 0.020       # 触发阈值，单位 V
TRIGGER_HYSTERESIS = 0.002      # 触发迟滞，单位 V

# 放大图的横轴范围（相对于触发时刻）
ZOOM_HALF_WIDTH_US = 0.30       # 显示 -0.3 ~ +0.3 us

# 是否保存图片和原始数据
SAVE_FIGURE = True
SAVE_DATA = True


# ==========================================
# 2. 连接 Red Pitaya
# ==========================================

print("Connecting to Red Pitaya...")

p = Pyrpl(config=CONFIG)
rp = p.rp
scope = rp.scope

print("Connected successfully!")


# ==========================================
# 3. 配置示波器
# ==========================================

scope.input1 = INPUT_CHANNEL

# 最高采样率：125 MS/s
scope.decimation = 1

# 不进行高分辨率平均
scope.average = False

# 只采集一条曲线
scope.trace_average = 1

# 下降沿触发
scope.trigger_source = "ch1_negative_edge"

scope.threshold = TRIGGER_THRESHOLD
scope.hysteresis = TRIGGER_HYSTERESIS

# 触发时刻位于采集时间窗中央
scope.trigger_delay = 0

print("\nScope configuration:")
print("Input:", scope.input1)
print("Decimation:", scope.decimation)
print("Sampling rate:", 125e6 / scope.decimation / 1e6, "MS/s")
print("Duration:", scope.duration * 1e6, "us")
print("Trigger:", scope.trigger_source)
print("Threshold:", scope.threshold, "V")


# ==========================================
# 4. 采集数据
# ==========================================

print("\nAcquiring waveform...")

ch1, ch2 = scope.single(timeout=5)

ch1 = np.asarray(ch1)
t = np.asarray(scope.times)

# 转换为微秒
t_us = t * 1e6

print("Acquisition complete!")
print("Number of points:", len(ch1))
print("Minimum voltage:", np.min(ch1), "V")
print("Maximum voltage:", np.max(ch1), "V")


# ==========================================
# 5. 绘图
# ==========================================

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(12, 8),
    constrained_layout=True
)

# ---- 图1：完整采集波形 ----

ax1.plot(t_us, ch1, linewidth=0.8)

ax1.axvline(
    0,
    linestyle="--",
    alpha=0.7,
    label="Trigger"
)

ax1.set_title("Full waveform")
ax1.set_xlabel("Time (us)")
ax1.set_ylabel("Voltage (V)")
ax1.grid(True, alpha=0.3)
ax1.legend()


# ---- 图2：单个脉冲放大 ----

ax2.plot(t_us, ch1, linewidth=1.2)

ax2.axvline(
    0,
    linestyle="--",
    alpha=0.7,
    label="Trigger"
)

ax2.axhline(
    TRIGGER_THRESHOLD,
    linestyle=":",
    alpha=0.7,
    label="Trigger threshold"
)

ax2.set_xlim(
    -ZOOM_HALF_WIDTH_US,
    ZOOM_HALF_WIDTH_US
)

ax2.set_title("Zoomed pulse")
ax2.set_xlabel("Time (us)")
ax2.set_ylabel("Voltage (V)")
ax2.grid(True, alpha=0.3)
ax2.legend()


# ==========================================
# 6. 保存数据和图片
# ==========================================

if SAVE_FIGURE:
    plt.savefig(
        "scope_pulse_zoom.png",
        dpi=200
    )
    print("\nSaved: scope_pulse_zoom.png")

if SAVE_DATA:
    np.savetxt(
        "scope_data.csv",
        np.column_stack((t_us, ch1)),
        delimiter=",",
        header="time_us,voltage_V",
        comments=""
    )
    print("Saved: scope_data.csv")


# 显示图像
plt.show()
