import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# ----------------------------
# Global physical parameters
lambda0 = 780e-9            # Central wavelength (m)
k0 = 2 * np.pi / lambda0    # Central wavevector (1/m)

# ----------------------------
# Data for omega page (temporal/frequency dimension)
kxmin = -70e3
kxmax = 70e3
domega_min = -150   # in MHz
domega_max = 150    # in MHz

kx_range = np.linspace(kxmin, kxmax, 100)
domega_range = np.linspace(domega_min, domega_max, 100)  # Frequency shift in MHz
KX, DOMEGA = np.meshgrid(kx_range, domega_range)

# ----------------------------
# Data for ky page (spatial 2D: kx and ky)
kymin = -70e3
kymax = 70e3
kx_range_ky = np.linspace(kxmin, kxmax, 100)
ky_range = np.linspace(kymin, kymax, 100)
KX_ky, KY = np.meshgrid(kx_range_ky, ky_range)

# ----------------------------
# Create the Dash app (with multi-page support)
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the underlying Flask server

# ----------------------------
# Define the index (home) page layout
index_page = html.Div([
    html.H1("Multi-Page Dashboard"),
    html.Hr(),
    html.Div([
        dcc.Link("Bogoliubov Dispersion with Temporal Dimension", href="/omega"),
    ], style={'padding': '10px'}),
    html.Br(),
    html.Div([
        dcc.Link("Bogoliubov Dispersion off k=0", href="/ky"),
    ], style={'padding': '10px'}),
])

