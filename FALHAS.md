# FALHAS — presenca-na-ia

| data | o que quebrou | menor correção | prompt \| infra |
|---|---|---|---|
| 2026-11-24 | menu do topo do guia vazava para o lado entre 861 e 1360 px (ES até 1688 px), pior com o link "Medir" | cortes do menu em 1900/1360/1160 px e espaço menor entre os links, nos 3 idiomas | prompt |
| 2026-11-24 | medir.py: `claude -p` não pesquisava (`--tools` só disponibiliza; a busca ficava sem permissão) e a resposta "não consegui pesquisar" entrava na nota | `--allowedTools WebSearch WebFetch` + guarda `SEM_BUSCA` que transforma esse aviso em falha | infra |
