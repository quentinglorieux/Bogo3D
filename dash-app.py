import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# ---------------------------------------------------
# Physical parameters for fluids of light
lambda0 = 780e-9            # Central wavelength (m)
k0 = 2 * np.pi / lambda0    # Central wavevector (1/m)
#n2 = 1e-14                  # Nonlinear index (m^2/W)
#I = 1e4                     # Intensity of the beam (W/m^2)

# The default nonlinear index modification is given in units of 1e-5.
# The slider will range from 0.1 to 10 so that, for example, a slider value of 1 means Δn = 1e-5.
Delta_n_default_factor = 1.0

# Wavevector range (in 1/m; note: 100 mm⁻¹ = 100e3 m⁻¹)
kx_range = np.linspace(-80e3, 80e3, 100)
ky_range = np.linspace(-80e3, 80e3, 100)
KX, KY = np.meshgrid(kx_range, ky_range)
# ---------------------------------------------------

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Bogoliubov Dispersion off k=0"),
    
    html.Div([
        html.Label("Nonlinear Index (Δn) [×10⁻⁵] (log scale)"),
        dcc.Slider(
            id='delta-n-slider',
            min=0.1,
            max=10,
            step=0.1,
            value=Delta_n_default_factor,
            marks={0.1: '0.1', 1: '1', 10: '10'},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '38%', 'display': 'inline-block', 'padding': '20px'}),
    
    html.Div([
        html.Label("Fixed kx Value (in mm-1)"),
        dcc.Slider(
            id='kx-slider',
            min=0,
            max=80000,
            step=5000,
            value=10000,
            marks={i: f"{i//1000} mm⁻¹" for i in range(0, 81000, 20000)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '38%', 'display': 'inline-block', 'padding': '20px'}),
    
    # Do not pass uirevision here because it’s not supported in this Dash version.
    dcc.Graph(id='dispersion-plot', style={'height': '700px'})
])

@app.callback(
    Output('dispersion-plot', 'figure'),
    [Input('delta-n-slider', 'value'),
     Input('kx-slider', 'value')]
)
def update_plot(delta_n_slider_value, kx_fixed):
    # Convert the Δn slider value to SI units:
    # Actual Δn = (slider value) × 1e-5.
    Delta_n = delta_n_slider_value * 1e-5

    # --- Compute the full 3D dispersion surface ---
    K = np.sqrt(KX**2 + KY**2)
    OmegaB = np.sqrt((K**2 / (2 * k0))**2 + K**2 * Delta_n)
    
    # --- Define the cut along fixed kx ---
    ky_cut = np.linspace(-80e3, 80e3, 100)
    K_cut = np.sqrt(kx_fixed**2 + ky_cut**2)
    OmegaB_cut = np.sqrt((K_cut**2 / (2 * k0))**2 + K_cut**2 * Delta_n)
    # Free (parabolic) dispersion (no interaction)
    OmegaB_free = (K_cut**2) / (2 * k0)
    
    # --- Derived parameter (e.g. the scaled healing length) ---
    k_xi = round(k0 * np.sqrt(Delta_n) * 1e-3)
    
    # --- Create subplots with 2 rows ---
    # Row 1: 3D plot for the dispersion surface and cut.
    # Row 2: 1D plot for the dispersion along ky.
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'xy'}]],
        column_widths=[0.7, 0.3],
        horizontal_spacing=0.05
    )
    
    # --- Row 1: Add the 3D dispersion surface ---
    fig.add_trace(go.Surface(
        x=KX / 1e3,  # Convert kx to mm⁻¹
        y=KY / 1e3,  # Convert ky to mm⁻¹
        z=OmegaB,
        colorscale='Viridis',
        opacity=0.8,
        showscale=False,
        name='Dispersion Surface'
    ), row=1, col=1)
    
    # --- Row 1: Add the 3D cut trace (interacting dispersion at fixed kx) ---
    fig.add_trace(go.Scatter3d(
        x=[kx_fixed / 1e3] * len(ky_cut),  # Fixed kx (mm⁻¹)
        y=ky_cut / 1e3,                    # Varying ky (mm⁻¹)
        z=OmegaB_cut,
        mode='lines',
        line=dict(color='orange', dash='dash', width=6),
        name='Cut'
    ), row=1, col=1)
    
    # --- Row 2: 1D plot of the dispersion along ky ---
    # Plot the interacting dispersion (red dashed line)
    fig.add_trace(go.Scatter(
        x=ky_cut / 1e3,
        y=OmegaB_cut,
        mode='lines',
        name='Interacting Dispersion',
        line=dict(color='red', dash='dash')
    ), row=1, col=2)
    
    # Plot the free (parabolic) dispersion (blue solid line)
    fig.add_trace(go.Scatter(
        x=ky_cut / 1e3,
        y=OmegaB_free,
        mode='lines',
        name='Free Dispersion',
        line=dict(color='blue')
    ), row=1, col=2)
    
    # --- Update Layout ---
    # Set uirevision inside the figure layout to preserve 3D orientation on updates.
    fig.update_layout(
        title=f"Bogoliubov Dispersion - k_xi = {k_xi} mm⁻¹",
        margin=dict(l=0, r=0, b=0, t=40),
        uirevision='constant'
    )
    
    # 3D scene axis titles
    fig.update_layout(
        scene=dict(
            xaxis_title='Wavevector k_x (mm⁻¹)',
            yaxis_title='Wavevector k_y (mm⁻¹)',
            zaxis_title='Frequency Ω_B (1/m)'
        )
    )
    # 1D plot axis titles
    fig.update_xaxes(title_text='Wavevector k_y (mm⁻¹)', row=1, col=2)
    fig.update_yaxes(title_text='Frequency Ω (1/m)', row=1, col=2)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)