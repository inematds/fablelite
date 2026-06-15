# Os 4 prompts do Mindset Fable (PT-BR, prontos pra colar)

Estes são os prompts do método, na ordem. Cada um corresponde a um script já
pronto neste repositório — você pode **colar o prompt** (e deixar o modelo
escrever o script) **ou** simplesmente rodar o script equivalente em `scripts/`.

> Onde vivem os logs: `~/.claude/projects/<projeto>/<sessão>.jsonl`.
> O campo de ouro: `message.model` — diz qual modelo escreveu cada turno.

---

## 1 · Debloat — destilar uma sessão  → `scripts/debloat_jsonl.py`

> A gordura nesses arquivos são os resultados das ferramentas, o conteúdo
> completo dos arquivos e a saída de comandos que são ecoados de volta para o
> contexto. Escreva para mim um pequeno script Python, `debloat_jsonl.py`, que
> pegue um arquivo de sessão do Claude Code em `~/.claude/projects` e reduza-o a
> uma transcrição leve. Mantenha minhas mensagens de usuário, as mensagens de
> texto do assistente, o modelo que escreveu cada turno e uma linha compacta por
> chamada de ferramenta mostrando o nome da ferramenta, e mantenha quaisquer
> blocos de raciocínio, se eles estiverem lá. Remova os payloads pesados dos
> resultados das ferramentas, os blobs de anexos e a contabilidade do harness.
> Quando terminar, execute-o em `demo_session.jsonl`, imprima o tamanho do
> arquivo antes e depois, e abra o arquivo reduzido para podermos ver a
> transcrição limpa.

**Equivalente pronto:** `python3 scripts/debloat_jsonl.py` (roda no `demo_session.jsonl`).

---

## 2 · Corpus por modelo + comportamento em números  → `scripts/extract_corpus.py`

> Cada turno do assistente registra qual modelo o escreveu, em um campo chamado
> `message.model`. Extraia todos os turnos que vieram do `claude-fable-5` do meu
> histórico completo, de todos os meus projetos, para um corpus combinado.
> Depois, analise como ele realmente se comportou, usando o que estiver
> registrado de forma confiável nos logs. Conte as mensagens do assistente e as
> minhas mensagens, o total de chamadas de ferramentas e quais ferramentas ele
> usou, quantas chamadas de ferramenta ele faz por turno e a ordem em que ele
> trabalha, como se ele lê um arquivo antes de editá-lo e se executa um teste
> depois das edições. Dê-me os padrões de comportamento como números reais
> medidos, não impressões.

**Equivalente pronto:** `python3 scripts/extract_corpus.py --model claude-fable-5`

---

## 3 · Comparar dois modelos + virar playbook  → `scripts/compare_models.py` + `scripts/make_playbook.py`

> Agora execute a mesma leitura comportamental exata nas minhas sessões do
> `claude-opus-4-8` e coloque as duas lado a lado. Mostre-me a distância no
> ritmo delas, a cadência das chamadas de ferramentas, as sequências de ações e
> as proporções, como leituras antes de edições e testes depois de edições.
> Depois, transforme essa diferença em um playbook, um único arquivo que eu
> possa apontar para o Opus 4.8, para que ele adote os padrões de tomada de
> decisão do Fable, as partes que se transferem para a produção. Seja honesto
> sobre onde o próprio Fable era fraco, para que o playbook corrija esse hábito
> em vez de copiá-lo.

**Equivalente pronto:**
```bash
python3 scripts/compare_models.py --a claude-fable-5 --b claude-opus-4-8 --out playbook/compare.json
python3 scripts/make_playbook.py --from-json playbook/compare.json --out playbook/fable-mindset-playbook.md
```

---

## 4 · Injetar o playbook no início da sessão  → `hooks/inject-playbook.sh`

> Quero usar os aprendizados de `fable-mindset-playbook.md` e quero que eles
> sejam sempre injetados no início da sessão:
>
> CC: `@"claude-code-guide (agent)"` Anexe um hook ao evento `SessionStart`
> para sempre injetar isso no contexto.

**Equivalente pronto:** veja `hooks/README.md` — hook `SessionStart` que lê o
playbook e o injeta como `additionalContext`. Alternativas: virar **skill**
(`~/.claude/skills/fable-mindset`) ou colar no `CLAUDE.md`.

---

## E se eu não tenho dados do Fable?

Use traces abertos no Hugging Face e rode o MESMO exercício:

```bash
pip install datasets
python3 scripts/import_hf_traces.py --dataset Glint-Research/Fable-5-traces
```
