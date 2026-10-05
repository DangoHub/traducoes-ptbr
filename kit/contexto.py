"""Contexto por pacote: AGENTE.md + o guia do jogo filtrado para os textos recebidos.

Do GUIA_TRADUCAO.md:
- texto corrido (fora de tabelas) entra sempre: universo, tom e regras gerais;
- linha de tabela entra só se algum termo da 1ª coluna aparece nas falas, em quem fala ou na cena;
- em "## Personagens", cada "### Nome / Apelido" entra só se o personagem fala ou é citado.
"""
import os
import re

from kit.util import REPO


def _termos(celula):
    c = re.sub(r"\([^)]*\)", "", celula).replace("**", "").replace("`", "")
    return [t for t in (x.strip(" .!?:;\"'“”") for x in re.split(r"[/,]", c)) if len(t) >= 2]


def _aparece(termos, alvo):
    return any(re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", alvo, re.I) for t in termos)


def _blocos(texto):
    blocos = [[None, 0, []]]
    for linha in texto.splitlines():
        m = re.match(r"^(#+)\s", linha)
        if m:
            blocos.append([linha, len(m.group(1)), []])
        else:
            blocos[-1][2].append(linha)
    return blocos


def _filtrar_tabelas(linhas, alvo):
    saida, tabela = [], []

    def fechar():
        if len(tabela) > 2:
            saida.extend(tabela)
        tabela.clear()

    for linha in linhas:
        if not linha.lstrip().startswith("|"):
            fechar()
            saida.append(linha)
            continue
        if len(tabela) < 2:
            tabela.append(linha)
            continue
        celula = linha.strip().strip("|").split("|")[0]
        if _aparece(_termos(celula), alvo):
            tabela.append(linha)
    fechar()
    return saida


def filtrar_guia(guia, alvo):
    """Devolve o guia só com as partes relevantes para `alvo` (falas, nomes e cenas concatenados)."""
    saida, em_personagens = [], False
    for cabecalho, nivel, linhas in _blocos(guia):
        if nivel == 1:
            continue
        if nivel == 2:
            em_personagens = cabecalho.lstrip("# ").lower().startswith("personagens")
        elif nivel == 3 and em_personagens and not _aparece(_termos(cabecalho.lstrip("# ")), alvo):
            continue
        corpo = _filtrar_tabelas(linhas, alvo)
        tinha_tabela = any(l.lstrip().startswith("|") for l in linhas)
        if tinha_tabela and not any(l.strip() for l in corpo):
            continue
        if cabecalho:
            saida.append(cabecalho)
        saida.extend(corpo)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(saida)).strip() + "\n"


def alvo_dos_itens(itens):
    partes = []
    for it in itens:
        partes += [it.get("en") or "", it.get("quem") or "", it.get("cena") or ""]
        partes += it.get("contexto", [])
    return "\n".join(partes)


def montar_contexto(p, nomes, itens):
    """Grava work/contexto/<pacote>.md e devolve (caminho, texto do guia inteiro, texto gerado)."""
    agente = open(os.path.join(REPO, "kit", "AGENTE.md"), encoding="utf-8").read().strip()
    guia_path = p.caminho("GUIA_TRADUCAO.md")
    guia = open(guia_path, encoding="utf-8").read() if os.path.isfile(guia_path) else ""
    filtrado = filtrar_guia(guia, alvo_dos_itens(itens))
    texto = (f"{agente}\n\n---\n\n# Guia deste pacote: {p.cfg['nome']}\n\n"
             f"Trechos do guia do jogo que valem para os textos que você recebeu.\n\n{filtrado}")
    nome = nomes[0] if len(nomes) == 1 else f"{nomes[0]}+{len(nomes) - 1}"
    path = os.path.join(p.work, "contexto", nome + ".md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(texto)
    return path, agente + "\n" + guia, texto
