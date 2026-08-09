# PROD 406 — Prompt & Model CI/CD

Companion lab for `genai-gurukul/modules/prod-406-prompt-model-cicd.html`.

```bash
cd genai-gurukul-labs
source .venv/bin/activate
GURUKUL_LAB=solution pytest prod-406/tests -q
# GURUKUL_LAB=starter pytest prod-406/tests -q
```

Offline — `ci_eval_gate` (quality + trace worsen) + sticky percentage rollout
(`sticky_bucket` / `in_rollout` / `choose_variant` / `canary_plan`).
LaunchDarkly-shaped teaching API only — no live flag service.
