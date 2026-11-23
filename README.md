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

---

## Instalação técnica

Pré-requisitos: Python 3.10+ (só biblioteca padrão). Nenhuma API é chamada: as perguntas são feitas à mão nas IAs.

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
| 9 | Todo mês | passos 3–4 + painel da Central → `kit/5-relatorio-mensal.md` | 🧠 |

## Licença

MIT
