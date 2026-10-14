"""Chat da terminale con l'agente.

Uso:
    python -m app.cli "Dov'è il mio ordine 1001?"    # una domanda sola
    python -m app.cli                                # chat (scrivi "esci" per uscire)
"""

import sys

from app.agent import ask, build_agent
from app.config import get_settings
from app.llm import MissingApiKeyError, build_llm


def _answer(agent, question: str) -> None:
    try:
        reply = ask(agent, question)
    except Exception as exc:  # errori del provider (quota, rete, chiave): messaggio breve, niente traceback
        print(f"ERRORE: {type(exc).__name__}: {str(exc)[:300]}")
        return
    if reply.tools_used:
        print(f"  [tool usati: {', '.join(reply.tools_used)}]")
    print(f"Agente> {reply.text}")


def main() -> int:
    try:
        llm = build_llm(get_settings())
    except MissingApiKeyError as exc:
        print(f"ERRORE: {exc}")
        return 1
    agent = build_agent(llm)

    if len(sys.argv) > 1:
        _answer(agent, " ".join(sys.argv[1:]))
        return 0

    print('Assistente clienti. Scrivi la domanda ("esci" per uscire).')
    while True:
        try:
            question = input("Tu> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"esci", "exit", "quit"}:
            break
        if question:
            _answer(agent, question)
    return 0


if __name__ == "__main__":
    sys.exit(main())