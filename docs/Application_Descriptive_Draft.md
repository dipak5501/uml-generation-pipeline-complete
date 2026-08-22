# UML-Pipeline: Descriptive Draft of the Application

**Automated UML Dataset Generation from Natural-Language Requirements with Multimodal Verification for Software Design**

Dipak Yadav  
Department of Computer Engineering and Computer Science  
California State University, Long Beach  
20 August 2026

**Software:** UML-Pipeline  
**Repository:** https://github.com/dipak5501/uml-generation-pipeline  
**Local interface:** http://127.0.0.1:8501  
**API documentation:** http://127.0.0.1:8000/docs  

---

## 1. Purpose of the application

UML-Pipeline is an interactive research system that turns a software requirement—or a fragment of source code—into a **design-phase UML diagram**, then **verifies** that diagram before it is stored as a dataset sample.

The application is built around a simple claim: generating PlantUML is not enough. A diagram may compile and still omit required entities, misuse relationships, or present a structure that is visually valid but conceptually incomplete. UML-Pipeline therefore combines generation, rendering, rule-based acceptance, and a three-model vision-language ensemble in one workflow.

A user can:

1. Enter a natural-language requirement (for example, “Build an online bookstore with inventory, carts, and checkout”) or paste source code.
2. Choose one or more diagram types: **class**, **object**, **component**, or **package**.
3. Obtain a structured technical specification, PlantUML source, a rendered PNG, per-model quality scores, a composite score **S**, a majority-vote flag **A**, and a dataset-acceptance decision.
4. Browse the full history of diagrams, rescore or regenerate related types, collect human ratings, inspect analytics, and export the dataset.

The same pipeline is used for a single interactive run and for batch construction of evaluation sets (for example, 50 sample requirements × 4 diagram types = 200 artifacts).

---

## 2. What the application produces

For each generation the system persists a **trace**, not only an image:

| Artifact | Meaning |
|----------|---------|
| Requirement or source text | The original user input |
| Input mode | `requirement` or `source_code` (language detected when code is supplied) |
| Technical specification | Structured JSON (entities, attributes, operations, relationships) plus raw text |
| PlantUML code | Type-specific UML script |
| Rendered diagram | PNG stored under `data/artifacts/` |
| Render attempts | Success or compiler/server messages per try |
| Repair attempts | Before/after PlantUML and the reason for each repair |
| Model scores | Integer 0–6 from each vision-language model, with weight and explanation |
| Composite **S** | MMMU-weighted average of the ensemble |
| Majority **A** | True if at least two models score ≥ τ (default 4) |
| Dataset accepted | True when render succeeds, **A** = 1, and **S** ≥ 3 |
| UML acceptance report | Syntax, compile, render, structure, and semantic/traceability gates |
| Human review (optional) | Four rubric dimensions and comments |

Export formats: **JSONL**, **CSV**, and **Parquet** (`GET /api/export/dataset`).

---

## 3. System architecture

UML-Pipeline is a two-process application on one host.

```
Browser
   │
   ▼
Streamlit UI  (:8501)          Clients: Generate, Batch, Gallery,
   │                           Human Evaluation, Analytics, Settings,
   │                           System Design
   ▼
FastAPI       (:8000)          REST + OpenAPI
   │
   ▼
Orchestration                  app/services/orchestration.py
   │
   ├── Providers               spec LLM, PlantUML LLM / LoRA, 3 VLMs
   ├── Validators & repair     syntax, UML structure, semantics
   ├── PlantUML render         local Java + JAR, or PlantUML HTTP server
   └── Persistence             SQLite  data/uml_app.db
                               PNG     data/artifacts/{id}/
```

- **UI** is a Streamlit multipage app (`ui/streamlit_app.py` and `ui/pages/`). It never loads models itself; it calls the API.
- **API** is FastAPI (`app/main.py`). On startup it creates the database schema, ensures the artifact directory exists, and mounts routers for generate, artifacts, human review, and analytics.
- **Jobs** run in an in-process thread pool (`app/jobs/runner.py`, four workers). The UI starts generation asynchronously so the user can change pages while a job runs; progress is polled via `GET /api/jobs/{id}`.
- **Core research logic** lives in `uml_pipeline/` (rendering, scoring helpers, LLM client) and is wrapped by `app/services/`.
- **Prompts** are versioned text files under `prompts/`, loaded through `app/prompts_registry.py`.

