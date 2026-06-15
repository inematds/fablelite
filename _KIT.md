# _KIT.md — Build Kit do curso "Fable Lite" (INEMA.CLUB v2)

> **Para os agentes de Trilha 2 e Trilha 3.** A Trilha 1 (fundação) já está pronta.
> Você DEVE ser idêntico a ela: mesmo `<head>`, mesmo manifesto, mesmo nav, mesmo
> rodapé, mesmos snippets de learn.*, mesmas convenções `data-*`. Só MUDA: a cor da
> trilha, os textos/tópicos do seu conteúdo, e a trilha ativa no nav.
>
> **Antes de escrever HTML:** carregue a skill `formato-curso-v2`, leia
> `references/MASTER_COMPLETO.md`, `LEARN-LAYER.md`, `SVG-FUTURISTA.md`,
> `CHECKLIST_REVISAO.md`. Siga os 28 Erros Críticos à risca.
>
> **Referência viva:** copie a estrutura exata de
> `curso/trilha1/index.html`, `curso/trilha1/modulo-1-1.html`,
> `curso/trilha1/modulo-1-2.html` e `index.html` (landing). Quando em dúvida, abra esses arquivos.

---

## 0. Regras de OURO (não negociáveis)

1. **Caminhos relativos, NUNCA absolutos.** O site é servido em sub-path:
   `https://inematds.github.io/fablelite/`. Profundidade por página:
   - **Landing** (`/index.html`): assets = `assets/...`, links = `curso/trilhaX/...`.
   - **Index de trilha** (`/curso/trilhaX/index.html`): assets = `../../assets/...`,
     landing = `../../index.html`, irmãs = `../trilhaY/index.html`, módulos = `modulo-X-Y.html`.
   - **Módulo** (`/curso/trilhaX/modulo-X-Y.html`): IGUAL ao index de trilha (`../../`, `../trilhaY/`, `modulo-X-Y.html`).
   - **Teste mental cada link.** Nunca `href="/..."` nem `src="/..."`.
2. **Assets compartilhados já existem** em `/assets/learn.css` e `/assets/learn.js`
   (copiados verbatim da skill). **NÃO os recrie.** Apenas referencie por `<link>`/`<script src>` relativo.
3. **Anti-FOUC, manifesto e meta-course em TODA página** — idênticos (colar daqui).
4. **6 tópicos por módulo**, ids `topico-1`..`topico-6`, cada um com 3 seções
   (O que é / Por que aprender / Conceitos-chave) — nos cards do index — e nos
   módulos completos, seções ricas com VARIEDADE de componentes (500-800 linhas).
5. **≥1 SVG futurista inline por módulo** + **1 hero SVG no index de trilha** (cor da trilha + ciano).

---

## 1. Bloco `<head>` COMPLETO (copiar; trocar só o `<title>`, a cor de acento do anti-FOUC se desejar, e os comentários)

> Ordem obrigatória: **(1) meta-course → (2) anti-FOUC bloqueante → (3) manifesto →
> (4) Tailwind → (5) learn.css → (6) `<style>` base+light+dark+SVG**. O anti-FOUC vem
> ANTES do Tailwind. **Troque `REL`**: landing usa `assets`, trilha/módulo usam `../../assets`.

