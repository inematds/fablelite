"""
fable_lib.py — núcleo de parsing e métricas para a técnica "Fable Mindset".

Lê os arquivos de sessão JSONL do Claude Code (um evento JSON por linha) e expõe:

  - iter_events(path)        : itera eventos, ignorando linhas vazias/corrompidas
  - normalize_turn(event)    : transforma um evento bruto em um "turno" limpo
  - lightweight_lines(turn)  : linhas de transcrição leve (debloat)
  - Metrics                  : acumulador de comportamento (contagens, ordem, ratios)

Tudo aqui é dependência ZERO (só stdlib). Os 4 CLIs do curso importam deste módulo
para nunca duplicarem a lógica de leitura do log.

ONDE VIVEM OS LOGS
------------------
    ~/.claude/projects/<projeto-com-traços>/<session-uuid>.jsonl

Cada LINHA é um evento. Os que importam para nós:

    {"type":"user",      "message":{"role":"user", "content": ... }, "timestamp": ...}
    {"type":"assistant", "message":{"role":"assistant", "model":"claude-fable-5",
                                    "content":[ ...blocos... ]}, "timestamp": ...}

O campo de OURO é `message.model` — é ele que diz QUAL modelo escreveu cada turno.
É isso que permite filtrar "tudo que o claude-fable-5 fez" de "tudo que o opus fez".
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from glob import glob
from typing import Iterable, Iterator


# ----------------------------------------------------------------------------- #
# 1. Leitura bruta do log
# ----------------------------------------------------------------------------- #

def iter_events(path: str) -> Iterator[dict]:
    """Itera os eventos de UM arquivo .jsonl, pulando linhas vazias/inválidas.

    Logs reais às vezes têm uma linha truncada no fim (sessão morta no meio).
    Por isso engolimos JSONDecodeError em vez de explodir — queremos a
    transcrição que dá pra recuperar, não a perfeição.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def iter_project_files(projects_dir: str | None = None) -> Iterator[str]:
    """Todos os .jsonl em ~/.claude/projects (recursivo)."""
    base = projects_dir or os.path.expanduser("~/.claude/projects")
    yield from sorted(glob(os.path.join(base, "**", "*.jsonl"), recursive=True))


# ----------------------------------------------------------------------------- #
# 2. Normalização de um evento em "turno"
# ----------------------------------------------------------------------------- #

# Ferramentas que MEXEM em arquivo (alvo de edição)
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "NotebookRead"}
# Heurística de "rodou teste": comando shell que parece suíte de testes
TEST_RE = re.compile(
    r"\b(pytest|jest|vitest|mocha|go\s+test|cargo\s+test|"
    r"npm\s+(?:run\s+)?test|yarn\s+test|pnpm\s+test|rspec|phpunit|"
    r"python\s+-m\s+pytest|tox|ctest|gradle\s+test|mvn\s+test)\b",
    re.IGNORECASE,
)


@dataclass
class Turn:
    """Um turno normalizado — o que sobra depois de jogar fora a gordura."""
    ts: str = ""
    role: str = ""           # "user" | "assistant" | "system" | "summary"
    model: str = ""          # só preenchido em assistant: claude-fable-5, etc.
    texts: list = field(default_factory=list)      # texto humano legível
    thinking: list = field(default_factory=list)   # texto de raciocínio (quase sempre VAZIO nos logs)
    has_thinking: bool = False  # houve bloco thinking/redacted_thinking (mesmo sem texto)
    tools: list = field(default_factory=list)      # [{"name","summary"}]
    is_human: bool = False   # True = prompt de verdade do usuário
    is_tool_result: bool = False  # True = harness devolvendo saída de ferramenta
    is_meta: bool = False    # injeção do harness (não conta como humano)
    is_sidechain: bool = False  # turno de subagente


