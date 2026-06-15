#!/usr/bin/env python3
"""
make_playbook.py — transforma o DELTA entre dois modelos num PLAYBOOK: um único
arquivo .md que você aponta para o Opus (via hook, skill ou CLAUDE.md) para ele
adotar os padrões de decisão do Fable que se transferem para produção.

O playbook NÃO copia o Fable cegamente. Ele:
  1. mede os dois modelos (reusando o compare),
  2. injeta os NÚMEROS REAIS no texto (não impressões),
  3. inverte hábitos onde o Fable era FRACO (verbosidade, over-thinking em
     tarefa trivial) em vez de replicá-los.

USO
    python make_playbook.py                                  # fable-5 vs opus-4-8
    python make_playbook.py --target claude-opus-4-8 --model-fable claude-fable-5
    python make_playbook.py --out ../playbook/fable-mindset-playbook.md
    python make_playbook.py --from-json compare.json         # reusa um compare já medido
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from fable_lib import Metrics, collect_model_metrics


def _metrics_from_dict(d: dict) -> Metrics:
    m = Metrics(model=d.get("model", ""))
    m.sessions = d.get("sessions", 0)
    m.assistant_turns = d.get("assistant_turns", 0)
    m.human_turns = d.get("human_turns", 0)
    m.thinking_turns = d.get("thinking_turns", 0)
    m.total_tool_calls = d.get("total_tool_calls", 0)
    # campos derivados são propriedades; guardamos os crus quando possível
    m.tools_per_turn = [d.get("avg_tools_per_turn", 0.0)] if d.get("avg_tools_per_turn") else []
    m.read_before_edit = 0
    m.edit_total = 0
    m._cached = d  # type: ignore[attr-defined]
    return m


def _get(d_or_m, key, default=0):
    if isinstance(d_or_m, dict):
        return d_or_m.get(key, default)
    return getattr(d_or_m, key, default)


def build_playbook(fable: dict, target: dict) -> str:
    """Gera o markdown do playbook a partir de dois dicts de métricas.

    A ordem das regras segue a FORÇA do sinal medido, não a ordem do vídeo:
    o delta robusto é o RACIOCÍNIO-ANTES-DE-AGIR. Os outros sinais entram com
    a ressalva honesta de tamanho de amostra.
    """
    fa, op = fable, target
    f_tpt = fa.get("avg_tools_per_turn", 0); o_tpt = op.get("avg_tools_per_turn", 0)
    f_think = fa.get("thinking_ratio", 0);   o_think = op.get("thinking_ratio", 0)
    f_rbe = fa.get("read_before_edit_ratio", 0); o_rbe = op.get("read_before_edit_ratio", 0)
    f_tae = fa.get("test_after_edit_ratio", 0);  o_tae = op.get("test_after_edit_ratio", 0)
    f_sess = fa.get("sessions", 0)
    fname = fa.get("model", "claude-fable-5")
    oname = op.get("model", "claude-opus-4-8")

    def pct(x): return f"{x*100:.0f}%"
    think_gap = (f_think - o_think) * 100
    # quem usa mais ferramentas por turno (direção honesta, sem assumir causa)
    if f_tpt > o_tpt:
        tpt_note = (f"o Fable fez MENOS ferramentas por turno ({f_tpt} vs {o_tpt}) — "
                    f"foi mais econômico, não mais agitado") if False else \
                   (f"o Fable fez MAIS ferramentas por turno ({f_tpt} vs {o_tpt})")
    elif f_tpt < o_tpt:
        tpt_note = (f"o Fable foi mais ECONÔMICO: menos ferramentas por turno "
                    f"({f_tpt} vs {o_tpt} do {oname}) e ainda assim resolvia — "
                    f"densidade, não thrashing")
    else:
        tpt_note = f"ambos com {f_tpt} ferramentas por turno"
    small = f_sess < 30
    sample_warn = (f"\n> ⚠️ **Amostra pequena de Fable ({f_sess} sessões).** Trate "
                   f"`read-antes-de-edit` e `teste-depois-de-edit` como BOA PRÁTICA "
                   f"a importar, não como delta estatisticamente firme. O sinal "
                   f"robusto aqui é o raciocínio-antes-de-agir.\n") if small else ""

    return f"""\
# Playbook do Mindset Fable — para {oname}

> Gerado por `make_playbook.py` a partir do delta medido entre **{fname}** e
> **{oname}** nas SUAS próprias sessões (`~/.claude/projects`). Números medidos,
> não impressões. Aponte este arquivo para o {oname} (hook `SessionStart`, skill
> ou `CLAUDE.md`) para ele adotar o ritmo do Fable nas partes que transferem.
{sample_warn}
## O delta, em números

