# GenAI Gurukul

Job-ready practitioner course in Generative AI — production RAG, agents, evaluation, safety, and delivery. Not a research degree; rigor comes from rubrics, track gates, and capstone acceptance criteria.

| Path | What it is |
|------|------------|
| [`genai-gurukul/`](genai-gurukul/) | Static course site (Hinglish lessons, catalog, design system) |
| [`genai-gurukul-labs/`](genai-gurukul-labs/) | Runnable Python labs (`starter/` / `solution/` / `tests/`) |
| [`PRD-GenAI-Gurukul.md`](PRD-GenAI-Gurukul.md) | Curriculum contract (when present in repo) |

## Serve the site

```bash
cd genai-gurukul
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080). The 24-module transcript strip and catalog both read from `assets/modules.js` — do not hand-copy the strip into every HTML file.

**Available now:** FOUND 101–103, CORE 201–202. Later modules stay locked until authored.

## Run labs

```bash
cd genai-gurukul-labs
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest found-101/tests found-102/tests found-103/tests core-201/tests core-202/tests -q
```

Reference solutions:

```bash
GURUKUL_LAB=solution pytest found-101/tests found-102/tests found-103/tests core-201/tests core-202/tests -q
```

## Sequencing (non-negotiable)

Evaluation fundamentals (APP 304) before RAG (APP 305). Advanced evaluation (PROD 401) before fine-tuning (PROD 402). Portfolio-facing artifacts are English; lesson pages are Hinglish.
