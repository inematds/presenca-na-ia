# 5. Modelo de relatório mensal

**[EMPRESA] — Presença na IA — [MÊS/ANO]**

| | Mês anterior | Este mês |
|---|---|---|
| Nota do diagnóstico (0–100, `medir.py relatorio`) | [n] | [n] |
| IAs em que a empresa aparece (de 4) | [n] | [n] |
| Respostas com o site certo | [n] | [n] |
| Respostas com confusão ou concorrente | [n] | [n] |
| Menções no painel da Central de Negócios | [n] | [n] |
| Cliques no site pelo ChatGPT | [n] | [n] |
| Visitas vindas das IAs (`medir.py visitas`) | [n] | [n] |

O painel da Central só mostra números quando há conversas suficientes (regra da OpenAI). Se aparecer
"sem dados", escreva isso, não estime.

**O que mudamos este mês:** [ex.: horário de fim de ano, produto novo, descrição revisada]

**O que ainda aparece errado:** [ex.: Gemini ainda mostra o telefone antigo; pedimos correção no Google]

**Próximo mês:** [o que vamos conferir]

A nota, o "aparece X de N" e os alertas saem prontos do `python3 kit/medir.py relatorio <empresa.json> --saida mes.md`; cole a curva no fim deste relatório.
