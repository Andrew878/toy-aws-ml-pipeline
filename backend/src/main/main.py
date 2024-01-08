import logging

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()


class NumbersInput(BaseModel):
    n: list[int | float]


@app.post("/model_predict")
async def model_predict(numbers: NumbersInput):
    logging.info(f"Making prediction with: {numbers.n}")
    return {"average": np.average(numbers.n)}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI server!"}
