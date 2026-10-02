"""Leitura/escrita mínima dos formatos do Telltale Tool usados por The Wolf Among Us.

- Blowfish modificado (versão 7) para arquivos .lenc
- Containers .ttarch2 (TTCN / TTCZ) com arquivo interno TTA3/TTA4
- CRC64 ECMA-182 dos nomes de arquivo
"""
import os
import struct
import zlib

from bf_const import P as _P0, S_FLAT as _S0

FABLES_KEY = bytes([
    0x85, 0xca, 0x8f, 0xa0, 0x89, 0xdf, 0x64, 0x73, 0xa2, 0xb2, 0xd6, 0xc6, 0x9e, 0xca, 0xc6, 0x88,
    0x99, 0x5a, 0x73, 0xd8, 0x9f, 0xe1, 0x9b, 0xe2, 0x96, 0x51, 0x9f, 0x9b, 0x9a, 0xce, 0xcd, 0x99,
    0xd2, 0x76, 0x62, 0x7f, 0xa7, 0xc4, 0x9b, 0xd8, 0xda, 0xe7, 0xa9, 0x9c, 0x67, 0x78, 0xb3, 0xd1,
    0xb1, 0xc8, 0x99, 0x64, 0xa0, 0xa2, 0x85,
])
M32 = 0xFFFFFFFF