def _short_input(name: str, inp: dict) -> str:
    """Resumo de UMA linha do input de uma ferramenta — nunca o payload inteiro."""
    if not isinstance(inp, dict):
        return ""
    if name in EDIT_TOOLS or name in READ_TOOLS:
        return str(inp.get("file_path") or inp.get("path") or inp.get("notebook_path") or "")
    if name == "Bash":
        cmd = str(inp.get("command", "")).replace("\n", " ")
        return (cmd[:80] + "…") if len(cmd) > 80 else cmd
    if name in ("Grep", "Glob"):
        return str(inp.get("pattern", ""))[:80]
    if name == "Task":
        return str(inp.get("description") or inp.get("subagent_type") or "")[:80]
    if name == "Skill":
        return str(inp.get("skill") or inp.get("command") or "")[:80]
    if name in ("WebFetch", "WebSearch"):
        return str(inp.get("url") or inp.get("query") or "")[:80]
    # genérico: pega o 1º campo string curto, sem despejar payload
    for v in inp.values():
        if isinstance(v, str) and len(v) <= 80:
            return v
    return ""


def normalize_turn(event: dict) -> Turn:
    """Converte um evento bruto do log em um Turn enxuto.

    Aqui mora a regra de o que é SINAL e o que é GORDURA:
      - texto do usuário/assistente  -> sinal (mantém)
      - blocos `thinking`            -> sinal (mantém, é o raciocínio)
      - `tool_use`                   -> vira UMA linha (nome + alvo curto)
      - `tool_result`               -> GORDURA (descartado; marca is_tool_result)
      - anexos / file contents       -> GORDURA (nunca copiados)
    """
    t = Turn()
    t.ts = event.get("timestamp", "") or ""
    t.role = event.get("type", "") or ""
    t.is_meta = bool(event.get("isMeta"))
    t.is_sidechain = bool(event.get("isSidechain"))

    msg = event.get("message") or {}
    if isinstance(msg, dict):
        t.model = msg.get("model", "") or ""
        content = msg.get("content")
    else:
        content = msg

    # content como string pura (turno de usuário simples)
    if isinstance(content, str):
        if content.strip():
            t.texts.append(content.strip())
        if t.role == "user" and not t.is_meta:
            t.is_human = True
        return t

    if not isinstance(content, list):
        return t

    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype == "text":
            txt = (block.get("text") or "").strip()
            if txt:
                t.texts.append(txt)
        elif btype in ("thinking", "redacted_thinking"):
            # ACHADO IMPORTANTE: nos logs do Claude Code o texto do raciocínio
            # vem VAZIO (só fica a `signature` cifrada). Dá para minerar a
            # PRESENÇA do raciocínio (pensou antes de agir?), não o texto dele.
            t.has_thinking = True
            th = (block.get("thinking") or "").strip()
            if th:
                t.thinking.append(th)
        elif btype == "tool_use":
            name = block.get("name", "?")
            t.tools.append({"name": name, "summary": _short_input(name, block.get("input", {}))})
        elif btype == "tool_result":
            # GORDURA pesada: saída de ferramenta ecoada de volta. Descartamos.
            t.is_tool_result = True
        # qualquer outro tipo (image/document/attachment) = gordura, ignora

    # Um turno "user" é HUMANO de verdade se tem texto, não é tool_result e não é meta
    if t.role == "user" and t.texts and not t.is_tool_result and not t.is_meta:
        t.is_human = True
    return t


# ----------------------------------------------------------------------------- #
# 3. Transcrição leve (debloat)
# ----------------------------------------------------------------------------- #

def lightweight_lines(turn: Turn, keep_thinking: bool = True) -> list[str]:
    """Linhas de transcrição leve para UM turno. Vazio = nada a mostrar."""
    out: list[str] = []
    stamp = turn.ts[:19].replace("T", " ") if turn.ts else ""

    if turn.role == "user" and turn.is_human:
        for tx in turn.texts:
            out.append(f"### 🧑 USER  ·  {stamp}\n{tx}")
    elif turn.role == "assistant":
        head = f"### 🤖 {turn.model or 'assistant'}  ·  {stamp}"
        body: list[str] = [head]
        if keep_thinking and turn.thinking:
            for th in turn.thinking:
                body.append(f"<thinking>\n{th}\n</thinking>")
        elif keep_thinking and turn.has_thinking:
            # raciocínio presente porém cifrado: marca o ritmo, sem o texto
            body.append("🧠 _(raciocinou — texto cifrado no log)_")
        for tx in turn.texts:
            body.append(tx)
        for tool in turn.tools:
            sm = f" — {tool['summary']}" if tool["summary"] else ""
            body.append(f"  ⏵ `{tool['name']}`{sm}")
        # só emite se tiver algo além do cabeçalho
        if len(body) > 1:
            out.append("\n".join(body))
    return out


