#!/usr/bin/env python3
"""
extract_corpus.py — extrai TODOS os turnos de um modelo do seu histórico
inteiro (todos os projetos em ~/.claude/projects) para um corpus combinado,
e lê o comportamento dele em NÚMEROS REAIS.

Cada turno do assistente registra qual modelo o escreveu, no campo
`message.model`. Filtramos por esse campo.

USO
    python extract_corpus.py                          # default: claude-fable-5
    python extract_corpus.py --model claude-opus-4-8
    python extract_corpus.py --model claude-fable-5 --out ./corpus_fable
    python extract_corpus.py --list                   # só lista os modelos que existem
    python extract_corpus.py --projects /caminho/para/projects

SAÍDA (em --out, default ./corpus_<modelo>/)
    transcript.md   transcrição leve só com os turnos do modelo
    stats.json      todas as métricas medidas
    e um relatório legível impresso no terminal.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from fable_lib import (
    Metrics, collect_model_metrics, discover_models, iter_events,
    iter_project_files, lightweight_lines, normalize_turn,
)


def print_report(m: Metrics) -> None:
    print(f"\n=== COMPORTAMENTO MEDIDO · {m.model} ===")
    print(f"  sessões com este modelo ......... {m.sessions}")
    print(f"  turnos lógicos (1/prompt humano)  {m.assistant_turns}")
    print(f"  linhas-evento do assistente ..... {m.assistant_lines}  (cada bloco = 1 linha)")
    print(f"  minhas mensagens (humano) ....... {m.human_turns}")
    print(f"  turnos que pensaram antes ....... {m.thinking_turns}  "
          f"({m.thinking_ratio:.0%} dos turnos lógicos)")
    print(f"  total de chamadas de ferramenta . {m.total_tool_calls}")
    print(f"  ferramentas por turno (média) ... {m.avg_tools_per_turn}")
    print(f"  ferramentas por turno (mediana) . {m.median_tools_per_turn}")
    print(f"  read-antes-de-edit (ratio) ...... {m.read_before_edit_ratio:.0%}  "
          f"({m.read_before_edit}/{m.edit_total} edições)")
    print(f"  teste-depois-de-edit (ratio) .... {m.test_after_edit_ratio:.0%}  "
          f"({m.test_after_edit_sessions}/{m.sessions_with_edit} sessões que editaram)")
    print("  ferramentas mais usadas:")
    for name, count in m.top_tools():
        bar = "█" * max(1, round(count / max(1, m.total_tool_calls) * 30))
        print(f"     {name:<14} {count:>6}  {bar}")


def write_corpus(model: str, out_dir: str, projects_dir: str | None) -> None:
    os.makedirs(out_dir, exist_ok=True)
    chunks: list[str] = []
    for path in iter_project_files(projects_dir):
        session_lines: list[str] = []
        for ev in iter_events(path):
            if ev.get("type") == "assistant" and (ev.get("message") or {}).get("model") != model:
                continue
            turn = normalize_turn(ev)
            # mantém só os turnos do modelo-alvo + os prompts humanos que os geraram
            if turn.role == "assistant" and turn.model != model:
                continue
            session_lines.extend(lightweight_lines(turn))
        if session_lines:
            rel = os.path.relpath(path, os.path.expanduser("~/.claude/projects"))
            chunks.append(f"\n\n========== SESSÃO: {rel} ==========\n")
            chunks.extend(session_lines)
    with open(os.path.join(out_dir, "transcript.md"), "w", encoding="utf-8") as fh:
        fh.write("\n\n".join(chunks) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Extrai o corpus de um modelo do histórico do Claude Code.")
    ap.add_argument("--model", default="claude-fable-5", help="modelo-alvo (default: claude-fable-5)")
    ap.add_argument("--out", help="pasta de saída (default: ./corpus_<modelo>)")
    ap.add_argument("--projects", help="pasta de projects (default: ~/.claude/projects)")
    ap.add_argument("--list", action="store_true", help="só lista os modelos presentes e sai")
    args = ap.parse_args()

    if args.list:
        models = discover_models(args.projects)
        if not models:
            print("Nenhum turno de assistente encontrado. Os logs estão em ~/.claude/projects?")
            return 1
        print("Modelos no seu histórico (por nº de turnos):")
        for name, count in models.most_common():
            print(f"  {count:>7}  {name}")
        return 0

    out_dir = args.out or os.path.join(".", f"corpus_{args.model.replace('/', '_')}")
    m = collect_model_metrics(args.model, args.projects)
    if m.assistant_turns == 0:
        print(f"✗ Nenhum turno de '{args.model}' encontrado. Rode --list para ver os modelos disponíveis.")
        return 1

    write_corpus(args.model, out_dir, args.projects)
    with open(os.path.join(out_dir, "stats.json"), "w", encoding="utf-8") as fh:
        json.dump(m.as_dict(), fh, ensure_ascii=False, indent=2)

    print_report(m)
    print(f"\n✓ corpus + stats escritos em: {out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
