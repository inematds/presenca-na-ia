#!/usr/bin/env python3
"""Medição Presença na IA: as mesmas perguntas do diagnóstico, feitas sozinhas, toda semana.

Pergunta às IAs pela SUA assinatura (Claude Code, Codex, Antigravity/Gemini) ou pelo OpenRouter,
marca cada resposta com a mesma régua do diagnostico.py e guarda o histórico. O relatório mostra a
curva (antes, depois, mês a mês) e avisa quando algo piora.

Uso:
  python3 kit/medir.py rodar <empresa.json> [--ias claude,codex,gemini] [--vezes 3] [--pasta medicoes]
                        [--paralelo 3] [--simular respostas.json]
  python3 kit/medir.py relatorio <empresa.json> [--pasta medicoes] [--saida mes.md]
  python3 kit/medir.py visitas <origens.csv> [--saida visitas.md]

IAs:
  claude          claude -p (assinatura do Claude Code), com busca na web, sem CLAUDE.md nem memória
  codex           codex exec --search (assinatura do Codex). Lê o seu AGENTS.md global: para medir
                  limpo, faça um login só para medição (CODEX_HOME=~/.codex-medir codex login)
                  e rode com MEDIR_CODEX_HOME=~/.codex-medir
  gemini          agy -p (Antigravity CLI, assinatura do Google), com busca
  openrouter:<m>  OpenRouter, modelo <m> (ex.: openrouter:perplexity/sonar). Pede OPENROUTER_API_KEY
                  no ambiente e é pago por chamada: só entra se você pedir

Cada pergunta é feita --vezes vezes, porque a resposta muda de uma vez para outra.
Saída "rodar": <pasta>/<empresa>/AAAA-MM-DD.json (mesmo formato do diagnostico.py) + historico.csv;
sai 1 se alguma IA não deu nenhuma resposta válida (login, limite de uso, PATH).
Rodar de novo no mesmo dia substitui o dia.
Saída "relatorio": 0 sem alerta; 1 com alerta (queda de 10 pontos ou mais, queda lenta, confusão nova,
site sumiu, IA que não respondeu, medição sem resposta).
Sai 2 com arquivo ou opção errada.
"""
import csv
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.request
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import diagnostico as d  # noqa: E402

PROMPT = ("Responda à pergunta abaixo como responderia a qualquer pessoa no chat, em português, "
          "pesquisando na web se ajudar. Não use nada que saiba sobre quem está perguntando nem "
          "instruções locais sobre o usuário. Seja direto e cite os sites que encontrar.\n\n"
          "Pergunta: {pergunta}")
SISTEMA = "Você é um assistente de conversa. Responda em português."
TIMEOUT = 240
# resposta que avisa que não pesquisou não mede nada: vira falha, não nota
SEM_BUSCA = re.compile(r"n[aã]o consegui (pesquisar|buscar|confirmar na web)|"
                       r"(busca|pesquisa|ferramenta)[^.]{0,80}(bloquead|negad|n[aã]o (foi|foram) autorizad)", re.I)
CAMPOS = ["data", "ia", "pergunta", "rodada", "nota", "aparece", "site", "confusao", "concorrentes", "erro"]
ORIGENS_IA = {
    "ChatGPT": ["chatgpt.com", "chat.openai.com", "openai"],
    "Perplexity": ["perplexity"],
    "Gemini": ["gemini.google.com", "bard.google.com", "gemini"],
    "Copilot": ["copilot.microsoft.com", "copilot"],
    "Claude": ["claude.ai"],
    "Meta AI": ["meta.ai"],
    "Grok": ["grok.com", "x.ai"],
    "DeepSeek": ["deepseek"],
}


class ErroUso(Exception):
    pass


