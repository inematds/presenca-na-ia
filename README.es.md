# Presencia en la IA

[![Presencia en la IA](guia/assets/banner-es.jpg)](https://inematds.github.io/presenca-na-ia/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

**Presencia en la IA** es un kit gratuito para ofrecer como servicio la organización de una empresa en las inteligencias artificiales: el registro en el Centro de Negocios de ChatGPT (lanzado en versión beta por OpenAI el 10/11/2026), la verificación de que la empresa pertenece a su dueño, la ficha con los datos correctos y el seguimiento mensual. Está pensado para quienes trabajan con tecnología, marketing digital, consultoría o agencias. Incluye el diagnóstico del «antes», la lista de verificación para el cliente, la propuesta, el informe mensual y una solicitud lista para que una IA prepare todo contigo.

Las empresas pagarán por aparecer en ChatGPT. El cliente pregunta a la IA quién presta ese servicio en su ciudad y la empresa no aparece, o aparece otra con un nombre parecido. Casi ningún dueño sabe que puede corregirlo.

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/presenca-na-ia/guia/es/**

## Kit hermano: el registro paso a paso

El paso a paso del registro en el Centro de Negocios, con las pantallas reales de nuestro caso (INEMATDS) y un agente que hace el registro en el navegador, está en **[inematds/empresa-no-chatgpt](https://github.com/inematds/empresa-no-chatgpt)** ([guía](https://inematds.github.io/empresa-no-chatgpt/guia/es/)). Este repositorio es la capa de **servicio**: cómo diagnosticar, vender, entregar y hacer el seguimiento para otras empresas.

## Basado en

- **OpenAI, «Empresas en ChatGPT» (10/11/2026):** beta; en el Centro de Negocios, la empresa reclama su perfil, actualiza la información y ve menciones, clics en el sitio web y los temas en los que aparece; 1.200 millones de personas usan ChatGPT cada semana. https://openai.com/pt-BR/index/introducing-businesses-chatgpt/
- **El registro real de INEMATDS (22/11/2026):** antes, una búsqueda de la marca mostraba un instituto de medio ambiente. Consulta el kit hermano.

## Solicitud para pegar en Claude Code o Codex

Consulta [`PEDIDO-AGENTE.md`](PEDIDO-AGENTE.md) (en portugués). Lee los dos kits, prepara contigo el diagnóstico, la propuesta y la ficha, y no modifica ninguna cuenta ni DNS sin tu «sí».

## Qué incluye el kit

| Archivo | Para qué sirve |
|---|---|
| [`kit/1-o-servico.md`](kit/1-o-servico.md) (en portugués) | las 5 piezas, los 3 paquetes, cómo calcular el precio y qué no prometer |
| [`kit/2-diagnostico.md`](kit/2-diagnostico.md) (en portugués) | las 4 preguntas y cómo interpretar el resultado |
| [`kit/3-checklist-cliente.md`](kit/3-checklist-cliente.md) (en portugués) | qué pedirle al cliente antes de empezar |
| [`kit/4-proposta.md`](kit/4-proposta.md) (en portugués) | modelo de propuesta |
| [`kit/5-relatorio-mensal.md`](kit/5-relatorio-mensal.md) (en portugués) | modelo del informe mensual |
| [`kit/diagnostico.py`](kit/diagnostico.py) | genera las preguntas y marca las respuestas (puntuación de 0 a 100) |
| [`kit/medir.py`](kit/medir.py) | hace las preguntas solo (suscripción u OpenRouter), guarda el historial, muestra la curva y las alertas; suma las visitas que llegan desde las IA |

---

## Instalación técnica

Requisitos previos: Python 3.10+ (solo biblioteca estándar). `diagnostico.py` no llama a ninguna IA: las preguntas se hacen a mano. `medir.py` pregunta solo con tu suscripción (Claude Code, Codex, Antigravity) y solo usa una API (OpenRouter) si se lo pides.

```bash
git clone https://github.com/inematds/presenca-na-ia && cd presenca-na-ia
python3 kit/diagnostico.py perguntas kit/exemplo-empresa.json
python3 kit/diagnostico.py relatorio kit/exemplo-empresa.json kit/exemplo-respostas-antes.json --saida antes.md
python3 kit/diagnostico.py relatorio kit/exemplo-empresa.json kit/exemplo-respostas-depois.json --saida depois.md
python3 -m unittest discover -s tests
```

- `exemplo-empresa.json`: `nome`, `apelidos`, `cidade`, `servico`, `site`, `concorrentes`, `confunde_com`.
- `exemplo-respostas-antes.json` / `exemplo-respostas-depois.json`: `{"<IA>": ["resposta 1", "resposta 2", "resposta 3", "resposta 4"]}`, un archivo para el antes y otro para el después; se ignoran las claves que empiezan con `_`. Las respuestas del ejemplo son ilustrativas.
- Marca confundida: si el nombre aparece junto con una organización de `confunde_com`, sin el sitio web correcto, no cuenta como «aparece». Los nombres se comparan como palabras completas («INEMA» no coincide con «cinema»).
- Puntuación por respuesta: aparece 40 + sitio web correcto 30 + sin confusión 20 + sin competidor 10. Devuelve 0 con el informe y 2 si el JSON es incorrecto.
- Pruebas (12): puntuación completa, ausente, confusión y competidor, marca confundida, palabra completa, acento y mayúsculas, dominio, preguntas, informes de antes y después del ejemplo, campo faltante, respuestas vacías, `--saida`.
- Pruebas de `medir.py` (20): sin llamar a ninguna IA ni API (respuestas simuladas y comandos falsos).

## Medir sin preguntar a mano

El cliente paga la mensualidad por la curva, no por la foto de un día. `kit/medir.py` reúne tres medidas:

1. **Visitas provenientes de las IAs** (dato real): exporta de Analytics el CSV de «Origen de la sesión» + «Sesiones» del mes y ejecuta `python3 kit/medir.py visitas origens.csv`. Suma ChatGPT (`chatgpt.com`), Perplexity, Gemini, Copilot, Claude, Meta AI, Grok y DeepSeek. Ejemplo: `kit/exemplo-origens.csv`.
2. **Panel del Centro de Negocios**: menciones y clics, copiados a mano en `kit/5-relatorio-mensal.md`.
3. **Las preguntas, hechas automáticamente**: las 4 preguntas del diagnóstico, `--vezes` veces cada una (por defecto, 3, porque la respuesta cambia), con la misma puntuación que `diagnostico.py`.

```bash
python3 kit/medir.py rodar kit/cliente.json --ias claude,codex,gemini --vezes 3   # todas las semanas
python3 kit/medir.py relatorio kit/cliente.json --saida mes.md                     # sale con 1 si hay una alerta
python3 kit/medir.py rodar kit/exemplo-empresa.json --ias claude,codex --vezes 1 \
  --simular kit/exemplo-simulado.json --pasta /tmp/teste                            # probar sin ninguna IA
```

| `--ias` | Cómo pregunta | Costo |
|---|---|---|
| `claude` | `claude -p` con búsqueda web, en una carpeta vacía, sin CLAUDE.md ni MCP | tu suscripción de Claude Code |
| `codex` | `codex --search exec`, en una carpeta vacía | tu suscripción de Codex |
| `gemini` | `agy -p` (Antigravity CLI) | tu suscripción de Google |
| `openrouter:<modelo>` | API de OpenRouter, p. ej.: `openrouter:perplexity/sonar`; necesita `OPENROUTER_API_KEY` | pago por llamada |

- **Salida:** `medicoes/<empresa>/AAAA-MM-DD.json` (mismo formato que el diagnóstico) y `medicoes/<empresa>/historico.csv`. Si vuelves a ejecutarlo el mismo día, reemplaza ese día.
- **Informe:** la curva con la puntuación de cada fecha, «aparece X de N» y «sitio correcto X de N» por IA, las confusiones que quedan y las alertas (caída de 10 puntos o más, una nueva confusión, una IA que dejó de mostrar el sitio). Sale con 1 cuando hay una alerta, así el programador puede avisarte.
- **Los fallos no cuentan en la puntuación:** el tiempo agotado, una respuesta vacía o una respuesta que dice que no pudo buscar se consideran fallos.
- **Codex limpio:** Codex lee tu `AGENTS.md` global. Para medir sin tus instrucciones personales, inicia sesión solo para esto (`CODEX_HOME=~/.codex-medir codex login`) y ejecútalo con `MEDIR_CODEX_HOME=~/.codex-medir`.
- **Límite honesto:** ya sea por suscripción o por API, la IA pregunta sin memoria ni ubicación y puede usar otro modelo. El número muestra la tendencia, no exactamente lo que ve cada persona. Por eso va de la mano con las visitas reales y el panel.
- **Programar (cron, todos los lunes a las 7 h):** `0 7 * * 1 cd ~/presenca-na-ia && python3 kit/medir.py rodar kit/cliente.json && python3 kit/medir.py relatorio kit/cliente.json --saida mes.md`
- **Prueba real (INEMA, 24/11/2026, 1 ronda por suscripción, 2 min):** puntuación 45. Codex y Gemini encontraron inema.club en 2 de 4 respuestas; Claude hizo la búsqueda y solo encontró el INEMA de Bahía (0 de 4).

## El proceso, de principio a fin

🧠 = tú con el agente · ⚙️ = script · 👤 = el dueño de la empresa

| # | Paso | Comando / qué sucede | Quién |
|---|---|---|---|
| 1 | Datos de la empresa | completar `kit/exemplo-empresa.json` (o una copia) | 🧠 |
| 2 | Preguntas | `python3 kit/diagnostico.py perguntas <empresa.json>` | ⚙️ |
| 3 | Respuestas | hacer las 4 preguntas en ChatGPT, Gemini, Claude y Perplexity; pegarlas en `respostas.json` | 🧠 |
| 4 | Diagnóstico | `python3 kit/diagnostico.py relatorio <empresa.json> <respostas.json> --saida antes.md` | ⚙️ |
| 5 | Propuesta | completar `kit/4-proposta.md` con el diagnóstico | 🧠 |
| 6 | Lista de verificación | pedirle al cliente lo que aparece en `kit/3-checklist-cliente.md` | 🧠 + 👤 |
| 7 | Registro y verificación | seguir [empresa-no-chatgpt](https://github.com/inematds/empresa-no-chatgpt) (TXT en el DNS; identidad verificada por el dueño) | 🧠 + 👤 |
| 8 | Después | repetir los pasos 3–4 con `--saida depois.md` y mostrárselo al cliente | ⚙️ |
| 9 | Cada semana | `python3 kit/medir.py rodar <empresa.json>` (con cron); a fin de mes `medir.py relatorio` + `medir.py visitas` + panel del Centro → `kit/5-relatorio-mensal.md` | ⚙️ + 🧠 |

## Licencia

MIT