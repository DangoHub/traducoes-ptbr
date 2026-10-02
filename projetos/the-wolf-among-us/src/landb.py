"""Parser/escritor de arquivos .landb (LanguageDB) de The Wolf Among Us.

Preserva todos os bytes originais e só reescreve o nome do personagem e a fala,
recalculando os campos de tamanho afetados.
"""
import struct

CLASS_LANGRES_CRC = bytes.fromhex("B09FD86334024F00")
CLASS_UNICODE = bytes.fromhex("53DCA533DBD6DC7E")
ENCODING = "cp1252"


class Landb:
    def __init__(self, data):
        self.data = data
        r = Reader(data)
        self.magic = r.raw(4)
        self.new_format = self.magic in (b"5VSM", b"6VSM")
        if self.new_format:
            self.hdr_size1, self.hdr_last_size, self.hdr_extra = r.u32(), r.u32(), r.u32()
        n = r.u32()
        classes = [r.raw(12) for _ in range(n)]
        self.has_crc = any(c[:8] == CLASS_LANGRES_CRC for c in classes)
        self.unicode = any(c[:8] == CLASS_UNICODE for c in classes)
        self.body_start = r.pos
        self.pre = r.raw(16)
        self.block_length_pos = r.pos
        r.u32()
        count = r.u32()
        self.records = []
        for _ in range(count):
            rec = {}
            start = r.pos
            r.u32()
            if self.has_crc:
                r.raw(8)
            rec["id"] = r.u32()
            r.u32()
            blk = r.u32()
            if self.has_crc:
                r.raw(8)
            else:
                r.raw(r.u32())
            r.u32()
            if self.has_crc:
                r.raw(8)
            else:
                r.raw(r.u32())
            r.u32()
            r.raw(r.u32())
            r.u32()
            rec["head"] = data[start:r.pos]
            r.u32()  # blockLangresSize
            r.u32()  # blockActorNameSize
            rec["actor"] = r.raw(r.u32())
            r.u32()  # blockActorSpeechSize
            rec["speech"] = r.raw(r.u32())
            tail_start = r.pos
            rec["block_size"] = r.u32()
            r.u32()
            if self.unicode:
                r.raw(r.u32() - 4)
            r.u32()
            rec["tail"] = data[tail_start:r.pos]
            self.records.append(rec)
        self.records_end = r.pos
        self.rest = data[r.pos:]

    def text(self, rec, field):
        return rec[field].decode("utf-8" if self.unicode else ENCODING)

    def set_text(self, rec, field, value):
        rec[field] = value.encode("utf-8" if self.unicode else ENCODING)

    def build(self):
        recs = bytearray()
        for rec in self.records:
            a, s = rec["actor"], rec["speech"]
            langres = 4 + (len(a) + 8) + (len(s) + 8) + rec["block_size"]
            recs += rec["head"]
            recs += struct.pack("<III", langres, len(a) + 8, len(a)) + a
            recs += struct.pack("<II", len(s) + 8, len(s)) + s
            recs += rec["tail"]
        block_length = 8 + len(recs)
        body = bytearray(self.pre)
        body += struct.pack("<II", block_length, len(self.records))
        body += recs
        out = bytearray(self.data[:self.body_start])
        main = body + self.rest
        if self.new_format:
            last = self.hdr_last_size
            main_size = len(main) - last
            struct.pack_into("<I", out, 4, main_size)
        out += main
        return bytes(out)


class Reader:
    def __init__(self, data):
        self.d = data
        self.pos = 0

    def u32(self):
        v = struct.unpack_from("<I", self.d, self.pos)[0]
        self.pos += 4
        return v

    def raw(self, n):
        if n < 0 or self.pos + n > len(self.d):
            raise ValueError(f"leitura fora do arquivo em {self.pos} (+{n})")
        v = self.d[self.pos:self.pos + n]
        self.pos += n
        return v