There is no Redis, Celery, or external message bus. A default project named “UML-Pipeline” is created on first use.

---

## 4. End-to-end generation pipeline

The function `run_single_generation()` in `app/services/orchestration.py` is the heart of the application. Every single and batch request follows the same stages.

### 4.1 Input preparation

The client sends:

- `requirement` — free text or source code (bounded in length);
- `diagram_type` or `diagram_types` — class, object, component, package;
- `input_mode` — `requirement` or `source_code`;
- `skip_vlm` — whether to compute the vision-language ensemble on this run;
- `async_mode` — default true for the UI.

If the user pastes code, `app/services/code_analysis.py` detects language (Python, Java, and related patterns) and extracts classes, methods, and relations to ground the specification. Requirement text is stored as `RequirementInput`. Optional examples on the Generate page (bookstore, hospital, food delivery, and a small Python order/payment snippet) are only starting points; any paragraph can be typed freely.

### 4.2 Stage 1 — Technical specification

A chat model (paper design: **Llama-3.2-1B-Instruct**) reads the requirement or a code-derived summary and emits a structured specification. Prompts:

- `prompts/requirement_to_tech_spec.v1.txt`
- `prompts/code_to_tech_spec.v1.txt`

The application then **grounds and validates** the JSON (`ensure_valid_spec` in `app/services/spec_json.py`): entity names are aligned with concepts in the source text, empty or malformed specifications are repaired, and a canonical schema is stored on `TechnicalSpecification` (raw text, structured JSON, prompt name/version, model, provider).

A **specification builder** can also instantiate the same JSON schema from the requirement using heuristic and concept grounding. That path is used when a fast, deterministic PlantUML mapping is preferred (interactive runs that skip the ensemble, and the 200-diagram structural-acceptance benchmark).

### 4.3 Stage 2 — PlantUML synthesis

The specification is converted to PlantUML with a type-specific prompt:

| Diagram | Prompt | Typical contents |
|---------|--------|------------------|
| Class | `tech_spec_to_class.v1.txt` | Classes, attributes, operations, associations, generalization |
| Object | `tech_spec_to_object.v1.txt` | Named instances, slots, links |
| Component | `tech_spec_to_component.v1.txt` | Components, provided/required interfaces, dependencies |
| Package | `tech_spec_to_package.v1.txt` | Nested packages and `..>` dependencies |

Three generators can produce the script:

1. **Specification builder** (`plantuml_from_spec`) — deterministic mapping from JSON to PlantUML; used for structural fidelity and the 200/200 acceptance study.
2. **Fine-tuned code model** — MLX LoRA on Qwen2.5-0.5B-Instruct-4bit (`models/uml-plantuml-lora/`), trained on an assembled Hugging Face UMLCode corpus of about 8,000 specification–PlantUML pairs.
3. **Reasoning code model** — DeepSeek-R1-Distill-Qwen-32B with chain-of-thought prompting, as specified in the paper. Private reasoning is stripped before display; only the final `@startuml` … `@enduml` block is kept (`app/services/cot.py`).

The orchestrator records which generator was used. An **adaptation memory** (`app/services/adaptation.py`) stores, per diagram type, which generator and repair strategy succeeded, so later runs can prefer winning strategies.

`ensure_faithful_plantuml` checks that the script still reflects the specification (entity coverage, diagram-type conventions) before rendering.

### 4.4 Validation, repair, and render

Before an image is produced, the pipeline applies a layered **acceptance stack** (`app/services/acceptance.py`):

