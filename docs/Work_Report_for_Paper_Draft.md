# Automated UML Dataset Generation from Natural-Language Requirements with Multimodal Verification

**Progress Report for Paper Draft**

Dipak Yadav  
Department of Computer Engineering and Computer Science  
California State University, Long Beach  
Student ID: 033783670  
20 August 2026

**Repository:** https://github.com/dipak5501/uml-generation-pipeline

---

## 1. Introduction

This report documents the implemented system for automated UML dataset generation from natural-language software requirements, with multimodal verification of the resulting diagrams. The work is intended to support drafting the paper of the same title.

Unified Modeling Language (UML) is the standard notation for communicating software design. Constructing class, object, component, and package diagrams from informal requirements is labor-intensive and difficult to scale. Large language models can synthesize PlantUML from text, but a diagram that compiles is not necessarily a faithful design artifact: entities may be omitted, relationships may be incorrect, or the structure may be visually valid while conceptually incomplete. The system therefore treats **generation and verification as a single pipeline**. A sample is retained for a quality-controlled dataset only when the diagram renders, the vision-language ensemble accepts it by majority vote, and the composite score meets a minimum threshold.

The implementation is an end-to-end application: requirement or source-code intake, structured specification, PlantUML synthesis, rendering with repair, three-model vision-language scoring, persistence of the full artifact trace, human review, analytics, and dataset export.

### 1.1 Research questions

- **RQ1.** How effectively can a decomposed LLM pipeline generate syntactically and semantically valid design-phase UML from natural-language requirements?
- **RQ2.** To what degree does the multimodal ensemble score \(S\) correlate with human expert ratings?
- **RQ3.** How does generation and verification accuracy vary across UML diagram families (class, object, component, package)?

### 1.2 Contributions

1. A three-stage pipeline that maps a requirement (or source code) to a structured specification, PlantUML, a rendered diagram, and a multimodal quality decision.
2. An MMMU-weighted composite score \(S\) with a render-failure indicator (failed render implies \(S = 0\)).
3. A majority-vote acceptance gate \(A\) with threshold \(\tau = 4\), and a dataset rule requiring \(A = 1\) and \(S \ge 3\).
4. A complete software system (API, user interface, database, export) that operationalizes the pipeline.
5. An evaluation design covering structural acceptance, live ensemble scoring, and human alignment (Section 7).

---

## 2. Method

### 2.1 Inputs and outputs

| Item | Description |
|------|-------------|
| Primary input | Natural-language software requirement |
| Secondary input | Source code (Python or Java) |
| Sample requirements | `sample_data/requirements.txt` (50 sentences) |
| Sample code | `sample_data/sample_code.py` |
| Diagram types | Class, object, component, package |
| Outputs | Technical specification (JSON), PlantUML source, PNG, per-model scores, composite \(S\), majority flag \(A\), dataset export (JSONL / CSV / Parquet) |

### 2.2 Stage 1 — Technical specification

Llama-3.2-1B-Instruct converts free-form requirements into a structured JSON specification (entities, attributes, operations, and relationships). A parallel prompt maps source code to the same specification schema. Versioned templates are stored as:

- `prompts/requirement_to_tech_spec.v1.txt`
- `prompts/code_to_tech_spec.v1.txt`

The specification is the intermediate representation consumed by Stage 2. A grounded specification builder can also instantiate the same JSON schema from the requirement text, providing a deterministic path used in the structural acceptance study (Section 6).

### 2.3 Stage 2 — PlantUML synthesis

PlantUML is produced by type-specific prompts:

- `prompts/tech_spec_to_class.v1.txt`
- `prompts/tech_spec_to_object.v1.txt`
- `prompts/tech_spec_to_component.v1.txt`
- `prompts/tech_spec_to_package.v1.txt`
- `prompts/repair_plantuml.v1.txt` (adaptive repair, up to three attempts)

The Stage-2 generators are:

| Generator | Description |
|-----------|-------------|
| Specification builder | Deterministic PlantUML derived from the Stage-1 JSON (`plantuml_from_spec`). Used for the 200/200 structural acceptance evaluation. |
| Fine-tuned code model | MLX LoRA on Qwen2.5-0.5B-Instruct-4bit, trained on an assembled Hugging Face UMLCode corpus of approximately 8,000 examples. |
| Reasoning code model | DeepSeek-R1-Distill-Qwen-32B with chain-of-thought prompting, as specified in the paper design. |