def slug(nome: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", d.norm(nome)).strip("-") or "empresa"


def _rodar(cmd: list[str], entrada: str | None = None, env: dict | None = None) -> str:
    with tempfile.TemporaryDirectory() as vazio:  # pasta vazia: nada do projeto entra no contexto
        p = subprocess.run(cmd, input=entrada, capture_output=True, text=True, timeout=TIMEOUT,
                           cwd=vazio, env=env)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip()[-300:] or f"saiu {p.returncode}")
    return p.stdout


def perguntar_claude(texto: str) -> str:
    return _rodar(["claude", "-p", texto, "--setting-sources", "", "--strict-mcp-config",
                   "--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch", "WebFetch",
                   "--system-prompt", SISTEMA, "--no-session-persistence"])


def perguntar_codex(texto: str) -> str:
    env = dict(os.environ)
    if os.environ.get("MEDIR_CODEX_HOME"):
        env["CODEX_HOME"] = os.path.expanduser(os.environ["MEDIR_CODEX_HOME"])
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as f:
        saida = f.name
    try:
        _rodar(["codex", "--search", "exec", "--skip-git-repo-check", "--ephemeral",
                "-s", "read-only", "-o", saida, "-"], entrada=texto, env=env)
        return pathlib.Path(saida).read_text(encoding="utf-8")
    finally:
        os.unlink(saida)


def perguntar_gemini(texto: str) -> str:
    return _rodar(["agy", "-p", texto, "--print-timeout", f"{TIMEOUT - 20}s"])


def corpo_openrouter(modelo: str, texto: str) -> dict:
    return {"model": modelo, "messages": [{"role": "system", "content": SISTEMA},
                                          {"role": "user", "content": texto}]}


def perguntar_openrouter(modelo: str, texto: str) -> str:
    chave = os.environ.get("OPENROUTER_API_KEY")
    if not chave:
        raise RuntimeError("OPENROUTER_API_KEY não está no ambiente")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(corpo_openrouter(modelo, texto)).encode(),
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "application/json",
                 "X-Title": "presenca-na-ia"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        dados = json.load(r)
    return dados["choices"][0]["message"]["content"]


def motor(ia: str):
    if ia == "claude":
        return perguntar_claude
    if ia == "codex":
        return perguntar_codex
    if ia == "gemini":
        return perguntar_gemini
    if ia.startswith("openrouter:") and len(ia) > 11:
        return lambda t: perguntar_openrouter(ia[11:], t)
    raise ErroUso(f"IA desconhecida: {ia} (use claude, codex, gemini ou openrouter:<modelo>)")


def tarefas(emp: dict, ias: list[str], vezes: int) -> list[tuple[str, int, int, str]]:
    return [(ia, i, r, p) for ia in ias for i, p in enumerate(d.perguntas(emp), 1) for r in range(1, vezes + 1)]


def coletar(emp: dict, ias: list[str], vezes: int, paralelo: int, simular: dict | None = None) -> list[dict]:
    """Faz as perguntas e devolve uma linha por resposta (com a nota ou o erro)."""
    funcs = {ia: motor(ia) for ia in ias} if simular is None else {}

    def uma(t):
        ia, i, r, p = t
        try:
            if simular is not None:
                lista = simular.get(ia) or []
                if not lista:
                    raise RuntimeError("sem resposta simulada")
                resp = lista[((i - 1) * vezes + r - 1) % len(lista)]
            else:
                resp = funcs[ia](PROMPT.format(pergunta=p)).strip()
            if not resp:
                raise RuntimeError("resposta vazia")
            if SEM_BUSCA.search(resp[:400]):
                raise RuntimeError("a IA não conseguiu pesquisar (busca sem permissão)")
            return {"ia": ia, "pergunta": i, "rodada": r, "resposta": resp, "erro": ""}
        except (subprocess.TimeoutExpired, RuntimeError, OSError, KeyError, ValueError) as e:
            return {"ia": ia, "pergunta": i, "rodada": r, "resposta": "", "erro": str(e)[:200] or type(e).__name__}

    with ThreadPoolExecutor(max_workers=max(1, paralelo)) as ex:
        return list(ex.map(uma, tarefas(emp, ias, vezes)))