1. **Syntax** — well-formed PlantUML bounds and diagram-type keywords (`plantuml_validate`).
2. **Compile** — PlantUML `-checkonly` when a local Java runtime is available.
3. **Render** — PNG via `uml_pipeline/render.py` (local `tools/plantuml.jar` or the PlantUML HTTP server).
4. **UML structure** — type-specific rules (`uml_structure.py`), including package nesting.
5. **Semantics / traceability** — entities and relations in the diagram must be accountable to the requirement (`traceability.py`). Specification–code **fidelity** is reported alongside.

If a gate fails, **repair** runs (maximum three attempts, `prompts/repair_plantuml.v1.txt`): the model receives the failing script, the error, and the specification, and returns a corrected script. Each attempt is stored as `RepairAttempt`. Each render try is stored as `RenderAttempt`.

**Render is a hard quality gate.** If the diagram does not render, the composite score **S** is defined to be 0 and the sample is not dataset-accepted.

### 4.5 Stage 3 — Multimodal verification

When scoring is requested, the PNG is sent to three vision-language models with `prompts/vlm_scoring.v1.txt`. The prompt asks the model to judge the **image against the original requirement** on four criteria (0–6):

1. Semantic correctness  
2. Structural completeness  
3. Syntactic accuracy  
4. Overall coherence  

The overall score is the rounded average of the four criteria. Explanations are stored with each `ModelScore`.

| Ensemble member | MMMU weight |
|-----------------|------------:|
| Qwen2.5-VL-3B-Instruct | 53.1 |
| Llama-3.2-11B-Vision-Instruct | 50.7 |
| Aya-Vision-8B | 39.9 |

**Composite score** (`app/services/scoring.py`):

\[
S_i = \delta_i \cdot \frac{\sum_{j=1}^{3} w_j s_{ij}}{\sum_{j=1}^{3} w_j}
\]

where \(\delta_i = 1\) if rendering succeeded and \(0\) otherwise. Worked example (render OK; scores 5, 4, 3): \(S \approx 4.09\).

**Majority gate:** a model votes yes if \(s_{ij} \ge \tau\) (\(\tau = 4\)). \(A_i = 1\) if at least two models vote yes.

**Dataset entry:** render success **and** \(A_i = 1\) **and** \(S_i \ge 3\). The UML acceptance stack may still record structural or semantic notes on the artifact.

Interactive Generate can omit Stage 3 (`skip_vlm`) so the user obtains a diagram and acceptance report first; **Rescore** on the gallery later runs the ensemble on the stored PNG.

---

## 5. User interface

The Streamlit app is the primary way to operate the system. The sidebar lists eight pages.

### 5.1 Home (Dashboard)

`ui/streamlit_app.py` is the landing page. It checks API health and analytics, then shows:

- live counts of artifacts, dataset-accepted samples, majority-accepted samples, and the active provider summary;
- four panels for Generate, Batch, Generated Diagrams, and System Design;
- a three-step usage path: write a requirement, choose a diagram type, inspect quality.

If the API is unreachable, the page explains how to start it (`./scripts/run_local.sh` or `make run`) and stops rather than showing empty tools.

### 5.2 Single Generation

`ui/pages/2_Single_Generation.py` is the main authoring surface.

- **Input type:** requirement paragraph or source code.  
- **Optional examples** fill the text area; the user may replace them entirely.  
- **Diagram type:** class, object, component, or package (one or several in one background job).  
- **Score with VLMs:** when enabled, Stage 3 runs after a successful render.  
- **Generate** enqueues `POST /api/generate` with `async_mode=true`. A banner shows job status (pending / running / completed).  

When the job finishes, the page presents the **artifact trace**:

- rendered PNG;  
- source requirement and technical specification;  
- PlantUML listing;  
- validation and acceptance summary;  
- per-model scores, composite **S**, majority **A**, dataset-accepted flag;  
- repair history if repairs occurred.

The user can stay on other pages while generation continues; the job tracker restores results when they return.

### 5.3 Batch Generation

`ui/pages/3_Batch_Generation.py` builds evaluation sets.

- Number of sample requirements (1–200, default 50).  
- Multiselect of diagram types (default: all four).  
- Optional custom sentence (creates *n* variants) or the built-in file `sample_data/requirements.txt`.  
- Preview of sample sentences via `GET /api/samples`.  
- Estimated artifact count = *n* × number of types (50 × 4 = 200).  

