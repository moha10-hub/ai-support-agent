# ai-support-agent

Un agente AI di assistenza clienti realizzato con LangGraph. Risponde alle domande sullo stato degli ordini interrogando una REST API tramite un tool invece di inventare le risposte.

**Stato: lavoro in corso.** Ciò che funziona oggi è elencato di seguito; la roadmap mostra i passi successivi.

## Cosa fa oggi

- **Ciclo dell'agente con LangGraph:** modello → tool → modello, finché il modello non ha una risposta
- **Chiamata ai tool:** `get_order_status` interroga una REST API Orders fittizia (FastAPI)
- **LLM gratuito di default:** Google Gemini (piano gratuito di AI Studio); OpenAI è opzionale tramite `LLM_PROVIDER=openai`
- **CLI chat:** fai una domanda singola oppure chatta in modo interattivo
- **14 test** che non richiedono connessione di rete né API key (LLM simulato, HTTP con mock)

## Scelte di progettazione

- **Gli argomenti generati dall'LLM non sono affidabili:** gli ID ordine devono contenere solo cifre, così valori come `../admin` non raggiungono mai l'URL
- **Gli errori del tool vengono restituiti come testo, non lanciati come eccezioni:** l'agente può spiegare il fallimento al cliente
- **Dati minimi:** il tool restituisce solo ciò che serve per rispondere (nessun nome cliente)
- **Limite di passaggi:** `MAX_GRAPH_STEPS` interrompe i cicli infiniti dei tool (verificato da un test)
- **Prompt hardening:** il prompt di sistema specifica al modello che l'output del tool è costituito da dati, non da istruzioni
- **Progettato per essere testabile:** la logica del tool è separata dal decoratore e l'agente accetta l'LLM come parametro

## Architettura

```mermaid
flowchart LR
    U["Cliente"] --> CLI["CLI: python -m app.cli"]
    CLI --> A["Nodo agente (LLM)"]
    A --> C{"Tool necessario?"}
    C -- sì --> T["Nodo tool: get_order_status"]
    T --> API["Orders API (mock, FastAPI)"]
    API --> T
    T --> A
    C -- no --> R["Risposta finale"]
    R --> U