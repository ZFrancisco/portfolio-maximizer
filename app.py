from dash import Dash, html, dcc, callback, Output, Input, State, MATCH
from dash import Input, Output, State, ALL, ctx, callback
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd

df = pd.read_csv('./all_stocks_5yr.csv')

app = Dash()

# Requires Dash 2.17.0 or later
app.layout = [
    html.H1(children='Portfolio Optimizer', style={'textAlign':'center'}),
    html.Hr(),
    html.Div([
        dcc.Dropdown(df['Name'].unique(), 'AAL', id='ticker_drop'),
        dcc.Graph(id='graph-content'),
    ]),
    html.Div([
        html.Label("How many views?", style={'marginRight': '10px'}),
        dcc.Input(id='num_views', type='number', debounce=True, min=2, step=1),
    ], style={'marginBottom': '20px'}, id="to_change"),
    html.Div(id='json-test', style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap'}),
]

@callback(
    
    Output('to_change', 'children'),
    Input('num_views', 'value'),
)

def generate_inputs(wanted_num):
    inputs = []
    for i in range(wanted_num):
        inputs.append(html.Div([
            html.Label(f"View {i + 1}:"),
            dcc.RadioItems(
                ['Relative', 'Absolute'],
                id={'type': 'view-type', 'index': i},
                value='Relative',
                style={'marginRight': '10px'}
            ),
            dcc.Dropdown(df['Name'].unique(), 'AAL', id={'type': 'ticker', 'index': i}, style={'marginRight': '10px'}),
            dcc.Input(id={'type': 'view-input', 'index': i}, type='number', placeholder=f"Enter view {i + 1}", min=0, step=1),
        ], style={'marginRight': '20px', 'display': 'flex', 'alignItems': 'center'}))
    
    return html.Div([
        *inputs,
        html.Button('Submit', id='submit-val', n_clicks=0)
    ], style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap'})


@callback(
    Output('json-test', 'children'),  
    Input('submit-val', 'n_clicks'),
    State({'type': 'view-type', 'index': ALL}, 'value'),
    State({'type': 'ticker', 'index': ALL}, 'value'),
    State({'type': 'view-input', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def store_views(n_clicks, types, tickers, values):
    views = []
    for t, k, v in zip(types, tickers, values):
        if k and v is not None:
            views.append({'type': t, 'ticker': k, 'value': v})
    return [html.Pre(str(views))]

@callback(
    Output('graph-content', 'figure'),
    Input('ticker_drop', 'value')
)

def update_graph(ticker):
    cleaned_df = df[df['Name'] == ticker]
    fig = px.line(cleaned_df, x='date', y='close', title='Stock Prices Over Time for {}'.format(ticker))
    return fig




if __name__ == '__main__':
    app.run(debug=True)