**Start batch job** calls `POST /api/generate/batch`. Progress is shown as completed/total. When finished, the user opens Generated Diagrams or Analytics.

### 5.4 Generated Diagrams (gallery)

`ui/pages/4_Generated_Diagrams.py` is the library of every stored diagram.

Filters: search in the requirement text, diagram type, render status, and acceptance (dataset accepted / majority OK / not accepted). Results are paginated.

Selecting a card opens:

- full PNG;  
- requirement, specification, PlantUML;  
- scores and gates;  
- **Rescore** (`POST /api/artifacts/{id}/rescore`);  
- **Repair** (`POST /api/artifacts/{id}/repair`);  
- **Generate another type** from the same requirement (class / object / component / package) as a new background job.

This page is the working archive for demos, human review sampling, and dataset inspection.

### 5.5 Human Evaluation

`ui/pages/5_Human_Evaluation.py` implements the paper rubric in the application.

The page displays `prompts/human_evaluation_rubric.v1.txt`, lists artifacts, shows the requirement excerpt, and collects:

- reviewer name and role (expert, student, advisor, author);  
- four sliders (1–5): semantic correctness, structural completeness, syntactic accuracy, overall coherence;  
- free-text comments.

**Save evaluation** posts `POST /api/human-review`. The mean of the four dimensions is stored. Analytics can later report correlation between human means and composite **S**.

### 5.6 Analytics

`ui/pages/6_Analytics.py` summarizes the database:

- counts: artifacts, render outcomes, package-related flags, majority accepted, dataset accepted;  
- human–AI correlation when reviews exist;  
- bar charts of composite **S** overall and by diagram type;  
- self-adaptation generator win rates;  
- repair attempt and success counts;  
- download links for JSONL, CSV, and Parquet export.

### 5.7 Settings

`ui/pages/7_Settings.py` is the operations view:

- API base URL and raw health JSON (`GET /api/settings/health`);  
- provider mode (mock, Ollama, Hugging Face, LoRA);  
- Java / PlantUML availability;  
- artifact counts and mean composite;  
- adaptation memory (which generator succeeded per diagram type).

Health is the place to confirm that models and rendering are configured before a demo.

### 5.8 System Design

`ui/pages/8_System_Design.py` is in-app documentation: architecture diagram, pipeline, dual-signal verification (**δ**, **A**, **S**), provider routing, storage layout, and local run commands. It is intended for advisors and committee members who open the running UI.

---

## 6. REST API

OpenAPI is served at `/docs`. All mutating generate/export/review routes can require `Authorization: Bearer` or `X-API-Key` when `API_ACCESS_TOKEN` is set.

| Method | Path | Role |
|--------|------|------|
| GET | `/` | Name, docs, health links |
| POST | `/api/generate` | Single or multi-type generation (async by default) |
| POST | `/api/generate/batch` | Cartesian product of requirements × types |
| GET | `/api/samples` | Preview built-in requirement sentences |
| GET | `/api/jobs/{id}` | Job status, progress, error |
| GET | `/api/jobs/{id}/artifacts` | Artifacts produced by a job |
| GET | `/api/artifacts` | List summaries |
| GET | `/api/artifacts/library` | Paginated gallery with filters |
| GET | `/api/artifacts/{id}` | Full trace |
| GET | `/api/artifacts/{id}/image` | PNG bytes |
| GET | `/api/artifacts/{id}/plantuml` | PlantUML text |
| POST | `/api/artifacts/{id}/rescore` | Re-run the VLM ensemble |
| POST | `/api/artifacts/{id}/repair` | Additional repair + render |
| POST | `/api/human-review` | Store a human rubric rating |
| GET | `/api/analytics/summary` | Aggregate metrics |
| GET | `/api/analytics/distributions` | Score histograms |
| GET | `/api/analytics/package-failures` | Package-oriented breakdown |
| GET | `/api/export/dataset` | `fmt=jsonl\|csv\|parquet` |
| GET | `/api/adaptation/status` | Generator/strategy memory |
| GET | `/api/settings/health` | Providers, Java, PlantUML, tokens |