class Blowfish7:
    def __init__(self, key=FABLES_KEY):
        p = list(_P0)
        s = [list(_S0[i * 256:(i + 1) * 256]) for i in range(4)]
        j = 0
        for i in range(18):
            data = 0
            for _ in range(4):
                data = ((data << 8) | key[j]) & M32
                j = (j + 1) % len(key)
            p[i] ^= data
        v = s[0][118]
        s[0][118] = struct.unpack("<I", struct.pack(">I", v))[0]
        self.p, self.s = p, s
        l = r = 0
        for i in range(0, 18, 2):
            l, r = self._enc_std(l, r)
            p[i], p[i + 1] = l, r
        for i in range(4):
            for k in range(0, 256, 2):
                l, r = self._enc_std(l, r)
                s[i][k], s[i][k + 1] = l, r

    def _enc_std(self, l, r):
        p = self.p
        for i in range(16):
            l ^= p[i]
            r ^= self._f(l)
            l, r = r, l
        l, r = r, l
        r ^= p[16]
        l ^= p[17]
        return l, r

    def _f(self, x):
        s = self.s
        return ((((s[0][x >> 24] + s[1][(x >> 16) & 255]) & M32) ^ s[2][(x >> 8) & 255]) + s[3][x & 255]) & M32

    def _enc(self, l, r):
        p = self.p
        order = (0, 3, 4, 1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        for i in order:
            l ^= p[i]
            r ^= self._f(l)
            l, r = r, l
        l, r = r, l
        r ^= p[16]
        l ^= p[17]
        return l, r

    def _dec(self, l, r):
        p = self.p
        for i in range(17, 1, -1):
            t = {4: p[2], 3: p[1], 2: p[4]}.get(i, p[i])
            l ^= t
            r ^= self._f(l)
            l, r = r, l
        l, r = r, l
        r ^= p[3]
        l ^= p[0]
        return l, r

    def _run(self, data, fn):
        out = bytearray(data)
        n = len(out) - len(out) % 8
        for i in range(0, n, 8):
            l, r = struct.unpack_from("<II", out, i)
            l, r = fn(l, r)
            struct.pack_into("<II", out, i, l, r)
        return bytes(out)

    def decrypt(self, data):
        return self._run(data, self._dec)

    def encrypt(self, data):
        return self._run(data, self._enc)


def _crc64_table():
    poly = 0x42F0E1EBA9EA3693
    table = []
    for i in range(256):
        crc = i << 56
        for _ in range(8):
            crc = ((crc << 1) ^ poly) if crc & (1 << 63) else (crc << 1)
            crc &= 0xFFFFFFFFFFFFFFFF
        table.append(crc)
    return table


_CRC64 = _crc64_table()


def crc64(name):
    crc = 0
    for b in name.lower().encode("latin-1"):
        crc = _CRC64[((crc >> 56) ^ b) & 0xFF] ^ ((crc << 8) & 0xFFFFFFFFFFFFFFFF)
    return crc


class TTArchive2:
    """Leitor sob demanda: só descompacta os blocos necessários."""

    def __init__(self, path):
        self.path = path
        self.f = open(path, "rb")
        magic = self.f.read(4)[::-1]
        self.magic = magic.decode("ascii")
        if self.magic == "TTCN":
            (self.length,) = struct.unpack("<Q", self.f.read(8))
            self.window = 0
        elif self.magic == "TTCZ":
            self.window, pages = struct.unpack("<II", self.f.read(8))
            offs = struct.unpack(f"<{pages + 1}Q", self.f.read(8 * (pages + 1)))
            self.chunk_offs = offs
            self.length = pages * self.window
        else:
            raise ValueError(f"Container não suportado: {self.magic}")
        self.payload_start = self.f.tell()
        self._cache = {}
        self._parse_tta()

    def _chunk(self, i):
        if i not in self._cache:
            if len(self._cache) > 64:
                self._cache.clear()
            a, b = self.chunk_offs[i], self.chunk_offs[i + 1]
            self.f.seek(a)
            raw = self.f.read(b - a)
            self._cache[i] = raw if len(raw) == self.window else zlib.decompress(raw, -15)
        return self._cache[i]

    def read_payload(self, pos, size):
        if self.magic == "TTCN":
            self.f.seek(self.payload_start + pos)
            return self.f.read(size)
        out = bytearray()
        while size > 0:
            ci, off = divmod(pos, self.window)
            chunk = self._chunk(ci)
            part = chunk[off:off + size]
            out += part
            pos += len(part)
            size -= len(part)
        return bytes(out)

    def _parse_tta(self):
        head = self.read_payload(0, 16)
        self.version = head[:4][::-1].decode("ascii")
        p = 4
        if self.version in ("TTA3", "TTA2"):
            p += 4
        names_size, count = struct.unpack_from("<II", self.read_payload(p, 8))
        p += 8
        ent_size = 28 if self.version != "TTA2" else 32
        table = self.read_payload(p, ent_size * count)
        p += ent_size * count
        names_blob = self.read_payload(p, names_size)
        self.files_offset = p + names_size
        self.entries = []
        for i in range(count):
            crc, off, size, preload, pg, po = struct.unpack_from("<QQIIHH", table, i * ent_size)
            start = pg * 0x10000 + po
            name = names_blob[start:names_blob.index(b"\0", start)].decode("latin-1")
            self.entries.append({"name": name, "crc": crc, "offset": off, "size": size})

    def read(self, entry):
        return self.read_payload(self.files_offset + entry["offset"], entry["size"])

    def close(self):
        self.f.close()


def write_ttarch2_ttcn(path, files, version="TTA3"):
    """files = [(nome, bytes)]. Gera um .ttarch2 sem compressão (TTCN)."""
    files = sorted(files, key=lambda f: crc64(f[0]))
    names = bytearray()
    pos = []
    for name, _ in files:
        pos.append(divmod(len(names), 0x10000))
        names += name.encode("latin-1") + b"\0"
    pages = (len(names) + 0xFFFF) // 0x10000
    names += b"\0" * (pages * 0x10000 - len(names))
    body = bytearray(version[::-1].encode("ascii"))
    if version in ("TTA3", "TTA2"):
        body += struct.pack("<I", 2)
    body += struct.pack("<II", pages * 0x10000, len(files))
    off = 0
    for (name, data), (pg, po) in zip(files, pos):
        body += struct.pack("<QQIIHH", crc64(name), off, len(data), 0, pg, po)
        off += len(data)
    body += names
    with open(path, "wb") as f:
        f.write(b"NCTT")
        f.write(struct.pack("<Q", len(body) + off))
        f.write(body)
        for _, data in files:
            f.write(data)


def decrypt_lenc(data, key=FABLES_KEY):
    return Blowfish7(key).decrypt(data)


def encrypt_lenc(data, key=FABLES_KEY):
    return Blowfish7(key).encrypt(data)
