"""Tool che l'agente può usare. Gli errori vengono restituiti come testo, non sollevati."""

from typing import Optional

import httpx
from langchain_core.tools import tool

from app.config import get_settings


def get_order_status_impl(order_id: str, *, client: Optional[httpx.Client] = None) -> str:
    """Logica del tool, separata dal decoratore così si può testare senza LLM."""
    order_id = order_id.strip()

    # L'argomento lo genera l'LLM: non è affidabile. Accettiamo solo numeri,
    # altrimenti un valore come "../admin" finirebbe dentro l'URL.
    if not order_id.isdigit():
        return "ERRORE: il numero d'ordine deve contenere solo cifre (esempio: 1001)."

    settings = get_settings()
    own_client = client is None
    if client is None:
        client = httpx.Client(
            base_url=settings.orders_api_url,
            timeout=settings.orders_api_timeout_seconds,
        )

    try:
        response = client.get(f"/orders/{order_id}")
    except httpx.TimeoutException:
        return "ERRORE: il sistema ordini non ha risposto in tempo. Riprova tra poco."
    except httpx.HTTPError:
        return "ERRORE: impossibile contattare il sistema ordini."
    finally:
        if own_client:
            client.close()

    if response.status_code == 404:
        return f"Nessun ordine trovato con numero {order_id}."
    if response.status_code != 200:
        return f"ERRORE: il sistema ordini ha risposto con codice {response.status_code}."

    data = response.json()
    # Restituiamo solo ciò che serve a rispondere: niente nome del cliente.
    lines = [f"Ordine {data['order_id']}", f"Stato: {data['status']}"]
    if data.get("carrier"):
        lines.append(f"Corriere: {data['carrier']}")
    if data.get("tracking_code"):
        lines.append(f"Codice di tracking: {data['tracking_code']}")
    if data.get("estimated_delivery"):
        lines.append(f"Consegna prevista: {data['estimated_delivery']}")
    return "\n".join(lines)


@tool
def get_order_status(order_id: str) -> str:
    """Restituisce lo stato di un ordine: spedizione, corriere, tracking e consegna prevista.

    Usalo quando il cliente chiede a che punto è un ordine o dove si trova il pacco.
    L'argomento order_id è il numero dell'ordine, solo cifre (esempio: "1001").
    """
    return get_order_status_impl(order_id)