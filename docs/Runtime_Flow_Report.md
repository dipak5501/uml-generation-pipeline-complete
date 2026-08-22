# Runtime flow check (live app)

Checked while API PID 76053 and UI PID 76056 were listening on `0.0.0.0:8000` and `:8501`.

## Verdict

**The app is up and the UI/API path is healthy.** Home page, health, and analytics respond in milliseconds. Dual Ollama is up (0.24 on `:11434`, 0.32 on `:11435`). PlantUML JAR and Java are present. LoRA adapter files are on disk.

**Generation is the slow part, not Streamlit.** A live job (**#231**) was still `running` after Stage-1 finished and the **MLX LoRA** model started loading. Several recent artifacts are `pending` with score 0 (jobs not finished). Older completed rows look fine (e.g. class/component **S = 5.0**, object **S = 4.44**).

---

## Current flow (what actually runs)

```
Browser (this Mac or Wi-Fi) 
  → Streamlit :8501
      → FastAPI :8000
          1. Stage 1  Ollama LLaMA 3.2 1B  → JSON spec (+ grounding)
          2. Stage 2  PlantUML
               • Score VLMs OFF  → spec-builder (seconds)
               • Score VLMs ON or class LoRA path → MLX Qwen2.5-0.5B LoRA
          3. Validate / repair (max 3)
          4. Render PNG (local JAR or plantuml.com)
          5. If Score VLMs ON → Qwen-VL + LLaMA-Vision + Aya-8B
          6. S (MMMU weights) + majority A + SQLite
```

---

## Timed while running

| Check | Result | Time |
|--------|--------|------|
| UI `http://127.0.0.1:8501` | 200 | **0.001 s** |
| `GET /api/settings/health` | 200 ok | **0.002 s** |
| `GET /api/analytics/summary` | 200 | **0.21 s** |
| Ollama :11434 / :11435 | 0.24.0 / 0.32.1 | OK |
| Job 231 | **running**, 0/1 complete | stuck in Stage 2 LoRA after Stage 1 |

Health messages: `spec/VLM=ollama · code=finetuned-mlx`, Aya local weights, `API_ACCESS_TOKEN` unset (LAN is open), PlantUML remote allowed as fallback.

---

## What takes more time (largest first)

1. **Three VLMs (if the checkbox is on)** — ~1–2+ min per diagram (Qwen 3B + LLaMA-11B-Vision + Aya-8B on this Mac). This is the paper score **S**, not drawing UML.
2. **LoRA Stage 2 (class, when scoring is on)** — first load of MLX adapters, then token generation. Job 231 is in this step. Can be **minutes** even for a short sentence (`FINETUNED_MAX_TOKENS` still high; we stop at `@enduml` when the new code is used).
3. **Stage 1 Ollama spec** — typically **10–40 s** (job 231 completed this; log: `Merged grounded concepts: Payment, Method, Book`).
4. **Render** — usually a few seconds (JAR or HTTP).
5. **UI pages** — not the bottleneck after the health-hang fix.

**Fast path:** Generate with **Score with VLMs unchecked** → spec-builder after Stage 1. Total often ~15–45 s (almost all Stage 1).

---

## Recent artifacts (sample)

| ID | Type | Render | S |
|----|------|--------|--:|
| 4746–4742 | class/object | **pending** | 0 |
| 4741 | object | success | 4.44 |
| 4740 | component | success | 5.00 |
| 4739 | class | success | 5.00 |

Pending rows mean a generate/LoRA/VLM job has not finished, not that the UI is frozen.

---

## What is good

- API and Streamlit respond; home page no longer waits on a hung Java health check.
- Ollama dual-serve is healthy.
- Completed diagrams show real scores (not all zeros).
- Component builder path has produced accepted renders.

## What is not good (expected on this laptop)

- One generate can occupy a worker on **LoRA** for a long time; the UI will poll job 231 until it ends.
- Full 3-VLM scoring is too heavy for “small UML” on this machine (same conclusion as the GPU request to Dr. Zhao).
- LAN API has no access token (fine at home, not for the public internet).

**For a quick diagram now:** wait for job 231 to finish or ignore it, open Generate, leave **Score with VLMs off**, one diagram type only.
