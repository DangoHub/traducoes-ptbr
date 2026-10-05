"""Testes do fluxo do kit com um jogo falso: python -m unittest kit.test_kit"""
import os
import tempfile
import unittest
from unittest import mock

from kit import correcoes, engines, montagem, projeto
from kit.contexto import filtrar_guia
from kit.engines.base import Engine
from kit.engines.unity_antoolkit import UnityANToolkit
from kit.lotes import preparar
from kit.util import carregar_json, salvar_json
from kit.validar import Regras, carregar_revisados, checar, validar_lote


def unidade(n, en, grupo="g1", quem="Jenna (F)", cat="dialogo"):
    return {"en": en, "alvos": [f"D|{n}"], "cat": cat, "grupo": grupo, "cena": grupo, "quem": quem,
            "tipo": "fala", "traduzir": True}


class EngineFalsa(Engine):
    nome = "falsa"
    unidades = []

    def extrair(self):
        return [dict(u, alvos=list(u["alvos"])) for u in self.unidades]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        raiz = os.path.join(self.tmp.name, "jogo")
        salvar_json(os.path.join(raiz, "jogo.json"), {"nome": "Jogo", "engine": "falsa", "lote_max_chars": 12000})
        for patcher in (mock.patch.object(projeto, "PROJETOS", self.tmp.name),
                        mock.patch.dict(engines.ENGINES, {"falsa": EngineFalsa})):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)
        EngineFalsa.unidades = [unidade(i, f"Line number {i}.") for i in range(1, 9)]
        self.p = projeto.Projeto("jogo")

    def chunk(self, nome):
        return carregar_json(os.path.join(self.p.chunks, nome + ".json"))

    def traduzir_tudo(self, trocas=None):
        for nome in self.p.lotes():
            out = {it["k"]: "Fala " + it["en"].split()[-1] for it in self.chunk(nome) if "k" in it}
            out.update(trocas or {})
            salvar_json(os.path.join(self.p.out, nome + ".json"), out)


class TraducaoIncremental(Base):
    def test_fala_alterada_vem_com_referencias_aprovadas(self):
        preparar(self.p)
        self.traduzir_tudo()
        EngineFalsa.unidades[5]["en"] = "Changed line."
        preparar(self.p)
        itens = self.chunk("dialogo_000")
        pendentes = [it for it in itens if "k" in it]
        refs = [it for it in itens if "k" not in it]
        self.assertEqual([it["en"] for it in pendentes], ["Changed line."])
        self.assertEqual(len(refs), 4)
        self.assertTrue(all("pt" in r for r in refs))
        self.assertEqual(itens[0].get("cena"), "g1")


class RetomadaSegura(Base):
    def test_saida_com_erro_vira_rascunho_e_lotes_sao_arquivados(self):
        preparar(self.p)
        self.traduzir_tudo({"3": ""})
        preparar(self.p)
        itens = [it for it in self.chunk("dialogo_000") if "k" in it]
        self.assertEqual(len(itens), 1)
        self.assertEqual(len(carregar_json(os.path.join(self.p.src, "traducoes.json"))), 7)
        self.assertTrue(os.path.isdir(os.path.join(self.p.work, "historico")))

    def test_rascunho_volta_com_o_motivo(self):
        EngineFalsa.unidades[2]["en"] = "<b><i>Hi</i></b> there."
        preparar(self.p)
        self.traduzir_tudo({"3": "<b><i>Oi</b></i> aí."})
        preparar(self.p)
        item = next(it for it in self.chunk("dialogo_000") if "k" in it)
        self.assertEqual(item["rascunho"], "<b><i>Oi</b></i> aí.")
        self.assertIn("fora de ordem", item["erro"])


class Correcoes(Base):
    def test_pacote_corrige_so_os_ids_e_registra_revisao(self):
        EngineFalsa.unidades[1]["en"] = "Jenna Wright arrives today."
        preparar(self.p)
        self.traduzir_tudo({"1": "", "2": "Jenna Wright arrives today."})
        nomes = correcoes.gerar(self.p, avisos=True)
        itens = correcoes.itens_do_pacote(self.p, nomes[0])
        self.assertEqual({i["id"]: i["problema"] for i in itens}, {"dialogo_000#1": "erro", "dialogo_000#2": "aviso"})
        self.assertIn("contexto", itens[0])
        salvar_json(os.path.join(correcoes.pasta(self.p), nomes[0] + ".saida.json"),
                    {"dialogo_000#1": "Fala 1.", "dialogo_000#2": "="})
        self.assertTrue(correcoes.aplicar(self.p, nomes[0]))
        regras = Regras(self.p.cfg["validacao"])
        _, ok, erros, avisos, _ = validar_lote(self.p, "dialogo_000", regras, False, carregar_revisados(self.p))
        self.assertEqual((ok, erros, avisos), (8, 0, 0))