Synchronous generate (`async_mode=false`) is used by tests and scripts and returns the artifact in the same HTTP response. The UI uses async jobs so navigation does not cancel work.

---

## 7. Data model

SQLModel tables in `app/models.py`, default engine SQLite `data/uml_app.db` (Postgres via `DATABASE_URL`).

| Table | Role |
|-------|------|
| Project | Named workspace (default “UML-Pipeline”) |
| GenerationJob | pending / running / completed / failed; total and completed counts |
| RequirementInput | Raw text and diagram type |
| TechnicalSpecification | Spec text, JSON, prompt and model metadata |
| UMLArtifact | Central row: PlantUML, image path, **S**, **A**, dataset flag, input mode, models |
| RenderAttempt | Per-try render log |
| RepairAttempt | Before/after PlantUML |
| ModelScore | One row per VLM |
| CompositeScore | Snapshot of **S**, votes, formula |
| Reviewer | Human rater identity |
| HumanReview | Four rubric integers and comments |
| PromptTemplate | Optional DB copy of prompts |
| SystemConfig | Key/value runtime flags |

Images are files; the database stores paths. Sidecar JSON can record acceptance and adaptation details next to the PNG.

---

## 8. Model providers

`app/providers/factory.py` selects backends from `.env` without changing orchestration.

| Mode | Typical flags | Use |
|------|-----------------|-----|
| Mock | `MOCK_PROVIDERS=true` | Deterministic specs, PlantUML, and scores for offline demos and tests |
| Ollama | `USE_OLLAMA=true` | Local Llama 3.2 1B for specs; Qwen2.5-VL and Llama-3.2-Vision for scoring |
| Hugging Face Inference | `USE_HF_INFERENCE=true` + `HF_TOKEN` | Cloud paper model IDs |
| OpenAI-compatible | `OPENAI_API_KEY` + `OPENAI_BASE_URL` | Hosted APIs or vLLM |
| Fine-tuned PlantUML | `USE_FINETUNED_CODE=true` | MLX LoRA adapter for the code stage |
| Aya-Vision-8B | `USE_AYA` and `VLM_AYA_BACKEND` | Third ensemble member: local transformers, HF, or vLLM (`openai_compat`) |

Paper model identifiers remain stable (`SPEC_MODEL`, `CODE_MODEL`, `VLM_MODELS`). Ollama tags and Hugging Face repo IDs are mapped automatically.

Rendering uses `PLANTUML_REMOTE` and `PLANTUML_PREFER_LOCAL`. Local Java plus `tools/plantuml.jar` is preferred when available; otherwise the public PlantUML server produces the PNG.

---

## 9. Prompts and rubrics

All generation and scoring text is file-backed so the paper method can be versioned independently of Python code.

| File | Role |
|------|------|
| `requirement_to_tech_spec.v1.txt` | Requirement → JSON spec |
| `code_to_tech_spec.v1.txt` | Source code → JSON spec |
| `tech_spec_to_class.v1.txt` | Spec → class PlantUML |
| `tech_spec_to_object.v1.txt` | Spec → object PlantUML |
| `tech_spec_to_component.v1.txt` | Spec → component PlantUML |
| `tech_spec_to_package.v1.txt` | Spec → package PlantUML |
| `tech_spec_to_flowchart.v1.txt` | Spec → activity/flowchart (prompt library) |
| `repair_plantuml.v1.txt` | Repair loop |
| `vlm_scoring.v1.txt` | Image + requirement → four criteria and SCORE |
| `human_evaluation_rubric.v1.txt` | Human 1–5 rubric shown in the UI |

---

## 10. Sample data and training

- `sample_data/requirements.txt` — 50 one-sentence system prompts used by batch generation and the 200-diagram acceptance benchmark.  
- `sample_data/sample_code.py` — example source for code-to-UML.  
- `scripts/build_training_corpus.py` — assembles about 8,000 public Hugging Face UMLCode pairs for LoRA.  
- `scripts/finetune_plantuml.py` / `make finetune` — trains the Qwen2.5-0.5B LoRA adapter used by Stage 2.

