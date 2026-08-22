# Monday meeting brief (Dr. Zhao)

Use this at 3:00 p.m. Keep manuscript figures vs this-build measurements separate.

Current code on GitHub `main`: `4cde2e4`. After freeze scripts land, tag **`eval-freeze-v1`** and do not mix later UI tweaks into tables.

---

## 1. Frozen-evaluation plan

### What the committee will ask
The **200/200** acceptance number is the **grounded spec-builder** path (JSON + deterministic PlantUML), not DeepSeek-32B and not LoRA-alone. The freeze must report **builder vs LLM path** on the **same** inputs.

### Two generation paths (same 50 requirements × 4 types = 200 jobs each)

| Path | What runs | What it answers |
|------|-----------|-----------------|
| **Builder** | Stage-1 JSON + `plantuml_from_spec` (current 200/200) | Structural/semantic gates when PlantUML is faithful to the spec |
| **LLM** | Stage-2 LoRA (and/or Ollama base) **with spec-builder replace disabled** | What the generator emits without the fidelity rewrite |

Disable in freeze config: `ensure_faithful_plantuml` replace, and `choose_generator` forced to `lora` (fallback to base LLM if LoRA invalid—not silent rebuild). Log `generator=` on every artifact.

### Live 3-VLM sample (thesis tables — not 12)

12 smoke runs stay in an appendix as reliability only.

**Proposed freeze set (live Qwen + LLaMA-Vision + Aya, `skip_vlm=false`):**

| Stratum | n | Notes |
|---------|--:|--------|
| Class | 40 | 30 NL + 10 source-code |
| Object | 40 | NL |
| Component | 40 | NL |
| Package | 40 | NL |
| **Total live 3-VLM** | **160** | 80 builder-path + 80 LLM-path, **paired** (same 80 texts × 2 paths) |

Paired 80 texts: 20 per type from `sample_data/requirements.txt` (plus 10 short Java/Python snippets in the class stratum). That is **160 scored images**, large enough for per-type means/CIs, still smaller than 8k.

**Optional stretch** if GPU time allows: 50 texts × 4 types × 2 paths = **400** scored diagrams.

**Not in the freeze:** full 8,000 × 3-VLM (order of **100+ GPU-hours**). Keep 8k as corpus/training scale; cite subsample for S.

### Metrics to freeze (JSON + markdown under `data/eval/freeze-v1/`)

Per path and per type: render rate, acceptance-stack pass rate, mean **S**, majority **A** rate, dataset-accepted rate, VLM availability (3/3), mean wall time. Plus LLM-vs-builder disagreement table (render OK on builder, fail on LLM, and vice versa).

### Tag and timeline (from Monday)

| When | Action |
|------|--------|
| This week | Flag `FORCE_GENERATOR=lora\|spec-builder`; freeze script; tag `eval-freeze-v1` when script is merged |
| Week 1 | Builder + LLM generate/render on 200+200 (VLM off) — answers compile/render without GPU |
| Week 2 | Live 3-VLM on 160 paired diagrams (or 400 if GPU arrives) |
| Week 3 | Package-failure examples + tables into Ch.5 |

---

## 2. Human-alignment proposal (do not drop)

**Design:** 2 raters × **40 stratified diagrams** = 80 ratings (matches Zhao’s example).

| Type | n | Selection |
|------|--:|-----------|
| Class | 10 | 8 NL + 2 source-code |
| Object | 10 | NL |
| Component | 10 | NL |
| Package | 10 | NL |

Draw the 40 from the **freeze 3-VLM set** (prefer **LLM path** so humans grade model output, not the builder). If an LLM render fails, substitute the next text in that stratum so humans always see a PNG (record substitutions).

**Rubric:** same four 0–6 criteria as VLMs (semantic, structural, syntactic, coherence). Mean of four = human overall. Independent rating; no S shown to raters.

**Raters:** two CS graduate students or lab members who know UML; 30-minute calibration on 4 gold diagrams (not in the 40).

**Time:** ~6–8 minutes per diagram after calibration → **~5 hours per rater** (plus 30 min calibration). Spreadsheet or existing Human Evaluation page.

**Statistics (this build only):**
- Pearson **r** (and Spearman) between human mean and **S**
- Per-criterion r vs each VLM if time
- Inter-rater: Pearson between the two humans; Cohen’s κ or weighted κ on rounded overall (0–6)
- Report n=40; do not reuse manuscript “80 experts / κ≈0.68” as this-build evidence

**If r is low:** weaken “quality-controlled” to “render-gated + VLM-scored; human correlation measured, limited” and discuss package/object.

---

## 3. Writing — section-level milestones

Software is ahead of prose. Propose (adjust with Zhao on Monday):

| Section | Milestone |
|---------|-----------|
| Ch.1 Introduction | Problem, 3-stage claim, contributions; no mixing 200/200 with paper 8k |
| Ch.2 Related work | Generation-only vs verify; MMMU as **weights** not UML benchmark |
| Ch.3 Method | Spec LLM, PlantUML LLM, render gate, S, A, τ=4, S≥3; path diagram |
| Ch.4 Implementation | UML-Pipeline: LoRA vs 32B, dual Ollama, builder, repair; **limitations in the same chapter** |
| Ch.5 Evaluation | Four blocks: (1) acceptance 6/6+200/200+5/5 **builder**; (2) LLM-path render/accept on same 200; (3) live 3-VLM n=160; (4) human n=40, 2 raters |
| Ch.6 Discussion | Package difficulty; builder vs LLM; what “quality-controlled” may claim |
| Ch.7 Conclusion + future | GPU, 32B, larger human set |
| Paper / Overleaf | Sync tables after freeze; same figure discipline |

Draft chapters exist locally; next pass is **method + eval** once freeze JSON exists, then format.

---

## 4. GPU-hours (send before Monday)

Assumptions: one **24 GB** GPU (L4/A10-class); three VLMs **kept loaded**; ~**45–90 s wall time per diagram** for the trio (not Mac 100–120 s). LoRA **0.5B already trained** on this Mac (~2000–4000 MLX iters); GPU hours below are **optional retrain + freeze scoring**.

| Work | n | Estimate |
|------|--:|----------|
| Optional retrain Qwen2.5-0.5B LoRA (QLoRA, ~4k steps) | 1 run | **2–6 GPU-h** |
| Optional larger code LoRA (7B) | 1 run | **12–20 GPU-h** (not required for freeze) |
| Generate/render 200 builder + 200 LLM (CPU/Mac OK) | 400 | **0 GPU-h** |
| Live 3-VLM **160** (recommended freeze) | 160 | **2–4 GPU-h** |
| Stretch 3-VLM **400** | 400 | **5–10 GPU-h** |
| Human study | 40 PNGs | **0 GPU-h** (already scored) |
| Full 8k × 3-VLM | 8000 | **~100–200 GPU-h** — **do not request for this freeze** |

**Request to size:** **~8–15 GPU-hours** covers optional 0.5B retrain + **160–400** live ensemble scores, with slack. A **short-term cloud L4 (~24 GB) for 2–3 days** is enough if no lab workstation. DeepSeek-32B **training** is out of scope; 32B is inference-only if a bigger GPU appears later.

---

## Live demo (Monday)

1. Same e-commerce sentence: **component** (boxes, not blank).  
2. Generate **another type** from gallery.  
3. Show **Score with VLMs** / rescore (or skip and say S is unscored).  
4. Say out loud: **200/200 = builder**; freeze will add **LLM path + 160 3-VLM + 40×2 humans**.
