# APP 309 — Multimodal GenAI (survey) lab

Companion lab for `genai-gurukul/modules/app-309-multimodal.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest app-309/tests -q
# after filling starter TODOs:
# GURUKUL_LAB=starter pytest app-309/tests -q
```

Offline via `FakeImageClient` (deterministic PNG bytes). Optional Ollama path uses
injectable `httpx` + `MockTransport` in tests — no GPU, no paid keys.
