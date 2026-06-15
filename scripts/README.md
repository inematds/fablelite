# scripts/ — o pipeline do Mindset Fable

Cinco scripts Python (stdlib pura, zero dependências — exceto `import_hf_traces.py`,
que precisa de `datasets`). Todos importam de `fable_lib.py`, que faz o parsing
dos logs JSONL e mede o comportamento.

```
fable_lib.py          núcleo: parser dos logs + métricas (TURNOS LÓGICOS)
debloat_jsonl.py      destila 1 sessão numa transcrição leve (antes/depois)
extract_corpus.py     extrai o corpus de 1 modelo de TODO o histórico + números
compare_models.py     2 modelos lado a lado: o delta de ritmo
make_playbook.py      transforma o delta num playbook .md acionável
import_hf_traces.py   sem dados próprios? usa o dataset aberto do Fable (HF)
demo_session.jsonl    sessão sintética p/ rodar tudo na hora
```

## Início rápido

```bash
cd scripts

# 1) Ver o debloat funcionando (sessão de exemplo)
python3 debloat_jsonl.py                       # 74% menor; abre a transcrição limpa

# 2) Quais modelos existem no SEU histórico?
python3 extract_corpus.py --list

# 3) Comportamento medido de um modelo
python3 extract_corpus.py --model claude-fable-5

# 4) Fable vs Opus, lado a lado (escreve compare.json)
python3 compare_models.py --a claude-fable-5 --b claude-opus-4-8 --out ../playbook/compare.json

# 5) Virar playbook
python3 make_playbook.py --from-json ../playbook/compare.json --out ../playbook/fable-mindset-playbook.md
```

## O que cada métrica significa (e o que NÃO significa)

| métrica | definição | cuidado |
|---|---|---|
| **turno lógico** | 1 prompt humano → tudo até o próximo prompt humano | o Claude Code grava **cada bloco** (thinking/text/tool_use) numa LINHA. Contar "por linha" dilui o sinal — por isso agrupamos. |
| **% turnos que pensam antes** | turnos lógicos com ≥1 bloco `thinking`/`redacted_thinking` | o **texto** do raciocínio vem VAZIO/cifrado nos logs — medimos **presença**, não conteúdo. |
| **ferramentas/turno** | nº de `tool_use` por turno lógico | mais ≠ melhor. Pode ser densidade OU thrashing. |
| **read-antes-de-edit** | edições cujo arquivo já tinha sido lido na sessão | heurística conservadora (casa por caminho). |
| **teste-depois-de-edit** | sessões que rodaram teste após editar | heurística por regex de comando (`pytest`, `jest`, `go test`…). |

## Achados reais (rodado no histórico deste repositório)

- `claude-fable-5`: **99%** dos turnos pensaram antes de agir · 6.57 ferramentas/turno (amostra: 7 sessões, 69 turnos lógicos).
- `claude-opus-4-8`: **54%** · 7.86 ferramentas/turno (1114 sessões).
- **Delta forte e transferível:** pensar-antes-de-agir (+45 pontos). Os demais sinais são boa prática, não delta firme (amostra de Fable pequena).
