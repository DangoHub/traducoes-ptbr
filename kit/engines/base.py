"""Interface comum dos plugins de engine.

Unidade de tradução (dict devolvido por extrair()):
    en       texto original
    alvos    lista de ids de destino (onde a tradução será gravada); mais de um = texto deduplicado.
             Cada id precisa ser único no arquivo final, mesmo que o jogo repita ids internos.
    cat      "dialogo" | "interface" | "textos"  (vira o prefixo do lote)
    grupo    id da conversa/tela; lotes nunca cortam um grupo no meio, se couber
    cena     rótulo legível do grupo (nome do diálogo, da missão...)
    quem     quem fala, ex.: "Jenna (F)"; None se não houver
    tipo     "fala" | "escolha" | "ui" | "nome" | "descricao" ...
    traduzir False para textos que vão como estão (números, placeholders)
"""


class Engine:
    nome = "base"

    def __init__(self, projeto):
        self.p = projeto

    def extrair(self):
        """Lê o jogo instalado, grava o esqueleto do arquivo final em src/ e devolve a lista de unidades."""
        raise NotImplementedError

    def montar(self, traducoes, destino):
        """Gera os arquivos traduzidos em `destino` a partir de src/ (sem precisar do jogo).

        traducoes: {id_alvo: [texto_en, texto_pt]}. Use a tradução só se texto_en for igual ao original atual
        (senão o texto mudou no jogo e a tradução está velha). Devolve [(arquivo_gerado, caminho_no_jogo)].
        """
        raise NotImplementedError

    def arquivo_de_verificacao(self):
        """Caminho relativo que existe na pasta do jogo; o instalador usa para reconhecê-la."""
        raise NotImplementedError
