# AI Presence

[![AI Presence](guia/assets/banner-en.jpg)](https://inematds.github.io/presenca-na-ia/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## What it is

**Presence in AI** is a free kit for offering businesses a service to organize their presence in AI tools: registering with the ChatGPT Business Directory (launched in beta by OpenAI on 11/10/2026), verifying that the business belongs to its owner, preparing a profile with accurate information, and monitoring it every month. It’s designed for people working in technology, digital marketing, consulting, or agencies. It includes a “before” diagnosis, a client checklist, a proposal, a monthly report, and a ready-to-use prompt for an AI to put everything together with you.

Businesses will pay to appear in ChatGPT. A client asks AI who provides a service in their city, but the business doesn’t appear—or another business with a similar name does. Almost no business owners know they can fix this.

## 📖 User guide

Full guide (landing page + step-by-step instructions): **https://inematds.github.io/presenca-na-ia/guia/en/**

## Companion kit: step-by-step registration

The step-by-step guide to registering with the Business Directory, using real screens from our case (INEMATDS) and an agent that handles registration in the browser, is in **[inematds/empresa-no-chatgpt](https://github.com/inematds/empresa-no-chatgpt)** ([guide](https://inematds.github.io/empresa-no-chatgpt/guia/en/)). This repo is the **service** layer: how to diagnose, sell, deliver, and monitor this service for other businesses.

## Based on

- **OpenAI, “Businesses in ChatGPT” (11/10/2026):** beta; in the Business Directory, businesses can claim their profile, update their information, and see mentions, website clicks, and the topics they appear for; 1.2 billion people use ChatGPT each week. https://openai.com/pt-BR/index/introducing-businesses-chatgpt/
- **INEMATDS’s actual registration (11/22/2026):** before, searches for the brand showed an environmental institute. See the companion kit.

## Prompt to paste into Claude Code or Codex

See [`PEDIDO-AGENTE.md`](PEDIDO-AGENTE.md) (in Portuguese). It reads both kits, works with you to create the diagnosis, proposal, and profile, and won’t touch any account or DNS without your “yes.”

## What’s in the kit

| File | Purpose |
|---|---|
| [`kit/1-o-servico.md`](kit/1-o-servico.md) (in Portuguese) | the 5 deliverables, the 3 packages, how to calculate the price, and what not to promise |
| [`kit/2-diagnostico.md`](kit/2-diagnostico.md) (in Portuguese) | the 4 questions and how to interpret the results |
| [`kit/3-checklist-cliente.md`](kit/3-checklist-cliente.md) (in Portuguese) | what to ask the client for before starting |
| [`kit/4-proposta.md`](kit/4-proposta.md) (in Portuguese) | proposal template |
| [`kit/5-relatorio-mensal.md`](kit/5-relatorio-mensal.md) (in Portuguese) | monthly report template |
| [`kit/diagnostico.py`](kit/diagnostico.py) | generates the questions and scores the answers (0–100) |
| [`kit/medir.py`](kit/medir.py) | asks the questions on its own (subscription or OpenRouter), keeps the history, shows the trend and alerts; adds up visits coming from AI |

---

## Technical setup

Prerequisites: Python 3.10+ (standard library only). `diagnostico.py` calls no AI: you ask the questions by hand. `medir.py` asks on its own through your subscription (Claude Code, Codex, Antigravity) and only uses an API (OpenRouter) if you ask it to.

```bash
git clone https://github.com/inematds/presenca-na-ia && cd presenca-na-ia
python3 kit/diagnostico.py perguntas kit/exemplo-empresa.json
python3 kit/diagnostico.py relatorio kit/exemplo-empresa.json kit/exemplo-respostas-antes.json --saida antes.md
python3 kit/diagnostico.py relatorio kit/exemplo-empresa.json kit/exemplo-respostas-depois.json --saida depois.md
python3 -m unittest discover -s tests
```

- `exemplo-empresa.json`: `nome`, `apelidos`, `cidade`, `servico`, `site`, `concorrentes`, `confunde_com`.
- `exemplo-respostas-antes.json` / `exemplo-respostas-depois.json`: `{"<IA>": ["resposta 1", "resposta 2", "resposta 3", "resposta 4"]}`, one file for before and another for after; keys beginning with `_` are ignored. The sample answers are illustrative.
- Misidentified brand: a name mentioned alongside an organization in `confunde_com`, without the correct website, does not count as “appearing.” Names are compared as whole words (“INEMA” does not match “cinema”).
- Score per answer: appears 40 + correct website 30 + no confusion 20 + no competitor 10. Exits with 0 for the report, 2 for invalid JSON.
- Tests (12): full score, missing, confusion and competitor, misidentified brand, whole word, accents and case, domain, questions, before and after sample reports, missing field, empty answers, `--saida`.
- `medir.py` tests (20): no AI or API calls (simulated answers and fake commands).

## Measure without asking by hand

Clients pay the monthly fee for the trend, not a snapshot of one day. `kit/medir.py` combines three measurements:

1. **Visits from AI tools** (real data): export the Analytics CSV with “Session source” + “Sessions” for the month, then run `python3 kit/medir.py visitas origens.csv`. It totals ChatGPT (`chatgpt.com`), Perplexity, Gemini, Copilot, Claude, Meta AI, Grok, and DeepSeek. Example: `kit/exemplo-origens.csv`.
2. **Business Directory dashboard**: mentions and clicks, copied by hand into `kit/5-relatorio-mensal.md`.
3. **Questions, asked automatically**: each of the 4 diagnostic questions, `--vezes` times each (default 3, because answers can vary), using the same scoring as `diagnostico.py`.

```bash
python3 kit/medir.py rodar kit/cliente.json --ias claude,codex,gemini --vezes 3   # every week
python3 kit/medir.py relatorio kit/cliente.json --saida mes.md                     # exits 1 if there is an alert
python3 kit/medir.py rodar kit/exemplo-empresa.json --ias claude,codex --vezes 1 \
  --simular kit/exemplo-simulado.json --pasta /tmp/teste                            # test without any AI
```

| `--ias` | How it asks | Cost |
|---|---|---|
| `claude` | `claude -p` with web search, in an empty folder, without CLAUDE.md or MCP | Your Claude Code subscription |
| `codex` | `codex --search exec`, in an empty folder | Your Codex subscription |
| `gemini` | `agy -p` (Antigravity CLI) | Your Google subscription |
| `openrouter:<modelo>` | OpenRouter API, e.g.: `openrouter:perplexity/sonar`; requires `OPENROUTER_API_KEY` | Pay per call |

- **Output:** `medicoes/<empresa>/AAAA-MM-DD.json` (same format as the diagnostic) and `medicoes/<empresa>/historico.csv`. Running it again on the same day replaces that day’s data.
- **Report:** the trend with the score for each date, “appears X of N” and “correct site X of N” for each AI, remaining confusions, and alerts (a drop of 10 points or more, a new confusion, or an AI that stopped showing the site). Exits with 1 when there is an alert, so the scheduler can notify you.
- **Failures don’t count toward the score:** timeouts, empty responses, or responses saying the search could not be completed are counted as failures.
- **Clean Codex:** Codex reads your global `AGENTS.md`. To measure without your personal instructions, log in just for this purpose (`CODEX_HOME=~/.codex-medir codex login`) and run with `MEDIR_CODEX_HOME=~/.codex-medir`.
- **Honest limitation:** whether using a subscription or the API, the AI asks without memory or location and may use a different model. The number shows the trend, not exactly what each person sees. That’s why it’s paired with real visits and the dashboard.
- **Schedule (cron, every Monday at 7 a.m.):** `0 7 * * 1 cd ~/presenca-na-ia && python3 kit/medir.py rodar kit/cliente.json && python3 kit/medir.py relatorio kit/cliente.json --saida mes.md`
- **Real test (INEMA, 11/24/2026, 1 subscription run, 2 min):** score 45. Codex and Gemini found inema.club in 2 of 4 responses; Claude searched and found only the INEMA in Bahia (0 of 4).

## The process, from start to finish

🧠 = you with the agent · ⚙️ = script · 👤 = business owner

| # | Step | Command / what happens | Who |
|---|---|---|---|
| 1 | Business details | fill in `kit/exemplo-empresa.json` (or a copy) | 🧠 |
| 2 | Questions | `python3 kit/diagnostico.py perguntas <empresa.json>` | ⚙️ |
| 3 | Answers | ask the 4 questions in ChatGPT, Gemini, Claude, and Perplexity; paste the answers into `respostas.json` | 🧠 |
| 4 | Diagnosis | `python3 kit/diagnostico.py relatorio <empresa.json> <respostas.json> --saida antes.md` | ⚙️ |
| 5 | Proposal | fill in `kit/4-proposta.md` with the diagnosis | 🧠 |
| 6 | Checklist | ask the client for the items in `kit/3-checklist-cliente.md` | 🧠 + 👤 |
| 7 | Registration and verification | follow [empresa-no-chatgpt](https://github.com/inematds/empresa-no-chatgpt) (TXT in DNS; identity verification by the owner) | 🧠 + 👤 |
| 8 | After | repeat steps 3–4 with `--saida depois.md` and show the client | ⚙️ |
| 9 | Every week | `python3 kit/medir.py rodar <empresa.json>` (via cron); at month end `medir.py relatorio` + `medir.py visitas` + Directory dashboard → `kit/5-relatorio-mensal.md` | ⚙️ + 🧠 |

## License

MIT