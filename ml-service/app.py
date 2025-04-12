from fastapi import FastAPI     # type: ignore
from pydantic import BaseModel     # type: ignore
import joblib   # type: ignore
import pandas as pd     # type: ignore

app = FastAPI()

model = joblib.load("model/crypto_direction_model.pkl")

class InputData(BaseModel):
    price: float
    quantity: float
    is_buy: float

@app.post("/predict")
def predict(data: InputData):
    """
    Endpoint POST che riceve i dati di una transazione e restituisce
    una predizione sulla direzione del prezzo (es. salita o discesa).

    Parametri JSON in ingresso:
    - price (float): Prezzo dell'operazione
    - quantity (float): Quantità dell'operazione
    - is_buy (float): 1.0 se acquisto, 0.0 se vendita

    Ritorna:
    - dict: Un dizionario contenente la predizione, ad esempio {"prediction": 1}
    """
    features = pd.DataFrame([[data.price, data.quantity, data.is_buy]], columns=["price", "quantity", "is_buy"])
    prediction = model.predict(features)[0]
    return {"prediction": int(prediction)}
