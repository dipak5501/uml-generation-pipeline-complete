# Set up UML-Pipeline on a new Mac

This repository is a **complete snapshot** of the application: source code, LoRA adapter, SQLite generation history, and Cursor agent transcripts (`cursor-chats/`).

Ollama model weights (~23 GB) and Aya local weights (~16 GB) are **not** in GitHub (too large). Pull Ollama models on the new machine.

## 1. Install

```bash
git clone https://github.com/dipak5501/uml-generation-pipeline-complete.git
cd uml-generation-pipeline-complete
make install
cp .env.example .env
```

Fill `HF_TOKEN` / `OPENAI_API_KEY` in `.env` if you use Hugging Face or OpenAI. Leave them empty for local Ollama.

## 2. Ollama (live VLMs)

Install [Ollama](https://ollama.com), then:

```bash
ollama pull llama3.2:1b
ollama pull qwen2.5vl:3b
ollama pull llama3.2-vision:11b
```

## 3. Run

```bash
./scripts/run_local.sh
```

- UI: http://127.0.0.1:8501
- API: http://127.0.0.1:8000/docs

Apple Silicon is required for `USE_FINETUNED_CODE=true` (MLX LoRA). On other machines set `USE_FINETUNED_CODE=false` in `.env`.

## 4. Cursor chats

Sign in to Cursor with the **same account**. Optional: copy `cursor-chats/` into the new workspace transcript folder under `~/.cursor/projects/` after you open this repo once.
