import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

# Lire le fichier CSV
df = pd.read_csv("patients.csv", parse_dates=["arrival_time", "departure_time"])

# Générer une timeline minute par minute
start_time = df['arrival_time'].min()
end_time = df['departure_time'].max()
timeline = pd.date_range(start=start_time, end=end_time, freq='1min')

# Calcul du nombre de patients pour chaque minute
patient_counts = []
for t in timeline:
    count = df[(df['arrival_time'] <= t) & (df['departure_time'] > t)].shape[0]
    patient_counts.append(count)

# Initialisation Dash
app = dash.Dash(__name__)
app.title = "Animation Occupation Hôpital"

# Layout
app.layout = html.Div([
    html.H2("Évolution du nombre de patients dans l'hôpital", style={'textAlign': 'center'}),
    dcc.Graph(id='live-graph'),
    dcc.Interval(
        id='interval-component',
        interval=200,  # 200ms entre chaque point → animation rapide
        n_intervals=0
    )
])

# Callback dynamique
@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    # Limiter à l’index maximum
    if n >= len(timeline):
        n = len(timeline) - 1

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timeline[:n+1],
        y=patient_counts[:n+1],
        mode='lines+markers',
        name='Patients'
    ))

    fig.update_layout(
        xaxis=dict(title='Temps'),
        yaxis=dict(title='Nombre de patients'),
        margin=dict(l=40, r=30, t=30, b=40),
        transition_duration=0
    )

    return fig

# Lancer le serveur
if __name__ == '__main__':
    app.run(debug=True)
