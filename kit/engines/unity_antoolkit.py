"""Unity + ANToolkit (Anduo Games, ex.: Third Crisis).

O jogo carrega StreamingAssets/Languages/customtranslated_<nome>.json e mostra "Custom <nome>" no menu.
O arquivo segue o formato das traduções oficiais (translated_es_translation.json): falas indexadas por
guid do diálogo + LineId, interface por guid etc. Entrada ausente = texto vazio no jogo, então o arquivo
final é sempre completo, com o inglês como reserva.

Quem fala não está no JSON: vem dos assets Dialogue/Character (lidos com UnityPy + typetree das DLLs).
"""
import copy
import os
import re
import sys

from kit.engines.base import Engine
from kit.util import carregar_json, salvar_json

try:
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
except ImportError:
    UnityPy = None

CAMPOS_TRADUZIDOS = ("text", "TranslatedName", "TranslatedDescription", "TranslatedDisplayName",
                     "TranslatedContents", "TranslatedToolTip")
SO_SIMBOLOS = re.compile(r"^[^A-Za-z]*$")
TOKEN_INTEIRO = re.compile(r"^#\w+#$")


def _ordem_natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


class UnityANToolkit(Engine):
    nome = "unity_antoolkit"

    @property
    def dados(self):
        return self.p.cfg["pasta_dados"]

    @property
    def pasta_idiomas(self):
        return os.path.join(self.dados, "StreamingAssets", "Languages")

    @property
    def nome_arquivo(self):
        return f"customtranslated_{self.p.cfg['nome_idioma']}.json"

    @property
    def esqueleto_path(self):
        return self.p.caminho("src", "esqueleto.json")

    def arquivo_de_verificacao(self):
        return self.pasta_idiomas

    # ---------- extração ----------

    def extrair(self):
        jogo = self.p.pasta_jogo
        modelo = carregar_json(os.path.join(jogo, self.pasta_idiomas, self.p.cfg["modelo"]))
        if modelo is None:
            raise SystemExit(f"Modelo não encontrado em {os.path.join(jogo, self.pasta_idiomas)}")

        esqueleto = copy.deepcopy(modelo)
        self._limpar(esqueleto)
        salvar_json(self.esqueleto_path, esqueleto, indent=None)

        meta = self._ler_dialogos(jogo)
        nao_traduzir = set(self.p.cfg.get("nao_traduzir", []))
        unidades = []

        def add(en, alvo, cat, grupo=None, cena=None, quem=None, tipo="fala"):
            if not isinstance(en, str) or not en.strip():
                return
            traduzir = not (SO_SIMBOLOS.match(en) or TOKEN_INTEIRO.match(en.strip()) or en in nao_traduzir)
            unidades.append({"en": en, "alvos": [alvo], "cat": cat, "grupo": grupo, "cena": cena,
                             "quem": quem, "tipo": tipo, "traduzir": traduzir})

        for dlg in sorted(modelo["Dialogues"], key=lambda d: _ordem_natural(d["name"])):
            linhas_meta = meta.get(dlg["guid"], {})
            for ln in dlg["Lines"]:
                quem = linhas_meta.get(ln["LineId"])
                add(ln["originalText"], f"D|{dlg['guid']}|{ln['LineId']}", "dialogo", dlg["guid"], dlg["name"], quem)
                for ch in ln["Choices"]:
                    add(ch["originalText"], f"C|{dlg['guid']}|{ln['LineId']}|{ch['choiceId']}", "dialogo",
                        dlg["guid"], dlg["name"], None, "escolha")

        for m in modelo["Missions"]:
            g = "M:" + m["Id"]
            add(m["Name"], f"M|{m['Id']}|Name", "textos", g, m["Name"], tipo="titulo de missao")
            add(m["Description"], f"M|{m['Id']}|Description", "textos", g, m["Name"], tipo="descricao de missao")
            for t in m["Tasks"]:
                add(t["DisplayName"], f"T|{m['Id']}|{t['Id']}", "textos", g, m["Name"], tipo="tarefa de missao")
        for j in modelo["JournalEntries"]:
            g = "J:" + j["Id"]
            add(j["Name"], f"J|{j['Id']}|Name", "textos", g, j["Name"], tipo="titulo do diario")
            add(j["Contents"], f"J|{j['Id']}|Contents", "textos", g, j["Name"], tipo="texto do diario")
        for it in modelo["Items"]:
            g = "I:" + it["Id"]
            add(it["Name"], f"I|{it['Id']}|Name", "textos", g, it["Name"], tipo="nome de item")
            add(it["Description"], f"I|{it['Id']}|Description", "textos", g, it["Name"], tipo="descricao de item")
        for a in modelo["Abilities"]:
            g = "A:" + a["Id"]
            add(a["Name"], f"A|{a['Id']}|Name", "textos", g, a["Name"], tipo="nome de habilidade")
            add(a["Tooltip"], f"A|{a['Id']}|Tooltip", "textos", g, a["Name"], tipo="descricao de habilidade")
        for s in modelo["SceneNames"]:
            add(s["Name"], f"N|{s['Id']}", "textos", "lugares", "Nomes de lugares", tipo="nome de lugar")

        for s in modelo["LocalizedStrings"]:
            add(s["originalText"], f"S|{s['Identifier']}", "interface", cena=s["Identifier"], tipo="ui")
        for u in modelo["UILocalizations"]:
            add(u["originalText"], f"U|{u['guid']}", "interface", tipo="ui")
        return self._deduplicar_interface(unidades)

    @staticmethod
    def _limpar(esqueleto):
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in CAMPOS_TRADUZIDOS and isinstance(v, str):
                        o[k] = ""
                    else:
                        walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(esqueleto)

    @staticmethod
    def _deduplicar_interface(unidades):
        saida, por_texto = [], {}
        for u in unidades:
            if u["cat"] != "interface":
                saida.append(u)
                continue
            if u["en"] in por_texto:
                por_texto[u["en"]]["alvos"] += u["alvos"]
            else:
                por_texto[u["en"]] = u
                saida.append(u)
        return saida

    # ---------- quem fala (assets) ----------

    def _ler_dialogos(self, jogo):
        """{guid: {lineId: "Nome (F)"}} a partir dos assets Dialogue/Character."""
        if UnityPy is None:
            print("AVISO: UnityPy/TypeTreeGeneratorAPI ausentes; lotes sairão sem 'quem fala'.")
            return {}
        data = os.path.join(jogo, self.dados)
        arquivos = sorted(f for f in os.listdir(data) if f.endswith(".assets") or f.startswith("level"))
        gen, nodes = None, {}
        classes = {"Dialogue": "Asuna.Dialogues.Dialogue", "Character": "Asuna.CharManagement.Character"}
        dialogos, personagens = {}, {}

        for f in arquivos:
            env = UnityPy.load(os.path.join(data, f))
            for obj in env.objects:
                if obj.type.name != "MonoBehaviour":
                    continue
                try:
                    base = obj.read(check_read=False)
                    cls = base.m_Script.read().m_ClassName
                except Exception:
                    continue
                if cls not in classes:
                    continue
                if gen is None:
                    gen = TypeTreeGenerator(obj.assets_file.unity_version)
                    gen.load_local_dll_folder(os.path.join(data, "Managed"))
                if cls not in nodes:
                    nodes[cls] = gen.get_nodes_up("Assembly-CSharp", classes[cls])
                chave = f"{f}:{obj.path_id}"
                try:
                    tr = obj.read_typetree(nodes[cls])
                except Exception:
                    if cls == "Character":
                        personagens[chave] = {"nome": base.m_Name, "genero": None}
                    continue
                if cls == "Character":
                    personagens[chave] = {"nome": tr.get("Name") or tr["m_Name"],
                                          "genero": ("M", "F")[tr.get("Gender", 0)]}
                    continue
                ext = [os.path.basename(e.path) for e in obj.assets_file.externals]

                def ref(p):
                    if not p["m_PathID"]:
                        return None
                    origem = f if p["m_FileID"] == 0 else ext[p["m_FileID"] - 1]
                    return f"{origem}:{p['m_PathID']}"
                dialogos[tr["Guid"]] = {"nome": tr["m_Name"], "linhas": {
                    l["LineID"]: {"speaker": l["Speaker"], "override": l["NameOverride"], "char": ref(l["Character"]),
                                  "preset": (l.get("PresetLocation", ""), l.get("PresetID", ""))}
                    for l in tr["Lines"]}}

        presets = {d["nome"]: d for d in dialogos.values()}
        falantes = {}
        for guid, d in dialogos.items():
            falantes[guid] = {}
            for lid, l in d["linhas"].items():
                loc, pid = l["preset"]
                if pid:
                    alvo = presets.get(loc.split("/")[-1], {}).get("linhas", {}).get(pid)
                    if alvo:
                        l = {**l, "speaker": alvo["speaker"], "override": alvo["override"], "char": alvo["char"]}
                falantes[guid][lid] = self._falante(l, personagens)

        generos = self._generos(personagens, falantes)
        resultado = {guid: {lid: self._rotulo(f, generos) for lid, f in linhas.items()} for guid, linhas in falantes.items()}
        print(f"Quem fala: {len(dialogos)} diálogos e {len(personagens)} personagens lidos dos assets.")
        return resultado

    @staticmethod
    def _falante(l, personagens):
        """(nome exibido no jogo, gênero do asset ou None), seguindo DialoguePopulateInfo do jogo."""
        c = personagens.get(l["char"]) if l["char"] else None
        nome = (l["override"] or c["nome"]) if c else l["speaker"]
        return (nome or "").strip(), (c["genero"] if c else None)

    def _generos(self, personagens, falantes):
        """Gênero por nome exibido. personagens.json do projeto (editável) completa o que os assets não dizem."""
        path = self.p.caminho("personagens.json")
        manual = carregar_json(path, {})
        auto = {}
        for c in personagens.values():
            if c["nome"] and c["genero"]:
                auto.setdefault(c["nome"], c["genero"])
        contagem = {}
        for linhas in falantes.values():
            for nome, g in linhas.values():
                if nome and nome != "Narrator":
                    contagem[nome] = contagem.get(nome, 0) + 1
                    if g:
                        auto.setdefault(nome, g)
        nomes = sorted(contagem, key=lambda n: -contagem[n])
        salvar_json(path, {n: manual.get(n, auto.get(n)) for n in nomes} | {n: g for n, g in manual.items() if n not in contagem})
        return {**auto, **{n: g for n, g in manual.items() if g}}

    @staticmethod
    def _rotulo(falante, generos):
        nome = falante[0]
        if not nome:
            return None
        if nome == "Narrator":
            return "Narrador"
        g = generos.get(nome)
        return f"{nome} ({g})" if g in ("F", "M") else nome

    # ---------- montagem ----------

    def montar(self, traducoes, destino):
        esq = carregar_json(self.esqueleto_path)
        if esq is None:
            raise SystemExit("src/esqueleto.json não existe; rode 'python -m kit extrair' primeiro.")
        usados = 0

        def pt(alvo, original):
            nonlocal usados
            t = traducoes.get(alvo)
            if t:
                usados += 1
                return t
            return original

        for d in esq["Dialogues"]:
            for ln in d["Lines"]:
                ln["text"] = pt(f"D|{d['guid']}|{ln['LineId']}", ln["originalText"])
                for ch in ln["Choices"]:
                    ch["text"] = pt(f"C|{d['guid']}|{ln['LineId']}|{ch['choiceId']}", ch["originalText"])
        for u in esq["UILocalizations"]:
            u["text"] = pt(f"U|{u['guid']}", u["originalText"])
        for s in esq["LocalizedStrings"]:
            s["text"] = pt(f"S|{s['Identifier']}", s["originalText"])
        for m in esq["Missions"]:
            m["TranslatedName"] = pt(f"M|{m['Id']}|Name", m["Name"])
            m["TranslatedDescription"] = pt(f"M|{m['Id']}|Description", m["Description"])
            for t in m["Tasks"]:
                t["TranslatedDisplayName"] = pt(f"T|{m['Id']}|{t['Id']}", t["DisplayName"])
        for j in esq["JournalEntries"]:
            j["TranslatedName"] = pt(f"J|{j['Id']}|Name", j["Name"])
            j["TranslatedContents"] = pt(f"J|{j['Id']}|Contents", j["Contents"])
        for it in esq["Items"]:
            it["TranslatedName"] = pt(f"I|{it['Id']}|Name", it["Name"])
            it["TranslatedDescription"] = pt(f"I|{it['Id']}|Description", it["Description"])
        for a in esq["Abilities"]:
            a["TranslatedName"] = pt(f"A|{a['Id']}|Name", a["Name"])
            a["TranslatedToolTip"] = pt(f"A|{a['Id']}|Tooltip", a["Tooltip"])
        for s in esq["SceneNames"]:
            s["TranslatedName"] = pt(f"N|{s['Id']}", s["Name"])

        os.makedirs(destino, exist_ok=True)
        arq = os.path.join(destino, self.nome_arquivo)
        salvar_json(arq, esq, indent=None)
        print(f"{self.nome_arquivo}: {usados} campos traduzidos", file=sys.stderr)
        return [(arq, os.path.join(self.pasta_idiomas, self.nome_arquivo).replace("\\", "/"))]
