"""API REST finta degli ordini: simula il gestionale dell'azienda."""

from typing import Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Orders API (finta)")


class Order(BaseModel):
    order_id: str
    customer: str
    status: Literal["in_preparazione", "spedito", "consegnato", "annullato"]
    carrier: Optional[str] = None
    tracking_code: Optional[str] = None
    estimated_delivery: Optional[str] = None


ORDERS: Dict[str, Order] = {
    "1001": Order(
        order_id="1001",
        customer="Mario Rossi",
        status="spedito",
        carrier="BRT",
        tracking_code="BRT123456",
        estimated_delivery="2026-10-16",
    ),
    "1002": Order(order_id="1002", customer="Giulia Bianchi", status="in_preparazione"),
    "1003": Order(
        order_id="1003",
        customer="Luca Verdi",
        status="consegnato",
        carrier="GLS",
        tracking_code="GLS987654",
        estimated_delivery="2026-10-08",
    ),
}


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str) -> Order:
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Ordine {order_id} non trovato")
    return order