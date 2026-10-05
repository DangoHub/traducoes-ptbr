"""Translation project: reads projetos/<game>/jogo.json and resolves the standard paths.

The keys of jogo.json stay in Portuguese (project data format); this class exposes them in English.
"""
import os

from kit.config import paths
from kit.engines import get_engine
from kit.platform.storage import load_json

DEFAULTS = {
    "lote_max_chars": 12000,
    "validacao": {
        "tags": [r"<[^<>]+>", r"\{[^{}]*\}"],
        "quebras_de_linha": True,
        "codificacao": "utf-8",
        "escolha_max_proporcao": 1.6,
    },
}


class Project:
    def __init__(self, slug):
        self.slug = slug
        self.root = os.path.join(paths.PROJECTS_DIR, slug)
        config = load_json(os.path.join(self.root, "jogo.json"))
        if config is None:
            raise SystemExit(f"Projeto não encontrado: {self.root}\\jogo.json")
        self.config = {
            **DEFAULTS,
            **config,
            "validacao": {**DEFAULTS["validacao"], **config.get("validacao", {})},
        }

    def path(self, *parts):
        return os.path.join(self.root, *parts)

    # ---------- settings ----------

    @property
    def name(self):
        return self.config["nome"]

    @property
    def version(self):
        return self.config["versao"]

    @property
    def steam_folder(self):
        return self.config["pasta_steam"]

    @property
    def steam_build(self):
        return self.config["steam_build"]

    @property
    def engine_name(self):
        return self.config["engine"]

    @property
    def batch_max_chars(self):
        return self.config["lote_max_chars"]

    @property
    def validation(self):
        return self.config["validacao"]

    @property
    def post_install_notice(self):
        return self.config.get("aviso_pos_instalacao", "")

    @property
    def game_dir(self):
        override = os.environ.get("PASTA_JOGO_" + self.slug.upper().replace("-", "_"))
        return override or os.path.join(paths.STEAM_COMMON_DIR, self.steam_folder)

    # ---------- folders and files ----------

    @property
    def chunks_dir(self):
        return self.path("chunks")

    @property
    def out_dir(self):
        return self.path("out")

    @property
    def work_dir(self):
        return self.path("work")

    @property
    def src_dir(self):
        return self.path("src")

    @property
    def index_path(self):
        return self.path("src", "indice.json")

    @property
    def translations_path(self):
        return self.path("src", "traducoes.json")

    @property
    def drafts_path(self):
        return self.path("src", "rascunhos.json")

    @property
    def reviewed_path(self):
        return self.path("src", "revisao.json")

    @property
    def summary_path(self):
        return self.path("src", "resumo.json")

    @property
    def guide_path(self):
        return self.path("GUIA_TRADUCAO.md")

    @property
    def glossary_path(self):
        return self.path("glossario.json")

    def chunk_path(self, batch):
        return os.path.join(self.chunks_dir, batch + ".json")

    def output_path(self, batch):
        return os.path.join(self.out_dir, batch + ".json")

    def batches(self):
        if not os.path.isdir(self.chunks_dir):
            return []
        return sorted(f[:-5] for f in os.listdir(self.chunks_dir) if f.endswith(".json"))

    def load_chunk(self, batch):
        return load_json(self.chunk_path(batch), [])

    def load_output(self, batch, default=None):
        return load_json(self.output_path(batch), default)

    def engine(self):
        return get_engine(self.engine_name)(self)