def debloat_file(path: str, keep_thinking: bool = True) -> str:
    """Transcrição leve de um arquivo de sessão inteiro, em Markdown."""
    chunks: list[str] = []
    for event in iter_events(path):
        turn = normalize_turn(event)
        chunks.extend(lightweight_lines(turn, keep_thinking=keep_thinking))
    return "\n\n".join(chunks) + "\n"


# ----------------------------------------------------------------------------- #
# 4. Métricas de comportamento (números reais, não impressões)
# ----------------------------------------------------------------------------- #

@dataclass
class Metrics:
    """Acumulador de comportamento de UM modelo, somado sobre N sessões."""
    model: str = ""
    sessions: int = 0
    assistant_turns: int = 0         # TURNOS LÓGICOS (1 prompt humano -> resposta inteira)
    assistant_lines: int = 0         # linhas-evento cruas do assistente (cada bloco é 1 linha)
    human_turns: int = 0
    thinking_turns: int = 0          # turnos lógicos com ≥1 bloco de raciocínio
    total_tool_calls: int = 0
    tools: Counter = field(default_factory=Counter)
    tools_per_turn: list = field(default_factory=list)  # 1 entrada por turno assistente
    # ordem de trabalho
    read_before_edit: int = 0        # edições precedidas por Read do mesmo arquivo
    edit_total: int = 0              # total de edições (denominador acima)
    test_after_edit_sessions: int = 0  # sessões que rodaram teste DEPOIS de editar
    sessions_with_edit: int = 0

    # --- agregação ---------------------------------------------------------- #
    def add_session(self, events: Iterable[dict]) -> None:
        """Acumula UMA sessão, agrupando linhas-evento em TURNOS LÓGICOS.

        Por que agrupar: o Claude Code grava cada bloco de conteúdo do assistente
        em uma LINHA separada (uma só p/ o thinking, outra p/ o texto, outra p/
        cada tool_use). Contar "por linha" dilui o sinal (texto puro tem 0
        ferramenta). Um TURNO LÓGICO = um prompt humano e tudo que o assistente
        fez até o próximo prompt humano. As linhas de tool_result no meio NÃO
        quebram o turno (são o harness devolvendo saída, não um humano).
        """
        self.sessions += 1
        files_read: set[str] = set()
        edited_in_session = False
        edit_seen_at: int | None = None
        test_after = False
        step = 0

        # acumuladores do turno lógico em aberto
        open_turn = False
        cur_tools = 0
        cur_think = False
        cur_lines = 0

        def close_turn() -> None:
            nonlocal open_turn, cur_tools, cur_think, cur_lines
            if open_turn and cur_lines > 0:
                self.assistant_turns += 1
                self.tools_per_turn.append(cur_tools)
                if cur_think:
                    self.thinking_turns += 1
            open_turn = False
            cur_tools = 0
            cur_think = False
            cur_lines = 0

        for event in events:
            turn = normalize_turn(event)

            if turn.role == "user" and turn.is_human:
                close_turn()           # fecha o turno anterior
                self.human_turns += 1
                open_turn = True        # abre o turno deste prompt
                continue
            if turn.role != "assistant":
                # tool_result / system / meta / attachment: fica DENTRO do turno
                continue

            # linha de assistente -> pertence ao turno lógico corrente
            if not open_turn:
                open_turn = True        # turno sem prompt humano antes (continuação)
            self.assistant_lines += 1
            cur_lines += 1
            if turn.has_thinking:
                cur_think = True

            for tool in turn.tools:
                step += 1
                name = tool["name"]
                target = tool["summary"]
                cur_tools += 1
                self.total_tool_calls += 1
                self.tools[name] += 1

                if name in READ_TOOLS and target:
                    files_read.add(target)
                if name in EDIT_TOOLS:
                    self.edit_total += 1
                    edited_in_session = True
                    if edit_seen_at is None:
                        edit_seen_at = step
                    if target and target in files_read:
                        self.read_before_edit += 1
                if name == "Bash" and TEST_RE.search(target or ""):
                    if edit_seen_at is not None and step > edit_seen_at:
                        test_after = True

        close_turn()  # fecha o último turno em aberto

        if edited_in_session:
            self.sessions_with_edit += 1
            if test_after:
                self.test_after_edit_sessions += 1

    # --- derivados (proporções) -------------------------------------------- #
    @property
    def avg_tools_per_turn(self) -> float:
        vals = [v for v in self.tools_per_turn]
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    @property
    def median_tools_per_turn(self) -> float:
        vals = sorted(self.tools_per_turn)
        if not vals:
            return 0.0
        n = len(vals)
        mid = n // 2
        return float(vals[mid]) if n % 2 else round((vals[mid - 1] + vals[mid]) / 2, 2)

    @property
    def read_before_edit_ratio(self) -> float:
        return round(self.read_before_edit / self.edit_total, 3) if self.edit_total else 0.0

    @property
    def test_after_edit_ratio(self) -> float:
        return (round(self.test_after_edit_sessions / self.sessions_with_edit, 3)
                if self.sessions_with_edit else 0.0)

    @property
    def thinking_ratio(self) -> float:
        return round(self.thinking_turns / self.assistant_turns, 3) if self.assistant_turns else 0.0

    def top_tools(self, n: int = 12) -> list[tuple[str, int]]:
        return self.tools.most_common(n)

    def as_dict(self) -> dict:
        return {
            "model": self.model,
            "sessions": self.sessions,
            "assistant_turns": self.assistant_turns,
            "assistant_lines": self.assistant_lines,
            "human_turns": self.human_turns,
            "thinking_turns": self.thinking_turns,
            "thinking_ratio": self.thinking_ratio,
            "total_tool_calls": self.total_tool_calls,
            "avg_tools_per_turn": self.avg_tools_per_turn,
            "median_tools_per_turn": self.median_tools_per_turn,
            "read_before_edit_ratio": self.read_before_edit_ratio,
            "test_after_edit_ratio": self.test_after_edit_ratio,
            "sessions_with_edit": self.sessions_with_edit,
            "top_tools": self.top_tools(),
        }


