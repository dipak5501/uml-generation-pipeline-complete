# Monday Meeting Report — CECS 698 / Thesis Evaluation Plan

**To:** Dr. Yutong Zhao  
**From:** Dipak Yadav (033783670) · dipak.yadav01@student.csulb.edu  
**Date:** 17 August 2026  
**Thesis:** *Automated UML Dataset Generation from Natural-Language Requirements with Multimodal Verification for Software Design*  
**Repository:** https://github.com/dipak5501/uml-generation-pipeline  
**Current `main` commit:** `4cde2e4`

---

## Purpose

Beyond the live application demo, this note proposes three deliverables for committee-ready evaluation and writing: (1) a **frozen-evaluation plan** that separates builder vs LLM paths and scales live 3-VLM scoring beyond 12 smoke runs; (2) a **scoped human-alignment study** (2 raters × 40 diagrams); and (3) **section-level thesis milestones** because software is ahead of the manuscript.

**Discipline:** Manuscript figures (8k balance, 80 experts, κ ≈ 0.68, class r ≈ 0.82) are **not** reused as this-build evidence unless re-run on the frozen commit.

---

## 1. Frozen-evaluation plan

### 1.1 What the committee will ask

The published **200/200** result uses the **grounded spec-builder** path (Stage-1 JSON → `plantuml_from_spec`). It does **not** measure what Stage-2 **LoRA / base LLM alone** produces without the fidelity rewrite. The freeze must answer:

> *When we remove the builder safety net, what does the LLM path achieve on the same inputs?*

The existing **12 live 3-VLM smoke runs** (`data/eval/live_vlm_reliability_summary.json`) are useful for **reliability appendix only** (11/12 render, mean S ≈ 4.93). They are **not** sufficient for thesis tables (per-type means, CIs, builder vs LLM comparison).

### 1.2 Two generation paths (same inputs)

| Path | Configuration | What it measures |
|------|---------------|------------------|
| **Builder** | Stage-1 JSON + `plantuml_from_spec`; `FORCE_GENERATOR=spec-builder` | Structural/semantic gates when PlantUML is faithful to the spec (reproduces 200/200 class of result) |
| **LLM** | Stage-2 LoRA (or Ollama base if LoRA invalid); **`ensure_faithful_plantuml` replace disabled**; `FORCE_GENERATOR=lora` | Raw generator output without spec-builder rewrite |

**Freeze requirements:**
- Log `generator=` on every artifact.
- Do not silently fall back from failed LoRA to builder during LLM-path runs.
- Same requirement texts for both paths.

**Bulk generate/render (no VLM):** 50 requirements × 4 types × 2 paths = **400 jobs** (200 builder + 200 LLM). Runs on Mac/CPU; **0 GPU-hours**.

### 1.3 Live 3-VLM sample — target size and stratification

**Recommended freeze (thesis tables): n = 160 scored diagrams**

Paired design: **80 unique texts × 2 paths** (builder + LLM).

| Stratum | n (per path) | Selection |
|---------|-------------:|-----------|
| Class | 40 | 30 NL from `sample_data/requirements.txt` + 10 short Java/Python snippets |
| Object | 40 | NL |
| Component | 40 | NL |
| Package | 40 | NL |
| **Total** | **160** | 80 texts × builder + 80 texts × LLM |

**Paired texts:** 20 per type drawn from `sample_data/requirements.txt` (50 lines available). Class stratum adds 10 code snippets for source-code mode coverage.

**Scoring:** Live Qwen2.5-VL-3B + LLaMA-3.2-11B-Vision + Aya-Vision-8B; `skip_vlm=false`; same τ = 4, S ≥ 3 gate as production.

**Optional stretch (if GPU time allows):** 50 texts × 4 types × 2 paths = **400** scored diagrams (~5–10 GPU-h).

**Explicitly out of scope:** Full 8,000 × 3-VLM (~100–200 GPU-h). The 8k corpus remains **training scale**; thesis **S** tables cite the 160 (or 400) subsample.

### 1.4 Metrics to freeze

All outputs under `data/eval/freeze-v1/` (JSON + markdown summary):

| Metric | Per path | Per type |
|--------|----------|----------|
| Render success rate | ✓ | ✓ |
| Acceptance-stack pass rate | ✓ | ✓ |
| Mean composite **S** | ✓ | ✓ |
| Majority **A** rate | ✓ | ✓ |
| Dataset-accepted rate (render ∧ A ∧ S ≥ 3) | ✓ | ✓ |
| VLM availability (3/3 scorers) | ✓ | ✓ |
| Mean wall time | ✓ | ✓ |

**Disagreement table:** builder render OK / LLM fail, and reverse — keyed by requirement id and diagram type.

