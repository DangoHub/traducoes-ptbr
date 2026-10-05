from kit.engines.unity_antoolkit import UnityANToolkit

ENGINES = {engine.name: engine for engine in (UnityANToolkit,)}


def get_engine(name):
    if name not in ENGINES:
        raise SystemExit(f"Engine desconhecida: {name}. Disponíveis: {', '.join(ENGINES)}")
    return ENGINES[name]
