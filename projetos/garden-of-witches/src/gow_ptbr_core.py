"""Patcher leve para os TextAssets de localização de Garden of Witches.

Não carrega o arquivo inteiro: lê apenas a tabela de objetos do SerializedFile,
grava os novos TextAssets no final do resources.assets e atualiza os ponteiros.
"""
import csv
import io
import json
import os
import struct

ASSETS_REL = os.path.join("Garden of Witches_Data", "resources.assets")
BACKUP_NAME = "ptbr_mod_backup.json"
TARGET_COLUMN = "en"
TEXTASSET_CLASS_ID = 49
MOD_VERSION = "1.1.0"


class PatchError(Exception):
    pass


def _align(pos, n=4):
    return (pos + n - 1) // n * n


class SerializedFile:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            head = f.read(48)
            _, _, self.version, _ = struct.unpack(">IIII", head[:16])
            if self.version < 22:
                raise PatchError(f"Formato de arquivo não suportado (versão {self.version}).")
            if head[16] != 0:
                raise PatchError("Arquivo big-endian não suportado.")
            self.metadata_size, self.file_size, self.data_offset, _ = struct.unpack(">IQQQ", head[20:48])
            meta = f.read(self.metadata_size)
        self._parse(meta, 48)

    def _parse(self, meta, base):
        p = meta.index(b"\0") + 1
        p += 4
        enable_typetree = meta[p]
        p += 1
        if enable_typetree:
            raise PatchError("Arquivo com typetree não suportado por este patcher.")
        (type_count,) = struct.unpack_from("<i", meta, p)
        p += 4
        self.class_ids = []
        for _ in range(type_count):
            class_id, _stripped, script_index = struct.unpack_from("<iBh", meta, p)
            p += 7
            if class_id == 114:
                p += 16
            p += 16
            self.class_ids.append(class_id)
        (obj_count,) = struct.unpack_from("<i", meta, p)
        p += 4
        self.object_count = obj_count
        self.objects = []
        entry = struct.Struct("<qqIi")
        for _ in range(obj_count):
            p = _align(base + p) - base
            path_id, byte_start, byte_size, type_id = entry.unpack_from(meta, p)
            if self.class_ids[type_id] == TEXTASSET_CLASS_ID:
                self.objects.append({
                    "entry_offset": base + p,
                    "path_id": path_id,
                    "byte_start": byte_start,
                    "byte_size": byte_size,
                    "class_id": TEXTASSET_CLASS_ID,
                })
            p += entry.size

    def read_object(self, f, obj):
        f.seek(self.data_offset + obj["byte_start"])
        return f.read(obj["byte_size"])

    def find_text_assets(self, names):
        found = {}
        with open(self.path, "rb") as f:
            for obj in self.objects:
                if obj["class_id"] != TEXTASSET_CLASS_ID:
                    continue
                f.seek(self.data_offset + obj["byte_start"])
                (n,) = struct.unpack("<i", f.read(4))
                if 0 < n < 256:
                    name = f.read(n).decode("utf-8", "replace")
                    if name in names:
                        raw = self.read_object(f, obj)
                        found[name] = (obj, decode_text_asset(raw))
        return found


def decode_text_asset(raw):
    (n,) = struct.unpack_from("<i", raw, 0)
    name = raw[4:4 + n].decode("utf-8")
    p = _align(4 + n)
    (m,) = struct.unpack_from("<i", raw, p)
    return name, raw[p + 4:p + 4 + m]


def encode_text_asset(name, script):
    nb = name.encode("utf-8")
    out = bytearray(struct.pack("<i", len(nb)) + nb)
    out += b"\0" * (_align(len(out)) - len(out))
    out += struct.pack("<i", len(script)) + script
    out += b"\0" * (_align(len(out)) - len(out))
    return bytes(out)


def translate_csv(script_bytes, key_cols, translations):
    """Substitui a coluna TARGET_COLUMN pelas traduções. key_cols = índices das colunas que formam a chave."""
    text = script_bytes.decode("utf-8")
    rows = list(csv.reader(io.StringIO(text, newline="")))
    col = rows[0].index(TARGET_COLUMN)
    hits = 0
    for r in rows[1:]:
        if len(r) <= col:
            continue
        key = "||".join(r[i] for i in key_cols)
        pt = translations.get(key)
        if pt:
            r[col] = pt
            hits += 1
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\r\n").writerows(rows)
    out = buf.getvalue()
    if not text.endswith("\r\n") and out.endswith("\r\n"):
        out = out[:-2]
    return out.encode("utf-8"), hits, len(rows) - 1