```html
<!DOCTYPE html>
<html lang="pt-BR" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="inema-course" content="fable-lite">
  <title>[TÍTULO DA PÁGINA] | Fable Lite</title>

  <!-- ANTI-FOUC: script BLOQUEANTE, ANTES do Tailwind e de qualquer <style>/<link> -->
  <script>
  (function () {
    try {
      var html = document.documentElement;
      var DEF = { theme: 'inema-dark', font: 'inter', fontScale: 100, lineWidth: 68, leading: 1.7, accent: 'emerald' };
      function clone(o) { var r = {}; for (var x in o) r[x] = o[x]; return r; }
      var p = clone(DEF);
      try {
        var raw = localStorage.getItem('inema.prefs');
        if (raw) { var parsed = JSON.parse(raw); if (parsed && typeof parsed === 'object') { for (var k in DEF) if (parsed[k] != null) p[k] = parsed[k]; } }
        else { var legacy = localStorage.getItem('theme'); if (legacy === 'light') p.theme = 'claro'; else if (legacy === 'dark') p.theme = 'inema-dark'; }
      } catch (e) { p = clone(DEF); }
      var THEMES = { 'inema-dark':{dark:true,attr:null,cs:'dark'},'claro':{dark:false,attr:null,cs:'light'},'sepia':{dark:false,attr:'sepia',cs:'light'},'foco':{dark:null,attr:'foco',cs:null},'contraste':{dark:true,attr:'contraste',cs:'dark'} };
      var t = THEMES[p.theme] || THEMES['inema-dark'];
      if (t.dark === true) html.classList.add('dark'); else if (t.dark === false) html.classList.remove('dark');
      if (t.attr) html.setAttribute('data-theme', t.attr); else html.removeAttribute('data-theme');
      html.style.colorScheme = (t.cs ? t.cs : (html.classList.contains('dark') ? 'dark' : 'light'));
      html.setAttribute('data-font', p.font || 'inter'); html.setAttribute('data-accent', p.accent || 'emerald');
      var s = html.style; var scale = (+p.fontScale || 100);
      s.setProperty('--inema-font-scale', (scale/100).toString()); s.setProperty('font-size', scale + '%');
      s.setProperty('--measure', (+p.lineWidth || 68) + 'ch'); s.setProperty('--lh-body', (+p.leading || 1.7).toString());
      var fam = p.font === 'system' ? 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif' : (p.font === 'leitura' ? '"Atkinson Hyperlegible", "Inter", system-ui, sans-serif' : '"Inter", system-ui, sans-serif');
      s.setProperty('--font-body', fam);
      var ACC = { emerald:[152,76,45], blue:[217,91,60], purple:[258,90,66], amber:[38,92,50], teal:[174,72,41], rose:[350,89,60] };
      var a = ACC[p.accent] || ACC.emerald;
      s.setProperty('--accent-h', a[0]+''); s.setProperty('--accent-s', a[1]+'%'); s.setProperty('--accent-l', a[2]+'%'); s.setProperty('--accent', 'hsl('+a[0]+' '+a[1]+'% '+a[2]+'%)');
    } catch (err) { try { document.documentElement.classList.add('dark'); document.documentElement.style.colorScheme = 'dark'; } catch (e) {} }
  })();
  </script>

  <!-- MANIFESTO DO CURSO (idêntico em TODAS as páginas — ver §2) -->
  <script type="application/json" data-inema-manifest>
  { ...COLE O JSON DA §2 AQUI... }
  </script>

  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = { darkMode: 'class', theme: { extend: { colors: { primary: '#FACC15', dark: { 900: '#111827', 800: '#1f2937', 700: '#374151', 600: '#4b5563' } } } } }
  </script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="REL/assets/learn.css">   <!-- REL = assets (landing) ou ../../assets (trilha/módulo) -->
  <style>
    body { font-family: 'Inter', sans-serif; }
    .dark body { background-color: #111827; }
    .topic-explanation { display: none; }
    .topic-explanation.active { display: block; }
    html:not(.dark) svg[role="img"] { filter: saturate(0.82) brightness(0.96); }

    /* Pulso dos SVGs (módulos) — só sem reduce-motion */
    @keyframes wf-pulse { 0%,100% { opacity:.55 } 50% { opacity:1 } }
    @media (prefers-reduced-motion: no-preference) {
      .wf-a { animation: wf-pulse 2.6s ease-in-out infinite; }
      .wf-a:nth-child(2){animation-delay:.25s} .wf-a:nth-child(3){animation-delay:.5s} .wf-a:nth-child(4){animation-delay:.75s}
    }

    /* ===== Light mode base ===== */
    html:not(.dark) body { background-color: #f8fafc; }
    html:not(.dark) .bg-dark-900 { background-color: #ffffff; }
    html:not(.dark) .bg-dark-800 { background-color: #f9fafb; }
    html:not(.dark) .bg-dark-700 { background-color: #f3f4f6; }
    html:not(.dark) .bg-dark-600 { background-color: #e5e7eb; }
    html:not(.dark) .text-neutral-100 { color: #111827; }
    html:not(.dark) .text-neutral-300 { color: #4b5563; }
    html:not(.dark) .text-neutral-400 { color: #6b7280; }
    html:not(.dark) .text-neutral-500 { color: #9ca3af; }
    html:not(.dark) .border-dark-600 { border-color: #d1d5db; }
    html:not(.dark) .border-dark-700 { border-color: #e5e7eb; }

    /* ===== Light mode — cor de ACENTO DA SUA TRILHA (ver §6) ===== */
    /* T2 = blue → #2563eb (37,99,235);  T3 = purple → #7c3aed (124,58,237) */
    html:not(.dark) .text-COR-400 { color: VALOR_LIGHT; }
    html:not(.dark) .bg-COR-500\/20 { background-color: rgba(R,G,B,0.12); }
    html:not(.dark) .bg-COR-500\/10 { background-color: rgba(R,G,B,0.08); }
    html:not(.dark) .border-COR-500\/30 { border-color: rgba(R,G,B,0.25); }
    html:not(.dark) .hover\:bg-COR-500\/30:hover { background-color: rgba(R,G,B,0.18); }
    html:not(.dark) .hover\:text-COR-400:hover { color: VALOR_LIGHT; }
    html:not(.dark) .hover\:bg-COR-500\/10:hover { background-color: rgba(R,G,B,0.08); }
    /* + inclua emerald/blue/purple-hover usados no NAV das outras trilhas */

    /* Remove gradientes + cores especiais */
    html:not(.dark) [class*="bg-gradient-to"] { background-image: none !important; }
    html:not(.dark) .text-primary { color: #a16207; }
    html:not(.dark) .bg-primary\/10 { background-color: rgba(161,98,7,0.08); }
    html:not(.dark) .border-primary\/40 { border-color: rgba(161,98,7,0.25); }
    html:not(.dark) .border-primary\/30 { border-color: rgba(161,98,7,0.22); }
    html:not(.dark) .text-sky-400 { color: #0369a1; }
    html:not(.dark) .text-yellow-400 { color: #a16207; }
    html:not(.dark) .text-red-400 { color: #b91c1c; }
    html:not(.dark) .hover\:text-sky-300:hover { color: #0284c7; }
    html:not(.dark) .hover\:text-yellow-300:hover { color: #854d0e; }
    html:not(.dark) .bg-dark-900\/95 { background-color: rgba(255,255,255,0.95); }

    /* ===== Bordas suavizadas no DARK (ambas as regras — Erro #15) ===== */
    .dark .border-dark-600 { border-color: #374151; }
    .dark .divide-dark-600 > :not([hidden]) ~ :not([hidden]) { border-color: #374151; }

    [id] { scroll-margin-top: 5rem; }   /* nav sticky = ~3.5rem; folga p/ foco/âncora (Erro #25) */
  </style>
</head>
```

