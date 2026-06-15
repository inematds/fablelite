#!/usr/bin/env bash
# SessionStart hook — injeta o Playbook do Mindset Fable no contexto inicial.
#
# Instale apontando este script no evento SessionStart do Claude Code
# (veja hooks/README.md). Ele lê o playbook e o devolve como `additionalContext`.
#
# Fail-open: se o playbook não existir, não quebra a sessão.

set -euo pipefail

PLAYBOOK="${FABLE_PLAYBOOK:-$HOME/projetos/fablelite/playbook/fable-mindset-playbook.md}"

if [ ! -f "$PLAYBOOK" ]; then
  printf '{"continue":true}\n'
  exit 0
fi

# Usa python3 para escapar o JSON com segurança (o playbook tem aspas, quebras, etc.)
python3 - "$PLAYBOOK" <<'PY'
import json, sys
try:
    txt = open(sys.argv[1], encoding="utf-8").read()
except Exception:
    print('{"continue":true}'); sys.exit(0)
ctx = "<fable-mindset-playbook>\n" + txt + "\n</fable-mindset-playbook>"
print(json.dumps({
    "continue": True,
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": ctx,
    },
}))
PY
