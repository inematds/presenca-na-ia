# Presença na IA

[![Presença na IA](guia/assets/banner.jpg)](https://inematds.github.io/presenca-na-ia/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

**Presença na IA** é um kit grátis para você oferecer, como serviço, a organização de uma empresa nas inteligências artificiais: o cadastro na Central de Negócios do ChatGPT (lançada em versão beta pela OpenAI em 10/11/2026), a verificação de que a empresa é do dono, a ficha com os dados certos e o acompanhamento todo mês. Serve para quem trabalha com tecnologia, marketing digital, consultoria ou agência. Traz o diagnóstico do "antes", o checklist do cliente, a proposta, o relatório mensal e um pedido pronto para uma IA montar tudo com você.

Empresas vão pagar para aparecer no ChatGPT. O cliente pergunta para a IA quem faz o serviço na cidade dele, e a empresa não aparece, ou aparece outra com nome parecido. Quase nenhum dono sabe que pode corrigir isso.

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/presenca-na-ia/guia/**

## Kit irmão: o cadastro passo a passo

O passo a passo do cadastro na Central de Negócios, com as telas reais do nosso caso (INEMATDS) e um agente que faz o cadastro no navegador, está no **[inematds/empresa-no-chatgpt](https://github.com/inematds/empresa-no-chatgpt)** ([guia](https://inematds.github.io/empresa-no-chatgpt/guia/)). Este repo é a camada de **serviço**: como diagnosticar, vender, entregar e acompanhar isso para outras empresas.

## Baseado em

- **OpenAI, "Empresas no ChatGPT" (10/11/2026):** beta; na Central de Negócios a empresa reivindica o perfil, atualiza as informações e vê menções, cliques no site e os temas em que aparece; 1,2 bilhão de pessoas usam o ChatGPT por semana. https://openai.com/pt-BR/index/introducing-businesses-chatgpt/
- **O cadastro real da INEMATDS (22/11/2026):** antes, a busca pela marca mostrava um instituto do meio ambiente. Ver o kit irmão.

## Pedido para colar no Claude Code ou no Codex

Ver [`PEDIDO-AGENTE.md`](PEDIDO-AGENTE.md). Ele lê os dois kits, monta o diagnóstico com você, a proposta e a ficha, e não mexe em conta nem DNS sem o seu "sim".

## O que tem no kit

| Arquivo | Para quê |
|---|---|
| [`kit/1-o-servico.md`](kit/1-o-servico.md) | as 5 peças, os 3 pacotes, como calcular o preço e o que não prometer |
| [`kit/2-diagnostico.md`](kit/2-diagnostico.md) | as 4 perguntas e como ler o resultado |
| [`kit/3-checklist-cliente.md`](kit/3-checklist-cliente.md) | o que pedir ao cliente antes de começar |
| [`kit/4-proposta.md`](kit/4-proposta.md) | modelo de proposta |
| [`kit/5-relatorio-mensal.md`](kit/5-relatorio-mensal.md) | modelo do relatório de todo mês |
| [`kit/diagnostico.py`](kit/diagnostico.py) | gera as perguntas e marca as respostas (nota 0–100) |
| [`kit/medir.py`](kit/medir.py) | faz as perguntas sozinho (assinatura ou OpenRouter), guarda o histórico, mostra a curva e os alertas; soma as visitas vindas das IAs |

---

## Instalação técnica

Pré-requisitos: Python 3.10+ (só biblioteca padrão). O `diagnostico.py` não chama nenhuma IA: as perguntas são feitas à mão. O `medir.py` pergunta sozinho pela sua assinatura (Claude Code, Codex, Antigravity) e só usa API (OpenRouter) se você pedir.

```bash
git clone https://github.com/inematds/presenca-na-ia && cd presenca-na-ia
python3 kit/diagnostico.py perguntas kit/exemplo-empresa.json
python3 kit/diagnostico.py relatorio kit/exemplo-empresa.json kit/exemplo-respostas-antes.json --saida antes.md
python3 kit/diagnostico.py relatorio kit/exemplo-empresa.json kit/exemplo-respostas-depois.json --saida depois.md
python3 -m unittest discover -s tests
```

- `exemplo-empresa.json`: `nome`, `apelidos`, `cidade`, `servico`, `site`, `concorrentes`, `confunde_com`.
- `exemplo-respostas-antes.json` / `exemplo-respostas-depois.json`: `{"<IA>": ["resposta 1", "resposta 2", "resposta 3", "resposta 4"]}`, um arquivo para o antes e outro para o depois; chaves que começam com `_` são ignoradas. As respostas do exemplo são ilustrativas.
- Marca trocada: nome citado junto com uma organização de `confunde_com`, sem o site certo, não conta como "aparece". Nomes são comparados como palavra inteira ("INEMA" não casa com "cinema").
- Nota de cada resposta: aparece 40 + site certo 30 + sem confusão 20 + sem concorrente 10. Sai 0 com o relatório, 2 com JSON errado.
- Testes (12): nota cheia, ausente, confusão e concorrente, marca trocada, palavra inteira, acento e caixa, domínio, perguntas, relatório antes e depois do exemplo, campo faltando, respostas vazias, `--saida`.
- Testes do `medir.py` (29): sem chamar IA nem API (respostas simuladas e comandos falsos).

## Medir sem perguntar à mão

O cliente paga a mensalidade pela curva, não pela foto de um dia. O `kit/medir.py` junta três medidas:

1. **Visitas vindas das IAs** (dado real): exporte do Analytics o CSV de "Origem da sessão" + "Sessões" do mês e rode `python3 kit/medir.py visitas origens.csv`. Ele soma ChatGPT (`chatgpt.com`), Perplexity, Gemini, Copilot, Claude, Meta AI, Grok e DeepSeek. Exemplo: `kit/exemplo-origens.csv`.
2. **Painel da Central de Negócios**: menções e cliques, copiados à mão para o `kit/5-relatorio-mensal.md`.
3. **As perguntas, feitas sozinhas**: as 4 perguntas do diagnóstico, `--vezes` vezes cada (padrão 3, porque a resposta muda), com a mesma nota do `diagnostico.py`.

```bash
python3 kit/medir.py rodar kit/cliente.json --ias claude,codex,gemini --vezes 3   # toda semana
python3 kit/medir.py relatorio kit/cliente.json --saida mes.md                     # sai 1 se houver alerta
python3 kit/medir.py rodar kit/exemplo-empresa.json --ias claude,codex --vezes 1 \
  --simular kit/exemplo-simulado.json --pasta /tmp/teste                            # testar sem IA nenhuma
```

| `--ias` | Como pergunta | Custo |
|---|---|---|
| `claude` | `claude -p` com busca na web, numa pasta vazia, sem CLAUDE.md nem MCP | sua assinatura do Claude Code |
| `codex` | `codex --search exec`, numa pasta vazia | sua assinatura do Codex |
| `gemini` | `agy -p` (Antigravity CLI) | sua assinatura do Google |
| `openrouter:<modelo>` | API do OpenRouter, ex.: `openrouter:perplexity/sonar`; precisa de `OPENROUTER_API_KEY` | pago por chamada |

- **Saída:** `medicoes/<empresa>/AAAA-MM-DD.json` (mesmo formato do diagnóstico) e `medicoes/<empresa>/historico.csv`. Rodar de novo no mesmo dia substitui o dia.
- **Relatório:** a curva com a nota geral e a de cada IA por data, "aparece X de N" e "site certo X de N" por IA (com `--vezes 3` são 12 respostas por IA), as confusões que restam e os alertas. Alertas: queda de 10 pontos ou mais contra a medição anterior, com as mesmas IAs; queda lenta (10 pontos abaixo da média das últimas 4); confusão nova; IA que parou de mostrar o site; IA que não respondeu; medição sem nenhuma resposta. Sai com 1 quando há alerta, então o agendador pode avisar você.
- **Falhas não contam na nota:** tempo esgotado, resposta vazia ou resposta que diz que não conseguiu pesquisar viram falha. Se uma IA não der nenhuma resposta válida (login vencido, limite de uso, comando fora do PATH), o `rodar` sai com 1 e o relatório avisa. A nota da semana compara só as IAs que responderam nas duas medições.
- **Codex limpo:** o Codex lê o seu `AGENTS.md` global. Para medir sem as suas instruções pessoais, faça um login só para isso (`CODEX_HOME=~/.codex-medir codex login`) e rode com `MEDIR_CODEX_HOME=~/.codex-medir`.
- **Limite honesto:** nenhuma das opções pergunta ao ChatGPT, que é onde o cliente se cadastrou. O Codex é da OpenAI, mas não é o ChatGPT. O ChatGPT só é medido pelo painel da Central e pelas visitas com origem `chatgpt.com`. E pela assinatura ou pela API a IA pergunta sem memória nem localização e pode usar outro modelo: o número mostra a tendência, não exatamente o que cada pessoa vê.
- **Custo:** 3 IAs × 4 perguntas × 3 vezes = 36 perguntas com busca na web por cliente, por semana (cerca de 5 a 10 minutos). Com muitos clientes isso pesa no limite de uso da assinatura: espalhe os clientes em dias ou horários diferentes, ou use `--vezes 2`.
- **Agendar (cron, toda segunda às 7h).** O cron não enxerga as pastas onde o `claude`, o `codex` e o `agy` costumam ficar. Rode `which claude codex agy python3`, troque `VOCE` pelo seu usuário e ponha as pastas que aparecerem no `PATH`. Abra com `crontab -e` e cole:

```cron
PATH=/usr/local/bin:/usr/bin:/bin:/home/VOCE/.local/bin:/home/VOCE/.npm-global/bin
MEDIR_CODEX_HOME=/home/VOCE/.codex-medir
MAILTO=voce@exemplo.com
0 7 * * 1 cd /home/VOCE/presenca-na-ia && mkdir -p relatorios && python3 kit/medir.py rodar kit/cliente.json >/dev/null 2>&1; python3 kit/medir.py relatorio kit/cliente.json --saida relatorios/$(date +\%F).md >/dev/null || echo "Presença na IA: alerta ou falha, veja relatorios/"
```

  Cada semana fica num arquivo `relatorios/AAAA-MM-DD.md`. O cron só escreve alguma coisa quando há alerta ou quando uma IA não respondeu, e o `MAILTO` manda isso para o seu e-mail. Isso só funciona se a máquina tiver servidor de e-mail configurado, o que computador pessoal e VPS comum quase nunca têm. Sem ele, abra o relatório toda segunda ou peça ao Claude Code para trocar o `echo` por uma mensagem no Telegram. Sem login de medição do Codex, apague a linha `MEDIR_CODEX_HOME`. Para medir também pelo OpenRouter, acrescente a linha `OPENROUTER_API_KEY=sua-chave` e passe `--ias claude,codex,gemini,openrouter:perplexity/sonar,...` no `rodar`. O cron existe no Linux e no macOS; no Windows, use o WSL (o Linux dentro do Windows). Confira na primeira segunda-feira se o arquivo apareceu.
- **Pelo OpenRouter, testados:** `openrouter:perplexity/sonar` (busca própria), `openrouter:deepseek/deepseek-v4.1-flash:online`, `openrouter:z-ai/glm-5.3:online` e `openrouter:openai/gpt-6.2-sol:online` (o mais perto do ChatGPT). O `:online` liga a busca na internet; sem ele o modelo responde só de memória. Custo medido: 16 perguntas = US$ 0,02. O ChatGPT fica de fora porque não tem linha de comando, e o Manus porque cada pergunta vira uma tarefa de agente de minutos que gasta créditos.
- **Primeira medição (INEMA, 24/11/2026):** nota geral 32. Pela assinatura, com 3 rodadas: Claude 20 (0 de 12), Gemini 49 (5 de 12), Codex no limite de uso. Pelo OpenRouter, com 1 rodada: Perplexity 35, DeepSeek 38, GLM 20, OpenAI 20. Ainda confunde com o Instituto do Meio Ambiente.

## O processo, do início ao fim

🧠 = você com o agente · ⚙️ = script · 👤 = o dono da empresa

| # | Passo | Comando / o que acontece | Quem |
|---|---|---|---|
| 1 | Dados da empresa | preencher `kit/exemplo-empresa.json` (ou uma cópia) | 🧠 |
| 2 | Perguntas | `python3 kit/diagnostico.py perguntas <empresa.json>` | ⚙️ |
| 3 | Respostas | fazer as 4 perguntas no ChatGPT, Gemini, Claude e Perplexity; colar no `respostas.json` | 🧠 |
| 4 | Diagnóstico | `python3 kit/diagnostico.py relatorio <empresa.json> <respostas.json> --saida antes.md` | ⚙️ |
| 5 | Proposta | preencher `kit/4-proposta.md` com o diagnóstico | 🧠 |
| 6 | Checklist | pedir ao cliente o que está em `kit/3-checklist-cliente.md` | 🧠 + 👤 |
| 7 | Cadastro e verificação | seguir o [empresa-no-chatgpt](https://github.com/inematds/empresa-no-chatgpt) (TXT no DNS; identidade pelo dono) | 🧠 + 👤 |
| 8 | Depois | refazer os passos 3–4 com `--saida depois.md` e mostrar ao cliente | ⚙️ |
| 9 | Toda semana | `python3 kit/medir.py rodar <empresa.json>` (pelo cron); no fim do mês `medir.py relatorio` + `medir.py visitas` + painel da Central → `kit/5-relatorio-mensal.md` | ⚙️ + 🧠 |

## Licença

MIT