> **Landing:** inclua as cores de acento das TRÊS trilhas (emerald+blue+purple) + hover + group-hover.
> **Index/módulo de trilha:** inclua a cor da SUA trilha completa + as outras 2 só com `text-COR-400`/`hover` (para o nav).

---

## 2. MANIFESTO JSON (idêntico em TODA página — cole sem alterar)

```json
{
  "course": "fable-lite",
  "tracks": [
    { "n": "1", "title": "Os Logs São Ouro", "modules": [
      { "id": "1-1", "title": "Onde Vivem as Conversas e a Anatomia de uma Sessão", "topics": 6, "href": "curso/trilha1/modulo-1-1.html" },
      { "id": "1-2", "title": "Gordura vs Ouro — e o Mito do Raciocínio Minerável", "topics": 6, "href": "curso/trilha1/modulo-1-2.html" }
    ]},
    { "n": "2", "title": "A Mão na Massa", "modules": [
      { "id": "2-1", "title": "Debloat: Destilando a Transcrição", "topics": 6, "href": "curso/trilha2/modulo-2-1.html" },
      { "id": "2-2", "title": "Corpus, Números e o Delta Fable vs Opus", "topics": 6, "href": "curso/trilha2/modulo-2-2.html" }
    ]},
    { "n": "3", "title": "Do Delta ao Playbook", "modules": [
      { "id": "3-1", "title": "Escrevendo o Playbook", "topics": 6, "href": "curso/trilha3/modulo-3-1.html" },
      { "id": "3-2", "title": "Injetando no Modelo (e Sem Dados Próprios)", "topics": 6, "href": "curso/trilha3/modulo-3-2.html" }
    ]}
  ]
}
```

