---
name: fable-mindset
description: Minera os logs JSONL do Claude Code (~/.claude/projects) para medir como cada modelo trabalha e gerar um playbook de comportamento. Use quando o usuário pedir para analisar/extrair o comportamento de um modelo a partir das sessões, comparar dois modelos (ex.: Fable 5 vs Opus), destilar/'debloat' uma sessão JSONL, gerar um playbook a partir do histórico, ou injetar esse playbook no início da sessão (hook/skill/CLAUDE.md). Gatilhos -> 'mindset fable', 'analisar minhas sessões', 'comparar modelos', 'debloat jsonl', 'playbook do modelo', 'extrair raciocínio dos logs'.
---

# Fable Mindset

Esta skill empacota uma técnica para **medir como cada modelo trabalha** a partir dos
logs do Claude Code e **virar isso num playbook** que você injeta no começo da sessão.

A ideia: o Claude Code grava cada sessão num arquivo JSONL em
`~/.claude/projects/<projeto>/<uuid>.jsonl` (um evento JSON por linha). Cada turno do
assistente carrega o campo `message.model` — é ele que diz **qual** modelo escreveu
aquele turno. Filtrando por esse campo, dá para extrair tudo o que um modelo fez,
medir o ritmo dele em números reais, e comparar dois modelos para achar o **delta**
que vira regra acionável.

Os scripts são stdlib pura (zero dependências, exceto `import_hf_traces.py`) e ficam em
`scripts/`. Todos importam de `scripts/fable_lib.py`, o núcleo de parsing e métricas.
Rode-os com `python3 scripts/<nome>.py`.

## Conceito-chave: TURNO LÓGICO

O Claude Code grava **cada bloco** de conteúdo do assistente em uma **linha** separada
(uma para o `thinking`, outra para o texto, outra para cada `tool_use`). Contar "por
linha" dilui o sinal — uma linha de texto puro tem 0 ferramenta.

Por isso a métrica é por **turno lógico**: *um prompt humano e tudo que o assistente fez
até o próximo prompt humano*. As linhas de `tool_result` no meio NÃO quebram o turno
(é o harness devolvendo a saída de uma ferramenta, não um humano falando).

## Achado honesto: raciocínio cifrado

