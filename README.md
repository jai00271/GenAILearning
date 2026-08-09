# GenAI Gurukul

Job-ready practitioner course in Generative AI — production RAG, agents, evaluation, safety, and delivery. Rigor comes from rubrics, track gates, and capstone acceptance criteria (not a masters-equivalent claim).

| Path | What |
|------|------|
| [`genai-gurukul/`](genai-gurukul/) | Static course site (Hinglish lessons) |
| [`genai-gurukul-labs/`](genai-gurukul-labs/) | Labs, checkpoints, challenges, capstone |

## Serve

```bash
cd genai-gurukul && python3 -m http.server 8080
```

Open http://localhost:8080 — catalog/transcript from `assets/modules.js`.

**All 24 modules are available**, plus CORE/APP/PROD track-challenge pages.

## Labs

```bash
cd genai-gurukul-labs
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
GURUKUL_LAB=solution pytest found-*/tests core-20*/tests app-30*/tests prod-40*/tests capstone/tests -q
```

## Sequencing locks (already reflected in content order)

1. APP 304 Evaluation **before** APP 305 RAG  
2. PROD 401 Advanced eval **before** PROD 402 Fine-tuning  
3. Track challenges after CORE 204, APP 308, PROD 406  
4. Capstone must meet written acceptance criteria (generic “chat with docs on Lambda” fails)

Portfolio artifacts (challenge memos, capstone writeups, interview one-pagers) are **English**. Lesson pages are Hinglish.
