# Playbook do Mindset Fable — para claude-opus-4-8

> Gerado por `make_playbook.py` a partir do delta medido entre **claude-fable-5** e
> **claude-opus-4-8** nas SUAS próprias sessões (`~/.claude/projects`). Números medidos,
> não impressões. Aponte este arquivo para o claude-opus-4-8 (hook `SessionStart`, skill
> ou `CLAUDE.md`) para ele adotar o ritmo do Fable nas partes que transferem.

> ⚠️ **Amostra pequena de Fable (7 sessões).** Trate `read-antes-de-edit` e `teste-depois-de-edit` como BOA PRÁTICA a importar, não como delta estatisticamente firme. O sinal robusto aqui é o raciocínio-antes-de-agir.

## O delta, em números

| sinal | claude-fable-5 | claude-opus-4-8 | leitura |
|---|---|---|---|
| **% de turnos que pensam antes de agir** | **99%** | 54% | **+45 pp — o sinal forte. Pense primeiro.** |
| ferramentas por turno (média) | 6.57 | 7.86 | o Fable foi mais ECONÔMICO: menos ferramentas por turno (6.57 vs 7.86 do claude-opus-4-8) e ainda assim resolvia — densidade, não thrashing. |
| read-antes-de-edit | 34% | 38% | boa prática (heurística conservadora). |
| teste-depois-de-edit | 0% | 3% | boa prática (amostra ruidosa). |

> **Honestidade sobre os dados:** o TEXTO do raciocínio não fica nos logs (vem
> cifrado, só a `signature`). O que medimos é a **presença** do raciocínio por
> turno — "pensou antes de agir?" — não o conteúdo do pensamento.

## Regras (o que TRANSFERE do Fable) — em ordem de força do sinal

1. **Pense antes de agir.** Em qualquer tarefa não-trivial, gaste 2–5 linhas
   planejando o caminho ANTES da primeira ferramenta. Este é o delta robusto:
   o Fable raciocinava em **99%** dos turnos contra **54%**
   do claude-opus-4-8 (+45 pontos). É a maior alavanca e a que mais transfere.

2. **Seja econômico com ferramentas — densidade, não agitação.** Medido:
   o Fable foi mais ECONÔMICO: menos ferramentas por turno (6.57 vs 7.86 do claude-opus-4-8) e ainda assim resolvia — densidade, não thrashing. A meta não é "fazer mais chamadas"; é cada chamada ter propósito.
   Quando há chamadas independentes (ler 3 arquivos sem dependência), faça-as no
   MESMO turno em vez de uma ida-e-volta por arquivo.

3. **Leia antes de editar — sempre.** Nunca edite um arquivo que você não leu
   neste contexto. (Os dois modelos ficaram modestos aqui — ~34%/38% —
   então é uma disciplina a SUBIR para 100%, não a copiar do Fable.)

4. **Feche o loop: teste/build depois de editar.** Editou código? Rode a suíte
   ou o build e relate o resultado REAL. Não declare "pronto" sem verificar.

5. **Sequência canônica:** entender → planejar (em texto) → ler os alvos →
   editar cirúrgico → verificar (teste/build) → relatar com o output real.

6. **Pare quando tiver o suficiente para agir.** Não re-derive fatos já
   estabelecidos nem pesquise opções que você não vai seguir.

## Onde o Fable era FRACO (NÃO copie isto)

> Um playbook honesto corrige o hábito ruim em vez de replicá-lo.

- **Over-thinking no trivial.** Raciocinar em 99% dos turnos é ótimo
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