- `topics` é a CONTAGEM de `[data-inema-topic]` reais do módulo. Como cada módulo tem
  6 tópicos, `topics: 6` em todos. **Se você mudar o nº de tópicos, atualize o manifesto
  em TODAS as páginas** (e ele tem que bater com o DOM, senão o % do curso fica errado — Erro #28).
- `course` casa com `<meta name="inema-course" content="fable-lite">`. `n`/`id` casam com `data-inema-track`/`data-inema-module`.

---

## 3. NAV (idêntico em TODAS as páginas — só muda a TRILHA ATIVA e os caminhos)

```html
<nav class="sticky top-0 z-50 bg-dark-900/95 backdrop-blur-sm border-b border-dark-600">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-center h-14">
      <div class="flex items-center space-x-4">
        <a href="REL_HOME/index.html" class="flex items-center space-x-2 text-yellow-400 hover:text-yellow-300">
          <span class="text-2xl">✨</span><span class="font-bold text-lg hidden sm:inline">Fable Lite</span>
        </a>
        <span class="text-neutral-600">|</span>
        <a href="https://inema.club" target="_blank" rel="noopener" class="text-sky-400 hover:text-sky-300 text-sm font-medium">INEMA.CLUB</a>
      </div>
      <div class="flex items-center space-x-1 sm:space-x-2">
        <!-- 3 botões de trilha. O DA PÁGINA ATUAL fica ativo: text-COR-400 bg-COR-500/10. Os outros: text-neutral-400 hover:text-COR-400 hover:bg-COR-500/10 transition-colors -->
        <a href="REL_T1" class="px-3 py-1.5 rounded-lg text-sm font-semibold {ATIVO? text-emerald-400 bg-emerald-500/10 : text-neutral-400 hover:text-emerald-400 hover:bg-emerald-500/10 transition-colors}">
          <span class="sm:hidden">T1</span><span class="hidden sm:inline">Os Logs São Ouro</span>
        </a>
        <a href="REL_T2" class="px-3 py-1.5 rounded-lg text-sm font-semibold {ATIVO? text-blue-400 bg-blue-500/10 : text-neutral-400 hover:text-blue-400 hover:bg-blue-500/10 transition-colors}">
          <span class="sm:hidden">T2</span><span class="hidden sm:inline">A Mão na Massa</span>
        </a>
        <a href="REL_T3" class="px-3 py-1.5 rounded-lg text-sm font-semibold {ATIVO? text-purple-400 bg-purple-500/10 : text-neutral-400 hover:text-purple-400 hover:bg-purple-500/10 transition-colors}">
          <span class="sm:hidden">T3</span><span class="hidden sm:inline">Do Delta ao Playbook</span>
        </a>
        <button type="button" data-inema-journey-open class="hidden sm:inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-neutral-300 hover:text-neutral-100 transition-colors text-sm">
          <span aria-hidden="true">◷</span><span>Minha jornada</span>
          <span class="inema-journey-badge hidden" data-inema-journey-badge data-count="0" aria-hidden="true"></span>
        </button>
        <button type="button" data-inema-appearance-toggle="[data-inema-appearance]" aria-expanded="false" class="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors" title="Aparência"><span aria-hidden="true">◑</span></button>
        <div data-inema-appearance class="inema-appearance-pop"></div>
        <button id="theme-toggle" class="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors" title="Tema claro/escuro">
          <svg id="theme-toggle-dark-icon" class="hidden w-5 h-5 text-neutral-300" fill="currentColor" viewBox="0 0 20 20"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path></svg>
          <svg id="theme-toggle-light-icon" class="hidden w-5 h-5 text-neutral-300" fill="currentColor" viewBox="0 0 20 20"><path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" fill-rule="evenodd" clip-rule="evenodd"></path></svg>
        </button>
      </div>
    </div>
  </div>
</nav>
```

**Caminhos por profundidade:**
| Token | Landing | Index de trilha / Módulo |
|---|---|---|
| `REL_HOME` | `.` (→ `index.html`) | `../..` (→ `../../index.html`) |
| `REL_T1` | `curso/trilha1/index.html` | `../trilha1/index.html` (ou `index.html` se você é a T1) |
| `REL_T2` | `curso/trilha2/index.html` | `../trilha2/index.html` (ou `index.html` se você é a T2) |
| `REL_T3` | `curso/trilha3/index.html` | `../trilha3/index.html` (ou `index.html` se você é a T3) |

> Na SUA própria trilha, o botão dela aponta para `index.html` (mesma pasta) e fica ativo.

---

## 4. RODAPÉ + CTA INEMA.CLUB

**Rodapé (toda página):**
```html
<footer class="border-t border-dark-600 py-8">
  <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-neutral-500 text-sm">
    <p>Fable Lite · <a href="https://inema.club" target="_blank" rel="noopener" class="text-sky-400 hover:text-sky-300">INEMA.CLUB</a> · 2026</p>
  </div>
</footer>
```

**CTA INEMA.CLUB (use na landing e onde fizer sentido fechar um bloco) — troque emerald pela cor da trilha:**
```html
<section class="mb-8">
  <div class="bg-gradient-to-br from-COR-900/40 via-dark-800 to-dark-800 rounded-xl border border-COR-500/30 p-8 text-center">
    <h2 class="text-2xl font-bold mb-3">[CHAMADA]</h2>
    <p class="text-neutral-300 mb-6 max-w-2xl mx-auto inema-prose">Este curso é parte da comunidade INEMA.CLUB — pesquisa, educação e experimentos com IA aplicada.</p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="[PRÓXIMO]" class="px-6 py-3 bg-COR-600 hover:bg-COR-500 text-white rounded-lg font-semibold transition-colors">[AÇÃO] →</a>
      <a href="https://inema.club" target="_blank" rel="noopener" class="px-6 py-3 bg-dark-700 hover:bg-dark-600 text-sky-400 rounded-lg font-semibold transition-colors">Visitar INEMA.CLUB</a>
    </div>
  </div>
</section>
```

---

## 5. learn.js + INEMA.init() (FIM do `<body>`, depois do JS-núcleo v1)

**5.1 — JS-núcleo v1 (cole ANTES do learn.js; igual em todas as páginas):**
```html
<script>
  function toggleTopic(button) {
    const topicItem = button.closest('.topic-item'); if (!topicItem) return;
    const explanation = topicItem.querySelector('.topic-explanation');
    const moduleCard = button.closest('.bg-dark-800') || document;
    moduleCard.querySelectorAll('.topic-explanation.active').forEach(exp => { if (exp !== explanation) exp.classList.remove('active'); });
    const willOpen = !explanation.classList.contains('active');
    explanation.classList.toggle('active');
    button.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
  }
  function openModal(modalId) { const m = document.getElementById(modalId); if (m) { m.classList.remove('hidden'); document.body.style.overflow = 'hidden'; } }
  function closeModal() { document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden')); document.body.style.overflow = 'auto'; }
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
  (function () {
    const themeToggle = document.getElementById('theme-toggle');
    const darkIcon = document.getElementById('theme-toggle-dark-icon');
    const lightIcon = document.getElementById('theme-toggle-light-icon');
    const html = document.documentElement;
    function sync() { const isDark = html.classList.contains('dark'); darkIcon.classList.toggle('hidden', !isDark); lightIcon.classList.toggle('hidden', isDark); }
    sync();
    themeToggle.addEventListener('click', () => {
      const goDark = !html.classList.contains('dark');
      if (window.INEMA && INEMA.setPref) INEMA.setPref('theme', goDark ? 'inema-dark' : 'claro');
      else { html.classList.toggle('dark'); localStorage.setItem('theme', goDark ? 'dark' : 'light'); }
      sync();
    });
    document.addEventListener('inema:progress', sync);
  })();
</script>
```

**5.2 — Camada de aprendizagem (cole por último; REL = `assets` na landing, `../../assets` em trilha/módulo):**
```html
<script src="REL/assets/learn.js"></script>
<script>if (window.INEMA && typeof window.INEMA.init === 'function') { window.INEMA.init(); }</script>
```
> `init()` é idempotente, feature-detect (só ativa o que tem `data-*`), e modo-efêmero se storage bloqueado.

---

## 6. Tokens de COR por trilha (onde trocam)

| Trilha | Slug Tailwind | dark `text-*-400` | light mode | rgb (bg/border) | hero gradiente | SVG primária / forte / fill |
|---|---|---|---|---|---|---|
| **T1** (pronta) | `emerald` | `#34d399` | `#059669` | `5,150,105` | `from-emerald-900/30` | `#34d399` / `#10b981` / `#0e2018` |
| **T2** (você) | `blue` | `#60a5fa` | `#2563eb` | `37,99,235` | `from-blue-900/30` | `#60a5fa` / `#3b82f6` / `#0e1622` |
| **T3** (você) | `purple` | `#c084fc` | `#7c3aed` | `124,58,237` | `from-purple-900/30` | `#c084fc` / `#a855f7` / `#1a1230` |

**Onde a cor troca (substitua TODAS as ocorrências de `emerald` da T1 pela sua):**
- Badge da trilha/módulo, header gradiente (`from-COR-900/30`), números em círculo,
  botões "Ver Completo"/"Marcar como lido"/CTA, hover dos cards, medidores `text-COR-400`,
  `border-COR-500/30`, `bg-COR-500/20`, TOC hover, breadcrumb hover, botão ativo no nav.
- **Bloco light-mode do `<style>`:** troque o bloco de acento (`text-COR-400`, `bg-COR-500/20`...) pela tabela acima.
- **SVGs:** primária = cor da trilha (tabela), secundária = **ciano `#38bdf8`** SEMPRE.
- **Ciano `#38bdf8` é constante** (agentes / ramo paralelo / fluxo de volta) — não troca.

**Cor fixa em qualquer trilha:** primary/yellow `#FACC15` (logo/dicas), sky `text-sky-400` (INEMA.CLUB), red `text-red-400` (não-fazer).

---

## 7. O que CADA agente de trilha deve produzir

### Trilha 2 — `curso/trilha2/` (cor BLUE) "A Mão na Massa"
- `index.html` — index da trilha: nav (T2 ativa), header + **1 hero SVG** (azul+ciano),
  progresso da trilha, **Mapa da trilha** (h2 `Mapa da trilha` + 2 cards-âncora `#modulo-2-1`/`#modulo-2-2`),
  h2 `Conteúdo detalhado`, 2 cards de módulo (cada um com 6 tópicos expansíveis de 3 seções,
  botões `Ver em Modal` + `Ver Completo` em `justify-start`), 2 modais com `<iframe>`, navegação T1↔T3, rodapé.
- `modulo-2-1.html` "Debloat: Destilando a Transcrição" — 6 tópicos:
  1. O que o debloat remove (a gordura na prática) · 2. O que preserva (o ouro) ·
  3. Antes/depois numa sessão real (~74%) · 4. `debloat_jsonl.py` por dentro (stdlib pura) ·
  5. A transcrição leve resultante (formato legível) · 6. Rodando no seu histórico vs no demo.
- `modulo-2-2.html` "Corpus, Números e o Delta Fable vs Opus" — 6 tópicos:
  1. `extract_corpus.py` — filtrar por modelo · 2. As métricas (turno lógico, % pensa-antes, ferr./turno, read-antes-de-edit, teste-depois-de-edit) ·
  3. **Os números reais** (Fable 99% vs Opus 54%; 6,57 vs 7,86 ferr./turno) · 4. O delta forte e transferível (+45 pontos) ·
  5. `compare_models.py` e o `compare.json` · 6. Cuidado com amostra pequena / o que NÃO afirmar.

### Trilha 3 — `curso/trilha3/` (cor PURPLE) "Do Delta ao Playbook"
- `index.html` — igual em estrutura à T2, cor purple, hero SVG roxo+ciano, Mapa com `#modulo-3-1`/`#modulo-3-2`, navegação T2↔(landing).
- `modulo-3-1.html` "Escrevendo o Playbook" — 6 tópicos:
  1. Do delta à regra (transformar número em instrução) · 2. `make_playbook.py` e o `.md` acionável ·
  3. Anatomia de uma regra de playbook · 4. "Pense antes de agir" como regra-âncora · 5. O que NÃO virar regra (sinais fracos) · 6. Versionar e revisar o playbook.
- `modulo-3-2.html` "Injetando no Modelo (e Sem Dados Próprios)" — 6 tópicos:
  1. Três canais de injeção: hook / skill / CLAUDE.md · 2. O hook `SessionStart` (`hooks/inject-playbook.sh`) ·
  3. Injetar via skill · 4. Injetar via CLAUDE.md · 5. **Sem dados próprios:** `import_hf_traces.py` + dataset `Glint-Research/Fable-5-traces` (HF) · 6. Medir o efeito (o loop fecha).

**Cada módulo:** 500-800 linhas, 6 seções ricas com VARIEDADE (≥2 grids ✓/✗, ≥1 timeline,
≥2 tip boxes, ≥1 code/mono box), **≥1 SVG futurista inline**, TOC+scrollspy, `data-inema-read-toggle`
por seção, `data-inema-doubt-toggle` por tópico, `data-inema-block` na prosa, resumo final + navegação.

---

## 8. Números reais + achado honesto (REUSE nos módulos — são verídicos)

- **Pensar-antes-de-agir:** Fable-5 = **99%** dos turnos lógicos · Opus-4.8 = **54%** → **delta +45 pontos** (o sinal FORTE e transferível).
- **Ferramentas/turno:** Fable-5 = **6,57** · Opus-4.8 = **7,86** (Fable foi mais econômico).
- **Debloat:** reduz uma sessão típica em **~74%**.
- **Amostra:** Fable = 7 sessões / 69 turnos lógicos (PEQUENA — não exagere os outros sinais); Opus = 1114 sessões.
- **ACHADO HONESTO (diferencial do curso):** o TEXTO do `thinking` vem **VAZIO/cifrado** nos logs (só a `signature`).
  Você **não** minera o pensamento literal — minera a **PRESENÇA** do raciocínio + o **texto visível** + a **sequência de ferramentas** (o *ritmo*).
- **Honestidade metodológica:** só "pensa-antes-de-agir" é delta firme; read-antes-de-edit e teste-depois-de-edit
  são boa prática medida por heurística conservadora, não delta robusto.

**Links a citar:** `scripts/` (este repo, README em `scripts/README.md`) · dataset aberto
`Glint-Research/Fable-5-traces` → `https://huggingface.co/datasets/Glint-Research/Fable-5-traces` · `https://inema.club`.

---

## 9. Convenção `data-inema-*` (contrato de ancoragem — NÃO improvise IDs)

```html
<!-- meta no <head> de TODA página -->
<meta name="inema-course" content="fable-lite">

<!-- HEADER do módulo (ou card exterior) -->
<header id="modulo-X-Y" data-inema-module="X-Y" data-inema-track="N"> … </header>

<!-- cada SEÇÃO de tópico no módulo completo -->
<section id="topico-N" data-inema-topic="modulo-X-Y#topico-N"> … </section>

<!-- prosa anotável (mX-Y-tN-pK = módulo-tópico-parágrafo, determinístico) -->
<p data-inema-block="mX-Y-tN-pK"> … </p>

<!-- marcar lido (justify-start! Erro #1 e #20) -->
<div class="flex justify-start mt-6">
  <button type="button" data-inema-read-toggle aria-pressed="false"
    class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-COR-500/20 border border-COR-500/30 text-COR-400 hover:bg-COR-500/30 transition-colors">
    <span class="inema-read-icon" aria-hidden="true">○</span><span class="inema-read-label">Marcar como lido</span>
  </button>
</div>

<!-- dúvida rápida (no header do tópico) -->
<button type="button" data-inema-doubt-toggle aria-pressed="false" title="Marcar dúvida neste tópico"
  class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-dark-700 border border-dark-600 text-neutral-300 hover:bg-dark-600 transition-colors text-sm">
  <span aria-hidden="true">?</span><span>Tenho dúvida</span></button>

<!-- medidores: escopo curso | trilha:N | modulo:X-Y -->
<div data-inema-meter="modulo:X-Y" class="inema-meter ..." role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-label="...">
  <span data-inema-meter-pct>0%</span>
  <div class="inema-bar"><div class="inema-bar__fill" data-inema-meter-fill></div></div>
  <span data-inema-meter-frac>0 de 0</span>
</div>

<!-- TOC + scrollspy (módulo) -->
<nav data-inema-toc aria-label="Índice da página">…<span data-inema-section-counter>1 de 6</span>… <a href="#topico-1" class="inema-toc-link">…</a></nav>
```

**Regras:** `data-inema-topic` é o id ESTÁVEL (não muda com layout/tema). IDs do módulo no
manifesto = `X-Y` (ex.: `2-1`), tópicos = `modulo-X-Y#topico-N`. Os accordions do INDEX
mantêm `onclick="toggleTopic(this)"` + `aria-expanded`/`aria-controls`.

---

## 10. Checklist rápido antes de entregar (Erros #1-#28)

- [ ] **#1** Botões de ação (módulo/read-toggle) em `flex justify-start` (nunca `justify-center space-x`).
- [ ] **#2** Números em círculo nos tópicos (nunca `▶`/seta).
- [ ] **#3/#11** 6 tópicos por módulo; cada tópico-card com 3 seções (O que é/Por que/Conceitos).
- [ ] **#4** INEMA.CLUB `text-sky-400` em toda página.
- [ ] **#5** Light-mode CSS completo (base + acento da trilha + sem gradiente + especiais + nav).
- [ ] **#6/#9** Título de módulo `text-2xl font-bold`; todos os cards do index com tópicos expansíveis.
- [ ] **#10** Cada card do index com `<a href="modulo-X-Y.html">Ver Completo</a>`.
- [ ] **#12** Index: h2 `Mapa da trilha` + cards-âncora (`justify-between`, X.Y esq + duração dir, emoji+título, subtítulo PUNCHY, sem círculo extra) + `id="modulo-X-Y"` nos cards grandes.
- [ ] **#13** Nav completo idêntico em TODAS as páginas (trilha ativa destacada).
- [ ] **#14** Módulos 500-800 linhas com VARIEDADE de componentes (não template 6x).
- [ ] **#15** Dark: ambas regras `.border-dark-600` E `.divide-dark-600 > ...` com `#374151`.
- [ ] **#16** Divisor "Conteúdo detalhado" = h2 simples.
- [ ] **#17** ≥1 SVG futurista inline por módulo + 1 hero SVG no index (cor da trilha + ciano, `role="img"`+`aria-label`, glow só na caixa-foco, `html:not(.dark) svg[role="img"]{filter:...}`).
- [ ] **#18** Anti-FOUC bloqueante separado no topo do `<head>`, acima do Tailwind, try/catch, default dark.
- [ ] **#19** `data-inema-course`/`-module`/`-track`/`-topic`/`-block` estáveis.
- [ ] **#20** Marcar-lido `<button aria-pressed>` + `justify-start` + teclado.
- [ ] **#21/#28** Manifesto idêntico em TODA página; `topics` bate com os `data-inema-topic` reais; medidores curso/trilha/módulo.
- [ ] **#22** Export/import via learn.js (não recriar; só plugar a jornada).
- [ ] **#23** Contraste por tema; ambar nunca como TEXTO em superfície clara; bridge de chrome via learn.css carregada.
- [ ] **#24** Highlight via learn.js (TreeWalker) — só plugar `data-inema-block`.
- [ ] **#25** `scroll-margin-top` nos `[id]`; jornada (learn.js) com foco preso.
- [ ] **#26** Modo efêmero garantido pelo learn.js (não quebra sem storage).
- [ ] **#27** `@media (prefers-reduced-motion)` nos SVGs animados.
- [ ] **Caminhos relativos** corretos por profundidade; ZERO `href="/..."`/`src="/..."`.

---

**Fundação entregue:** `index.html` (landing), `assets/learn.css`, `assets/learn.js`,
`curso/trilha1/index.html`, `curso/trilha1/modulo-1-1.html`, `curso/trilha1/modulo-1-2.html`.
Copie a estrutura exata desses arquivos. Boa construção. — INEMA.CLUB
