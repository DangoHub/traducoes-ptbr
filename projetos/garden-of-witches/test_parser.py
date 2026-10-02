import sys, time
sys.path.insert(0, r"C:\gow_mod\src")
import gow_ptbr_core as core
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Garden of Witches"
t = time.time()
sf = core.SerializedFile(core.game_assets_path(GAME))
print("objects", sf.object_count, len(sf.objects), "types", len(sf.class_ids), "t", round(time.time() - t, 1))
found = sf.find_text_assets({"System", "Story"})
for name, fn in (("System", "ta/System__16811.txt"), ("Story", "ta/Story__16979.txt")):
    obj, (n, script) = found[name]
    ref = open(fn, "rb").read()
    print(name, obj["path_id"], "match", script == ref,
          "reencode ok", len(core.encode_text_asset(n, script)) == obj["byte_size"])
    _, hits, total = core.translate_csv(script, (0, 1) if name == "System" else (0,), {})
    same, _, _ = core.translate_csv(script, (0, 1) if name == "System" else (0,), {})
    print("  csv roundtrip identical", same == script)
print("t", round(time.time() - t, 1))
