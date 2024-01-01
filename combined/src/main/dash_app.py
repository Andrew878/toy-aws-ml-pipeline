import asyncio
import logging
import os

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import psycopg2
import requests
from dash import Input, Output, dash_table, dcc, html
from dash.exceptions import PreventUpdate

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
# Debug: Print environment variables
print("Environment Variables:")
for key in os.environ:
    print(f"{key}: {os.environ[key]}")

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# Add a button for refreshing the data
refresh_button = dbc.Button(
    "Refresh Data", id="refresh-button", className="mb-3", n_clicks=0
)

# Add a placeholder for the data table
data_table = dash_table.DataTable(id="data-table")
# App layout
app.layout = dbc.Container(
    [
        dbc.Row(
            dbc.Col(
                html.H1("Average Calculator without FastAPI"),
                width={"size": 6, "offset": 3},
            )
        ),
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
        dbc.Row(
            dbc.Col(
                html.H2("Get history of inputs"),
                width={"size": 6, "offset": 3},
            )
        ),
        dbc.Row(dbc.Col(refresh_button)),
        dbc.Row(dbc.Col(data_table)),
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
        average = asyncio.run(model_predict(numbers_list))
        average_str = str(average)
        add_to_db(input_value, average_str)
        return average_str
    except ValueError:
        return "Invalid input. Please enter numbers separated by commas."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to server: {e}"


async def model_predict(numbers):
    return np.average(numbers)


def get_db_connection():
    logging.info("Connecting to DB")
    try:
        return psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
        )
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise


def add_to_db(input_value: str, average_str: str) -> None:
    logging.info(f"Inserting to DB: {input_value},{average_str}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (input, prediction) VALUES (%s, %s)",
        (input_value, average_str),
    )
    conn.commit()
    cursor.close()
    conn.close()


# Assuming you have a function to fetch the latest 20 entries from your database
def fetch_latest_entries():
    logging.info(f"Fetching last 20 entries from DB")
    connection = get_db_connection()
    query = "SELECT * FROM predictions ORDER BY created_at DESC LIMIT 20"
    return pd.read_sql_query(query, connection)


@app.callback(
    Output("data-table", "data"),
    [Input("refresh-button", "n_clicks")],
    prevent_initial_call=True,
)
def update_table(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return fetch_latest_entries().to_dict("records")


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)