Generated scripts pass syntax and UML-structure validators, then the **render gate** (PlantUML with Java). Render success is required before vision-language scoring. Render failure sets \(S = 0\).

### 2.4 Stage 3 — Multimodal verification

Each rendered diagram is scored independently by three vision-language models. Weights are the models’ MMMU benchmark accuracies, used as a principled proxy for multimodal reasoning:

| Model | MMMU weight \(w_j\) |
|-------|---------------------:|
| Qwen2.5-VL-3B-Instruct | 53.1 |
| Llama-3.2-11B-Vision-Instruct | 50.7 |
| Aya-Vision-8B | 39.9 |

Each model assigns integer scores on four criteria (0–6)—semantic correctness, structural completeness, syntactic accuracy, and overall coherence—and an overall score. The scoring prompt (`prompts/vlm_scoring.v1.txt`) evaluates the diagram image against the **original requirement**. The human rubric uses the same four dimensions (`prompts/human_evaluation_rubric.v1.txt`).

**Composite score.** Let \(s_{ij}\) be the score of VLM \(j\) on diagram \(i\), and let \(\delta_i = 1\) if diagram \(i\) renders and \(0\) otherwise:

\[
S_i = \delta_i \cdot \frac{\sum_{j=1}^{3} w_j s_{ij}}{\sum_{j=1}^{3} w_j}
\]

Worked example (render success; scores \(5\), \(4\), \(3\)):

\[
S = \frac{53.1 \times 5 + 50.7 \times 4 + 39.9 \times 3}{143.7} \approx 4.09
\]

**Majority-vote gate.** With threshold \(\tau = 4\),

\[
v_{ij} = \mathbf{1}[s_{ij} \ge \tau], \qquad
A_i = \mathbf{1}\Bigl[\sum_{j=1}^{3} v_{ij} \ge 2\Bigr]
\]

A diagram enters the validated dataset if it renders, \(A_i = 1\), and \(S_i \ge 3\). A separate UML acceptance stack (structure and requirement–diagram traceability) is applied in addition to the ensemble decision.

---

## 3. Implementation

The pipeline is delivered as a local and deployable application.

| Layer | Implementation |
|-------|----------------|
| API | FastAPI (port 8000), OpenAPI documentation |
| Interface | Streamlit (port 8501): Dashboard, Single Generation, Batch Generation, Generated Diagrams, Human Evaluation, Analytics, Settings, System Design |
| Persistence | SQLite (`data/uml_app.db`): projects, jobs, specifications, artifacts, render attempts, repair attempts, per-model scores, composite scores, human reviews |
| Inference backends | Ollama, Hugging Face Inference Providers, OpenAI-compatible / vLLM, MLX LoRA |
| Jobs | In-process thread pool with job status polling |
| Export | JSONL, CSV, Parquet |
| Packaging | Docker Compose, Render blueprint, Makefile |
| Tests | Scoring formulas, validators, specification-to-PlantUML, API, acceptance |

### 3.1 Application programming interface

- `POST /api/generate` — single requirement or source-code generation  
- `POST /api/generate/batch` — batch generation from the sample file or a custom set  
- `GET /api/jobs/{id}` — job status  
- `GET /api/artifacts/{id}` — artifact trace, image, and PlantUML  
- `POST /api/artifacts/{id}/rescore` and `/repair`  
- `POST /api/human-review`  
- `GET /api/analytics/summary`, `/distributions`, `/package-failures`  
- `GET /api/export/dataset`  
- `GET /api/settings/health`

### 3.2 Training corpus and fine-tuning

An 8,000-example training corpus was assembled from public Hugging Face UMLCode datasets (`scripts/build_training_corpus.py`), covering class, object, component, and package PlantUML paired with specifications. The corpus is used to fine-tune the Stage-2 LoRA adapter (`scripts/finetune_plantuml.py`). Generation-time verification (Stage 3) is applied when diagrams are produced through the application, independently of corpus assembly.

---

## 4. Completed evaluation

