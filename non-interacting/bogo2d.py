import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Constants (in arbitrary units)
hbar = 1.0  # Reduced Planck's constant
m = 1.0     # Mass of the boson
g = 1.0     # Interaction strength
n = 1.0     # Density of the condensate

# Wavevector range for kx and ky
kx = np.linspace(-3, 3, 100)
ky = np.linspace(-3, 3, 100)
KX, KY = np.meshgrid(kx, ky)
K = np.sqrt(KX**2 + KY**2)

# Bogoliubov dispersion relation
omega = np.sqrt((hbar**2 * K**2) / (2 * m) * ((hbar**2 * K**2) / (2 * m) + 2 * g * n))

# Select a fixed kx value for the cut
kx_fixed = 0.2  # Change this value for different cuts
ky_cut = np.linspace(-3, 3, 100)
K_cut = np.sqrt(kx_fixed**2 + ky_cut**2)
omega_cut = np.sqrt((hbar**2 * K_cut**2) / (2 * m) * ((hbar**2 * K_cut**2) / (2 * m) + 2 * g * n))

# Plot the 3D dispersion
fig = plt.figure(figsize=(12, 5))
ax = fig.add_subplot(121, projection='3d')
surf = ax.plot_surface(KX, KY, omega, cmap='viridis', alpha=0.8)
ax.plot(ky_cut, [kx_fixed] * len(ky_cut), omega_cut, 'r--', linewidth=2, label='Cut at $k_x$={}'.format(kx_fixed))
ax.set_xlabel(r'Wavevector $k_x$')
ax.set_ylabel(r'Wavevector $k_y$')
ax.set_zlabel(r'Energy $\omega(k)$')
ax.set_title("Bogoliubov Dispersion Relation in 2D")
ax.legend()

# Plot the cut
ax2 = fig.add_subplot(122)
ax2.plot(ky_cut, omega_cut, 'b-', label=r'$\omega(k_x={}, k_y)$'.format(kx_fixed))
ax2.set_xlabel(r'Wavevector $k_y$')
ax2.set_ylabel(r'Energy $\omega(k)$')
ax2.set_title("Cut along fixed $k_x$={}".format(kx_fixed))
ax2.legend()
ax2.grid()

plt.show()