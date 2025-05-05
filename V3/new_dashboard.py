import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

# Nom du fichier CSV
CSV_FILE = "data/data_sim.csv"

# Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = "Dashboard Patients - Mise à jour temps réel"

# Layout de l'application
app.layout = html.Div([
    html.H2("Données des patients - Mise à jour temps réel", style={'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='live-graph'),
        dcc.Graph(id='live-graph2'),

    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),

    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)
])

# Callback pour mettre à jour le graphique avec les données du CSV relu
@app.callback(
    Output('live-graph', 'figure'),
    Output('live-graph2', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n_intervals):
    try:
        # Lire les données à chaque rafraîchissement
        df = pd.read_csv(CSV_FILE)

        # Vérification des colonnes attendues
        if 'minute' not in df.columns or 'patients_arrives' not in df.columns:
            raise ValueError("Le fichier CSV doit contenir les colonnes 'minute' et 'patients_arrives'.")

        # Tri des données
        df = df.sort_values('minute').reset_index(drop=True)

        # Construire le graphique
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['minute'],
            y=df['patients_en_attente'] ,
            mode='lines',
            line_shape='spline',
            name='Patients en attente'
        ))

        fig.update_layout(
            xaxis_title='Minute',
            yaxis_title='Patients en attente',
            margin=dict(l=40, r=30, t=30, b=40),
            transition_duration=0
        )

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df['minute'],
            y=df['medecins_occupes'],
            mode='lines',
            line_shape='spline',
            name='Médecins occupés'
        ))

        fig2.update_layout(
            xaxis_title='Minute',
            yaxis_title='Médecins occupés',
            margin=dict(l=40, r=30, t=30, b=40),
            transition_duration=0
        )


        return fig, fig2

    except Exception as e:
        # En cas d’erreur de lecture ou de format
        return go.Figure().add_annotation(
            text=f"Erreur : {str(e)}",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )

# Lancer le serveur Dash
if __name__ == '__main__':
    app.run(debug=True)
