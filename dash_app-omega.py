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
D0 = 10e-15                 # Group velocity dispersion (s^2/m)

Delta_n_default_factor = 1.0
kxmin=-70e3
kxmax=70e3
domega_min=-150
domega_max=150

# Wavevector range (in 1/m; note: 100 mm⁻¹ = 100e3 m⁻¹)
kx_range = np.linspace(kxmin, kxmax, 100)
domega_range = np.linspace(domega_min, domega_max, 100)  # Frequency shift in MHz
KX, DOMEGA = np.meshgrid(kx_range, domega_range)
# ---------------------------------------------------

# Create the Dash app
app = dash.Dash(__name__)
server = app.server  # Expose the underlying Flask server

app.layout = html.Div([
    html.H1("Bogoliubov Dispersion with Temporal Dimension"),
    
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
        html.Label("Fixed kx Value (in mm⁻¹)"),
        dcc.Slider(
            id='kx-slider',
            min=0,
            max=30,
            step=1,
            value=10,
            marks={1: '1', 10: '10', 30: '30'},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '38%', 'display': 'inline-block', 'padding': '20px'}),
    
    dcc.Graph(id='dispersion-plot', style={'height': '700px'})
])

@app.callback(
    Output('dispersion-plot', 'figure'),
    [Input('delta-n-slider', 'value'),
     Input('kx-slider', 'value')]
)
def update_plot(delta_n_slider_value, kx_fixed_slider_value):
    Delta_n = delta_n_slider_value * 1e-5
    kx_fixed = kx_fixed_slider_value * 1e3

    K = np.sqrt(KX**2)
    OmegaB = np.sqrt(
        (K**2 / (2 * k0) + D0 * (DOMEGA * 1e6)**2)**2 + K**2 * Delta_n + (DOMEGA * 1e6)**2 * D0 * k0 * Delta_n
    )
    
    domega_cut = np.linspace(domega_min, domega_max, 100)
    K_cut = np.sqrt(kx_fixed**2)
    OmegaB_cut = np.sqrt(
        (K_cut**2 / (2 * k0) + D0 * (domega_cut * 1e6)**2)**2 + K_cut**2 * Delta_n + (domega_cut * 1e6)**2 * D0 * k0 * Delta_n
    )
    OmegaB_free = (K_cut**2) / (2 * k0) + D0 * (domega_cut * 1e6)**2
    
    k_xi = round(k0 * np.sqrt(Delta_n) * 1e-3)
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'xy'}]],
        column_widths=[0.7, 0.3],
        horizontal_spacing=0.05
    )
    
    fig.add_trace(go.Surface(
        x=KX / 1e3,
        y=DOMEGA,
        z=OmegaB,
        colorscale='Viridis',
        opacity=0.8,
        showscale=False,
        name='Dispersion Surface'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter3d(
        x=[kx_fixed / 1e3] * len(domega_cut),
        y=domega_cut,
        z=OmegaB_cut,
        mode='lines',
        line=dict(color='orange', dash='dash', width=6),
        name='Cut'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=domega_cut,
        y=OmegaB_cut,
        mode='lines',
        name='Interacting Dispersion',
        line=dict(color='red', dash='dash')
    ), row=1, col=2)
    
    fig.add_trace(go.Scatter(
        x=domega_cut,
        y=OmegaB_free,
        mode='lines',
        name='Free Dispersion',
        line=dict(color='blue')
    ), row=1, col=2)
    
    fig.update_layout(
        title=f"Bogoliubov Dispersion - k_xi = {k_xi} mm⁻¹",
        margin=dict(l=0, r=0, b=0, t=40),
        uirevision='constant'
    )
    fig.update_layout(
        scene=dict(
            xaxis_title='Wavevector k_x (mm⁻¹)',
            yaxis_title='Frequency Shift Δω (MHz)',
            zaxis_title='Frequency Ω_B (1/m)'
        )
    )
    fig.update_xaxes(title_text='Frequency Shift Δω (MHz)', row=1, col=2)
    fig.update_yaxes(title_text='Frequency Ω (1/m)', row=1, col=2)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
