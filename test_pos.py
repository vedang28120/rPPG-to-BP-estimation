import sys
import numpy as np

# Mock implementation of pos_engine logic
target_points = 875
new_fps = 125
l = int(new_fps * 1.6) # 200
n_125 = target_points

h = np.zeros(n_125)
for i in range(n_125 - l + 1):
    S = np.ones(l) # Fake signal with DC 1
    h[i:i+l] += S - np.mean(S) # Since mean is 1, S - mean is 0

# Wait, if S is a sine wave
t = np.linspace(0, 7.0, n_125)
S_full = np.sin(2 * np.pi * 1.0 * t)

h2 = np.zeros(n_125)
for i in range(n_125 - l + 1):
    S = S_full[i:i+l]
    h2[i:i+l] += S - np.mean(S)

import matplotlib.pyplot as plt
plt.plot(h2)
plt.savefig('test_pos.png')

print("Max of h2:", np.max(h2))
print("Mean of middle:", np.mean(np.abs(h2[200:600])))
print("Mean of edges:", np.mean(np.abs(h2[0:50])))