class Validacao(unittest.TestCase):
    def setUp(self):
        self.r = Regras(projeto.PADROES["validacao"])

    def test_tags_cruzadas_sao_erro(self):
        erros, _ = checar("<b><i>Hello</i></b>", "<b><i>Olá</b></i>", self.r)
        self.assertTrue(any("fora de ordem" in e for e in erros))
        self.assertEqual(checar("<b><i>Hello</i></b>", "<b><i>Olá</i></b>", self.r)[0], [])

    def test_onomatopeia_igual_nao_gera_aviso(self):
        self.assertEqual(checar("<i>Haaahh... Nghh... Mmmf...</i>", "<i>Haaahh... Nghh... Mmmf...</i>", self.r)[1], [])
        self.assertTrue(checar("Lorem ipsum dolor sit", "Lorem ipsum dolor sit", self.r)[1])


class VerificacaoFinal(Base):
    def test_montagem_final_exige_lotes_completos(self):
        preparar(self.p)
        self.assertTrue(montagem.verificar(self.p))
        self.traduzir_tudo()
        self.assertEqual(montagem.verificar(self.p), [])


class ContextoPorLote(unittest.TestCase):
    GUIA = """# Guia
## O jogo
Universo.
## Personagens
### Rida
- Fala quebrado.
### Ray / Lumber Rats
- Sotaque caipira.
## Glossário
| Inglês | PT |
|---|---|
| Crush Waves (laser) | Ondas de Paixão |
| Townhall | Prefeitura |
"""

    def test_guia_filtrado_pelos_textos_e_falantes(self):
        texto = filtrar_guia(self.GUIA, "Rida (F)\nThe Crush Waves hit me.")
        self.assertIn("Universo.", texto)
        self.assertIn("Fala quebrado.", texto)
        self.assertIn("Ondas de Paixão", texto)
        self.assertNotIn("Sotaque caipira", texto)
        self.assertNotIn("Prefeitura", texto)


class DeduplicacaoInterface(unittest.TestCase):
    def test_textos_iguais_so_se_juntam_na_mesma_funcao(self):
        def ui(alvo, en, cena):
            return {"en": en, "alvos": [alvo], "cat": "interface", "grupo": None, "cena": cena, "quem": None,
                    "tipo": "ui", "traduzir": True}
        saida = UnityANToolkit._deduplicar_interface([
            ui("S|Settings.TextureQuality.High", "High", "Settings.TextureQuality.High"),
            ui("S|Settings.GrassDetail.High", "High", "Settings.GrassDetail.High"),
            ui("S|Settings.ControlsTab", "Controls", "Settings.ControlsTab"),
            ui("S|Settings.ControlsTab", "Controls", "Settings.ControlsTab"),
            ui("U|a", "Back", None), ui("U|b", "Back", None),
        ])
        self.assertEqual([(u["en"], len(u["alvos"])) for u in saida],
                         [("High", 1), ("High", 1), ("Controls", 1), ("Back", 2)])


class AlvosUnicos(unittest.TestCase):
    DADOS = {"Dialogues": [{"guid": "g", "Lines": [{"LineId": "l", "originalText": "Hi", "Choices": [
        {"choiceId": "", "originalText": "Show the lights."}, {"choiceId": "", "originalText": "Give supplies."}]}]}],
        "UILocalizations": [], "LocalizedStrings": [], "Missions": [], "JournalEntries": [], "SceneNames": [],
        "Items": [{"Id": "x", "Name": "Holy Armor", "Description": "d1"}, {"Id": "x", "Name": "Elven Leather", "Description": "d2"}],
        "Abilities": []}

    def test_id_repetido_no_jogo_vira_alvo_proprio(self):
        alvos = [a for a, *_ in UnityANToolkit.campos(self.DADOS)]
        self.assertEqual(len(alvos), len(set(alvos)))
        self.assertIn("C|g|l|~1", alvos)
        self.assertIn("I|x|Name~1", alvos)

    def test_traducao_de_outro_texto_nao_e_usada(self):
        with tempfile.TemporaryDirectory() as tmp:
            salvar_json(os.path.join(tmp, "src", "esqueleto.json"), self.DADOS)
            p = mock.Mock(caminho=lambda *x: os.path.join(tmp, *x), cfg={"nome_idioma": "PT", "pasta_dados": "D"})
            arq, _ = UnityANToolkit(p).montar({"I|x|Name": ["Holy Armor", "Armadura Sagrada"],
                                               "I|x|Name~1": ["Old text", "Texto velho"]}, tmp)[0]
            itens = carregar_json(arq)["Items"]
            self.assertEqual([i["TranslatedName"] for i in itens], ["Armadura Sagrada", "Elven Leather"])


if __name__ == "__main__":
    unittest.main()
