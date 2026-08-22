#!/usr/bin/env python3
"""10–15 page combined thesis + application report (no course codes or calendar dates)."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "Thesis_and_Application_Report.pdf"

INK = colors.HexColor("#14212b")
ACCENT = colors.HexColor("#0f766e")
LIGHT = colors.HexColor("#f3efe6")
LINE = colors.HexColor("#d5cfc2")
MUTED = colors.HexColor("#3a4a57")


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "T", parent=base["Title"], fontName="Helvetica-Bold", fontSize=16,
            leading=20, textColor=INK, alignment=TA_CENTER, spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "S", parent=base["Normal"], fontName="Helvetica", fontSize=10.5,
            leading=14, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4,
        ),
        "meta": ParagraphStyle(
            "M", parent=base["Normal"], fontSize=9, leading=12,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=12.5,
            leading=16, textColor=ACCENT, spaceBefore=12, spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=10.5,
            leading=13, textColor=INK, spaceBefore=8, spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=9.8,
            leading=12, textColor=INK, spaceBefore=6, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "B", parent=base["Normal"], fontName="Helvetica", fontSize=9.3,
            leading=12.3, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bu", parent=base["Normal"], fontName="Helvetica", fontSize=9.0,
            leading=11.8, textColor=INK,
        ),
        "cell": ParagraphStyle(
            "C", parent=base["Normal"], fontName="Helvetica", fontSize=7.8,
            leading=10.3, textColor=INK,
        ),
        "cellh": ParagraphStyle(
            "CH", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=7.8,
            leading=10.3, textColor=colors.white,
        ),
        "caption": ParagraphStyle(
            "Cap", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=8,
            leading=10, textColor=MUTED, spaceAfter=8, spaceBefore=2,
        ),
        "toc": ParagraphStyle(
            "TOC", parent=base["Normal"], fontName="Helvetica", fontSize=10,
            leading=14, textColor=INK, leftIndent=8, spaceAfter=2,
        ),
    }


def bullets(items, style):
    return ListFlowable(
        [ListItem(Paragraph(i, style), leftIndent=8, bulletColor=ACCENT) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=12,
    )


def P(text, st):
    return Paragraph(text, st)


def table(rows, col_widths, header=True):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    cmds = [
        ("FONTSIZE", (0, 0), (-1, -1), 7.8),
        ("BACKGROUND", (0, 1 if header else 0), (-1, -1), LIGHT),
        ("TEXTCOLOR", (0, 1 if header else 0), (-1, -1), INK),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        cmds.extend([
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ])
    t.setStyle(TableStyle(cmds))
    return t


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(0.7 * inch, 0.5 * inch, letter[0] - 0.7 * inch, 0.5 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#5a6a75"))
    canvas.drawString(0.7 * inch, 0.34 * inch, "Thesis and Application Report — UML-Pipeline")
    canvas.drawRightString(letter[0] - 0.7 * inch, 0.34 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    s = styles()
    c, h = s["cell"], s["cellh"]
    story = []

    story.append(P("Thesis and Application Report", s["title"]))
    story.append(P(
        "Automated UML Dataset Generation from Natural-Language Requirements<br/>"
        "with Multimodal Verification for Software Design",
        s["subtitle"],
    ))
    story.append(P(
        "Student: Dipak Yadav &nbsp;·&nbsp; Advisor: Dr. Yutong Zhao<br/>"
        "California State University, Long Beach<br/>"
        "Code: https://github.com/dipak5501/uml-generation-pipeline",
        s["meta"],
    ))

    story.append(P("Contents", s["h1"]))
    for line in [
        "1. Abstract",
        "2. Problem, motivation, and research goal",
        "3. Thesis contributions and research questions",
        "4. Related positioning",
        "5. Thesis method: three-stage pipeline",
        "6. Scoring, majority vote, and dataset gate",
        "7. Design-phase UML types",
        "8. Manuscript evaluation (paper figures)",
        "9. The UML-Pipeline application",
        "10. System design and modules",
        "11. Features (UI, API, quality, LAN, Colab)",
        "12. Training and evaluation data",
        "13. Measured results from this implementation",
        "14. Thesis versus application (alignment)",
        "15. Limitations, threats, and remaining work",
        "16. Conclusion",
    ]:
        story.append(P(line, s["toc"]))

    story.append(PageBreak())

    # 1
    story.append(P("1. Abstract", s["h1"]))
    story.append(P(
        "This report describes both the thesis research and the software that implements it. "
        "The thesis addresses a practical gap in AI for software engineering: large language "
        "models can draft UML from text, but drafts are often invalid or semantically wrong, "
        "and there is no scalable way to verify diagrams for a research-quality dataset. "
        "The proposed method is a three-stage pipeline. Stage 1 converts a natural-language "
        "requirement (or source code) into a structured technical specification using a small "
        "instruction-tuned language model (LLaMA 3.2-1B-Instruct). Stage 2 synthesizes PlantUML "
        "for class, object, component, and package diagrams using a reasoning code model "
        "(DeepSeek-R1-Distill-Qwen-32B in the paper; a local LoRA adapter plus a spec-faithful "
        "builder in the on-device application). Stage 3 renders PlantUML to an image. A failed "
        "render forces composite score S = 0. Three vision–language models score each image "
        "from 0 to 6 on semantic correctness, structural completeness, syntactic accuracy, and "
        "overall coherence. Scores are combined with MMMU weights 53.1, 50.7, and 39.9. A "
        "majority-vote gate A (threshold τ = 4, at least two models) plus S ≥ 3 decides dataset "
        "inclusion.",
        s["body"],
    ))
    story.append(P(
        "The UML-Pipeline application is the runnable realization of that method: FastAPI and "
        "Streamlit, SQLite persistence, PlantUML rendering, dual-Ollama local VLMs, optional "
        "Aya-Vision-8B weights, adaptive repair, multi-layer acceptance, and a gallery that can "
        "spawn another diagram type from the same input. This report separates manuscript "
        "evaluation figures from numbers measured on the current code, and states limitations "
        "honestly (local Stage 2 is not always the 32B model; human-alignment study is specified "
        "in the UI but not yet executed; free Colab GPUs can score Qwen2.5-VL-3B only).",
        s["body"],
    ))

    # 2
    story.append(P("2. Problem, motivation, and research goal", s["h1"]))
    story.append(P(
        "Unified Modeling Language diagrams are a standard design-phase artifact. They communicate "
        "types, instances, components, and module structure to developers and reviewers. Producing "
        "them by hand is slow, inconsistent across engineers, and expensive to scale for dataset "
        "construction. Organizations that want machine-learning models for software design need "
        "paired examples of requirements, specifications, diagrams, and quality labels. Those "
        "pairs are scarce compared with source-code corpora.",
        s["body"],
    ))
    story.append(P(
        "Recent language models can emit PlantUML or similar notations from a paragraph. Generation "
        "alone is not enough. Typical failure modes include: empty or unrenderable diagrams; the "
        "wrong UML type (for example a class diagram when a package diagram was requested); invented "
        "names that do not appear in the requirement (hallucination); omitted domain entities "
        "(low recall); illegal nesting or dependency arrows in package diagrams; and fluent text "
        "that looks plausible to a reader who does not check the image. A pipeline that only "
        "generates therefore pollutes any downstream dataset.",
        s["body"],
    ))
    story.append(P(
        "The thesis goal is to treat generation and verification as one system. Input is a "
        "requirement or source file. Output is a technical specification, PlantUML, a rendered "
        "PNG when compilation succeeds, a continuous quality score S, a binary majority decision "
        "A, and a dataset-accepted flag. The research product is both a method (dual LLM + VLM "
        "ensemble + render gate) and a public implementation that others can rerun.",
        s["body"],
    ))
    story.append(P(
        "Elevator statement of the thesis: automatically generate design-phase UML from "
        "natural-language requirements using a dual-LLM pipeline, then verify each diagram with "
        "an ensemble of vision–language models and MMMU-weighted scoring so the resulting dataset "
        "is both large and quality-controlled.",
        s["body"],
    ))

    # 3
    story.append(P("3. Thesis contributions and research questions", s["h1"]))
    story.append(P("3.1 Contributions", s["h2"]))
    story.append(bullets([
        "A decomposed three-stage pipeline: specification, PlantUML synthesis, render and multimodal verification.",
        "MMMU-weighted composite scoring with an explicit render-failure indicator (failed PNG ⇒ S = 0).",
        "A majority-vote acceptance gate on top of continuous scores, used as a dataset filter together with S ≥ 3.",
        "Restriction to design-phase UML types (class, object, component, package), matching the paper scope.",
        "Public code (UML-Pipeline) so the method is inspectable and locally runnable.",
        "Engineering additions required for reliability: JSON spec validity, grounded builders, adaptive repair, traceability checks. These support the thesis claims; they are not a replacement for the paper models.",
    ], s["bullet"]))
    story.append(P("3.2 Questions the work is designed to answer", s["h2"]))
    story.append(bullets([
        "Can a small spec model plus a code/reasoning model produce renderable UML from free-form requirements at useful scale?",
        "Does a three-VLM ensemble with unequal MMMU weights provide a more stable quality signal than a single scorer?",
        "Does majority vote at τ = 4, combined with S ≥ 3, reject empty, hallucinated, or type-wrong diagrams while keeping strong class diagrams?",
        "Which diagram type remains hardest (the paper and this implementation both point to package, then object)?",
        "How closely can a local application (LoRA + builder + Ollama) reproduce the paper method when DeepSeek-R1-32B is not on the laptop?",
    ], s["bullet"]))

    # 4
    story.append(P("4. Related positioning", s["h1"]))
    story.append(P(
        "Prior UML-from-text systems typically optimize generation: prompt a model, maybe repair "
        "syntax, and stop. Program-comprehension tools recover class diagrams from source but do "
        "not start from natural language and do not score the image. Multimodal benchmarks such as "
        "MMMU measure general visual reasoning; this thesis reuses those published scores as "
        "weights, not as a claim that UML scoring is MMMU. The distinctive combination here is "
        "(i) a two-model generation split (extract then reason), (ii) render-as-hard-gate, "
        "(iii) three VLMs looking at the actual diagram image against the specification, and "
        "(iv) dual output (S and A) for dataset construction. The application adds deterministic "
        "gates so that VLMs are not the only filter for empty PlantUML.",
        s["body"],
    ))
    story.append(P(
        "Compared with syntax-only linters, PlantUML compile is necessary but not sufficient: a "
        "diagram can compile and still omit Book and Member or invent UnicornLauncher. Compared "
        "with asking a text-only LLM to “grade” PlantUML source, VLMs see layout, missing boxes, "
        "and wrong arrow heads as they appear to a designer. Compared with a single VLM, unequal "
        "MMMU weights give more influence to the stronger generalist (Qwen 3B at 53.1) without "
        "dropping the other two votes required for majority A. The application still runs "
        "traceability in software so that dataset gating does not depend only on stochastic scores.",
        s["body"],
    ))
    story.append(P(
        "Scope exclusions are deliberate. The work does not claim automatic generation of legal "
        "sequence diagrams, SysML, or architecture decision records. It does not claim that LoRA "
        "0.5B equals DeepSeek-R1-32B. It does not claim that Colab T4 scoring is the paper "
        "ensemble. Those distinctions keep the thesis falsifiable.",
        s["body"],
    ))

    # 5
    story.append(P("5. Thesis method: three-stage pipeline", s["h1"]))
    story.append(P("5.1 Stage 1 — Technical specification", s["h2"]))
    story.append(P(
        "Paper model: LLaMA 3.2-1B-Instruct. The task is information extraction and organization, "
        "not long-horizon reasoning, so a small open model is appropriate. Input is a free-form "
        "requirement. Output is a structured specification: summary, entities (name, kind, "
        "attributes, methods), relationships (source, target, type, optional label), and "
        "type-specific fields (components and interfaces; packages and containment; objects and "
        "slots). The application stores this as JSON, runs validity checks, and merges names "
        "harvested from the text (verb–object patterns, actors such as “Customers can…”, shopping "
        "cart, and so on) so Stage 2 is not starved of domain vocabulary. Source-code mode uses "
        "structural analysis. Scripts with no class or type declarations are not turned into "
        "invented UML classes.",
        s["body"],
    ))
    story.append(P("5.2 Stage 2 — PlantUML synthesis", s["h2"]))
    story.append(P(
        "Paper model: DeepSeek-R1-Distill-Qwen-32B, prompted to reason (chain-of-thought style) "
        "and then emit only PlantUML. Diagram types are class, object, component, and package. "
        "Sequence, use-case, deployment, and activity/flowchart are out of product scope; the "
        "application’s UML structure rules reject sequence as a product type.",
        s["body"],
    ))
    story.append(P(
        "Local application path: an MLX LoRA adapter on Qwen2.5-0.5B-Instruct-4bit trained on "
        "open Hugging Face UMLCode PlantUML pairs, plus a deterministic spec-faithful builder. "
        "The 0.5B adapter is class-heavy. Component and package therefore default to the grounded "
        "builder until LoRA has enough proven samples. If LoRA emits empty @startuml/@enduml, the "
        "builder result is kept. Adaptive repair (at most three attempts) applies category-specific "
        "strategies: sanitize syntax, inject missing names, strip hallucinations, rebuild from spec, "
        "targeted LLM edit. Empty repair output is discarded.",
        s["body"],
    ))
    story.append(P("5.3 Stage 3 — Render and multimodal verification", s["h2"]))
    story.append(P(
        "PlantUML is compiled (including -checkonly) and rendered to PNG via a local JAR when Java "
        "is present, or a remote PlantUML server. Layout is not scored as a separate aesthetic "
        "model; unreadable or missing images score 0. Three VLMs receive the image and the "
        "specification and must answer SCORE: integer 0–6 and EXPLANATION covering the four "
        "criteria. Paper models and MMMU weights: Qwen2.5-VL-3B (53.1), LLaMA-3.2-11B-Vision (50.7), "
        "Aya-Vision-8B (39.9). Local runtimes: Qwen on Ollama 0.32, LLaMA-Vision on Ollama 0.24 "
        "(two Ollama versions because one binary cannot host both architectures), Aya via local "
        "Hugging Face weights or an OpenAI-compatible GPU server. Scoring always invokes all three "
        "providers when they are configured; a failed provider is marked unavailable (None) so it "
        "does not drag S to zero as a fake numeric 0.",
        s["body"],
    ))

    story.append(PageBreak())

    # 6
    story.append(P("6. Scoring, majority vote, and dataset gate", s["h1"]))
    story.append(P(
        "Let s_j be the integer score of model j and w_j its MMMU weight. If rendering fails, "
        "S = 0. Otherwise S = Σ(w_j · s_j) / Σ(w_j) over models with a numeric score (unavailable "
        "models omitted). Majority: v_j = 1 if s_j ≥ τ, else 0, with default τ = 4. A = 1 if "
        "Σ v_j ≥ 2. Dataset entry requires render success, A = 1, and S ≥ 3.0. This dual signal "
        "lets analysis use a continuous quality number while dataset construction uses a hard gate.",
        s["body"],
    ))
    story.append(table(
        [
            [P("Signal", h), P("Definition", h), P("Role", h)],
            [P("Render gate δ", c), P("PNG produced", c), P("δ = 0 ⇒ S = 0; artifact not dataset-accepted", c)],
            [P("Per-model s_j", c), P("Integer 0–6 from VLM text protocol", c), P("Four-criterion rubric vs specification", c)],
            [P("Composite S", c), P("MMMU-weighted mean of available s_j", c), P("Continuous quality; thesis tables", c)],
            [P("Majority A", c), P("≥2 models with s_j ≥ 4", c), P("Pass/fail for inclusion", c)],
            [P("Dataset flag", c), P("δ ∧ A ∧ (S ≥ 3)", c), P("Export filter /api/export/dataset", c)],
        ],
        [1.4 * inch, 2.6 * inch, 3.1 * inch],
    ))
    story.append(P("Table 1. Verification signals implemented in app/services/scoring.py.", s["caption"]))
    story.append(P(
        "Human evaluation in the application uses the same four criteria so that a later "
        "correlation study (Pearson r between mean human score and S; agreement among raters) "
        "can be attached without changing the rubric. That study is specified, not completed.",
        s["body"],
    ))

    # 7
    story.append(P("7. Design-phase UML types", s["h1"]))
    story.append(P(
        "The thesis and the application generate four types only. This matches the paper’s "
        "design-phase focus and avoids mixing behavioral sequence charts or UI flowcharts into "
        "the same scoring protocol.",
        s["body"],
    ))
    story.append(table(
        [
            [P("Type", h), P("Design question it answers", h), P("PlantUML sketch", h), P("Known difficulty", h)],
            [P("Class", c), P("What types exist, with fields, operations, and relations?", c),
             P("class Name { … } ; --|&gt; *-- o-- --&gt;", c),
             P("Strongest in paper and LoRA; default generate type", c)],
            [P("Object", c), P("What instances and links exist in a snapshot?", c),
             P('object "x" as x { slot = v }', c),
             P("Weaker NL render rate in bulk tests", c)],
            [P("Component", c), P("What deployable/logical parts and interfaces?", c),
             P("[Name] ; () \"IName\" ; ..&gt;", c),
             P("LoRA was empty; spec-builder is the local default", c)],
            [P("Package", c), P("How are types grouped; who depends on whom?", c),
             P("package P { … } ; ..&gt;", c),
             P("Hardest in the paper (~18.9% failure); nesting/dependency errors", c)],
        ],
        [0.95 * inch, 2.15 * inch, 1.9 * inch, 2.1 * inch],
    ))
    story.append(P("Table 2. Product UML types.", s["caption"]))
    story.append(P(
        "Component generation was a concrete application defect: LoRA plus a name filter could "
        "emit a blank diagram. The builder now never emits zero components; noun harvest includes "
        "actors and verb objects. An e-commerce requirement produced Cart, Product, Order, Payment, "
        "and related components with successful render and UML acceptance.",
        s["body"],
    ))

    # 8
    story.append(P("8. Manuscript evaluation (paper figures)", s["h1"]))
    story.append(P(
        "The following figures are the evaluation story reported for the research paper. They "
        "must not be presented as live measurements of the current laptop run unless regenerated "
        "from a frozen code snapshot.",
        s["body"],
    ))
    story.append(table(
        [
            [P("Claim in the manuscript", h), P("Reported figure", h)],
            [P("Dataset scale", c), P("About 8,000 samples (2,000 × 4 diagram types)", c)],
            [P("Class diagrams", c), P("About 95.7% render success; Pearson r ≈ 0.82 vs human", c)],
            [P("Package diagrams", c), P("About 18.9% failure; r ≈ 0.55 vs human", c)],
            [P("Human study", c), P("80 experts; Fleiss κ ≈ 0.68; 40 stratified diagrams", c)],
            [P("Failure analysis", c), P("Package errors often nesting vs dependency semantics", c)],
        ],
        [2.6 * inch, 4.5 * inch],
    ))
    story.append(P("Table 3. Paper-reported results (manuscript, not this application’s eval scripts).", s["caption"]))

    story.append(PageBreak())

    # 9
    story.append(P("9. The UML-Pipeline application", s["h1"]))
    story.append(P(
        "UML-Pipeline is a local web application: FastAPI on port 8000 and Streamlit on port 8501, "
        "started with scripts/run_local.sh. Persistence is SQLite (artifacts, jobs, model scores, "
        "repairs, human reviews) plus PNG files. The UI can be opened on this machine or, when "
        "bound to the LAN, on another device on the same Wi-Fi (browser only; compute stays on "
        "the host). Optional Google Colab scoring packs already-rendered PNGs for Qwen2.5-VL-3B "
        "on a free T4; that path does not replace the live three-VLM ensemble.",
        s["body"],
    ))
    story.append(P("9.1 User-facing pages", s["h2"]))
    story.append(table(
        [
            [P("Page", h), P("Purpose", h)],
            [P("Dashboard", c), P("Health, counts, recent activity", c)],
            [P("Generate", c), P("NL or source; one or all four types; Score with VLMs (all three); async jobs", c)],
            [P("Batch", c), P("Sample requirements × types for evaluation-scale runs", c)],
            [P("Generated Diagrams", c), P("Gallery; rescore; generate another UML type from the same input", c)],
            [P("Human Evaluation", c), P("Four-criterion rubric aligned with VLMs", c)],
            [P("Analytics", c), P("S distributions, render rates, package failures, adaptation rates", c)],
            [P("Settings", c), P("Providers, LoRA, VLM backends, health messages", c)],
            [P("System Design", c), P("In-app architecture notes", c)],
        ],
        [1.8 * inch, 5.3 * inch],
    ))
    story.append(P("Table 4. Streamlit pages.", s["caption"]))

    # 10
    story.append(P("10. System design and modules", s["h1"]))
    story.append(P(
        "Clients (Streamlit, optional HTTP) call FastAPI routers. Orchestration "
        "(run_single_generation) executes Stage 1–3, repair, acceptance, scoring, and persist. "
        "A thread-pool job runner keeps the UI responsive. Fine-tuning is offline (make finetune) "
        "and is not on the request path.",
        s["body"],
    ))
    story.append(P(
        "Flow: intake and clip → JSON spec (LLM + grounding) → choose_generator (lora / "
        "spec-builder / llm) → sanitize and validate PlantUML → repair loop → compile/render → "
        "deterministic acceptance → three VLMs unless skip_vlm → apply S and A → SQLite + PNG.",
        s["body"],
    ))
    story.append(table(
        [
            [P("Module", h), P("Responsibility", h)],
            [P("app/routers/generate.py", c), P("POST generate and batch; GET samples", c)],
            [P("app/routers/artifacts.py", c), P("Jobs, library, PNG, PlantUML, rescore, repair", c)],
            [P("app/routers/analytics.py", c), P("Summary, distributions, package failures, export, health, adaptation", c)],
            [P("app/routers/human_review.py", c), P("Four-criterion reviews", c)],
            [P("app/services/orchestration.py", c), P("End-to-end generation and score_image (all three VLMs)", c)],
            [P("app/services/spec_json.py", c), P("JSON validity and NL/code grounding", c)],
            [P("app/services/plantuml_from_spec.py", c), P("Typed builders and fidelity replace", c)],
            [P("app/services/repair.py, adaptation.py", c), P("Category repair; generator/strategy win rates", c)],
            [P("app/services/acceptance.py and uml_structure.py, traceability.py", c),
             P("Syntax, compile, render, UML rules, semantics", c)],
            [P("app/providers/", c), P("Mock, Ollama, HF, OpenAI-compat, MLX LoRA, local Aya", c)],
            [P("prompts/*.v1.txt", c), P("Versioned Stage-1, Stage-2, VLM, repair, human rubric", c)],
        ],
        [2.4 * inch, 4.7 * inch],
    ))
    story.append(P("Table 5. Principal software modules.", s["caption"]))
    story.append(table(
        [
            [P("Stage", h), P("Paper model", h), P("Application runtime", h)],
            [P("Spec", c), P("LLaMA 3.2-1B-Instruct", c), P("Ollama llama3.2:1b; mock; optional HF", c)],
            [P("PlantUML", c), P("DeepSeek-R1-Distill-Qwen-32B", c),
             P("MLX LoRA 0.5B and/or spec-builder; 32B optional remote", c)],
            [P("VLM 1", c), P("Qwen2.5-VL-3B (53.1)", c), P("Ollama qwen2.5vl:3b :11435; or Colab T4 pack", c)],
            [P("VLM 2", c), P("LLaMA-3.2-11B-Vision (50.7)", c), P("Ollama llama3.2-vision:11b :11434", c)],
            [P("VLM 3", c), P("Aya-Vision-8B (39.9)", c), P("Local transformers weights or vLLM openai_compat", c)],
        ],
        [1.2 * inch, 2.4 * inch, 3.5 * inch],
    ))
    story.append(P("Table 6. Model routing.", s["caption"]))

    # 11
    story.append(P("11. Features", s["h1"]))
    story.append(bullets([
        "Two input modes: paragraph requirements and source code (structure-first for long files).",
        "Generate one type or all four; gallery can add missing types from the stored requirement.",
        "Interactive option to skip VLMs for a fast PNG; default scoring runs all three models.",
        "Rescore endpoint and UI buttons for artifacts that were stored with S = 0 because scoring was skipped.",
        "Multi-layer acceptance independent of VLMs (empty body, missing names, hallucinations, bad packages, sequence-as-product).",
        "Self-adaptation memory (data/adaptation_memory.json) preferring winning generators and repair strategies.",
        "Dataset export filtered by majority A and S ≥ 3.",
        "Optional API_ACCESS_TOKEN for LAN or public deploy.",
        "LAN bind (0.0.0.0) so another device on the same Wi-Fi can open the host’s Streamlit URL.",
        "Colab export (scripts/export_colab_pack.py) and notebook notebooks/colab_vlm_score.ipynb for Qwen-on-T4.",
        "Mock providers so the UI runs without GPUs for demonstrations of flow, not of S.",
    ], s["bullet"]))

    story.append(PageBreak())

    # 12
    story.append(P("12. Training and evaluation data", s["h1"]))
    story.append(P("12.1 Training (LoRA / corpus scripts)", s["h2"]))
    story.append(P(
        "scripts/build_training_corpus.py targets about 8,000 rows from open Hugging Face UMLCode "
        "sets (class RAW; object, component, and package scored; mixed UC/class/sequence filtered "
        "to paper types; optional activity/deployment only as fill). Local supplements: 1,000 "
        "natural-language scenarios across 20 domains and 19 languages, and 1,000 source snippets "
        "across 20 programming languages. Fine-tune JSONL lives under data/finetune/. Adapters "
        "land in models/uml-plantuml-lora/. Training files are gitignored; scripts rebuild them.",
        s["body"],
    ))
    story.append(table(
        [
            [P("Hugging Face source (open)", h), P("Type role", h)],
            [P("UMLCode-ClassDiagram-DeepSeek-32B-Reasoning-RAW", c), P("Class pairs", c)],
            [P("UMLCode_ObjectDiagram_Scored", c), P("Object", c)],
            [P("UMLCode_ComponentDiagram_Scored", c), P("Component", c)],
            [P("UMLCode_PackageDiagram_Scored", c), P("Package", c)],
            [P("UMLCode-DeepSeek-32B-Reasoning-UC-Class-Sequence-Scored", c), P("Filtered top-up; sequence dropped", c)],
        ],
        [4.5 * inch, 2.6 * inch],
    ))
    story.append(P("Table 7. Open training sources (scripts/build_training_corpus.py).", s["caption"]))

    story.append(P("12.2 Testing and evaluation sets used by the application", s["h2"]))
    story.append(table(
        [
            [P("Set", h), P("n", h), P("Use", h)],
            [P("Golden cases.json", c), P("6", c), P("Named-entity regression", c)],
            [P("sample_data/requirements.txt × 4 types", c), P("50 × 4 = 200", c), P("Deterministic acceptance benchmark", c)],
            [P("Negative controls", c), P("5", c), P("Must reject empty/missing/hallucination/syntax/sequence", c)],
            [P("Live 3-VLM smoke", c), P("12", c), P("Scorer availability, render, mean S", c)],
            [P("NL scenarios eval", c), P("1,000", c), P("Generate/render; VLM mocked for throughput", c)],
            [P("Code-language eval", c), P("1,000", c), P("Generate/render; VLM mocked", c)],
            [P("Colab pack", c), P("up to 20 newest PNGs", c), P("Qwen-only GPU scoring off-box", c)],
        ],
        [2.4 * inch, 1.5 * inch, 3.2 * inch],
    ))
    story.append(P(
        "Table 8. Evaluation inventory. Mixed-kind runs in the listed campaigns: 6+200+5+12+1000+1000 = 2,223. "
        "The 8,000 HF rows train LoRA; they are not a completed live 3-VLM pass of the UI.",
        s["caption"],
    ))

    # 13
    story.append(P("13. Measured results from this implementation", s["h1"]))
    story.append(P(
        "These numbers come from repository scripts and reports. They are the evidence for the "
        "application, distinct from Table 3.",
        s["body"],
    ))
    story.append(P("13.1 Deterministic acceptance (no VLM)", s["h2"]))
    story.append(P(
        "Path: grounded Stage-1 JSON → PlantUML builder → compile → render → UML rules → "
        "semantic/traceability. Source: reports/acceptance_eval.md.",
        s["body"],
    ))
    story.append(table(
        [
            [P("Set", h), P("Result", h)],
            [P("Golden", c), P("6/6 full-pipeline accepted; mean repair iterations 0.0", c)],
            [P("Benchmark 200", c), P("200/200 generated, compiled, rendered, UML-valid, semantically accepted", c)],
            [P("Negatives", c), P("5/5 correctly rejected; 0 false accepts", c)],
        ],
        [1.8 * inch, 5.3 * inch],
    ))
    story.append(P("Table 9. Acceptance stack (structural/semantic gates, not S).", s["caption"]))

    story.append(P("13.2 Live three-VLM smoke", s["h2"]))
    story.append(table(
        [
            [P("Metric", h), P("Result", h)],
            [P("All 3 scorers available", c), P("12/12", c)],
            [P("Render success", c), P("11/12 (91.7%)", c)],
            [P("Mean S when render succeeded", c), P("≈ 4.93 / 6", c)],
            [P("Wall time (full ensemble, workstation)", c), P("~100–120 seconds per diagram", c)],
            [P("Render failure", c), P("One package diagram; S = 0 by the paper gate", c)],
        ],
        [3.2 * inch, 3.9 * inch],
    ))
    story.append(P("Table 10. data/eval/live_vlm_reliability_summary.json.", s["caption"]))

    story.append(P("13.3 Bulk generate/render (VLM mocked)", s["h2"]))
    story.append(table(
        [
            [P("Set", h), P("n", h), P("Valid UML + PNG", h)],
            [P("Multilingual NL", c), P("1,000", c), P("974 (97.4%)", c)],
            [P("Multi-language source", c), P("1,000", c), P("1,000 (100%)", c)],
        ],
        [2.6 * inch, 1.4 * inch, 3.1 * inch],
    ))
    story.append(P(
        "Table 11. Throughput/render, not dataset-accepted S. Weakest NL type in that run: object.",
        s["caption"],
    ))

    story.append(PageBreak())

    # 14
    story.append(P("14. Thesis versus application (alignment)", s["h1"]))
    story.append(table(
        [
            [P("Thesis element", h), P("In the application?", h), P("Notes", h)],
            [P("Stage 1 small spec LLM", c), P("Yes", c), P("JSON + grounding; heuristic recovery if LLM JSON fails", c)],
            [P("Stage 2 32B reasoner", c), P("Optional / remote", c), P("Local default: LoRA + spec-builder", c)],
            [P("Four UML types", c), P("Yes", c), P("UI and API literals; sequence rejected", c)],
            [P("Render ⇒ S = 0", c), P("Yes", c), P("verify_scores render_ok flag", c)],
            [P("Three VLMs + MMMU weights", c), P("Yes when Score with VLMs is on", c), P("All three providers called; Colab is Qwen-only sidecar", c)],
            [P("Majority A and S ≥ 3", c), P("Yes", c), P("Export and dataset_accepted", c)],
            [P("Human correlation study", c), P("Protocol only", c), P("UI rubric ready; study not run", c)],
            [P("8k scored dataset freeze", c), P("Corpus scripts + partial evals", c), P("Not a full live 3-VLM pass of 8k from this UI", c)],
            [P("Public GitHub", c), P("Yes", c), P("dipak5501/uml-generation-pipeline", c)],
        ],
        [2.1 * inch, 1.7 * inch, 3.3 * inch],
    ))
    story.append(P("Table 12. Alignment matrix. Engineering extras (repair, adaptation, gallery) support reliability.", s["caption"]))
    story.append(P(
        "Honest reading: the application is a complete demonstration of the thesis architecture "
        "and a strong local substitute for Stage 2. It is not, by itself, a reprint of every "
        "manuscript table. Thesis writing still needs a frozen eval snapshot, package-failure "
        "examples, and either a human study or an explicit scope note.",
        s["body"],
    ))

    story.append(P("14.1 Worked example (same requirement, four types)", s["h2"]))
    story.append(P(
        "Requirement (paraphrase of a stored e-commerce case): customers create accounts, browse "
        "products, add items to a shopping cart, place orders, pay, and track deliveries; "
        "administrators manage products and orders. Stage 1 grounding yields names such as "
        "Customer, Account, Product, Cart, Order, Payment, Delivery, Administrator. Class view: "
        "types and associations (Customer to Order, Order to Payment). Object view: instances "
        "cart1, order1 and links. Component view: [Cart], [Order], [Payment] with interfaces "
        "(the path that previously rendered blank). Package view: grouping such as core vs "
        "checkout with dependencies. The gallery action “generate another type from this input” "
        "is how the application keeps those four views on one requirement without retyping. "
        "VLM scoring, when enabled, attaches s_j and S to each view separately because the image "
        "and notation differ even when the spec is shared.",
        s["body"],
    ))

    story.append(P("14.2 HTTP surface (for reproducibility)", s["h2"]))
    story.append(P(
        "Researchers reproducing the application without the UI can call the same orchestration. "
        "POST /api/generate with requirement, diagram_type or diagram_types, input_mode, "
        "async_mode, skip_vlm. Batch generate uses sample lines or a custom sentence. "
        "GET /api/jobs/{id} and /api/jobs/{id}/artifacts poll results. GET /api/artifacts/library "
        "feeds the gallery. POST /api/artifacts/{id}/rescore reruns all three VLMs on a stored PNG. "
        "GET /api/export/dataset applies A and S ≥ 3. GET /api/settings/health reports provider "
        "mix. Optional Bearer API_ACCESS_TOKEN protects mutating routes on a LAN or host.",
        s["body"],
    ))

    story.append(PageBreak())

    story.append(P("14.3 Evaluation protocol recommended for the thesis freeze", s["h2"]))
    story.append(P(
        "To turn application measurements into thesis tables without mixing builder-only numbers "
        "with VLM numbers, a freeze should report four blocks on one tagged commit: (1) golden + "
        "200 + negatives for the acceptance stack; (2) live 3-VLM on a stratified slice (all four "
        "types, NL and source, at least the current 12-run smoke, preferably larger); (3) render "
        "success by type on the 1,000 NL and 1,000 code sets with VLMs mocked, clearly labeled; "
        "(4) if humans are used, the same 40-diagram stratification as the paper, four criteria, "
        "Fleiss κ and Pearson r vs S. Colab Qwen-only CSVs may be an appendix for VLM-1, not a "
        "substitute for the ensemble.",
        s["body"],
    ))

    # 15
    story.append(P("15. Limitations, threats, and remaining work", s["h1"]))
    story.append(P(
        "Deterministic acceptance uses failure categories that also drive repair order: syntax, "
        "compile, render, uml_structure, missing_element, wrong_relationship, hallucinated_entity, "
        "package_hierarchy, and semantic_alignment. Negative controls in eval_acceptance.py encode "
        "the intended rejects: empty PlantUML, names that ignore the requirement, extra invented "
        "types, broken package braces, and sequence diagrams offered as a product type. A thesis "
        "appendix can reprint those five cases as qualitative evidence that the gate is not a "
        "rubber stamp.",
        s["body"],
    ))
    story.append(P(
        "Versioned prompts under prompts/ keep Stage 1 (requirement_to_tech_spec, code_to_tech_spec), "
        "Stage 2 (tech_spec_to_class/object/component/package), VLM scoring, repair, and the human "
        "rubric reproducible. Changing a prompt without bumping the version would silently invalidate "
        "old S values; the v1 suffix is part of the experimental protocol.",
        s["body"],
    ))
    story.append(P("15.1 Limitations", s["h2"]))
    story.append(bullets([
        "On-device Stage 2 is not DeepSeek-R1-32B; LoRA is small and class-skewed.",
        "Three-VLM scoring is slow on a laptop; skipping VLMs stores S as unscored/0 and must not be reported as model quality.",
        "Unavailable VLMs must be None, not numeric 0, or S is biased downward.",
        "Dual Ollama is a local engineering constraint, not a paper contribution.",
        "Colab free GPU cannot host Aya-8B or LLaMA-11B-Vision.",
        "LAN UI sharing does not pool compute; other devices are thin clients.",
        "PlantUML remote render sends diagram text to an HTTP server unless local Java is preferred.",
        "Human-alignment (r, κ) remains a manuscript figure until re-run on this code.",
    ], s["bullet"]))
    story.append(P("15.2 Threats to validity", s["h2"]))
    story.append(P(
        "Construct: VLM scores are proxy labels, not UML expert grades, until correlation is "
        "measured on this build. Internal: golden and 200-case acceptance use the grounded builder "
        "path, which can overstate Stage-2 LLM quality. External: sample requirements are short "
        "English design sentences, not industrial specifications. Conclusion: high acceptance on "
        "the builder path does not imply the 32B model would match those rates, nor the reverse.",
        s["body"],
    ))
    story.append(P("15.3 Remaining work", s["h2"]))
    story.append(bullets([
        "Freeze live 3-VLM + acceptance tables from a tagged commit.",
        "Package-diagram failure catalogue from /api/analytics/package-failures.",
        "Execute or explicitly descope the human-alignment protocol.",
        "University thesis format pass, citation audit, paper revision on Overleaf.",
        "Optional: cloud GPU (vLLM) for Aya or the full ensemble to reduce wall time.",
    ], s["bullet"]))

    # 16
    story.append(P("16. Conclusion", s["h1"]))
    story.append(P(
        "The thesis proposes a three-stage, dual-LLM, render-gated, MMMU-weighted VLM ensemble "
        "for turning requirements into verified design-phase UML and a gated dataset. The "
        "UML-Pipeline application implements that architecture end to end: specification JSON, "
        "PlantUML (LoRA and grounded builders), compile/render, deterministic acceptance, three "
        "local VLMs, majority A and composite S, human rubric, analytics, and public code. "
        "Measured on this implementation, the acceptance stack is 6/6 golden and 200/200 "
        "benchmark with 5/5 true negatives; a 12-run live VLM smoke showed 11/12 render success "
        "and mean S ≈ 4.93 when render succeeded; bulk render tests reached 97.4% (NL) and 100% "
        "(code) without live VLMs. Remaining gaps are the human study, a frozen 3-VLM dataset "
        "table, package-failure write-up, and manuscript formatting—not the existence of a "
        "working pipeline.",
        s["body"],
    ))
    story.append(Spacer(1, 10))
    story.append(P(
        "Respectfully submitted,<br/><b>Dipak Yadav</b><br/>"
        "https://github.com/dipak5501/uml-generation-pipeline",
        s["body"],
    ))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.7 * inch,
        title="Thesis and Application Report",
        author="Dipak Yadav",
    )
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)
    print(OUT)


if __name__ == "__main__":
    build()
