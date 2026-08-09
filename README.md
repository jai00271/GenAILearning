# GenAI Gurukul

Job-ready practitioner course in Generative AI — production RAG, agents, evaluation, safety, and delivery. Rigor comes from rubrics, track gates, and capstone acceptance criteria (not a masters-equivalent claim).

| Path | What |
|------|------|
| [`genai-gurukul/`](genai-gurukul/) | Static course site (Hinglish lessons) |
| [`genai-gurukul-labs/`](genai-gurukul-labs/) | Labs, checkpoints, challenges, capstone |

## Serve

Serve from the **repo root** (parent of both `genai-gurukul/` and `genai-gurukul-labs/`). If you start the server only inside `genai-gurukul/`, browser links to `genai-gurukul-labs/...` return **404**.

Use `serve.py` (not plain `http.server`) so the bottom-right **Ask Gurukul** chat can call Cursor:

```bash
# From this folder (GEN AI / repo root)
pip install cursor-sdk
# .env already has CURSOR_API_KEY=...
python serve.py
```

- Course site: http://localhost:8080/genai-gurukul/  (or http://127.0.0.1:8080/genai-gurukul/)
- Example lab folder: http://localhost:8080/genai-gurukul-labs/found-101/
- Chat health: http://localhost:8080/api/tutor/health

Catalog/transcript come from `genai-gurukul/assets/modules.js`. Module cards, transcript codes, Labs links, and external docs open in a **new tab**.

Lesson pages auto-link key terms (dashed teal). Click → right **concept sidepanel** with a deeper Hinglish explainer, SVG diagram/chart, and pitfalls (`assets/concepts.js`).

Bottom-right **chat icon** opens Ask Gurukul (Cursor agent, current lesson as context). Key stays in `.env`, never in the browser.

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
