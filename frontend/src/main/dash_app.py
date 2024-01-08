import json
import logging

import dash
import dash_bootstrap_components as dbc
import requests
from dash import Input, Output, dcc, html

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Average Calculator"), width={"size": 6, "offset": 3})),
        dbc.Row(
            dbc.Col(
                dcc.Input(
                    id="number-input",
                    type="text",
                    placeholder="Enter numbers separated by commas",
                ),
                width=6,
            )
        ),
        dbc.Row(
            dbc.Col(
                html.Button("Calculate Average", id="calculate-button"),
                width={"size": 2, "offset": 5},
            )
        ),
        dbc.Row(dbc.Col(html.Div(id="output-average"), width={"size": 6, "offset": 3})),
    ],
    fluid=True,
)


# Callback to update the average
@app.callback(
    Output("output-average", "children"),
    Input("calculate-button", "n_clicks"),
    [Input("number-input", "value")],
)
def update_output(n_clicks, input_value):
    if n_clicks is None or input_value is None:
        return "Enter numbers to calculate the average"

    try:
        # Convert input string to list of numbers
        numbers_list = [float(num.strip()) for num in input_value.split(",")]
        # Prepare data for the API request
        payload = json.dumps({"n": numbers_list})
        headers = {"Content-Type": "application/json"}
        # Send request to FastAPI endpoint
        logging.info(f"Fast-API request: {payload},{headers}")
        # response = requests.post(
        #     "http://fastapi:8000/model_predict", data=payload, headers=headers
        # )
        response = requests.post("http://fastapi.dummyfastapi:8000/model_predict", data=payload, headers=headers)
        logging.info(f"Fast-API response: {response}")
        average = response.json()["average"]
        return f"Average: {average}"
    except ValueError:
        return "Invalid input. Please enter numbers separated by commas."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to server: {e}"


# Run the app
if __name__ == "__main__":
    logging.info("Starting dash frontend...")
    app.run_server(debug=True, host="0.0.0.0", port=8050)
