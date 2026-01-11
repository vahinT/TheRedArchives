import os
from Engine.math3d import Vec3
from Engine.part import Part


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def load_workspace(engine, path="Workspace"):
    if not os.path.isdir(path):
        return

    for filename in os.listdir(path):
        if not filename.endswith(".part"):
            continue

        filepath = os.path.join(path, filename)
        data = _read_kv_file(filepath)

        pos = Vec3(*_parse_vec(data.get("pos", "0,0,0")))
        size = Vec3(*_parse_vec(data.get("size", "1,1,1")))
        collidable = data.get("collidable", "true").lower() == "true"

        color = (200, 200, 200)
        if "color" in data:
            color = hex_to_rgb(data["color"])

        part = Part(pos, size, collidable, color)
        engine.world.add_part(part)


def load_scripts(world, path="ScriptService"):
    if not os.path.isdir(path):
        return

    for filename in os.listdir(path):
        if filename.endswith(".bix"):
            with open(os.path.join(path, filename), "r", encoding="utf-8") as f:
                code = f.read()

            print(f"[Loader] Loaded script: {filename}")
            world.add_script(code)


def _read_kv_file(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
    return data


def _parse_vec(text):
    return [float(v) for v in text.split(",")]
