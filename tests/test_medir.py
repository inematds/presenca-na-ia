"""Testes do medir.py, sem chamar IA nem API: python3 -m unittest discover -s tests"""
import csv
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "kit"))
import medir as m  # noqa: E402

EMP = {"nome": "Padaria Sol", "apelidos": [], "cidade": "Curitiba", "servico": "padaria",
       "site": "https://padariasol.com.br", "concorrentes": ["Pão Dourado"], "confunde_com": ["Hotel Sol"]}
BOA = "A Padaria Sol (padariasol.com.br) é ótima."
RUIM = "Você quis dizer o Hotel Sol? Recomendo o Pão Dourado."


def rodar(*args):
    return subprocess.run([sys.executable, str(RAIZ / "kit" / "medir.py"), *args],
                          capture_output=True, text=True, cwd=RAIZ)


class TestColeta(unittest.TestCase):
    def test_tarefas_4_perguntas_vezes_ias(self):
        self.assertEqual(len(m.tarefas(EMP, ["claude", "codex"], 3)), 24)

    def test_simulado_marca_e_conta_falha(self):
        c = m.coletar(EMP, ["claude", "codex"], 2, 2, {"claude": [BOA]})
        self.assertEqual(len(c), 16)
        self.assertTrue(all(x["erro"] for x in c if x["ia"] == "codex"))
        self.assertTrue(all(x["resposta"] == BOA for x in c if x["ia"] == "claude"))

    def test_resposta_sem_busca_vira_falha(self):
        aviso = "Não consegui pesquisar na web agora porque a ferramenta de busca foi bloqueada. A Padaria Sol..."
        c = m.coletar(EMP, ["claude"], 1, 1, {"claude": [aviso]})
        self.assertTrue(all("não conseguiu pesquisar" in x["erro"] for x in c))

    def test_claude_libera_a_busca(self):
        feito = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch.object(m.subprocess, "run", return_value=feito) as run:
            m.perguntar_claude("oi")
        cmd = run.call_args[0][0]
        self.assertEqual(cmd[cmd.index("--allowedTools") + 1:cmd.index("--allowedTools") + 3], ["WebSearch", "WebFetch"])

    def test_ia_desconhecida(self):
        with self.assertRaises(m.ErroUso):
            m.motor("chatgpt-web")
        with self.assertRaises(m.ErroUso):
            m.motor("openrouter:")

    def test_timeout_vira_erro_nao_derruba(self):
        with mock.patch.object(m, "motor", return_value=mock.Mock(side_effect=subprocess.TimeoutExpired("x", 1))):
            c = m.coletar(EMP, ["claude"], 1, 1)
        self.assertEqual(len(c), 4)
        self.assertTrue(all(x["erro"] for x in c))

    def test_claude_roda_isolado_em_pasta_vazia(self):
        feito = mock.Mock(returncode=0, stdout="ok", stderr="")
        with mock.patch.object(m.subprocess, "run", return_value=feito) as run:
            self.assertEqual(m.perguntar_claude("oi"), "ok")
        cmd, kw = run.call_args[0][0], run.call_args[1]
        self.assertIn("--setting-sources", cmd)
        self.assertIn("--strict-mcp-config", cmd)
        self.assertEqual(list(pathlib.Path(kw["cwd"]).glob("*")) if pathlib.Path(kw["cwd"]).exists() else [], [])

    def test_codex_usa_home_de_medicao(self):
        def falso(cmd, **kw):
            pathlib.Path(cmd[cmd.index("-o") + 1]).write_text("resposta codex", encoding="utf-8")
            self.assertEqual(kw["env"]["CODEX_HOME"], "/tmp/codex-medir")
            self.assertEqual(cmd[:3], ["codex", "--search", "exec"])
            return mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.dict(m.os.environ, {"MEDIR_CODEX_HOME": "/tmp/codex-medir"}), \
                mock.patch.object(m.subprocess, "run", side_effect=falso):
            self.assertEqual(m.perguntar_codex("oi"), "resposta codex")

    def test_openrouter_sem_chave_nao_chama(self):
        with mock.patch.dict(m.os.environ, {}, clear=True), mock.patch.object(m.urllib.request, "urlopen") as u:
            with self.assertRaises(RuntimeError):
                m.perguntar_openrouter("perplexity/sonar", "oi")
            u.assert_not_called()

    def test_corpo_openrouter(self):
        c = m.corpo_openrouter("perplexity/sonar", "oi")
        self.assertEqual(c["model"], "perplexity/sonar")
        self.assertEqual(c["messages"][-1], {"role": "user", "content": "oi"})


