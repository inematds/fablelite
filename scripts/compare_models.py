#!/usr/bin/env python3
"""
compare_models.py — coloca DOIS modelos lado a lado e mede a distância no
ritmo deles: cadência de chamadas de ferramenta, sequências de ação e as
proporções (read-antes-de-edit, teste-depois-de-edit, quanto raciocina).

É o passo do curso onde a gente vê o DELTA entre, por exemplo, o
claude-fable-5 e o claude-opus-4-8 — a diferença que vira o playbook.

USO
    python compare_models.py                                   # fable-5  vs  opus-4-8
    python compare_models.py --a claude-fable-5 --b claude-opus-4-8
    python compare_models.py --a ... --b ... --out compare.json --projects /path
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from fable_lib import Metrics, collect_model_metrics


ROWS = [
    ("sessões",                    lambda m: m.sessions,                  "{:.0f}"),
    ("turnos do assistente",       lambda m: m.assistant_turns,           "{:.0f}"),
    ("turnos com raciocínio",      lambda m: m.thinking_turns,            "{:.0f}"),
    ("% turnos c/ raciocínio",     lambda m: m.thinking_ratio * 100,      "{:.0f}%"),
    ("chamadas de ferramenta",     lambda m: m.total_tool_calls,          "{:.0f}"),
    ("ferramentas/turno (média)",  lambda m: m.avg_tools_per_turn,        "{:.2f}"),
    ("ferramentas/turno (mediana)",lambda m: m.median_tools_per_turn,     "{:.1f}"),
    ("% read-antes-de-edit",       lambda m: m.read_before_edit_ratio*100,"{:.0f}%"),
    ("% teste-depois-de-edit",     lambda m: m.test_after_edit_ratio*100, "{:.0f}%"),
]


def _fmt(val, spec):
    try:
        return spec.format(val)
    except Exception:
        return str(val)


def print_side_by_side(a: Metrics, b: Metrics) -> None:
    la, lb = a.model, b.model
    w0, w1, w2 = 28, max(14, len(la)), max(14, len(lb))
    print()
    print(f"{'métrica':<{w0}} {la:>{w1}} {lb:>{w2}}   Δ")
    print("─" * (w0 + w1 + w2 + 10))
    for label, getter, spec in ROWS:
        va, vb = getter(a), getter(b)
        sa, sb = _fmt(va, spec), _fmt(vb, spec)
        try:
            delta = va - vb
            ds = ("+" if delta > 0 else "") + _fmt(delta, spec)
        except Exception:
            ds = ""
        print(f"{label:<{w0}} {sa:>{w1}} {sb:>{w2}}   {ds}")
    print()
    # leitura qualitativa do delta de cadência (honesta: mais ferramentas/turno
    # NÃO é automaticamente "melhor" — pode ser densidade de trabalho OU thrashing)
    if a.avg_tools_per_turn and b.avg_tools_per_turn and a.avg_tools_per_turn != b.avg_tools_per_turn:
        hi, lo = (a, b) if a.avg_tools_per_turn >= b.avg_tools_per_turn else (b, a)
        print(f"⮕ {hi.model} faz MAIS ferramentas por turno "
              f"({hi.avg_tools_per_turn} vs {lo.avg_tools_per_turn}). Cuidado: mais "
              f"ferramentas/turno pode ser densidade de trabalho OU idas-e-voltas (thrashing). "
              f"Cruze sempre com o raciocínio antes de concluir.")
    if a.thinking_ratio != b.thinking_ratio:
        more = a if a.thinking_ratio > b.thinking_ratio else b
        less = b if more is a else a
        print(f"⮕ {more.model} pensa antes de agir com mais frequência "
              f"({more.thinking_ratio:.0%} vs {less.thinking_ratio:.0%} dos turnos). "
              f"É o hábito mais transferível: forçar {less.model} a planejar mais.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Compara o comportamento de dois modelos.")
    ap.add_argument("--a", default="claude-fable-5", help="modelo A (default: claude-fable-5)")
    ap.add_argument("--b", default="claude-opus-4-8", help="modelo B (default: claude-opus-4-8)")
    ap.add_argument("--out", help="escreve o comparativo em JSON neste caminho")
    ap.add_argument("--projects", help="pasta de projects (default: ~/.claude/projects)")
    args = ap.parse_args()

    a = collect_model_metrics(args.a, args.projects)
    b = collect_model_metrics(args.b, args.projects)

    if a.assistant_turns == 0 and b.assistant_turns == 0:
        print("✗ Nenhum dos dois modelos tem turnos no histórico. Rode "
              "`python extract_corpus.py --list` para ver o que existe.", file=sys.stderr)
        return 1
    for m in (a, b):
        if m.assistant_turns == 0:
            print(f"⚠ aviso: nenhum turno de '{m.model}' encontrado — "
                  f"a coluna dele vem zerada. (Sem dados de Fable? Use o dataset aberto; "
                  f"veja import_hf_traces.py.)")

    print_side_by_side(a, b)

    if args.out:
        payload = {"a": a.as_dict(), "b": b.as_dict()}
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"✓ comparativo salvo em: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
