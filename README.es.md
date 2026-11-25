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
- Pruebas de `medir.py` (29): sin llamar a ninguna IA ni API (respuestas simuladas y comandos falsos).

## Medir sin preguntar a mano

El cliente paga la mensualidad por la curva, no por la foto de un día. El `kit/medir.py` junta tres medidas:

1. **Visitas que llegan desde las IAs** (dato real): exporte de Analytics el CSV de "Origen de la sesión" + "Sesiones" del mes y ejecute `python3 kit/medir.py visitas origens.csv`. Él suma ChatGPT (`chatgpt.com`), Perplexity, Gemini, Copilot, Claude, Meta AI, Grok y DeepSeek. Ejemplo: `kit/exemplo-origens.csv`.
2. **Panel del Centro de Negocios**: menciones y clics, copiados a mano al `kit/5-relatorio-mensal.md`.
3. **Las preguntas, hechas solas**: las 4 preguntas del diagnóstico, `--vezes` veces cada una (por defecto 3, porque la respuesta cambia), con la misma nota de `diagnostico.py`.

```bash
python3 kit/medir.py rodar kit/cliente.json --ias claude,codex,gemini --vezes 3   # cada semana
python3 kit/medir.py relatorio kit/cliente.json --saida mes.md                     # sale 1 si hay alerta
python3 kit/medir.py rodar kit/exemplo-empresa.json --ias claude,codex --vezes 1 \
  --simular kit/exemplo-simulado.json --pasta /tmp/teste                            # probar sin ninguna IA
```

| `--ias` | Cómo pregunta | Costo |
|---|---|---|
| `claude` | `claude -p` con búsqueda en la web, en una carpeta vacía, sin CLAUDE.md ni MCP | su suscripción de Claude Code |
| `codex` | `codex --search exec`, en una carpeta vacía | su suscripción de Codex |
| `gemini` | `agy -p` (Antigravity CLI) | su suscripción de Google |
| `openrouter:<modelo>` | API de OpenRouter, ej.: `openrouter:perplexity/sonar`; necesita `OPENROUTER_API_KEY` | se paga por llamada |

- **Salida:** `medicoes/<empresa>/AAAA-MM-DD.json` (mismo formato del diagnóstico) y `medicoes/<empresa>/historico.csv`. Ejecutar de nuevo el mismo día reemplaza el día.
- **Informe:** la curva con la nota general y la de cada IA por fecha, "aparece X de N" y "sitio correcto X de N" por IA (con `--vezes 3` son 12 respuestas por IA), las confusiones que quedan y las alertas. Alertas: caída de 10 puntos o más frente a la medición anterior, con las mismas IAs; caída lenta (10 puntos por debajo del promedio de las últimas 4); confusión nueva; IA que dejó de mostrar el sitio; IA que no respondió; medición sin ninguna respuesta. Sale con 1 cuando hay alerta, así el programador de tareas puede avisarle.
- **Las fallas no cuentan en la nota:** tiempo agotado, respuesta vacía o respuesta que dice que no pudo buscar se vuelven falla. Si una IA no da ninguna respuesta válida (sesión vencida, límite de uso, comando fuera del PATH), el `rodar` sale con 1 y el informe avisa. La nota de la semana compara solo las IAs que respondieron en las dos mediciones.
- **Codex limpio:** Codex lee su `AGENTS.md` global. Para medir sin sus instrucciones personales, haga un login solo para esto (`CODEX_HOME=~/.codex-medir codex login`) y ejecute con `MEDIR_CODEX_HOME=~/.codex-medir`.
- **Límite honesto:** ninguna de las opciones le pregunta a ChatGPT, que es donde el cliente se registró. Codex es de OpenAI, pero no es ChatGPT. ChatGPT solo se mide por el panel del Centro y por las visitas con origen `chatgpt.com`. Y, ya sea por suscripción o por API, la IA pregunta sin memoria ni ubicación y puede usar otro modelo: el número muestra la tendencia, no exactamente lo que ve cada persona.
- **Costo:** 3 IAs × 4 preguntas × 3 veces = 36 preguntas con búsqueda en la web por cliente, por semana (unos 5 a 10 minutos). Con muchos clientes esto pesa en el límite de uso de la suscripción: reparta los clientes en días u horarios distintos, o use `--vezes 2`.
- **Programar (cron, todos los lunes a las 7 h).** El cron no ve las carpetas donde suelen estar `claude`, `codex` y `agy`. Ejecute `which claude codex agy python3`, cambie `VOCE` por su usuario y ponga en el `PATH` las carpetas que aparezcan. Abra con `crontab -e` y pegue:

```cron
PATH=/usr/local/bin:/usr/bin:/bin:/home/VOCE/.local/bin:/home/VOCE/.npm-global/bin
MEDIR_CODEX_HOME=/home/VOCE/.codex-medir
MAILTO=voce@exemplo.com
0 7 * * 1 cd /home/VOCE/presenca-na-ia && mkdir -p relatorios && python3 kit/medir.py rodar kit/cliente.json >/dev/null 2>&1; python3 kit/medir.py relatorio kit/cliente.json --saida relatorios/$(date +\%F).md >/dev/null || echo "Presencia en la IA: alerta o falla, vea relatorios/"
```

  Cada semana queda en un archivo `relatorios/AAAA-MM-DD.md`. El cron solo escribe algo cuando hay alerta o cuando una IA no respondió, y el `MAILTO` envía eso a su correo. Esto solo funciona si la máquina tiene un servidor de correo configurado, algo que una computadora personal y un VPS común casi nunca tienen. Sin él, abra el informe todos los lunes o pida a Claude Code que cambie el `echo` por un mensaje en Telegram. Sin login de medición de Codex, borre la línea `MEDIR_CODEX_HOME`. Para medir también por OpenRouter, agregue la línea `OPENROUTER_API_KEY=sua-chave` y pase `--ias claude,codex,gemini,openrouter:perplexity/sonar,...` en el `rodar`. El cron existe en Linux y macOS; en Windows, use WSL (el Linux dentro de Windows). Verifique el primer lunes si apareció el archivo.
- **Por OpenRouter, probados:** `openrouter:perplexity/sonar` (búsqueda propia), `openrouter:deepseek/deepseek-v4.1-flash:online`, `openrouter:z-ai/glm-5.3:online` y `openrouter:openai/gpt-6.2-sol:online` (el más cercano a ChatGPT). El `:online` activa la búsqueda en internet; sin él el modelo responde solo de memoria. Costo medido: 16 preguntas = US$ 0,02. ChatGPT queda fuera porque no tiene línea de comandos, y Manus porque cada pregunta se vuelve una tarea de agente de minutos que gasta créditos.
- **Primera medición (INEMA, 24/11/2026):** nota general 32. Por suscripción, con 3 rondas: Claude 20 (0 de 12), Gemini 49 (5 de 12), Codex en el límite de uso. Por OpenRouter, con 1 ronda: Perplexity 35, DeepSeek 38, GLM 20, OpenAI 20. Todavía lo confunde con el Instituto do Meio Ambiente.

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