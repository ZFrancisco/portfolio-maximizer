from dash import Dash, html, dcc, callback, Output, Input, State, MATCH
from dash import Input, Output, State, ALL, ctx, callback
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
from logic import calculate

df = pd.read_csv('./all_stocks_5yr.csv')

app = Dash(suppress_callback_exceptions=True)

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
        dcc.Input(id='num_views', type='number', debounce=True, min=1, step=1),
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
            dcc.Dropdown(df['Name'].unique(), 'AAL', id={'type': 'ticker-a', 'index': i}, style={'marginRight': '10px'}),
            html.H2('IF YOU SELECTED ABSOLUTE PLEASE MAKE SECOND TICKER THE SAME AS FIRST'),
            dcc.Dropdown(df['Name'].unique(), 'AAL', id={'type': 'ticker-b', 'index': i}, style={'marginRight': '10px'}),
            dcc.Input(id={'type': 'view-input', 'index': i}, type='number', placeholder=f"Enter positive difference of stock 1 over 2 for view {i + 1}", min=0, step=1),
        ], style={'marginRight': '20px', 'display': 'flex', 'alignItems': 'center'}))
    
    return html.Div([
        *inputs,
        html.Button('Submit', id='submit-val', n_clicks=0)
    ], style={'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap'})


@callback(
    Output('json-test', 'children'),  
    Input('submit-val', 'n_clicks'),
    State({'type': 'view-type', 'index': ALL}, 'value'),
    State({'type': 'ticker-a', 'index': ALL}, 'value'),
    State({'type': 'ticker-b', 'index': ALL}, 'value'),
    State({'type': 'view-input', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def store_views(n_clicks, types, ticker_a, ticker_b, values):
    views = {'type': [], 'ticker_a': [], 'ticker_b': [], 'value': []}
    for i in range(len(types)):
        if types[i] and ticker_a[i] and ticker_b[i] and values[i]:
            views['type'].append(types[i])
            views['ticker_a'].append(ticker_a[i])
            views['ticker_b'].append(ticker_b[i])
            views['value'].append(values[i])
        else:
            print("Invalid input detected. Please check your inputs.")
    #use HOF here
    expected_returns = calculate(pd.DataFrame(views)) 
    return str(expected_returns)

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
