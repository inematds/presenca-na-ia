# FALHAS — presenca-na-ia

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-11-24 | alerta de queda lenta comparava misturas diferentes de IAs e inventava piora | usar a mesma interseção de IAs em toda a janela e no dia atual; cobrir adição, falha e troca de IAs | prompt |
| 2026-11-24 | links EN/ES do agendamento abriam âncoras inexistentes no README português | apontar para blob/main/README.en.md e README.es.md com suas âncoras | prompt |
| 2026-11-24 | tradução central preservou em PT a prosa da tabela EN por misturar comandos e texto | pedir tradução apenas da prosa das células, preservando só os trechos entre crases | prompt |
| 2026-11-24 | menu do guia vazava em 600 px entre o modo celular e o desktop | antecipar a quebra do menu de 520 para 720 px nos 3 idiomas | prompt |
| 2026-11-24 | menu do topo do guia vazava para o lado entre 861 e 1360 px (ES até 1688 px), pior com o link "Medir" | cortes do menu em 1900/1360/1160 px e espaço menor entre os links, nos 3 idiomas | prompt |
| 2026-11-24 | medir.py: `claude -p` não pesquisava (`--tools` só disponibiliza; a busca ficava sem permissão) e a resposta "não consegui pesquisar" entrava na nota | `--allowedTools WebSearch WebFetch` + guarda `SEM_BUSCA` que transforma esse aviso em falha | infra |