# ----------------------------
# Define the omega page layout with the extra cut-mode switch and sliders
omega_layout = html.Div([
    dcc.Link("← Back to Home", href="/"),
    html.H1("Bogoliubov Dispersion with Temporal Dimension"),
    
    # Nonlinear index slider
    html.Div([
        html.Label("Nonlinear Index (Δn) [×10⁻⁵] (log scale)"),
        dcc.Slider(
            id='delta-n-slider-omega',
            min=0.1,
            max=10,
            step=0.1,
            value=1,
            marks={0.1: '0.1', 1: '1', 10: '10'},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),
    
    # GVD slider
    html.Div([
        html.Label("Group Velocity Dispersion (GVD) D₀ [×10⁻15 s²/m]"),
        dcc.Slider(
            id='gvd-slider-omega',
            min=1,
            max=100,
            step=1,
            value=10,  # Default value: 10 corresponds to 10e-15 s²/m
            marks={1: '1', 10: '10', 50: '50', 100: '100'},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),
    
    # Switch to select the cut mode
    html.Div([
        html.Label("Cut Direction:"),
        dcc.RadioItems(
            id='cut-mode-radio',
            options=[
                {'label': 'Fixed kx', 'value': 'fix_kx'},
                {'label': 'Fixed Δω', 'value': 'fix_domega'}
            ],
            value='fix_kx',
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], style={'width': '10%', 'padding': '20px', 'display': 'inline-block'}),
    
    # Div containing the fixed kx slider (shown only when mode is "fix_kx")
    html.Div(id='kx-slider-div', children=[
        html.Label("Fixed kx Value (in mm⁻¹)"),
        dcc.Slider(
            id='kx-slider-omega',
            min=0,
            max=30,
            step=1,
            value=10,
            marks={1: '1', 10: '10', 30: '30'},
            tooltip={"placement": "bottom", "always_visible": True},
        )
    ], style={'width': '25%', 'display': 'inline-block', 'padding': '20px'}),
    
    # Div containing the fixed Δω slider (shown only when mode is "fix_domega")
    html.Div(id='domega-slider-div', children=[
        html.Label("Fixed Δω Value (in MHz)"),
        dcc.Slider(
            id='domega-slider-omega',
            min=0,
            max=100,
            step=1,
            value=0,
            marks={ 0: '0', 100: '100'},
            tooltip={"placement": "bottom", "always_visible": True},
        )
    ], style={'width': '10%', 'display': 'inline-block', 'padding': '20px'}),
    
    dcc.Graph(id='dispersion-plot-omega', style={'height': '700px'})
])

# ----------------------------
# Define the ky page layout (unchanged)
ky_layout = html.Div([
    dcc.Link("← Back to Home", href="/"),
    html.H1("Bogoliubov Dispersion off k=0"),
    
    html.Div([
        html.Label("Nonlinear Index (Δn) [×10⁻⁵] (log scale)"),
        dcc.Slider(
            id='delta-n-slider-ky',
            min=0.1,
            max=10,
            step=0.1,
            value=1,
            marks={0.1: '0.1', 1: '1', 10: '10'},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '38%', 'display': 'inline-block', 'padding': '20px'}),
    
    html.Div([
        html.Label("Fixed kx Value (in mm⁻¹)"),
        dcc.Slider(
            id='kx-slider-ky',
            min=0,
            max=30,
            step=1,
            value=10,
            marks={1: '1', 10: '10', 30: '30'},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ], style={'width': '38%', 'display': 'inline-block', 'padding': '20px'}),
    
    dcc.Graph(id='dispersion-plot-ky', style={'height': '700px'})
])

# ----------------------------
# Define the main app layout with a Location to handle multi-page routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# ----------------------------
# Callback to route between pages
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/omega':
        return omega_layout
    elif pathname == '/ky':
        return ky_layout
    else:
        return index_page

# ----------------------------
# Callback to toggle the visibility of the kx and Δω slider divs
@app.callback(
    [Output('kx-slider-div', 'style'),
     Output('domega-slider-div', 'style')],
    [Input('cut-mode-radio', 'value')]
)
def update_slider_visibility(cut_mode):
    if cut_mode == 'fix_kx':
        return {'width': '25%', 'display': 'inline-block', 'padding': '20px'}, {'display': 'none'}
    else:
        return {'display': 'none'}, {'width': '25%', 'display': 'inline-block', 'padding': '20px'}

# ----------------------------
# Callback for the omega page that updates the dispersion plot
@app.callback(
    Output('dispersion-plot-omega', 'figure'),
    [Input('delta-n-slider-omega', 'value'),
     Input('gvd-slider-omega', 'value'),
     Input('cut-mode-radio', 'value'),
     Input('kx-slider-omega', 'value'),
     Input('domega-slider-omega', 'value')]
)
def update_omega_plot(delta_n_slider_value, gvd_slider_value, cut_mode,
                      kx_slider_value, domega_slider_value):
    # Convert slider values to physical parameters
    Delta_n = delta_n_slider_value * 1e-5
    D0 = gvd_slider_value * 1e-15

    # Compute the dispersion surface (always over the grid defined by KX and DOMEGA)
    K = np.sqrt(KX**2)
    OmegaB = np.sqrt(
        (K**2/(2*k0) + D0*(DOMEGA*1e6)**2)**2 +
        K**2 * Delta_n +
        (DOMEGA*1e6)**2 * D0*k0*Delta_n
    )
    
    # Depending on the selected cut mode, compute the cut data differently.
    if cut_mode == 'fix_kx':
        # Fixed kx: the cut is taken along Δω for a constant kx value.
        kx_fixed = kx_slider_value * 1e3  # Convert mm⁻¹ to m
        domega_cut = np.linspace(domega_min, domega_max, 100)
        K_cut = kx_fixed  # constant (a scalar)
        OmegaB_cut = np.sqrt(
            (K_cut**2/(2*k0) + D0*(domega_cut*1e6)**2)**2 +
            K_cut**2 * Delta_n +
            (domega_cut*1e6)**2 * D0*k0*Delta_n
        )
        OmegaB_free = (K_cut**2)/(2*k0) + D0*(domega_cut*1e6)**2
        # For the 3D cut, x is constant and y is the Δω axis.
        cut_3d_x = [kx_fixed/1e3] * len(domega_cut)
        cut_3d_y = domega_cut
        # For the 2D subplot, x is Δω.
        cut_2d_x = domega_cut
        xaxis_title = "Frequency Shift Δω (MHz)"
    else:
        # Fixed Δω: the cut is taken along kx for a constant Δω value.
        domega_fixed = domega_slider_value  # already in MHz
        kx_cut = np.linspace(kxmin, kxmax, 100)
        K_cut = np.abs(kx_cut)  # use absolute value (as in the dispersion formula)
        OmegaB_cut = np.sqrt(
            (K_cut**2/(2*k0) + D0*(domega_fixed*1e6)**2)**2 +
            K_cut**2 * Delta_n +
            (domega_fixed*1e6)**2 * D0*k0*Delta_n
        )
        OmegaB_free = (K_cut**2)/(2*k0) + D0*(domega_fixed*1e6)**2
        # For the 3D cut, x is kx and y is constant.
        cut_3d_x = kx_cut/1e3
        cut_3d_y = [domega_fixed] * len(kx_cut)
        # For the 2D subplot, x is kx.
        cut_2d_x = kx_cut/1e3
        xaxis_title = "Wavevector kx (mm⁻¹)"
    
    k_xi = round(k0 * np.sqrt(Delta_n) * 1e-3)
    
    # Create the figure with two subplots: one 3D and one 2D.
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'xy'}]],
        column_widths=[0.7, 0.3],
        horizontal_spacing=0.05
    )
    
    # Add the dispersion surface (3D)
    fig.add_trace(go.Surface(
        x=KX/1e3,
        y=DOMEGA,
        z=OmegaB,
        colorscale='Viridis',
        opacity=0.8,
        showscale=False,
        name='Dispersion Surface'
    ), row=1, col=1)
    
    # Add the cut trace on the 3D subplot
    fig.add_trace(go.Scatter3d(
        x=cut_3d_x,
        y=cut_3d_y,
        z=OmegaB_cut,
        mode='lines',
        line=dict(color='orange', dash='dash', width=6),
        name='Cut'
    ), row=1, col=1)
    
    # Add the interacting and free dispersion curves on the 2D subplot
    fig.add_trace(go.Scatter(
        x=cut_2d_x,
        y=OmegaB_cut,
        mode='lines',
        name='Interacting Dispersion',
        line=dict(color='red', dash='dash')
    ), row=1, col=2)
    
    fig.add_trace(go.Scatter(
        x=cut_2d_x,
        y=OmegaB_free,
        mode='lines',
        name='Free Dispersion',
        line=dict(color='blue')
    ), row=1, col=2)
    
    # Update layout and axes labels
    fig.update_layout(
        title=f"Bogoliubov Dispersion - k_xi = {k_xi} mm⁻¹",
        margin=dict(l=0, r=0, b=0, t=40),
        uirevision='constant'
    )
    
    # For the 3D scene, the axes remain the same regardless of cut mode.
    fig.update_layout(
        scene=dict(
            xaxis_title='Wavevector k_x (mm⁻¹)',
            yaxis_title='Frequency Shift Δω (MHz)',
            zaxis_title='Frequency Ω_B (1/m)'
        )
    )
    # Set the x-axis label of the 2D subplot based on the cut mode.
    fig.update_xaxes(title_text=xaxis_title, row=1, col=2)
    fig.update_yaxes(title_text="Frequency Ω (1/m)", row=1, col=2)
    
    return fig

# ----------------------------
# Callback for the ky page (unchanged)
@app.callback(
    Output('dispersion-plot-ky', 'figure'),
    [Input('delta-n-slider-ky', 'value'),
     Input('kx-slider-ky', 'value')]
)
def update_ky_plot(delta_n_slider_value, kx_fixed_slider_value):
    Delta_n = delta_n_slider_value * 1e-5
    kx_fixed = kx_fixed_slider_value * 1e3

    # Compute the dispersion surface on the (kx, ky) grid
    K = np.sqrt(KX_ky**2 + KY**2)
    OmegaB = np.sqrt((K**2/(2*k0))**2 + K**2 * Delta_n)
    
    # Compute the dispersion cut along a fixed kx value over ky
    ky_cut = np.linspace(kymin, kymax, 100)
    K_cut = np.sqrt(kx_fixed**2 + ky_cut**2)
    OmegaB_cut = np.sqrt((K_cut**2/(2*k0))**2 + K_cut**2 * Delta_n)
    OmegaB_free = (K_cut**2)/(2*k0)
    
    k_xi = round(k0 * np.sqrt(Delta_n) * 1e-3)
    
    # Create the figure with two subplots: 3D and 2D
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scene'}, {'type': 'xy'}]],
        column_widths=[0.7, 0.3],
        horizontal_spacing=0.05
    )
    
    fig.add_trace(go.Surface(
        x=KX_ky/1e3,
        y=KY/1e3,
        z=OmegaB,
        colorscale='Viridis',
        opacity=0.8,
        showscale=False,
        name='Dispersion Surface'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter3d(
        x=[kx_fixed/1e3]*len(ky_cut),
        y=ky_cut/1e3,
        z=OmegaB_cut,
        mode='lines',
        line=dict(color='orange', dash='dash', width=6),
        name='Cut'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=ky_cut/1e3,
        y=OmegaB_cut,
        mode='lines',
        name='Interacting Dispersion',
        line=dict(color='red', dash='dash')
    ), row=1, col=2)
    
    fig.add_trace(go.Scatter(
        x=ky_cut/1e3,
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
            yaxis_title='Wavevector k_y (mm⁻¹)',
            zaxis_title='Frequency Ω_B (1/m)'
        )
    )
    fig.update_xaxes(title_text='Wavevector k_y (mm⁻¹)', row=1, col=2)
    fig.update_yaxes(title_text='Frequency Ω (1/m)', row=1, col=2)
    
    return fig

# ----------------------------
# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)