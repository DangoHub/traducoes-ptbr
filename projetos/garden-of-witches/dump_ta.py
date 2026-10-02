import UnityPy, os
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Garden of Witches\Garden of Witches_Data"
OUT = r"C:\gow_mod\ta"
os.makedirs(OUT, exist_ok=True)
env = UnityPy.load(os.path.join(GAME, "resources.assets"))
for obj in env.objects:
    if obj.type.name == "TextAsset":
        d = obj.read()
        data = d.m_Script
        if isinstance(data, str):
            data = data.encode("utf-8", "surrogateescape")
        name = f"{d.m_Name}__{obj.path_id}.txt"
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(data)
        print(obj.path_id, d.m_Name, len(data), data[:60])
