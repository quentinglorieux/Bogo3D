import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Physical parameters for fluids of light
lambda0 = 780e-9  # Central wavelength (m)
k0 = 2 * np.pi / lambda0  # Central wavevector (1/m)
n2 = 1e-14  # Nonlinear index (m^2/W)
I = 1e4  # Intensity of the beam (W/m^2)

# Calculate nonlinear index modification
# Delta_n = n2 * I  # Nonlinear index modification
Delta_n =1e-5;

# Wavevector range for kx and ky (0 to 100 mm^-1)
kx = np.linspace(-80e3, 80e3, 100)  # Convert to 1/m (100 mm^-1 = 100e3 m^-1)
ky = np.linspace(-80e3, 80e3, 100)
KX, KY = np.meshgrid(kx, ky)
K = np.sqrt(KX**2 + KY**2)

# Corrected NLSE Bogoliubov dispersion relation (Omega_B)
OmegaB = np.sqrt((K**2 / (2 * k0))**2 + K**2 * Delta_n)

# Select a fixed kx value for the cut
kx_fixed = 10e3  # Fix kx at 50 mm^-1 (convert to 1/m)
ky_cut = np.linspace(-80e3, 80e3, 100)
K_cut = np.sqrt(kx_fixed**2 + ky_cut**2)
OmegaB_cut = np.sqrt((K_cut**2 / (2 * k0))**2 + K_cut**2 * Delta_n)
OmegaB_free = (K_cut**2 / (2 * k0))

k_xi=round(k0*np.sqrt(Delta_n)*1e-3)

# Plot the 3D dispersion
fig = plt.figure(figsize=(12, 5))
ax = fig.add_subplot(121, projection='3d')
surf = ax.plot_surface(KX / 1e3, KY / 1e3, OmegaB, cmap='viridis', alpha=0.8)
ax.plot(ky_cut / 1e3, [kx_fixed / 1e3] * len(ky_cut), OmegaB_cut, 'r--', linewidth=2, label='Cut at $k_x$={:.1f}$ mm^{{-1}}$'.format(kx_fixed / 1e3))
ax.set_xlabel(r'Wavevector $k_x$ (mm$^{-1}$)')
ax.set_ylabel(r'Wavevector $k_y$ (mm$^{-1}$)')
ax.set_zlabel(r'Bogoliubov Frequency $\Omega_B(k)$ (1/m)')
ax.set_title(f"Bogoliubov Dispersion - $k_\\xi={k_xi:.0f}$ mm$^{{-1}}$")
ax.legend()
k_xi
# Plot the cut
ax2 = fig.add_subplot(122)
ax2.plot(ky_cut / 1e3, OmegaB_cut, 'b-', label=r'$\Omega_B(k_x={:.1f}, k_y)$'.format(kx_fixed / 1e3))
ax2.plot(ky_cut / 1e3, OmegaB_free, 'g--', label=r'Non-interacting parabola')
ax2.set_xlabel(r'Wavevector $k_y$ (mm$^{-1}$)')
ax2.set_ylabel(r'Bogoliubov Frequency $\Omega_B(k)$ (1/m)')
ax2.set_title("Cut along fixed $k_x$={:.1f} mm$^{{-1}}$".format(kx_fixed / 1e3))
ax2.set_ylim(0, max(OmegaB_cut))  # Ensure vertical axis starts from 0
ax2.legend()
ax2.grid()

plt.show()