### 1.5 Commit tag and reproducibility

| Item | Plan |
|------|------|
| **Baseline commit (today)** | `4cde2e4` on `main` |
| **Pre-freeze work (this week)** | Add `FORCE_GENERATOR` flag, freeze script (`scripts/eval_freeze_v1.py`), config snapshot in `data/eval/freeze-v1/config.json` |
| **Tag after merge** | **`eval-freeze-v1`** — all thesis tables for this build reference this tag only |
| **Rule** | No UI tweaks or scoring changes mixed into freeze tables after tag; bugfixes → new tag `eval-freeze-v1.1` with changelog |

### 1.6 Timeline

| Week | Dates (approx.) | Deliverable |
|------|-----------------|-------------|
| **Week 0** | 17–23 Aug 2026 | Merge freeze script + `FORCE_GENERATOR`; tag **`eval-freeze-v1`** |
| **Week 1** | 24–30 Aug | Generate/render **200 builder + 200 LLM** (VLM off); acceptance tables |
| **Week 2** | 31 Aug – 6 Sep | Live 3-VLM on **160** paired diagrams (2–4 GPU-h on L4/A10 or Mac if needed) |
| **Week 3** | 7–13 Sep | Package-failure case study + tables drafted into **Ch.5 / Ch.6** |

**GPU request:** ~**8–15 GPU-hours** total (160–400 live scores + optional LoRA retrain slack). Short-term cloud **L4 (~24 GB) for 2–3 days** is sufficient if no lab workstation.

### 1.7 What we can claim after the freeze

| Claim | Before freeze | After freeze |
|-------|---------------|--------------|
| Builder path structural acceptance | 200/200 (existing) | Reconfirmed on tagged commit |
| LLM path alone | Unknown | Measured on same 200 inputs |
| Live **S** / **A** at thesis scale | 12 smoke runs only | **n = 160** (or 400) with per-type stats |
| “Quality-controlled dataset” | Render + gate only | Gate + measured **S**; human **r** still needs §2 |

---

## 2. Human-alignment study — concrete proposal

### 2.1 Why we keep it (scoped, not dropped)

Without **any** human correlation measured on **this build**, the thesis must weaken “quality-controlled” to “render-gated + VLM-scored.” A small, well-designed study is preferable to dropping human alignment entirely.

### 2.2 Design summary

| Parameter | Value |
|-----------|-------|
| **Diagrams** | **n = 40**, stratified by type |
| **Raters** | **2** (CS graduate students or lab members with UML familiarity) |
| **Total ratings** | **80** (2 × 40) |
| **Source** | Draw from **freeze 3-VLM set**, prefer **LLM path** (humans grade model output, not builder) |
| **Blinding** | Raters see requirement + PNG only; **no S, no A, no model names** |

### 2.3 Stratification (40 diagrams)

| Type | n | Notes |
|------|--:|-------|
| Class | 10 | 8 NL + 2 source-code |
| Object | 10 | NL |
| Component | 10 | NL |
| Package | 10 | NL |

**Substitution rule:** If an LLM-path diagram fails render, substitute the next requirement in that stratum so every human rating has a PNG. Log substitutions in `data/eval/freeze-v1/human_study_manifest.json`.

### 2.4 Rubric and procedure

**Same four criteria as VLMs (0–6 each):**
1. Semantic correctness  
2. Structural completeness  
3. Syntactic accuracy (UML notation)  
4. Overall coherence  

**Human overall** = mean of four criteria.

**Calibration (30 min):** 4 gold diagrams (not in the 40) with advisor or lead rater to align scale.

**Rating time:** ~6–8 min/diagram → **~5 h/rater** + 30 min calibration.

**Collection:** Spreadsheet export or existing **Human Evaluation** page in Streamlit (`ui/pages/5_Human_Evaluation.py`); store JSON under `data/eval/freeze-v1/human_ratings/`.

### 2.5 Statistics (this build only)

| Analysis | Method |
|----------|--------|
| Human vs **S** | Pearson **r** and Spearman ρ (n = 40 diagram means) |
| Inter-rater agreement | Pearson between two raters; Cohen’s κ (or weighted κ) on rounded overall (0–6) |
| Per-type | Report means by diagram type; do not over-claim on n = 10 |
| Optional | Per-criterion r vs each VLM if time permits |

**Do not cite:** manuscript “80 experts, κ ≈ 0.68, r ≈ 0.82 class” as this-build evidence.

### 2.6 Interpretation plan

| Outcome | Thesis language |
|---------|-----------------|
| **r ≥ 0.6** (class-heavy) | “Automated **S** correlates moderately with expert judgment on this subsample.” |
| **r lower on package/object** | Discuss type difficulty; align with package render failures |
| **Low overall r** | Weaken to “render-gated + VLM-scored; human correlation measured, limited”; emphasize gate + failure analysis |

