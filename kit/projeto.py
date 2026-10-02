"""Projeto de tradução: lê projetos/<jogo>/jogo.json e resolve os caminhos padrão."""
import os

from kit.engines import obter
from kit.util import PROJETOS, carregar_json

PADROES = {
    "lote_max_chars": 12000,
    "validacao": {
        "tags": [r"<[^<>]+>", r"\{[^{}]*\}"],
        "quebras_de_linha": True,
        "codificacao": "utf-8",
        "escolha_max_proporcao": 1.6,
    },
}


class Projeto:
    def __init__(self, slug):
        self.slug = slug
        self.root = os.path.join(PROJETOS, slug)
        cfg = carregar_json(os.path.join(self.root, "jogo.json"))
        if cfg is None:
            raise SystemExit(f"Projeto não encontrado: {self.root}\\jogo.json")
        self.cfg = {**PADROES, **cfg, "validacao": {**PADROES["validacao"], **cfg.get("validacao", {})}}

    def caminho(self, *partes):
        return os.path.join(self.root, *partes)

    @property
    def chunks(self):
        return self.caminho("chunks")

    @property
    def out(self):
        return self.caminho("out")

    @property
    def work(self):
        return self.caminho("work")

    @property
    def src(self):
        return self.caminho("src")

    @property
    def indice_path(self):
        return self.caminho("src", "indice.json")

    @property
    def pasta_jogo(self):
        env = os.environ.get("PASTA_JOGO_" + self.slug.upper().replace("-", "_"))
        if env:
            return env
        return os.path.join(r"C:\Program Files (x86)\Steam\steamapps\common", self.cfg["pasta_steam"])

    def engine(self):
        return obter(self.cfg["engine"])(self)

    def lotes(self):
        if not os.path.isdir(self.chunks):
            return []
        return sorted(f[:-5] for f in os.listdir(self.chunks) if f.endswith(".json"))
