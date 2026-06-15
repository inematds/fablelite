#!/usr/bin/env python3
"""
import_hf_traces.py — e se você mal teve tempo de conversar com o Fable e não
tem dados próprios para analisar?

Pessoas abriram as próprias sessões com o Fable 5 no Hugging Face. Este script
baixa um desses datasets (default: `Glint-Research/Fable-5-traces`) e roda o
MESMO exercício comportamental do curso sobre dados de terceiros — mesma leitura
de ferramentas/turno, raciocínio, ordem de trabalho.

REQUISITO
    pip install datasets            # huggingface datasets

USO
    python import_hf_traces.py                                  # Glint-Research/Fable-5-traces
    python import_hf_traces.py --dataset OUTRO/dataset --split train
    python import_hf_traces.py --out ./corpus_fable_hf

NOTA DE HONESTIDADE
    O schema de um dataset comunitário não é garantido. Este importador é
    DEFENSIVO: tenta mapear os formatos mais comuns (lista de mensagens estilo
    chat, eventos JSONL embutidos, ou transcrição crua) para os mesmos turnos
    que o resto do curso usa. Se a contagem sair estranha, abra um registro com
    `--peek` e ajuste o mapeamento em `record_to_events()`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from fable_lib import Metrics, normalize_turn


def record_to_events(rec: dict) -> list[dict]:
    """Tenta normalizar UM registro do dataset numa lista de eventos no formato
    do Claude Code (type + message{role,model,content}). Defensivo de propósito.
    """
    # caso 1: registro já é uma lista de eventos JSONL (campo "events"/"trace")
    for key in ("events", "trace", "session", "jsonl"):
        val = rec.get(key)
        if isinstance(val, list) and val and isinstance(val[0], dict):
            return val
        if isinstance(val, str):
            out = []
            for line in val.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            if out:
                return out

    # caso 2: lista de mensagens estilo chat (role/content)
    for key in ("messages", "conversation", "turns", "dialog"):
        msgs = rec.get(key)
        if isinstance(msgs, list) and msgs and isinstance(msgs[0], dict):
            events = []
            model = rec.get("model") or "claude-fable-5"
            for msg in msgs:
                role = msg.get("role") or msg.get("from") or ""
                content = msg.get("content") or msg.get("value") or msg.get("text") or ""
                ev = {"type": role, "message": {"role": role, "content": content}}
                if role == "assistant":
                    ev["message"]["model"] = msg.get("model") or model
                events.append(ev)
            return events

    # caso 3: nada reconhecido
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Importa traces do Fable do Hugging Face e mede o comportamento.")
    ap.add_argument("--dataset", default="Glint-Research/Fable-5-traces", help="id do dataset no HF Hub")
    ap.add_argument("--split", default="train", help="split (default: train)")
    ap.add_argument("--model", default="claude-fable-5", help="rótulo do modelo nos registros")
    ap.add_argument("--out", help="pasta de saída (default: ./corpus_<dataset>_hf)")
    ap.add_argument("--peek", action="store_true", help="só mostra o 1º registro e sai (para inspecionar o schema)")
    args = ap.parse_args()

    try:
        from datasets import load_dataset  # type: ignore
    except ImportError:
        print("✗ Falta a lib `datasets`. Instale com:  pip install datasets", file=sys.stderr)
        return 1

    print(f"baixando {args.dataset} [{args.split}] …")
    ds = load_dataset(args.dataset, split=args.split)

    if args.peek:
        print(json.dumps(ds[0], ensure_ascii=False, indent=2)[:4000])
        return 0

    out_dir = args.out or os.path.join(".", f"corpus_{args.dataset.split('/')[-1]}_hf")
    os.makedirs(out_dir, exist_ok=True)

    m = Metrics(model=args.model)
    mapped = 0
    for rec in ds:
        events = record_to_events(rec)
        if events:
            m.add_session(events)
            mapped += 1

    if mapped == 0:
        print("✗ Não consegui mapear nenhum registro. Rode com --peek para ver o schema "
              "e ajuste record_to_events().", file=sys.stderr)
        return 1

    with open(os.path.join(out_dir, "stats.json"), "w", encoding="utf-8") as fh:
        json.dump(m.as_dict(), fh, ensure_ascii=False, indent=2)

    print(f"\n=== COMPORTAMENTO MEDIDO (dataset aberto) · {args.model} ===")
    print(f"  registros mapeados ............. {mapped}")
    print(f"  turnos do assistente ........... {m.assistant_turns}")
    print(f"  ferramentas por turno (média) .. {m.avg_tools_per_turn}")
    print(f"  % turnos com raciocínio ........ {m.thinking_ratio:.0%}")
    print(f"  read-antes-de-edit ............. {m.read_before_edit_ratio:.0%}")
    print(f"  teste-depois-de-edit ........... {m.test_after_edit_ratio:.0%}")
    print("  top ferramentas:")
    for name, count in m.top_tools():
        print(f"     {name:<14} {count}")
    print(f"\n✓ stats em: {out_dir}/stats.json")
    print("  Agora rode make_playbook.py --from-json para virar playbook (a=estes dados).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
