# GenAI Gurukul

Job-ready practitioner course in Generative AI — production RAG, agents, evaluation, safety, and delivery. Not a research degree; rigor comes from rubrics, track gates, and capstone acceptance criteria.

| Path | What it is |
|------|------------|
| [`genai-gurukul/`](genai-gurukul/) | Static course site (Hinglish lessons, catalog, design system) |
| [`genai-gurukul-labs/`](genai-gurukul-labs/) | Runnable Python labs (`starter/` / `solution/` / `tests/`) |

## Serve the site

```bash
cd genai-gurukul
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080). Transcript + catalog read from `assets/modules.js`.

**Available now:** FOUND 101–103, CORE 201–204 + CORE challenge, APP 301–303. Next required: **APP 304 Evaluation Fundamentals** (before any RAG).

## Run labs

```bash
cd genai-gurukul-labs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
GURUKUL_LAB=solution pytest found-*/tests core-20*/tests app-30*/tests -q
```

## Sequencing (non-negotiable)

Evaluation fundamentals (APP 304) before RAG (APP 305). Advanced evaluation (PROD 401) before fine-tuning (PROD 402). Portfolio-facing artifacts are English; lesson pages are Hinglish.