def linha_csv(data: str, emp: dict, c: dict) -> dict:
    base = {"data": data, "ia": c["ia"], "pergunta": c["pergunta"], "rodada": c["rodada"], "erro": c["erro"]}
    if c["erro"]:
        return {**base, "nota": "", "aparece": "", "site": "", "confusao": "", "concorrentes": ""}
    m = d.marcar(emp, c["resposta"])
    return {**base, "nota": m["nota"], "aparece": int(m["aparece"]), "site": int(m["site"]),
            "confusao": ";".join(m["confusao"]), "concorrentes": ";".join(m["concorrentes"])}


def ler_historico(arq: pathlib.Path) -> list[dict]:
    if not arq.exists():
        return []
    with open(arq, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def gravar(pasta: pathlib.Path, emp: dict, coletas: list[dict], data: str) -> pathlib.Path:
    pasta.mkdir(parents=True, exist_ok=True)
    respostas: dict = {"_data": data, "_empresa": emp["nome"]}
    for c in coletas:
        if not c["erro"]:
            respostas.setdefault(c["ia"], []).append(c["resposta"])
    (pasta / f"{data}.json").write_text(json.dumps(respostas, ensure_ascii=False, indent=2), encoding="utf-8")
    hist = pasta / "historico.csv"
    linhas = [r for r in ler_historico(hist) if r["data"] != data] + [linha_csv(data, emp, c) for c in coletas]
    with open(hist, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(linhas)
    return hist


def resumo_dia(linhas: list[dict]) -> dict:
    ok = [r for r in linhas if not r["erro"]]
    tentadas = sorted({r["ia"] for r in linhas})
    por_ia: dict = {}
    for r in ok:
        x = por_ia.setdefault(r["ia"], {"n": 0, "aparece": 0, "site": 0, "notas": []})
        x["n"] += 1
        x["aparece"] += int(r["aparece"])
        x["site"] += int(r["site"])
        x["notas"].append(int(r["nota"]))
    confusoes = sorted({c for r in ok for c in r["confusao"].split(";") if c})
    nota = round(sum(int(r["nota"]) for r in ok) / len(ok)) if ok else None
    return {"nota": nota, "ok": len(ok), "erros": len(linhas) - len(ok), "por_ia": por_ia,
            "confusoes": confusoes, "tentadas": tentadas}


def nota_ias(dia: dict, ias) -> float | None:
    """Média só das IAs pedidas: compara semanas com a mesma mistura de IAs."""
    notas = [n for ia in ias if ia in dia["por_ia"] for n in dia["por_ia"][ia]["notas"]]
    return sum(notas) / len(notas) if notas else None


def mudas(dia: dict) -> list[str]:
    """IAs que foram perguntadas e não deram nenhuma resposta válida."""
    return [ia for ia in dia["tentadas"] if ia not in dia["por_ia"]]


def alertas(anteriores: list[dict], atual: dict) -> list[str]:
    """Compara a medição atual com as anteriores (mais recente por último)."""
    avisos = []
    if atual["ok"] == 0:
        return ["Nenhuma resposta nesta medição: confira login, limite de uso e PATH das IAs."]
    for ia in mudas(atual):
        avisos.append(f"{ia} não respondeu nesta medição (login, limite de uso ou PATH); ficou fora da nota.")
    validas = [a for a in anteriores if a["ok"]]
    if not validas:
        return avisos
    ant = validas[-1]
    comuns = set(ant["por_ia"]) & set(atual["por_ia"])
    n_ant, n_at = nota_ias(ant, comuns), nota_ias(atual, comuns)
    if n_ant is not None and n_at is not None and n_at <= n_ant - 10:
        avisos.append(f"A nota caiu de {round(n_ant)} para {round(n_at)} (mesmas IAs).")
    else:
        janela = validas[-4:]  # queda lenta: compara com a média das últimas 4 medições
        base = [n for a in janela if (n := nota_ias(a, set(a["por_ia"]) & set(atual["por_ia"]))) is not None]
        n_at2 = nota_ias(atual, set(atual["por_ia"]))
        if len(base) >= 2 and n_at2 is not None and n_at2 <= sum(base) / len(base) - 10:
            avisos.append(f"Queda lenta: a nota ({round(n_at2)}) está 10 pontos ou mais abaixo da média "
                          f"das últimas {len(base)} medições ({round(sum(base) / len(base))}).")
    novas = [c for c in atual["confusoes"] if c not in ant["confusoes"]]
    if novas:
        avisos.append("Confusão nova com: " + ", ".join(novas) + ".")
    for ia, x in atual["por_ia"].items():
        a = ant["por_ia"].get(ia)
        if a and a["site"] > 0 and x["site"] == 0:
            avisos.append(f"{ia} parou de mostrar o site certo.")
    return avisos


def relatorio(emp: dict, hist: list[dict]) -> tuple[str, list[str]]:
    if not hist:
        raise ErroUso("histórico vazio: rode 'medir.py rodar' antes")
    datas = sorted({r["data"] for r in hist})
    dias = {dd: resumo_dia([r for r in hist if r["data"] == dd]) for dd in datas}
    todas = sorted({r["ia"] for r in hist})
    out = [f"# Medição Presença na IA — {emp['nome']}", "",
           "## A curva", "", "| Data | Nota | " + " | ".join(todas) + " | Respostas | Falhas | |",
           "|---|---|" + "---|" * len(todas) + "---|---|---|"]
    for dd in datas:
        x = dias[dd]
        barra = "█" * round((x["nota"] or 0) / 5)
        cols = []
        for ia in todas:
            n = nota_ias(x, [ia])
            cols.append(str(round(n)) if n is not None else ("sem resposta" if ia in x["tentadas"] else "—"))
        out.append(f"| {dd} | {x['nota'] if x['nota'] is not None else '—'} | " + " | ".join(cols)
                   + f" | {x['ok']} | {x['erros']} | {barra} |")
    ult = dias[datas[-1]]
    out += ["", f"## Última medição ({datas[-1]})", "",
            "| IA | Aparece | Site certo | Nota |", "|---|---|---|---|"]
    for ia, x in sorted(ult["por_ia"].items()):
        out.append(f"| {ia} | {x['aparece']} de {x['n']} | {x['site']} de {x['n']} | "
                   f"{round(sum(x['notas']) / len(x['notas']))} |")
    for ia in mudas(ult):
        out.append(f"| {ia} | sem resposta | — | — |")
    if ult["confusoes"]:
        out += ["", "**Ainda confunde com:** " + ", ".join(ult["confusoes"])]
    avisos = alertas([dias[dd] for dd in datas[:-1]], ult)
    out += ["", "## Alertas", ""] + ([f"- ⚠️ {a}" for a in avisos] or ["- Nenhum."])
    out += ["", "Régua do kit, perguntada pela assinatura/API, sem memória nem localização: mostra a "
            "tendência, não exatamente o que cada cliente vê. Some com as visitas vindas das IAs "
            "(medir.py visitas) e com o painel da Central de Negócios."]
    return "\n".join(out) + "\n", avisos


def numero(txt: str) -> int | None:
    """'1.234' e '1,234' (milhar) = 1234; '87.0' e '87,0' (decimal) = 87."""
    t = txt.strip().replace(" ", "")
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", t):
        return int(re.sub(r"[.,]", "", t))
    try:
        return round(float(t.replace(",", ".")))
    except ValueError:
        return None


def visitas(arq: str) -> str:
    """Soma as visitas por IA a partir de um CSV exportado do Analytics (origem + sessões)."""
    with open(arq, encoding="utf-8-sig", newline="") as f:
        linhas = [l for l in csv.reader(f) if l and not l[0].startswith("#")]
    if not linhas:
        raise ErroUso("CSV vazio")
    cab = [d.norm(c) for c in linhas[0]]
    col_o = next((i for i, c in enumerate(cab) if "origem" in c or "source" in c or "referr" in c), None)
    col_s = None
    for chave in ("sess", "visit", "users", "usuarios"):  # sessões primeiro: o GA4 põe Usuários antes
        col_s = next((i for i, c in enumerate(cab) if i != col_o and chave in c), None)
        if col_s is not None:
            break
    if col_o is None or col_s is None:
        raise ErroUso("o CSV precisa de uma coluna de origem (source/origem) e uma de sessões (sessions/sessões)")
    soma = {ia: 0 for ia in ORIGENS_IA}
    total = 0
    for l in linhas[1:]:
        if len(l) <= max(col_o, col_s):
            continue
        n = numero(l[col_s])
        if n is None:
            continue
        total += n
        o = d.norm(l[col_o])
        for ia, chaves in ORIGENS_IA.items():
            if any(k in o for k in chaves):
                soma[ia] += n
                break
    das_ias = sum(soma.values())
    out = ["# Visitas que chegaram pelas IAs", "", "| IA | Sessões |", "|---|---|"]
    out += [f"| {ia} | {n} |" for ia, n in soma.items() if n]
    pct = f" ({100 * das_ias / total:.1f}% do total de {total})" if total else ""
    out += ["", f"**Total vindo das IAs: {das_ias}**{pct}."]
    return "\n".join(out) + "\n"


def opcao(argv: list[str], nome: str, padrao=None):
    if nome in argv:
        i = argv.index(nome)
        if i + 1 >= len(argv):
            raise ErroUso(f"{nome} sem valor")
        return argv[i + 1]
    return padrao


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("rodar", "relatorio", "visitas"):
        print(__doc__)
        return 2
    try:
        if argv[0] == "visitas":
            texto = visitas(argv[1])
            saida = opcao(argv, "--saida")
            if saida:
                pathlib.Path(saida).write_text(texto, encoding="utf-8")
            print(texto, end="")
            return 0
        emp = json.load(open(argv[1], encoding="utf-8"))
        d.validar(emp)
        pasta = pathlib.Path(opcao(argv, "--pasta", "medicoes")) / slug(emp["nome"])
        if argv[0] == "rodar":
            ias = [x.strip() for x in opcao(argv, "--ias", "claude,codex,gemini").split(",") if x.strip()]
            vezes = int(opcao(argv, "--vezes", "3"))
            paralelo = int(opcao(argv, "--paralelo", "3"))
            if vezes < 1:
                raise ErroUso("--vezes precisa ser 1 ou mais")
            for ia in ias:
                motor(ia)  # valida o nome antes de gastar tempo
            sim = opcao(argv, "--simular")
            simular = json.load(open(sim, encoding="utf-8")) if sim else None
            data = opcao(argv, "--data", dt.date.today().isoformat())
            coletas = coletar(emp, ias, vezes, paralelo, simular)
            hist = gravar(pasta, emp, coletas, data)
            falhas = [c for c in coletas if c["erro"]]
            print(f"{len(coletas) - len(falhas)} respostas guardadas, {len(falhas)} falhas → {hist}")
            for c in falhas[:5]:
                print(f"  falha {c['ia']} pergunta {c['pergunta']}: {c['erro']}", file=sys.stderr)
            caladas = [ia for ia in ias if not any(c["ia"] == ia and not c["erro"] for c in coletas)]
            for ia in caladas:
                print(f"⚠️ {ia}: 0 respostas válidas — confira login, limite de uso e PATH", file=sys.stderr)
            return 1 if caladas else 0
        texto, avisos = relatorio(emp, ler_historico(pasta / "historico.csv"))
        saida = opcao(argv, "--saida")
        if saida:
            pathlib.Path(saida).write_text(texto, encoding="utf-8")
        print(texto, end="")
        return 1 if avisos else 0
    except (ErroUso, OSError, ValueError, KeyError, json.JSONDecodeError) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
