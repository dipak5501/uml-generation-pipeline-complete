#!/usr/bin/env bash
# Start UML-Pipeline API + UI and keep them running.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="$HOME/.local/bin:$HOME/Applications/Ollama.app/Contents/Resources:/Applications/Ollama.app/Contents/Resources:$PATH"
export PYTHONPATH="$ROOT"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

mkdir -p "$ROOT/data" /tmp
API_LOG="${UML_API_LOG:-/tmp/uml-api.log}"
UI_LOG="${UML_UI_LOG:-/tmp/uml-ui.log}"
PID_DIR="${UML_PID_DIR:-$ROOT/data/run}"
mkdir -p "$PID_DIR"

# Dual Ollama for paper VLMs (0.24 mllama + 0.32 qwen)
if [ -x "$ROOT/scripts/ensure_ollama_dual.sh" ]; then
  bash "$ROOT/scripts/ensure_ollama_dual.sh" || true
elif ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  if command -v ollama >/dev/null 2>&1; then
    nohup ollama serve > /tmp/ollama-serve.log 2>&1 &
    sleep 2
  else
    open -a Ollama 2>/dev/null || open "$HOME/Applications/Ollama.app" 2>/dev/null || true
    sleep 3
  fi
fi

stop_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
  if [ -n "$pids" ]; then
    kill $pids 2>/dev/null || true
    sleep 1
    pids="$(lsof -ti tcp:"$port" 2>/dev/null || true)"
    [ -n "$pids" ] && kill -9 $pids 2>/dev/null || true
  fi
}

stop_port 8000
stop_port 8501

# Listen on all interfaces so phones/laptops on the same Wi-Fi can open the UI.
# Streamlit still talks to FastAPI on this Mac; other devices only need a browser.
BIND_HOST="${UML_BIND_HOST:-0.0.0.0}"
LAN_IP=""
for iface in en0 en1 en2; do
  LAN_IP="$(ipconfig getifaddr "$iface" 2>/dev/null || true)"
  [ -n "$LAN_IP" ] && break
done
if [ -z "$LAN_IP" ]; then
  LAN_IP="$(ifconfig 2>/dev/null | awk '/inet / && $2 != "127.0.0.1" {print $2; exit}')"
fi
# Browser download links (export) may use a LAN host; Streamlit→API stays loopback.
export API_BASE_URL="http://127.0.0.1:8000"
export PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
if [ -n "$LAN_IP" ]; then
  export PUBLIC_API_BASE_URL="http://${LAN_IP}:8000"
fi

PY="$ROOT/.venv/bin/python"
UVICORN="$ROOT/.venv/bin/uvicorn"
STREAMLIT="$ROOT/.venv/bin/streamlit"

if [ ! -x "$UVICORN" ]; then
  echo "Missing venv. Run: make install" >&2
  exit 1
fi

# Detach into a new session so IDE/Cursor shells cannot kill servers when
# their terminal ends (plain `nohup … &` still shares the process group).
: >"$API_LOG"
: >"$UI_LOG"
"$PY" - "$PID_DIR/api.pid" "$API_LOG" "$UVICORN" app.main:app --host "$BIND_HOST" --port 8000 <<'PY'
import os, subprocess, sys
pid_file, log_path, *cmd = sys.argv[1:]
with open(log_path, "a") as log:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        cwd=os.environ.get("PWD") or os.getcwd(),
        env=os.environ.copy(),
    )
open(pid_file, "w").write(str(proc.pid))
print(proc.pid)
PY

"$PY" - "$PID_DIR/ui.pid" "$UI_LOG" "$STREAMLIT" run ui/streamlit_app.py \
  --server.port 8501 --server.address "$BIND_HOST" --server.headless true \
  --server.enableCORS false --server.enableXsrfProtection false <<'PY'
import os, subprocess, sys
pid_file, log_path, *cmd = sys.argv[1:]
with open(log_path, "a") as log:
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        cwd=os.environ.get("PWD") or os.getcwd(),
        env=os.environ.copy(),
    )
open(pid_file, "w").write(str(proc.pid))
print(proc.pid)
PY

# Wait until healthy
ok=0
for i in $(seq 1 40); do
  if curl --max-time 3 -sf http://127.0.0.1:8000/docs >/dev/null \
     && curl --max-time 3 -sf http://127.0.0.1:8501/ >/dev/null; then
    ok=1
    break
  fi
  sleep 0.5
done

echo "API pid=$(cat "$PID_DIR/api.pid")  log=$API_LOG"
echo "UI  pid=$(cat "$PID_DIR/ui.pid")  log=$UI_LOG"
if [ "$ok" -eq 1 ]; then
  echo "READY"
  echo "This Mac:     http://127.0.0.1:8501"
  if [ -n "$LAN_IP" ]; then
    echo "Other device: http://${LAN_IP}:8501"
    echo "Same Wi-Fi only. If it fails, allow Python/Streamlit in macOS Firewall"
    echo "(System Settings → Network → Firewall) for ports 8501 and 8000."
  else
    echo "Could not detect Wi-Fi IP. On this Mac run: ipconfig getifaddr en0"
  fi
    echo "API docs:     ${PUBLIC_API_BASE_URL}/docs"
  exit 0
fi

echo "FAILED to become healthy" >&2
tail -40 "$API_LOG" >&2 || true
tail -40 "$UI_LOG" >&2 || true
exit 1