def game_assets_path(game_dir):
    return os.path.join(game_dir, ASSETS_REL)


def backup_path(game_dir):
    return os.path.join(game_dir, "Garden of Witches_Data", BACKUP_NAME)


def is_installed(game_dir):
    bp = backup_path(game_dir)
    if not os.path.exists(bp):
        return False
    info = json.load(open(bp, encoding="utf-8"))
    return os.path.getsize(game_assets_path(game_dir)) == info["patched_file_size"]


def uninstall(game_dir, log=print):
    bp = backup_path(game_dir)
    ap = game_assets_path(game_dir)
    if not os.path.exists(bp):
        raise PatchError("A tradução não está instalada (backup não encontrado).")
    info = json.load(open(bp, encoding="utf-8"))
    if os.path.getsize(ap) != info["patched_file_size"]:
        os.remove(bp)
        raise PatchError("O arquivo do jogo foi alterado (provavelmente uma atualização da Steam). "
                         "O jogo já está no estado original; backup antigo descartado.")
    with open(ap, "r+b") as f:
        for e in info["entries"]:
            f.seek(e["entry_offset"] + 8)
            f.write(struct.pack("<qI", e["byte_start"], e["byte_size"]))
        f.seek(24)
        f.write(struct.pack(">Q", info["original_file_size"]))
        f.truncate(info["original_file_size"])
    os.remove(bp)
    log("Tradução removida. Jogo restaurado ao original.")


def install(game_dir, translations, log=print):
    """translations = {"System": {grupo||codigo: texto}, "Story": {nome: texto}}"""
    ap = game_assets_path(game_dir)
    if not os.path.exists(ap):
        raise PatchError(f"Não encontrei {ASSETS_REL} em:\n{game_dir}")
    if os.path.exists(backup_path(game_dir)):
        try:
            log("Versão anterior detectada, removendo antes de reinstalar...")
            uninstall(game_dir, log)
        except PatchError as e:
            log(str(e))

    log("Lendo índice do resources.assets...")
    sf = SerializedFile(ap)
    original_size = os.path.getsize(ap)
    if original_size != sf.file_size:
        raise PatchError("Tamanho do arquivo não confere com o cabeçalho; arquivo corrompido? "
                         "Verifique a integridade dos arquivos na Steam.")
    found = sf.find_text_assets({"System", "Story"})
    if set(found) != {"System", "Story"}:
        raise PatchError("Não encontrei as tabelas de texto (System/Story). Versão do jogo incompatível?")

    payloads = []
    for name, key_cols in (("System", (0, 1)), ("Story", (0,))):
        obj, (asset_name, script) = found[name]
        new_script, hits, total = translate_csv(script, key_cols, translations[name])
        log(f"{name}: {hits} de {total} linhas traduzidas.")
        payloads.append((obj, encode_text_asset(asset_name, new_script)))

    entries = []
    with open(ap, "r+b") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        for obj, data in payloads:
            start = _align(pos, 16)
            f.write(b"\0" * (start - pos))
            f.write(data)
            pos = start + len(data)
            entries.append({"entry_offset": obj["entry_offset"], "byte_start": obj["byte_start"],
                            "byte_size": obj["byte_size"], "path_id": obj["path_id"]})
            f.seek(obj["entry_offset"])
            path_id = struct.unpack("<q", f.read(8))[0]
            if path_id != obj["path_id"]:
                raise PatchError("Inconsistência na tabela de objetos; abortando.")
            f.write(struct.pack("<qI", start - sf.data_offset, len(data)))
            f.seek(0, os.SEEK_END)
        new_size = f.tell()
        f.seek(24)
        f.write(struct.pack(">Q", new_size))

    json.dump({"mod_version": MOD_VERSION, "original_file_size": original_size,
               "patched_file_size": new_size, "entries": entries},
              open(backup_path(game_dir), "w", encoding="utf-8"), indent=1)
    log("Tradução instalada com sucesso!")


def read_current_text(game_dir, name):
    sf = SerializedFile(game_assets_path(game_dir))
    return sf.find_text_assets({name})[name][1][1]