Structural and semantic acceptance was measured on the specification-builder path (Stage-1 JSON → deterministic PlantUML → render → UML rules → requirement traceability), without substituting vision-language scores for those gates.

| Study | Result |
|-------|--------|
| Golden regression | 6/6 generated, compiled, rendered, UML-valid, and semantically accepted |
| Sample requirements × four diagram types | **200/200** full-pipeline accepted |
| Negative controls | 5/5 correctly rejected |

Source: `reports/acceptance_eval.md`.

Unit tests cover the composite formula (render failure implies \(S = 0\)), the majority gate, the dataset rule, specification parsing, PlantUML construction, and API contracts. The application supports single generation, batch generation, gallery inspection, rescoring, human review, and export.

---

## 5. Mapping to the paper

| Paper section | Content available from this implementation |
|---------------|--------------------------------------------|
| Introduction | Problem, three-stage claim, research questions, contributions |
| Related work | Generation versus verification; MMMU used as ensemble weights |
| Method | Stages 1–3, prompts, render gate, equations for \(S\) and \(A\), \(\tau = 4\), \(S \ge 3\) |
| Implementation | FastAPI / Streamlit system, backends, LoRA, artifact trace, export |
| Experimental design | Section 7 of this report |
| Results | Structural acceptance (Section 4); ensemble and human tables from the design in Section 7 |

Draft abstract:

> This paper presents an automated three-stage pipeline for generating design-phase UML artifacts from natural-language requirements and validating them through multimodal verification. Stage 1 uses Llama-3.2-1B-Instruct to convert free-form requirements into structured JSON specifications. Stage 2 synthesizes PlantUML for class, object, component, and package diagrams. Stage 3 renders each artifact and evaluates it with an ensemble of three vision-language models—Qwen2.5-VL-3B, Llama-3.2-11B-Vision, and Aya-Vision-8B—whose scores are combined by MMMU-weighted aggregation together with a majority-vote acceptance gate. The accompanying system records full generation traces and supports human evaluation and dataset export. On a 200-diagram structural-acceptance benchmark (50 requirements × four diagram types), the specification-builder path accepted 200/200 artifacts.

---

## 6. Proposed experimental design for Results

The following studies complete the empirical section of the paper on the implemented system.

### 6.1 Generation paths

| Path | Configuration |
|------|----------------|
| Builder | Stage-1 specification and `plantuml_from_spec` |
| LLM | Stage-2 fine-tuned (or base) code model on the same inputs |

Design: 50 requirements × 4 diagram types × 2 paths = 400 generated artifacts. Metrics: render rate and UML-acceptance rate per path and per type.

### 6.2 Live three-VLM scoring

Paired sample of **n = 160** scored diagrams (80 texts × two paths; 40 per type; class stratum includes source-code inputs). Scoring uses Qwen2.5-VL-3B, Llama-3.2-11B-Vision, and Aya-Vision-8B with \(\tau = 4\) and dataset rule \(S \ge 3\).

Reported metrics (per path and per type): render success, acceptance-stack pass rate, mean \(S\), majority \(A\) rate, dataset-accepted rate, and wall-clock time. Optional extension: \(n = 400\).

### 6.3 Human alignment (RQ2)

| Parameter | Design |
|-----------|--------|
| Diagrams | 40, stratified 10 per type |
| Raters | 2, UML-familiar |
| Rubric | Semantic, structural, syntactic, coherence (0–6); overall = mean of four |
| Blinding | Requirement and PNG only; ensemble scores hidden |
| Statistics | Pearson and Spearman correlation of human overall versus \(S\); inter-rater agreement |

---

## 7. Artifacts

| Artifact | Location |
|----------|----------|
| Source code | https://github.com/dipak5501/uml-generation-pipeline |
| Application | `./scripts/run_local.sh` — UI `http://127.0.0.1:8501`, API `http://127.0.0.1:8000/docs` |
| Acceptance results | `reports/acceptance_eval.md` |
| Scoring implementation | `app/services/scoring.py` |
| Prompt templates | `prompts/` |
| Sample data | `sample_data/` |
| LaTeX working copy | `paper/main.tex` |

---

*Department of Computer Engineering and Computer Science, California State University, Long Beach · 20 August 2026*
