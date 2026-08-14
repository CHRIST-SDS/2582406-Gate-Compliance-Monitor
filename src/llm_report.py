"""
Local LLM stage: generates a short, human-readable incident report
whenever the compliance engine flags a non-compliant entry.

Talks to Ollama running locally (default http://localhost:11434) -
NO cloud API calls. Requires `ollama serve` running and a model pulled,
e.g.:  ollama pull llama3

Falls back to a template-based report if Ollama isn't reachable, so
the pipeline still runs during development/demo without the model
running.
"""
import datetime

MODEL_NAME = "llama3"


def _template_report(event: dict) -> str:
    return (
        f"[INCIDENT REPORT - TEMPLATE FALLBACK]\n"
        f"Timestamp: {datetime.datetime.now().isoformat(timespec='seconds')}\n"
        f"Gate: {event.get('gate_id', 'Main Gate')}\n"
        f"Detected Reg No: {event.get('reg_no', 'UNKNOWN')}\n"
        f"Reason: {event.get('reason', 'Not found in library profile database')}\n"
        f"Recommended Action: Deny entry, notify security desk for manual verification.\n"
    )


def generate_incident_report(event: dict, model: str = MODEL_NAME) -> str:
    """
    event example:
    {
        "gate_id": "Main Gate",
        "reg_no": "REG9123",
        "reason": "Reg. No. not found in library database" | "Card expired on 2026-05-01",
    }
    """
    prompt = (
        "You are a campus security assistant. Write a short, professional "
        "incident report (4-5 sentences, no headers) for a gate compliance "
        "monitoring system. Do not invent facts beyond what's given.\n\n"
        f"Gate: {event.get('gate_id', 'Main Gate')}\n"
        f"Detected Reg No: {event.get('reg_no', 'UNKNOWN')}\n"
        f"Compliance issue: {event.get('reason', 'Unknown issue')}\n"
        f"Time: {datetime.datetime.now().isoformat(timespec='seconds')}\n"
    )

    try:
        import ollama
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        print(f"[llm_report] Ollama unavailable ({e}). Using template fallback.")
        return _template_report(event)