| sinal | {fname} | {oname} | leitura |
|---|---|---|---|
| **% de turnos que pensam antes de agir** | **{pct(f_think)}** | {pct(o_think)} | **+{think_gap:.0f} pp — o sinal forte. Pense primeiro.** |
| ferramentas por turno (média) | {f_tpt} | {o_tpt} | {tpt_note}. |
| read-antes-de-edit | {pct(f_rbe)} | {pct(o_rbe)} | boa prática (heurística conservadora). |
| teste-depois-de-edit | {pct(f_tae)} | {pct(o_tae)} | boa prática (amostra ruidosa). |

> **Honestidade sobre os dados:** o TEXTO do raciocínio não fica nos logs (vem
> cifrado, só a `signature`). O que medimos é a **presença** do raciocínio por
> turno — "pensou antes de agir?" — não o conteúdo do pensamento.

## Regras (o que TRANSFERE do Fable) — em ordem de força do sinal

1. **Pense antes de agir.** Em qualquer tarefa não-trivial, gaste 2–5 linhas
   planejando o caminho ANTES da primeira ferramenta. Este é o delta robusto:
   o Fable raciocinava em **{pct(f_think)}** dos turnos contra **{pct(o_think)}**
   do {oname} (+{think_gap:.0f} pontos). É a maior alavanca e a que mais transfere.

2. **Seja econômico com ferramentas — densidade, não agitação.** Medido:
   {tpt_note}. A meta não é "fazer mais chamadas"; é cada chamada ter propósito.
   Quando há chamadas independentes (ler 3 arquivos sem dependência), faça-as no
   MESMO turno em vez de uma ida-e-volta por arquivo.

3. **Leia antes de editar — sempre.** Nunca edite um arquivo que você não leu
   neste contexto. (Os dois modelos ficaram modestos aqui — ~{pct(f_rbe)}/{pct(o_rbe)} —
   então é uma disciplina a SUBIR para 100%, não a copiar do Fable.)

4. **Feche o loop: teste/build depois de editar.** Editou código? Rode a suíte
   ou o build e relate o resultado REAL. Não declare "pronto" sem verificar.

5. **Sequência canônica:** entender → planejar (em texto) → ler os alvos →
   editar cirúrgico → verificar (teste/build) → relatar com o output real.

6. **Pare quando tiver o suficiente para agir.** Não re-derive fatos já
   estabelecidos nem pesquise opções que você não vai seguir.

## Onde o Fable era FRACO (NÃO copie isto)

> Um playbook honesto corrige o hábito ruim em vez de replicá-lo.

- **Over-thinking no trivial.** Raciocinar em {pct(f_think)} dos turnos é ótimo
  no difícil e desperdício num rename de uma linha. **Correção:** raciocínio
  proporcional à dificuldade — tarefa mecânica vai direto.
- **Verbosidade.** Tendia a narrar demais o que ia fazer. **Correção:** aja; o
  resumo vem curto DEPOIS, com caminhos de arquivo e o que foi verificado.
- **Planejamento que vira ensaio.** **Correção:** o plano cabe em poucas linhas;
  a profundidade vai para a execução.

## Checklist de uma linha (cole no topo de tarefas de código)

`entender → plano curto → ler → editar → testar → relatar (com output)`  ·
pense-antes-no-não-trivial · ferramenta-com-propósito · read-before-edit→100% ·
teste-depois-de-edit · sem-verbosidade · sem-over-think-no-trivial
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Gera o playbook do Mindset Fable.")
    ap.add_argument("--model-fable", default="claude-fable-5", help="modelo de referência (default: claude-fable-5)")
    ap.add_argument("--target", default="claude-opus-4-8", help="modelo a ser corrigido (default: claude-opus-4-8)")
    ap.add_argument("--from-json", help="reusa um compare.json já medido (a=fable, b=target)")
    ap.add_argument("--projects", help="pasta de projects (default: ~/.claude/projects)")
    ap.add_argument("--out", default=os.path.join("..", "playbook", "fable-mindset-playbook.md"),
                    help="arquivo .md de saída")
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as fh:
            data = json.load(fh)
        fable_d, target_d = data["a"], data["b"]
    else:
        fable_m = collect_model_metrics(args.model_fable, args.projects)
        target_m = collect_model_metrics(args.target, args.projects)
        if fable_m.assistant_turns == 0:
            print(f"⚠ Sem turnos de '{args.model_fable}'. Use o dataset aberto "
                  f"(import_hf_traces.py) ou um compare.json via --from-json.", file=sys.stderr)
        fable_d, target_d = fable_m.as_dict(), target_m.as_dict()

    md = build_playbook(fable_d, target_d)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(f"✓ playbook escrito em: {args.out}")
    print("  Aponte-o para o modelo via hook SessionStart, skill ou CLAUDE.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