class TestHistorico(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.pasta = pathlib.Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def medir(self, data, resp):
        return m.gravar(self.pasta, EMP, m.coletar(EMP, ["claude"], 1, 1, {"claude": [resp]}), data)

    def test_mesmo_dia_substitui(self):
        self.medir("2026-11-01", BOA)
        hist = self.medir("2026-11-01", BOA)
        self.assertEqual(len(m.ler_historico(hist)), 4)
        self.assertTrue((self.pasta / "2026-11-01.json").exists())

    def test_json_do_dia_serve_no_diagnostico(self):
        self.medir("2026-11-01", BOA)
        resp = json.loads((self.pasta / "2026-11-01.json").read_text(encoding="utf-8"))
        texto, media = m.d.relatorio(EMP, resp)
        self.assertEqual(media, 100)

    def test_curva_e_alerta_de_queda(self):
        self.medir("2026-11-01", BOA)
        hist = self.medir("2026-11-08", RUIM)
        texto, avisos = m.relatorio(EMP, m.ler_historico(hist))
        self.assertIn("| 2026-11-01 | 100 |", texto)
        self.assertIn("| 2026-11-08 | 0 |", texto)
        self.assertTrue(any("caiu de 100 para 0" in a for a in avisos))
        self.assertTrue(any("Hotel Sol" in a for a in avisos))
        self.assertTrue(any("parou de mostrar o site" in a for a in avisos))

    def test_melhora_nao_alerta(self):
        self.medir("2026-11-01", RUIM)
        hist = self.medir("2026-11-08", BOA)
        _, avisos = m.relatorio(EMP, m.ler_historico(hist))
        self.assertEqual(avisos, [])

    def medir_ias(self, data, por_ia):
        return m.gravar(self.pasta, EMP, m.coletar(EMP, list(por_ia), 1, 1, por_ia), data)

    def test_ia_que_cai_nao_gera_queda_falsa_e_avisa(self):
        self.medir_ias("2026-11-01", {"claude": [BOA], "codex": [BOA.replace("padariasol.com.br", "")]})
        hist = self.medir_ias("2026-11-08", {"claude": [], "codex": [BOA.replace("padariasol.com.br", "")]})
        texto, avisos = m.relatorio(EMP, m.ler_historico(hist))
        self.assertFalse(any("caiu" in a for a in avisos), avisos)
        self.assertTrue(any("claude não respondeu" in a for a in avisos))
        self.assertIn("sem resposta", texto)

    def test_falha_total_alerta(self):
        self.medir("2026-11-01", BOA)
        hist = m.gravar(self.pasta, EMP, m.coletar(EMP, ["claude"], 1, 1, {"claude": []}), "2026-11-08")
        _, avisos = m.relatorio(EMP, m.ler_historico(hist))
        self.assertTrue(any("Nenhuma resposta" in a for a in avisos))

    def test_queda_depois_de_semana_quebrada_ainda_alerta(self):
        self.medir("2026-11-01", BOA)
        m.gravar(self.pasta, EMP, m.coletar(EMP, ["claude"], 1, 1, {"claude": []}), "2026-11-08")
        hist = self.medir("2026-11-15", RUIM)
        _, avisos = m.relatorio(EMP, m.ler_historico(hist))
        self.assertTrue(any("caiu de 100 para 0" in a for a in avisos))

    def test_queda_lenta_alerta(self):
        meia = "A Padaria Sol é boa."  # aparece, sem site: 70
        self.assertEqual(m.d.marcar(EMP, meia)["nota"], 70)
        for data, resp in (("2026-11-01", [BOA] * 4), ("2026-11-08", [BOA] * 4),
                           ("2026-11-15", [BOA, BOA, BOA, meia]),      # 92,5: caiu 7,5
                           ("2026-11-22", [BOA, BOA, meia, meia])):    # 85: caiu 7,5 de novo
            hist = self.medir_ias(data, {"claude": resp})
        _, avisos = m.relatorio(EMP, m.ler_historico(hist))
        self.assertFalse(any("caiu" in a for a in avisos), avisos)
        self.assertTrue(any("Queda lenta" in a for a in avisos), avisos)

    def test_queda_lenta_com_mistura_diferente_nao_inventa_piora(self):
        casos = [
            [{"claude": [BOA]}, {"claude": [BOA]},
             {"claude": [BOA], "codex": ["Não conheço essa empresa."]}],
            [{"claude": [BOA], "codex": [BOA]}, {"claude": [BOA]},
             {"claude": [BOA], "codex": []}],
            [{"claude": [BOA]}, {"codex": [BOA]},
             {"gemini": ["Não conheço essa empresa."]}],
        ]
        for caso in casos:
            with self.subTest(ias=[list(dia) for dia in caso]):
                dias = []
                for por_ia in caso:
                    coletas = m.coletar(EMP, list(por_ia), 1, 1, por_ia)
                    linhas = [m.linha_csv("2026-11-24", EMP, c) for c in coletas]
                    dias.append(m.resumo_dia(linhas))
                avisos = m.alertas(dias[:-1], dias[-1])
                self.assertFalse(any("Queda lenta" in a for a in avisos), avisos)

    def test_historico_vazio(self):
        with self.assertRaises(m.ErroUso):
            m.relatorio(EMP, [])


class TestVisitas(unittest.TestCase):
    def test_exemplo_ga4(self):
        t = m.visitas(str(RAIZ / "kit" / "exemplo-origens.csv"))
        self.assertIn("| ChatGPT | 87 |", t)
        self.assertIn("Total vindo das IAs: 111**", t)
        self.assertIn("do total de 1985", t)

    def test_ga4_com_usuarios_antes_de_sessoes(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as f:
            csv.writer(f).writerows([["Origem / mídia da sessão", "Usuários", "Sessões"],
                                     ["chatgpt.com / referral", "60", "87"], ["google / organic", "900", "1.204"]])
        t = m.visitas(f.name)
        self.assertIn("| ChatGPT | 87 |", t)
        self.assertIn("do total de 1291", t)

    def test_ga4_em_espanhol(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8", newline="") as f:
            csv.writer(f).writerows([["Origen de la sesión", "Usuarios", "Sesiones"],
                                     ["perplexity.ai", "5", "9"], ["google", "100", "120"]])
        t = m.visitas(f.name)
        self.assertIn("| Perplexity | 9 |", t)
        self.assertIn("do total de 129", t)

    def test_numero(self):
        self.assertEqual(m.numero("87.0"), 87)
        self.assertEqual(m.numero("87,0"), 87)
        self.assertEqual(m.numero("1.204"), 1204)
        self.assertEqual(m.numero("1,204"), 1204)
        self.assertIsNone(m.numero("—"))

    def test_csv_sem_colunas(self):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            csv.writer(f).writerows([["a", "b"], ["1", "2"]])
        with self.assertRaises(m.ErroUso):
            m.visitas(f.name)


class TestLinhaDeComando(unittest.TestCase):
    def test_rodar_simulado_e_relatorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = rodar("rodar", "kit/exemplo-empresa.json", "--ias", "claude,codex", "--vezes", "1",
                      "--pasta", tmp, "--simular", "kit/exemplo-simulado.json", "--data", "2026-11-24")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("8 respostas guardadas, 0 falhas", r.stdout)
            r = rodar("relatorio", "kit/exemplo-empresa.json", "--pasta", tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("Instituto do Meio Ambiente", r.stdout)

    def test_ia_calada_sai_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = rodar("rodar", "kit/exemplo-empresa.json", "--ias", "claude,gemini", "--vezes", "1",
                      "--pasta", tmp, "--simular", "kit/exemplo-simulado.json")
            self.assertEqual(r.returncode, 1)
            self.assertIn("gemini: 0 respostas válidas", r.stderr)

    def test_ia_errada_sai_2(self):
        r = rodar("rodar", "kit/exemplo-empresa.json", "--ias", "bing")
        self.assertEqual(r.returncode, 2)

    def test_sem_args_sai_2(self):
        self.assertEqual(rodar().returncode, 2)


if __name__ == "__main__":
    unittest.main()