def collect_model_metrics(
    model: str,
    projects_dir: str | None = None,
    files: list[str] | None = None,
    cap_lines: int | None = None,
) -> Metrics:
    """Varre todos os projetos e acumula métricas SÓ dos turnos do `model`.

    Truque: uma mesma sessão pode misturar modelos. Para o cálculo de ordem
    (read-before-edit etc.) processamos a sessão inteira, mas só somamos os
    turnos do assistente cujo `message.model` bate com o alvo.

    `cap_lines`: se dado, PARA de acumular assim que o modelo atinge ~esse número
    de PASSOS (linhas-evento do assistente). Serve para comparar dois modelos em
    amostras do MESMO tamanho — sem isso, o modelo com histórico gigante domina e
    o delta vira artefato de amostra (ver `compare_models.py --cap-turns`).
    """
    m = Metrics(model=model)
    paths = files if files is not None else list(iter_project_files(projects_dir))
    for path in paths:
        events = list(iter_events(path))
        # a sessão "conta" para este modelo se ele escreveu algum turno aqui
        has_model = any(
            ev.get("type") == "assistant" and (ev.get("message") or {}).get("model") == model
            for ev in events
        )
        if not has_model:
            continue
        # filtra: mantém turnos humanos + turnos do assistente DESTE modelo
        filtered = [
            ev for ev in events
            if ev.get("type") != "assistant"
            or (ev.get("message") or {}).get("model") == model
        ]
        m.add_session(filtered)
        if cap_lines and m.assistant_lines >= cap_lines:
            break
    return m


def discover_models(projects_dir: str | None = None) -> Counter:
    """Histograma de quais modelos aparecem nos logs (e quantos turnos cada um)."""
    c: Counter = Counter()
    for path in iter_project_files(projects_dir):
        for ev in iter_events(path):
            if ev.get("type") == "assistant":
                mdl = (ev.get("message") or {}).get("model")
                if mdl:
                    c[mdl] += 1
    return c


def human_size(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"
