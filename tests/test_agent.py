"""Test dell'agente con un LLM finto"""

from typing import Any, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool

from app.agent import FALLBACK_REPLY, ask, build_agent, content_to_text


class ScriptedChatModel(BaseChatModel):
    """LLM finto: restituisce le risposte preparate, una per chiamata (l'ultima si ripete)."""

    responses: List[AIMessage]
    calls: int = 0
    seen: List[List[BaseMessage]] = []

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedChatModel":
        return self  # al finto non serve sapere quali tool esistono

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.seen.append(list(messages))
        template = self.responses[min(self.calls, len(self.responses) - 1)]
        # Copia nuova a ogni chiamata e senza id: LangGraph unisce i messaggi con lo stesso id,
        # quindi restituire sempre lo stesso oggetto equivale a "aggiornare" il messaggio, non ad aggiungerne uno.
        message = template.model_copy(update={"id": None})
        self.calls += 1
        return ChatResult(generations=[ChatGeneration(message=message)])


@tool
def get_order_status(order_id: str) -> str:
    """Tool finto con lo stesso nome di quello vero."""
    return f"Ordine {order_id}\nStato: spedito"


def _tool_call(order_id: str) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[{"name": "get_order_status", "args": {"order_id": order_id}, "id": "call_1"}],
    )


def test_agent_uses_tool_then_answers():
    llm = ScriptedChatModel(
        responses=[_tool_call("1001"), AIMessage(content="Il tuo ordine 1001 è stato spedito.")]
    )
    agent = build_agent(llm, tools=[get_order_status])

    reply = ask(agent, "Dov'è il mio ordine 1001?")

    assert reply.text == "Il tuo ordine 1001 è stato spedito."
    assert reply.tools_used == ["get_order_status({'order_id': '1001'})"]
    # Alla seconda chiamata il modello ha ricevuto il risultato del tool.
    second_call = llm.seen[1]
    tool_messages = [m for m in second_call if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert "spedito" in tool_messages[0].content


def test_agent_answers_without_tool():
    llm = ScriptedChatModel(responses=[AIMessage(content="Mi dai il numero d'ordine?")])
    agent = build_agent(llm, tools=[get_order_status])

    reply = ask(agent, "Dov'è il mio pacco?")

    assert reply.text == "Mi dai il numero d'ordine?"
    assert reply.tools_used == []
    assert llm.calls == 1


def test_agent_stops_when_model_loops_forever():
    # Il modello chiede il tool all'infinito: il limite di passi deve fermarlo.
    llm = ScriptedChatModel(responses=[_tool_call("1001")])
    agent = build_agent(llm, tools=[get_order_status])

    reply = ask(agent, "Dov'è il mio ordine 1001?")

    assert reply.text == FALLBACK_REPLY


def test_content_to_text_handles_string_and_blocks():
    assert content_to_text("  ciao  ") == "ciao"
    assert content_to_text([{"type": "text", "text": "ci"}, {"type": "text", "text": "ao"}]) == "ciao"
    assert content_to_text([{"type": "thinking", "thinking": "..."}, "ciao"]) == "ciao"
    assert content_to_text(None) == ""