import bpy
import os
import json

from constants import NAMES, DECIMATED_BASE, GLTF_DIR, INDEX_FILEPATH


def convert(input_dir: str, output_dir: str, name: str):
    bpy.ops.import_scene.obj(filepath=os.path.join(input_dir, f"{name}.obj"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(output_dir, f"{name}.gltf"),
        use_selection=True,
        export_format="GLTF_EMBEDDED",
        export_normals=False,
    )


def export_gltf(
    input_base: str, output_dir: str, names: list[str], index_filepath: str = None
):
    print("EXPORTING")
    for i, name in enumerate(names):
        print(i, name)
        input_dirpath = os.path.join(input_base, name)
        os.makedirs(output_dir, exist_ok=True)

        convert(input_dirpath, output_dir, name)

        if index_filepath:
            os.makedirs
    if index_filepath:
        os.makedirs(os.path.dirname(index_filepath), exist_ok=True)
        index = [
            os.path.join(output_dir.split("public")[-1], name + ".gltf")
            for name in names
        ]
        with open(index_filepath, "w") as file:
            json.dump(index, file, indent=2)


if __name__ == "__main__":
    export_gltf(DECIMATED_BASE, GLTF_DIR, NAMES, index_filepath=INDEX_FILEPATH)
