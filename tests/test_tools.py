import httpx
import pytest

from app.tools import get_order_status_impl


def make_client(handler):
    """Client HTTP finto: la risposta la decide la funzione handler, nessun server vero."""
    return httpx.Client(base_url="http://test", transport=httpx.MockTransport(handler))


def test_order_found():
    def handler(request):
        assert request.url.path == "/orders/1001"
        return httpx.Response(
            200,
            json={
                "order_id": "1001",
                "customer": "Mario Rossi",
                "status": "spedito",
                "carrier": "BRT",
                "tracking_code": "BRT123456",
                "estimated_delivery": "2026-10-16",
            },
        )

    result = get_order_status_impl("1001", client=make_client(handler))
    assert "spedito" in result
    assert "BRT123456" in result
    assert "Mario Rossi" not in result  # il nome del cliente non deve uscire


def test_order_not_found():
    client = make_client(lambda request: httpx.Response(404, json={"detail": "non trovato"}))
    assert "Nessun ordine trovato" in get_order_status_impl("9999", client=client)


def test_timeout_is_returned_as_text():
    def handler(request):
        raise httpx.ReadTimeout("timeout", request=request)

    result = get_order_status_impl("1001", client=make_client(handler))
    assert "non ha risposto in tempo" in result


def test_server_error_is_returned_as_text():
    client = make_client(lambda request: httpx.Response(500))
    assert "codice 500" in get_order_status_impl("1001", client=client)


def test_invalid_id_never_calls_the_api():
    def handler(request):
        pytest.fail("L'API non deve essere chiamata con un id non valido")

    result = get_order_status_impl("../admin", client=make_client(handler))
    assert result.startswith("ERRORE")