O **texto** do raciocínio (`<thinking>`) NÃO fica nos logs — vem cifrado, só sobra a
`signature`. Então o que se mede é a **presença** do raciocínio por turno ("pensou antes
de agir?"), **não o conteúdo** do pensamento. Toda conclusão sobre "pensar antes" é sobre
frequência, não sobre o que foi pensado. Mantenha essa honestidade ao relatar resultados.

## O pipeline em 5 passos

Rode da pasta da skill. Os caminhos `--out` abaixo são sugestões; ajuste à vontade.

```bash
# 1) DEBLOAT — destila 1 sessão numa transcrição leve (remove tool_results, dumps,
#    anexos; ~74% menor). Útil para LER uma sessão antes de minerar tudo.
python3 scripts/debloat_jsonl.py CAMINHO/da/sessao.jsonl -o limpa.md --no-open

# 2) LISTAR MODELOS — quais modelos existem no SEU histórico e quantos turnos cada um.
python3 scripts/extract_corpus.py --list

# 3) EXTRAIR CORPUS — pega TODOS os turnos de 1 modelo de todo o histórico
#    (escreve transcript.md + stats.json) e imprime os números medidos.
python3 scripts/extract_corpus.py --model claude-fable-5

# 4) COMPARAR — 2 modelos lado a lado: o delta de ritmo. Salve o compare.json.
python3 scripts/compare_models.py --a claude-fable-5 --b claude-opus-4-8 --out compare.json

# 5) PLAYBOOK — transforma o delta num .md acionável, com os números reais injetados.
python3 scripts/make_playbook.py --from-json compare.json --out fable-mindset-playbook.md
```

Notas de uso:
- `extract_corpus.py --model X` e `compare_models.py --a X --b Y` aceitam `--projects /caminho`
  para apontar para outra pasta de logs (default: `~/.claude/projects`).
- `make_playbook.py` pode rodar direto do histórico (sem `--from-json`), medindo na hora;
  passar `--from-json compare.json` reaproveita uma medição já feita (mais rápido).
- **Amostras desiguais enganam.** Se um modelo tem MUITO mais histórico que o outro, use
  `compare_models.py --cap-turns N` para comparar ~N passos de cada — senão o delta vira
  artefato de amostra (o lado diluído cai). O script avisa quando os tamanhos divergem muito.
- O playbook NÃO copia o modelo de referência cegamente: ele **inverte** os hábitos
  fracos (verbosidade, over-thinking no trivial) em vez de replicá-los.

## O que cada métrica significa (e o que NÃO significa)

| métrica | definição | cuidado |
|---|---|---|
| **turno lógico** | 1 prompt humano → tudo até o próximo prompt humano | contar "por linha" dilui o sinal; por isso agrupamos em turnos lógicos. |
| **% turnos que pensam antes** | turnos lógicos com ≥1 bloco `thinking`/`redacted_thinking` | o **texto** do raciocínio vem cifrado — mede-se **presença**, não conteúdo. |
| **ferramentas/turno** (média/mediana) | nº de `tool_use` por turno lógico | mais ≠ melhor. Pode ser densidade de trabalho OU thrashing (idas-e-voltas). |
| **read-antes-de-edit** | edições cujo arquivo já tinha sido lido na sessão | heurística conservadora (casa por caminho de arquivo). |
| **teste-depois-de-edit** | sessões que rodaram teste após editar | heurística por regex de comando (`pytest`, `jest`, `go test`, `cargo test`…). |

Leitura honesta do delta: o sinal **robusto e transferível** costuma ser o
**pensar-antes-de-agir**. Os demais (read-before-edit, teste-depois-de-edit) são **boa
prática a importar**, não delta estatisticamente firme — principalmente se a amostra de um
dos modelos for pequena (o `make_playbook.py` já avisa quando < 30 sessões).

## Achado real de referência (e a lição de amostra)

Cuidado com o tamanho da amostra — é a parte mais fácil de errar. Numa primeira medição,
com uma amostra LOCAL pequena (7 sessões), o `claude-fable-5` aparecia pensando antes em
**99%** dos turnos vs **54%** do `claude-opus-4-8` (+45 pontos). Esse número era
**inflado**. Medindo em AMOSTRA GRANDE (≈4.900 passos do dataset aberto), o honesto é
**~85% vs 54% (+31 pontos)** — gap real, mas menor.

E a amostra pequena enganou nas DUAS direções: além de inflar o "pensar antes", ela
ESCONDEU o sinal mais forte — **teste-depois-de-edit: ~41% (Fable) vs ~2% (Opus)** — que
na amostra de 7 sessões dava 0%. As contagens de ferramentas/turno também NÃO confirmam
"Fable econômico": em amostra grande ele faz MAIS (~10/turno).

Lição: nunca conclua de amostra pequena; equilibre os tamanhos antes de comparar
(`compare_models.py --cap-turns N`) e confirme em amostra grande. Seus números vão variar;
o pipeline mede os **seus** dados.

## Sem dados próprios? Use o dataset aberto

Se você mal usou o modelo de referência e não tem sessões dele para minerar, há traces
públicos no Hugging Face. O `Glint-Research/Fable-5-traces` é um **dump cru de
`~/.claude/projects/`** — arquivos `.jsonl` no formato nativo do Claude Code (com os
blocos `thinking`/`tool_use` preservados), NÃO um chat achatado. Então roda o MESMO
exercício comportamental sobre dados de terceiros.

O importador baixa os `.jsonl` direto pela API do HF — **só stdlib, sem a lib
`datasets`** — e mede com o `fable_lib`:

```bash
python3 scripts/import_hf_traces.py --peek                # inspeciona (lista + modelos do 1º)
python3 scripts/import_hf_traces.py --out corpus_fable_hf # baixa tudo + escreve stats.json
python3 scripts/import_hf_traces.py --limit-files 30      # baixa no máx. N sessões
```

Foi assim que medimos o Fable em amostra grande (≈4.900 passos). Depois, monte um
`compare.json` com `{"a": <stats daqui>, "b": <stats do seu modelo>}` e rode
`make_playbook.py --from-json` (lado `a` = estes dados).

## Como injetar o playbook na sessão

O `fable-mindset-playbook.md` gerado é feito para ser lido pelo modelo no **início** da
sessão. Três formas, da mais automática à mais manual:

1. **Hook `SessionStart`** — configure um hook em `settings.json` que injeta o conteúdo do
   playbook no contexto a cada nova sessão. É o caminho mais automático e não depende de
   você lembrar.
2. **Skill** — coloque o playbook no corpo de uma skill (ou aponte para ele) cujo gatilho
   seja tarefas de código, para o modelo consultá-lo quando relevante.
3. **`CLAUDE.md`** — cole o playbook (ou um resumo dele) no `CLAUDE.md` do projeto, ou
   importe o arquivo. Simples e versionado junto do repo.

O objetivo em todos os casos é o mesmo: o modelo-alvo começa a sessão já com o ritmo do
modelo de referência nas partes que **transferem** (pensar antes de agir, ler antes de
editar, fechar o loop com teste), sem herdar os hábitos fracos.
