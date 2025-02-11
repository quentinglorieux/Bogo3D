import numpy as np
import plotly.graph_objects as go
import shinyswatch
from shiny import App, render, ui

# Physical parameters for fluids of light
lambda0 = 800e-9  # Central wavelength (m)
k0 = 2 * np.pi / lambda0  # Central wavevector (1/m)
n2 = 1e-14  # Nonlinear index (m^2/W)
I = 1e4  # Intensity of the beam (W/m^2)

# Default nonlinear index modification
Delta_n_default = 1e-5

# Wavevector range (in m^-1; note: 100 mm^-1 = 100e3 m^-1)
kx_range = np.linspace(-80e3, 80e3, 100)
ky_range = np.linspace(-80e3, 80e3, 100)
KX, KY = np.meshgrid(kx_range, ky_range)

# Define UI
app_ui = ui.page_fluid(
    ui.h1("Bogoliubov Dispersion with Sliders"),
    
    ui.input_slider(
        "delta_n", "Nonlinear Index Modification (Δn)",
        min=1e-6, max=1e-4, value=Delta_n_default, step=1e-6
    ),
    ui.input_slider(
        "kx_fixed", "Fixed kx Value (mm⁻¹)",
        min=-80, max=80, value=10, step=5
    ),
    
    # Use output_ui for arbitrary UI output (HTML in our case)
    ui.output_ui("dispersion_plot")
)

# Server logic
def server(input, output, session):

    @output
    @render.ui  # Use render.ui since we are returning a UI element (HTML)
    def dispersion_plot():
        # Read inputs
        Delta_n = input.delta_n()
        kx_fixed = input.kx_fixed() * 1e3  # Convert from mm⁻¹ to m⁻¹

        # Compute dispersion over the grid
        K = np.sqrt(KX**2 + KY**2)
        OmegaB = np.sqrt((K**2 / (2 * k0))**2 + K**2 * Delta_n)

        # Create a “cut” along fixed kx: vary ky while keeping kx fixed
        ky_cut = np.linspace(-80e3, 80e3, 100)
        K_cut = np.sqrt(kx_fixed**2 + ky_cut**2)
        OmegaB_cut = np.sqrt((K_cut**2 / (2 * k0))**2 + K_cut**2 * Delta_n)

        k_xi = round(k0 * np.sqrt(Delta_n) * 1e-3)

        # Create the Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Surface(
            x=KX / 1e3,  # Convert kx from m^-1 to mm^-1 for plotting
            y=KY / 1e3,  # Convert ky from m^-1 to mm^-1
            z=OmegaB,
            colorscale='Viridis',
            opacity=0.8
        ))
        fig.add_trace(go.Scatter3d(
            x=[kx_fixed / 1e3] * len(ky_cut),  # Fixed kx (mm^-1)
            y=ky_cut / 1e3,                    # ky variable (mm^-1)
            z=OmegaB_cut,
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Cut'
        ))
        fig.update_layout(
            title=f"Bogoliubov Dispersion - k_xi={k_xi} mm⁻¹",
            scene=dict(
                xaxis_title='Wavevector k_x (mm⁻¹)',
                yaxis_title='Wavevector k_y (mm⁻¹)',
                zaxis_title='Bogoliubov Frequency Ω_B(k) (1/m)'
            )
        )

        # Convert the Plotly figure to HTML. The include_plotlyjs="cdn" argument
        # ensures that the Plotly JS library is loaded from the CDN.
        html_fig = fig.to_html(include_plotlyjs="cdn")
        
        # Return the HTML wrapped in a Shiny UI element.
        return ui.HTML(html_fig)

# Create the Shiny app
app = App(app_ui, server)