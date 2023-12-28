import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import requests
import asyncio
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Average Calculator without FastAPI"), width={'size': 6, 'offset': 3})
    ),
    dbc.Row(
        dbc.Col(dcc.Input(id='number-input', type='text', placeholder='Enter numbers separated by commas'), width=6)
    ),
    dbc.Row(
        dbc.Col(html.Button('Calculate Average', id='calculate-button'), width={'size': 2, 'offset': 5})
    ),
    dbc.Row(
        dbc.Col(html.Div(id='output-average'), width={'size': 6, 'offset': 3})
    )
], fluid=True)


# Callback to update the average
@app.callback(
    Output('output-average', 'children'),
    Input('calculate-button', 'n_clicks'),
    [Input('number-input', 'value')],
)
def update_output(n_clicks, input_value):
    if n_clicks is None or input_value is None:
        return 'Enter numbers to calculate the average'

    try:
        # Convert input string to list of numbers
        numbers_list = [float(num.strip()) for num in input_value.split(',')]
        # Prepare data for the API request
        average = asyncio.run(model_predict(numbers_list))
        return str(average)
    except ValueError:
        return 'Invalid input. Please enter numbers separated by commas.'
    except requests.exceptions.RequestException as e:
        return f'Error connecting to server: {e}'

async def model_predict(numbers):
    return {"average": np.average(numbers)}

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
