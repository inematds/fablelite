#!/usr/bin/env python3
"""
import_hf_traces.py — e se você mal teve tempo de conversar com o Fable e não
tem dados próprios para minerar?

Pessoas abriram as próprias sessões do Claude Code no Hugging Face. O dataset
`Glint-Research/Fable-5-traces` NÃO é um chat achatado: é um DUMP CRU de
`~/.claude/projects/` — arquivos .jsonl no formato nativo do Claude Code, com a
estrutura de blocos (`thinking`, `tool_use`) preservada. Ou seja: dá para rodar
o MESMO exercício comportamental do curso sobre dados de terceiros.

Este script baixa esses .jsonl direto pela API do Hugging Face — só stdlib, SEM
a lib `datasets` — para uma pasta local, e então mede o comportamento do modelo
com o mesmo `fable_lib` do resto do curso.

USO
    python import_hf_traces.py                       # baixa + mede claude-fable-5
    python import_hf_traces.py --peek                # só inspeciona (lista + modelos do 1º)
    python import_hf_traces.py --out ./corpus_fable_hf
    python import_hf_traces.py --dataset OUTRO/dataset --model claude-fable-5
    python import_hf_traces.py --limit-files 30      # baixa no máx. N sessões
    python import_hf_traces.py --include-subagents   # inclui sessões de subagente

DEPOIS: para virar playbook, monte um compare.json com
    {"a": <stats daqui>, "b": <stats do SEU modelo>}
e rode `make_playbook.py --from-json`. (lado `a` = Fable do dataset aberto.)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

from fable_lib import collect_model_metrics, discover_models

_API = "https://huggingface.co/api/datasets/{ds}/tree/main?recursive=true"
_RESOLVE = "https://huggingface.co/datasets/{ds}/resolve/main/{path}"
_UA = {"User-Agent": "fable-mindset/1.0"}


def _get_json(url: str):
    req = urllib.request.Request(url, headers=_UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def list_session_files(ds: str, include_subagents: bool) -> list[dict]:
    """Arquivos .jsonl de sessão dentro de claude/projects/ no repo do dataset."""
    out = []
    for t in _get_json(_API.format(ds=ds)):
        if t.get("type") != "file":
            continue
        p = t.get("path", "")
        if not (p.startswith("claude/projects/") and p.endswith(".jsonl")):
            continue
        if "/subagents/" in p and not include_subagents:
            continue
        out.append(t)
    return out


def download(ds: str, path: str, dest: str) -> bool:
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    try:
        req = urllib.request.Request(_RESOLVE.format(ds=ds, path=path), headers=_UA)
        with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as fh:
            fh.write(r.read())
        return True
    except Exception as e:
        print(f"  falha ao baixar {path}: {e}", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Baixa traces CRUS do Fable no Hugging Face e mede o comportamento.")
    ap.add_argument("--dataset", default="Glint-Research/Fable-5-traces", help="id do dataset no HF Hub")
    ap.add_argument("--model", default="claude-fable-5", help="modelo a medir nos traces")
    ap.add_argument("--out", help="pasta de saída (default: ./corpus_<dataset>_hf)")
    ap.add_argument("--limit-files", type=int, default=None, help="baixa no máximo N sessões")
    ap.add_argument("--include-subagents", action="store_true", help="inclui sessões de subagente")
    ap.add_argument("--peek", action="store_true", help="só inspeciona: lista + modelos do 1º arquivo")
    args = ap.parse_args()

    try:
        files = list_session_files(args.dataset, args.include_subagents)
    except Exception as e:
        print(f"✗ não consegui listar o dataset {args.dataset}: {e}", file=sys.stderr)
        return 1
    if not files:
        print("✗ nenhum .jsonl em claude/projects/ neste dataset. Confira o id.", file=sys.stderr)
        return 1

    total_mb = sum(t.get("size", 0) for t in files) / 1e6
    print(f"dataset {args.dataset}: {len(files)} sessões em claude/projects/ ({total_mb:.1f} MB)")

    out_dir = args.out or os.path.join(".", f"corpus_{args.dataset.split('/')[-1]}_hf")
    os.makedirs(out_dir, exist_ok=True)

    if args.peek:
        first = files[0]
        if download(args.dataset, first["path"], os.path.join(out_dir, "peek.jsonl")):
            dm = discover_models(out_dir)
            print(f"1º arquivo: {first['path']}")
            print("modelos no 1º arquivo (passos):", dict(dm.most_common(8)))
            print("→ schema OK: são eventos crus do Claude Code (type/message/model).")
        return 0

    sel = files if args.limit_files is None else files[: args.limit_files]
    print(f"baixando {len(sel)} sessões para {out_dir} ...")
    ok = sum(download(args.dataset, t["path"], os.path.join(out_dir, f"{i:04d}.jsonl"))
             for i, t in enumerate(sel))
    print(f"download ok: {ok}/{len(sel)}")

    dm = discover_models(out_dir)
    print("modelos presentes (passos):", dict(dm.most_common(8)))

    m = collect_model_metrics(args.model, projects_dir=out_dir)
    with open(os.path.join(out_dir, "stats.json"), "w", encoding="utf-8") as fh:
        json.dump(m.as_dict(), fh, ensure_ascii=False, indent=2)

    print(f"\n=== COMPORTAMENTO MEDIDO (dataset aberto) · {args.model} ===")
    print(f"  sessões ........................ {m.sessions}")
    print(f"  turnos do assistente ........... {m.assistant_turns}")
    print(f"  passos (linhas-evento) ......... {m.assistant_lines}")
    print(f"  % turnos com raciocínio ........ {m.thinking_ratio:.0%}")
    print(f"  ferramentas por turno (média) .. {m.avg_tools_per_turn}")
    print(f"  read-antes-de-edit ............. {m.read_before_edit_ratio:.0%}")
    print(f"  teste-depois-de-edit ........... {m.test_after_edit_ratio:.0%}")
    print(f"\n✓ stats em: {out_dir}/stats.json")
    print("  Para virar playbook: monte compare.json {\"a\": <estes stats>, "
          "\"b\": <stats do seu modelo>} e rode make_playbook.py --from-json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
