# Fable Lite 🔶

> Garimpe o **raciocínio** dos modelos nos logs do Claude Code, meça como cada um
> trabalha em **números reais**, e transforme o delta num **playbook** que faz o
> Opus agir mais como o Fable 5.

Não dá pra clonar o poder do Fable 5 — esse poder está nos pesos do modelo. Mas
os seus logs do Claude Code guardam o **ritmo de trabalho** de cada modelo que
você usou. Este projeto extrai esse ritmo e o destila num playbook que você
injeta em qualquer modelo (Opus, Codex, open-source) para uma execução mais
disciplinada.

🌐 **Curso (INEMA.CLUB v2):** https://inematds.github.io/fablelite/

---

## O pipeline

```
~/.claude/projects/*.jsonl   (logs pesados)
        │
        ▼  debloat_jsonl.py         destila 1 sessão  → transcrição leve (~74% menor)
        ▼  extract_corpus.py        filtra por message.model → corpus + números
        ▼  compare_models.py        Fable-5 vs Opus-4.8 → o delta de ritmo
        ▼  make_playbook.py         o delta → playbook.md acionável
        ▼  hooks/inject-playbook.sh injeta no SessionStart (ou skill / CLAUDE.md)
```

## Início rápido

```bash
cd scripts
python3 debloat_jsonl.py                         # vê o debloat (sessão de exemplo)
python3 extract_corpus.py --list                 # quais modelos há no seu histórico?
python3 compare_models.py --a claude-fable-5 --b claude-opus-4-8 --out ../playbook/compare.json
python3 make_playbook.py --from-json ../playbook/compare.json --out ../playbook/fable-mindset-playbook.md
```

Sem dados do Fable? Use os traces abertos:
```bash
pip install datasets
python3 scripts/import_hf_traces.py --dataset Glint-Research/Fable-5-traces
```

## Achados reais (medidos neste histórico)

| sinal | Fable-5 | Opus-4.8 | leitura |
|---|---|---|---|
| **% turnos que pensam antes de agir** | **99%** | 54% | **+45 pp — o sinal forte e transferível** |
| ferramentas/turno (média) | 6.57 | 7.86 | Fable foi mais econômico |
| debloat | — | — | ~74% menor por sessão |

> **Honestidade:** o TEXTO do raciocínio não fica nos logs (vem cifrado, só a
> `signature`). Mede-se a **presença** do raciocínio por turno, não o conteúdo.
> E a amostra de Fable é pequena (7 sessões) — o delta de pensar-antes é robusto;
> `read-before-edit`/`test-after-edit` são boa prática, não delta firme.

## Estrutura

```
index.html              landing do curso (GitHub Pages)
curso/trilhaN/          trilhas e módulos (formato INEMA.CLUB v2)
scripts/                o pipeline (Python stdlib puro) + demo_session.jsonl
prompts/PROMPTS.md      os 4 prompts PT-BR prontos pra colar
playbook/               o playbook gerado + compare.json
hooks/                  inject-playbook.sh + como plugar no SessionStart
skill/fable-mindset/    a skill empacotando a técnica
```

## Créditos

Método inspirado na ideia de minerar os arquivos JSONL de sessão para imitar o
"mindset" de um modelo. Dataset aberto de referência:
[`Glint-Research/Fable-5-traces`](https://huggingface.co/datasets/Glint-Research/Fable-5-traces).
Feito para o [INEMA.CLUB](https://inema.club).
