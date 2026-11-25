import sys

import bpy


def args_after_double_dash():
    argv = sys.argv
    if "--" not in argv:
        raise SystemExit(
            "usage: blender -b --python convert.py -- INPUT.obj OUTPUT.glb"
        )
    args = argv[argv.index("--") + 1 :]
    if len(args) != 2:
        raise SystemExit(
            "usage: blender -b --python convert.py -- INPUT.obj OUTPUT.glb"
        )
    return args[0], args[1]


def main():
    src, dst = args_after_double_dash()

    bpy.ops.wm.read_factory_settings(use_empty=True)

    result = bpy.ops.wm.obj_import(filepath=src)
    if "FINISHED" not in result:
        raise SystemExit(f"OBJ import failed: {src}")

    if not bpy.context.scene.objects:
        raise SystemExit(f"OBJ import produced no objects: {src}")

    result = bpy.ops.export_scene.gltf(filepath=dst, export_format="GLB")
    if "FINISHED" not in result:
        raise SystemExit(f"GLB export failed: {dst}")

    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()
