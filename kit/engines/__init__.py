from kit.engines.unity_antoolkit import UnityANToolkit

ENGINES = {e.nome: e for e in (UnityANToolkit,)}


def obter(nome):
    if nome not in ENGINES:
        raise SystemExit(f"Engine desconhecida: {nome}. Disponíveis: {', '.join(ENGINES)}")
    return ENGINES[nome]
