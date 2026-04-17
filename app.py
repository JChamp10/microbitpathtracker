import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
import os

# ---- File picker ----
Tk().withdraw()
file_path = filedialog.askopenfilename(title="Select your micro:bit CSV file")

if not file_path:
    print("No file selected.")
    exit()

# ---- Load CSV ----
data = pd.read_csv(file_path)
print("Columns found:", list(data.columns))

# ---- Auto-detect columns ----
def find_column(name_options):
    for col in data.columns:
        for opt in name_options:
            if opt in col.lower():
                return col
    return None

x_col = find_column(["x"])
y_col = find_column(["y"])
z_col = find_column(["z"])

if not x_col or not y_col or not z_col:
    raise Exception("Couldn't find x, y, z columns.")

ax = data[x_col].values
ay = data[y_col].values
az = data[z_col].values

# ---- Convert mg → m/s^2 ----
g = 9.81
ax = ax * g / 1000
ay = ay * g / 1000
az = az * g / 1000

# ---- Smooth ----
def smooth(data, window=5):
    return np.convolve(data, np.ones(window)/window, mode='same')

ax = smooth(ax)
ay = smooth(ay)
az = smooth(az)

# ---- Remove gravity ----
az = az - np.mean(az)

# ---- Integrate ----
dt = 1.0

vx, vy, vz = [0], [0], [0]
px, py, pz = [0], [0], [0]

for i in range(1, len(ax)):
    vx_new = vx[-1] + ax[i] * dt
    vy_new = vy[-1] + ay[i] * dt
    vz_new = vz[-1] + az[i] * dt

    # Drift reduction
    if abs(ax[i]) < 0.1:
        vx_new *= 0.5
    if abs(ay[i]) < 0.1:
        vy_new *= 0.5
    if abs(az[i]) < 0.1:
        vz_new *= 0.5

    vx.append(vx_new)
    vy.append(vy_new)
    vz.append(vz_new)

    px.append(px[-1] + vx_new * dt)
    py.append(py[-1] + vy_new * dt)
    pz.append(pz[-1] + vz_new * dt)

px = np.array(px)
py = np.array(py)
pz = np.array(pz)

# ---- Save image ----
output_path = os.path.join(os.path.dirname(file_path), "path_output.png")

plt.figure()
plt.plot(px, py)
plt.title("Estimated Path")
plt.xlabel("X (m)")
plt.ylabel("Y (m)")
plt.axis("equal")
plt.grid()

plt.savefig(output_path)
plt.show()

print(f"Saved image to: {output_path}")
