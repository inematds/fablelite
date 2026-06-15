# hooks/ — injetar o playbook automaticamente

O passo final do método: fazer o playbook entrar no contexto **sozinho**, no
começo de cada sessão. Três formas, da mais automática à mais simples.

## A) Hook `SessionStart` (injeção automática)

1. Torne o script executável:
   ```bash
   chmod +x ~/projetos/fablelite/hooks/inject-playbook.sh
   ```
2. Adicione ao `~/.claude/settings.json` (ou `.claude/settings.json` do projeto):
   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "matcher": "startup",
           "hooks": [
             { "type": "command", "command": "bash ~/projetos/fablelite/hooks/inject-playbook.sh" }
           ]
         }
       ]
     }
   }
   ```
3. Pronto. A cada nova sessão, o playbook entra como `additionalContext`.

> Quer apontar para outro playbook? Defina `FABLE_PLAYBOOK=/caminho/para/playbook.md`
> no ambiente. O hook é **fail-open**: se o arquivo não existir, a sessão segue normal.

## B) Skill

A skill `fable-mindset` (em `~/.claude/skills/fable-mindset/`) carrega o playbook
sob demanda e ainda traz os scripts. Use quando quiser invocar explicitamente em
vez de injetar sempre.

## C) `CLAUDE.md`

O caminho mais simples: cole o conteúdo do playbook (ou um link para ele) no seu
`CLAUDE.md` global ou de projeto. Ele já é auto-injetado em toda sessão.

---

### Qual escolher?

- **Sempre ativo, sem pensar** → hook `SessionStart` (A).
- **Sob demanda + os scripts juntos** → skill (B).
- **Mínimo esforço** → `CLAUDE.md` (C).
