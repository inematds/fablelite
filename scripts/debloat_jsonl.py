#!/usr/bin/env python3
"""
debloat_jsonl.py — destila um arquivo de sessão do Claude Code numa
transcrição LEVE.

A gordura desses arquivos são os RESULTADOS de ferramenta, o conteúdo completo
de arquivos e a saída de comandos ecoada de volta para o contexto. Este script
mantém só o que importa:

    ✓ minhas mensagens de usuário
    ✓ as mensagens de TEXTO do assistente
    ✓ o MODELO que escreveu cada turno (message.model)
    ✓ uma linha compacta por chamada de ferramenta (nome + alvo curto)
    ✓ os blocos de raciocínio (<thinking>), se existirem

    ✗ payloads pesados de tool_result
    ✗ blobs de anexo / conteúdo de arquivo
    ✗ contabilidade do harness (usage, uuids, sidechain, meta…)

USO
    python debloat_jsonl.py                      # roda no demo_session.jsonl
    python debloat_jsonl.py minha_sessao.jsonl   # roda num arquivo seu
    python debloat_jsonl.py s.jsonl -o limpa.md  # escolhe a saída
    python debloat_jsonl.py s.jsonl --no-thinking
    python debloat_jsonl.py s.jsonl --no-open    # não tenta abrir no editor

Sem argumentos, ele roda no demo_session.jsonl que mora ao lado deste script,
imprime o tamanho antes/depois e abre a transcrição limpa — exatamente o
fluxo do curso para você conferir o formato na primeira vez.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from fable_lib import debloat_file, human_size


def _open_in_editor(path: str) -> None:
    """Abre o arquivo no $EDITOR / xdg-open, sem travar se não houver um."""
    opener = os.environ.get("EDITOR")
    try:
        if opener:
            subprocess.Popen([opener, path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        print(f"(não consegui abrir automaticamente — abra você: {path})")


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Destila uma sessão JSONL do Claude Code.")
    ap.add_argument("input", nargs="?", default=os.path.join(here, "demo_session.jsonl"),
                    help="arquivo .jsonl de entrada (default: demo_session.jsonl ao lado do script)")
    ap.add_argument("-o", "--output", help="arquivo .md de saída (default: <input>.clean.md)")
    ap.add_argument("--no-thinking", action="store_true", help="descarta blocos <thinking>")
    ap.add_argument("--no-open", action="store_true", help="não abre a saída no editor")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"✗ arquivo não encontrado: {args.input}", file=sys.stderr)
        return 1

    out_path = args.output or (os.path.splitext(args.input)[0] + ".clean.md")

    before = os.path.getsize(args.input)
    transcript = debloat_file(args.input, keep_thinking=not args.no_thinking)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(transcript)
    after = os.path.getsize(out_path)

    shrink = (1 - after / before) * 100 if before else 0
    print("┌─ debloat_jsonl ───────────────────────────────")
    print(f"│ entrada : {args.input}")
    print(f"│ saída   : {out_path}")
    print(f"│ antes   : {human_size(before)}")
    print(f"│ depois  : {human_size(after)}")
    print(f"│ redução : {shrink:.1f}%  ({human_size(before)} → {human_size(after)})")
    print("└───────────────────────────────────────────────")

    if not args.no_open:
        _open_in_editor(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
