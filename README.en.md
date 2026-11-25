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
- `medir.py` tests (29): no AI or API calls (simulated answers and fake commands).

## Measure without asking by hand

The client pays the monthly fee for the curve, not for a one-day snapshot. `kit/medir.py` combines three measurements:

1. **Visits coming from the AIs** (real data): export the month's "Session source" + "Sessions" CSV from Analytics and run `python3 kit/medir.py visitas origens.csv`. It adds up ChatGPT (`chatgpt.com`), Perplexity, Gemini, Copilot, Claude, Meta AI, Grok and DeepSeek. Example: `kit/exemplo-origens.csv`.
2. **Business Directory dashboard**: mentions and clicks, copied by hand into `kit/5-relatorio-mensal.md`.
3. **The questions, asked automatically**: the 4 diagnostic questions, `--vezes` times each (default 3, because the answer changes), with the same score as `diagnostico.py`.

```bash
python3 kit/medir.py rodar kit/cliente.json --ias claude,codex,gemini --vezes 3   # every week
python3 kit/medir.py relatorio kit/cliente.json --saida mes.md                     # exits 1 if there is an alert
python3 kit/medir.py rodar kit/exemplo-empresa.json --ias claude,codex --vezes 1 \
  --simular kit/exemplo-simulado.json --pasta /tmp/teste                            # test without any AI
```

| `--ias` | How it asks | Cost |
|---|---|---|
| `claude` | `claude -p` with web search, in an empty folder, with no CLAUDE.md or MCP | your Claude Code subscription |
| `codex` | `codex --search exec`, in an empty folder | your Codex subscription |
| `gemini` | `agy -p` (Antigravity CLI) | your Google subscription |
| `openrouter:<modelo>` | OpenRouter API, e.g. `openrouter:perplexity/sonar`; needs `OPENROUTER_API_KEY` | paid per call |

- **Output:** `medicoes/<empresa>/AAAA-MM-DD.json` (same format as the diagnostic) and `medicoes/<empresa>/historico.csv`. Running again on the same day replaces that day.
- **Report:** the curve with the overall score and each AI's score by date, "appears X of N" and "right site X of N" per AI (with `--vezes 3` that is 12 answers per AI), the confusions that remain, and the alerts. Alerts: a drop of 10 points or more against the previous measurement, with the same AIs; a slow decline (10 points below the average of the last 4); a new confusion; an AI that stopped showing the site; an AI that did not respond; a measurement with no answers at all. It exits with 1 when there is an alert, so the scheduler can notify you.
- **Failures do not count toward the score:** a timeout, an empty answer, or an answer saying it could not search counts as a failure. If an AI gives no valid answer at all (expired login, usage limit, command not in the PATH), `rodar` exits with 1 and the report warns about it. The week's score compares only the AIs that responded in both measurements.
- **Clean Codex:** Codex reads your global `AGENTS.md`. To measure without your personal instructions, create a login just for this (`CODEX_HOME=~/.codex-medir codex login`) and run with `MEDIR_CODEX_HOME=~/.codex-medir`.
- **Honest limit:** none of the options asks ChatGPT, which is where the client registered. Codex is from OpenAI, but it is not ChatGPT. ChatGPT is measured only by the Directory dashboard and by visits with origin `chatgpt.com`. And through the subscription or the API, the AI asks without memory or location and may use a different model: the number shows the trend, not exactly what each person sees.
- **Cost:** 3 AIs × 4 questions × 3 times = 36 questions with web search per client, per week (about 5 to 10 minutes). With many clients this weighs on the subscription's usage limit: spread the clients across different days or times, or use `--vezes 2`.
- **Schedule (cron, every Monday at 7 am).** Cron does not see the folders where `claude`, `codex` and `agy` usually live. Run `which claude codex agy python3`, replace `VOCE` with your username and put the folders that show up in the `PATH`. Open it with `crontab -e` and paste:

```cron
PATH=/usr/local/bin:/usr/bin:/bin:/home/VOCE/.local/bin:/home/VOCE/.npm-global/bin
MEDIR_CODEX_HOME=/home/VOCE/.codex-medir
MAILTO=voce@exemplo.com
0 7 * * 1 cd /home/VOCE/presenca-na-ia && mkdir -p relatorios && python3 kit/medir.py rodar kit/cliente.json >/dev/null 2>&1; python3 kit/medir.py relatorio kit/cliente.json --saida relatorios/$(date +\%F).md >/dev/null || echo "Presence in AI: alert or failure, see relatorios/"
```

  Each week gets its own file `relatorios/AAAA-MM-DD.md`. Cron only writes anything when there is an alert or when an AI did not respond, and `MAILTO` sends that to your email. This only works if the machine has a mail server configured, which personal computers and ordinary VPSs almost never have. Without one, open the report every Monday or ask Claude Code to replace the `echo` with a Telegram message. Without a Codex measurement login, delete the `MEDIR_CODEX_HOME` line. To also measure through OpenRouter, add the line `OPENROUTER_API_KEY=sua-chave` and pass `--ias claude,codex,gemini,openrouter:perplexity/sonar,...` to `rodar`. Cron exists on Linux and macOS; on Windows, use WSL (Linux inside Windows). On the first Monday, check that the file showed up.
- **Through OpenRouter, tested:** `openrouter:perplexity/sonar` (its own search), `openrouter:deepseek/deepseek-v4.1-flash:online`, `openrouter:z-ai/glm-5.3:online` and `openrouter:openai/gpt-6.2-sol:online` (the closest to ChatGPT). `:online` turns on internet search; without it the model answers from memory only. Measured cost: 16 questions = US$ 0.02. ChatGPT is left out because it has no command line, and Manus because each question becomes an agent task lasting minutes that spends credits.
- **First measurement (INEMA, 11/24/2026):** overall score 32. Through the subscription, with 3 rounds: Claude 20 (0 of 12), Gemini 49 (5 of 12), Codex at the usage limit. Through OpenRouter, with 1 round: Perplexity 35, DeepSeek 38, GLM 20, OpenAI 20. It still gets confused with the Instituto do Meio Ambiente (the Environment Institute).

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