The 8,000-row corpus trains the PlantUML generator. Dataset membership for *application* outputs is decided at generation time by render, **A**, and **S**, not by corpus membership alone.

---

## 11. Analytics, adaptation, and export

**Analytics** compute, from SQLite: total artifacts, mean **S**, render and package flags, majority and dataset rates, repair statistics, score histograms by type, and Pearson correlation between human overall ratings and **S** when both exist.

**Self-adaptation** records generator and repair outcomes per diagram type in `data/adaptation_memory.json` (and the Settings/Analytics views). Subsequent runs can prefer strategies with higher success rates.

**Export** writes each artifact as a record suitable for further analysis or Hugging Face-style release: requirement, diagram type, specification, PlantUML, scores, **S**, **A**, dataset flag, and image path.

---

## 12. Configuration, tests, and how to run

Principal environment variables (see `.env.example`): `MOCK_PROVIDERS`, `USE_OLLAMA`, `USE_HF_INFERENCE`, `USE_FINETUNED_CODE`, `USE_AYA`, `SPEC_MODEL`, `CODE_MODEL`, `VLM_MODELS`, `ACCEPTANCE_TAU`, `MIN_COMPOSITE_FOR_DATASET`, `PLANTUML_REMOTE`, `API_ACCESS_TOKEN`, `HF_TOKEN`.

**Local start:**

```bash
./scripts/run_local.sh
# or
make run
```

- UI: http://127.0.0.1:8501  
- API: http://127.0.0.1:8000/docs  

**Tests:** `make test` — scoring (render ⇒ \(S=0\), majority, dataset gate), spec JSON, PlantUML-from-spec, validators, API, security, VLM parse, acceptance.

**Containers:** `Dockerfile` and `docker-compose.yml` (API 8000, UI 8501). **Render:** `render.yaml` (API + UI services). **Cloud GPU for Aya:** `scripts/deploy_aya_vllm_gcp.sh`.

---

## 13. Typical usage path

1. Start the API and UI. Confirm Settings health.  
2. Open **Generate**, type a requirement, choose a diagram type, run the job.  
3. Inspect the PNG, specification, PlantUML, **S**, **A**, and dataset flag.  
4. Open **Generated Diagrams** to rescore or generate the other three types from the same text.  
5. Optionally rate the diagram on **Human Evaluation**.  
6. Use **Batch** for 50 × 4 evaluation sets.  
7. Inspect **Analytics** and export JSONL/CSV/Parquet.  
8. Use **System Design** when explaining the architecture.

---

## 14. Role of the application in the paper

UML-Pipeline is the operational form of the three-stage method:

- Stage 1 — Llama-3.2-1B-Instruct specification;  
- Stage 2 — PlantUML via specification builder, LoRA, and/or DeepSeek-R1-32B;  
- Stage 3 — Qwen2.5-VL-3B, Llama-3.2-11B-Vision, and Aya-Vision-8B, combined as **S** and **A**.

The specification-builder path has been measured at **200/200** full-pipeline acceptance on `sample_data/requirements.txt` × four types, with golden 6/6 and 5/5 true negatives on controls (`reports/acceptance_eval.md`). Live ensemble tables and human alignment use the same application: gallery sampling, Human Evaluation, and dataset export.

---

## 15. Project layout

```
app/            FastAPI, models, providers, orchestration, routers, jobs
ui/             Streamlit multipage interface
uml_pipeline/   Render, scoring helpers, LLM client
prompts/        Versioned templates
sample_data/    Requirements and sample source
tests/          Unit and API tests
data/           SQLite, artifacts, training (runtime)
models/         LoRA adapters
scripts/        Run, corpus, fine-tune, deploy, eval
paper/          LaTeX working copy
docs/           Design and reports
```

---

*UML-Pipeline — Department of Computer Engineering and Computer Science, California State University, Long Beach · 20 August 2026*
