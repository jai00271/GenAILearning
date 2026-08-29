# GenAI Gurukul

Job-ready practitioner course in Generative AI — production RAG, agents, evaluation, safety, and delivery — plus **Phase 2: Engineering Manager** for Technical Managers moving to EM roles at large orgs. Rigor comes from rubrics, track gates, and written acceptance criteria (not a masters-equivalent claim).

| Path | What |
|------|------|
| [`genai-gurukul/`](genai-gurukul/) | Static course site (Hinglish lessons) |
| [`genai-gurukul-labs/`](genai-gurukul-labs/) | Labs, checkpoints, challenges, capstone |

## Phases

| Phase | Track codes | Intent |
|-------|-------------|--------|
| **1 · GenAI practitioner** | FOUND → CORE → APP → PROD → CAP | Ship production GenAI with eval, cost, and failure modes |
| **2 · Engineering Manager** | EM 601–612 (+ track challenge) | People systems, hiring bar, delivery ownership, GenAI team design, EM interview narrative |

Phase 2 does **not** replace Phase 1. Start EM after (or alongside) GenAI depth if you already lead engineers as a Technical Manager.

## Serve

Serve from the **repo root** (parent of both `genai-gurukul/` and `genai-gurukul-labs/`). If you start the server only inside `genai-gurukul/`, browser links to `genai-gurukul-labs/...` return **404**.

Use `serve.py` (not plain `http.server`) so the bottom-right **Ask Gurukul** chat can call Cursor:

```bash
# From this folder (GEN AI / repo root)
pip install cursor-sdk
# .env already has CURSOR_API_KEY=...
python serve.py
```

- Course site: http://127.0.0.1:8080/genai-gurukul/  *(Windows: `localhost` mat use karo — `::1` empty response de sakta hai)*
- Phase 2 entry: http://127.0.0.1:8080/genai-gurukul/modules/em-601-role-shift.html
- Example lab folder: http://127.0.0.1:8080/genai-gurukul-labs/found-101/
- Chat health: http://127.0.0.1:8080/api/tutor/health

Catalog/transcript come from `genai-gurukul/assets/modules.js`. Module cards, transcript codes, Labs links, and external docs open in a **new tab**.

Lesson pages auto-link key terms (dashed teal). Click → right **concept sidepanel** with a deeper Hinglish explainer, SVG diagram/chart, and pitfalls (`assets/concepts.js`).

Bottom-right **chat icon** opens Ask Gurukul (Cursor agent, current lesson as context). Key stays in `.env`, never in the browser.

**Phase 1:** 24 GenAI modules + CORE/APP/PROD track challenges. **Phase 2:** EM 601–612 + EM track challenge.

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
5. EM track: role-shift → operating system → coaching → hiring → performance → delivery → stakeholders → tech judgment → GenAI teams → culture → incidents → interview narrative → EM challenge

Portfolio artifacts (challenge memos, capstone writeups, interview one-pagers) are **English**. Lesson pages are Hinglish.