### 2.7 Human study timeline

| When | Action |
|------|--------|
| Week 2 (parallel with 3-VLM) | Finalize 40-diagram manifest from freeze LLM-path outputs |
| Week 3 | Recruit 2 raters; calibration session |
| Week 4 | Ratings complete; compute r, κ; table for Ch.5 |
| By mid-Sep | Human-alignment subsection draft in thesis |

**GPU-hours for human study:** **0** (PNGs and **S** already computed during freeze).

---

## 3. Writing — section-level milestones

Software (~95%) is ahead of manuscript (~60%). Proposed milestones for advisor approval on Monday:

### 3.1 Chapter map and targets

| Section | Target date | Milestone / exit criterion |
|---------|-------------|----------------------------|
| **Ch.1 Introduction** | 30 Aug 2026 | Problem, 3-stage claim, contributions; **explicitly separate** 200/200 builder result from 8k corpus scale |
| **Ch.2 Related work** | 6 Sep 2026 | Generation-only vs verify; MMMU as **weights**, not UML benchmark |
| **Ch.3 Method** | 13 Sep 2026 | Spec LLM, PlantUML LLM, render gate, **S**, **A**, τ = 4, S ≥ 3; builder vs LLM path diagram |
| **Ch.4 Implementation** | 20 Sep 2026 | UML-Pipeline stack: LoRA vs 32B, dual Ollama, builder, repair, SQLite; **limitations in same chapter** |
| **Ch.5 Evaluation** | 4 Oct 2026 | Four blocks: (1) builder 6/6 + 200/200 + 5/5 negatives; (2) LLM-path on same 200; (3) live 3-VLM **n = 160**; (4) human **n = 40**, 2 raters |
| **Ch.6 Discussion** | 11 Oct 2026 | Package difficulty; builder vs LLM gap; what “quality-controlled” may claim given measured **r** |
| **Ch.7 Conclusion** | 18 Oct 2026 | Contributions, limits, future (32B inference, larger human set, GPU scale) |
| **Appendices** | 25 Oct 2026 | 12 smoke-run reliability; freeze config; human rubric; sample diagrams |
| **Paper / Overleaf** | Sync after Ch.5 freeze tables | Same figure discipline; no manuscript numbers without freeze tag |

### 3.2 Formatting and committee pass (post-content)

| Task | Target |
|------|--------|
| CSULB Format Manual paste + double-space | Nov 2026 |
| Citation audit (primary PDFs) | Oct 2026 |
| Committee content review (Zhao / Basit / Qin) | Oct–Nov 2026 |
| Final thesis + code freeze | **2 Nov 2026** (agreement deadline) |

### 3.3 Writing priority order

1. **Ch.3 Method + Ch.5 Evaluation** — blocked only until Week 2–3 freeze JSON exists; start Method skeleton now.  
2. **Ch.4 Implementation** — can draft from current repo immediately.  
3. **Ch.1–2** — light polish once evaluation framing is fixed.  
4. **Ch.6–7** — after human **r** is known.

---

## 4. Summary ask for Monday

Please confirm or adjust:

1. **Freeze sample:** **n = 160** live 3-VLM (80 paired texts × 2 paths), optional stretch **n = 400**.  
2. **Tag:** **`eval-freeze-v1`** after freeze script merges this week.  
3. **Human study:** **2 raters × 40** stratified diagrams from LLM-path freeze set.  
4. **Writing:** Section dates above; prioritize **Ch.3 + Ch.5** once freeze tables exist.  
5. **GPU:** Request **~8–15 GPU-hours** (or 2–3 days cloud L4) for Week 2 scoring.

---

## 5. One-page status (for oral close)

| Track | Status |
|-------|--------|
| Application / pipeline | Largely complete (`4cde2e4`); demo ready |
| Builder acceptance | 200/200 + golden 6/6 + 5/5 negatives |
| Live 3-VLM at thesis scale | **Planned** (160); 12 smoke runs done |
| LLM-path alone | **Planned** (paired 200 + 80 texts × 2 paths scored) |
| Human alignment | **Proposed** (40 × 2 raters); not yet executed |
| Thesis writing | Draft exists; **eval chapters need freeze data** |

**Elevator close:** “The app implements the thesis pipeline. The freeze tags `eval-freeze-v1`, compares builder vs LLM on the same inputs, scores 160 diagrams with live 3-VLM, and adds 40 human-rated diagrams so we can report correlation on this build—not manuscript placeholders.”

---

*Prepared for Monday meeting with Dr. Zhao — 17 August 2026.*
