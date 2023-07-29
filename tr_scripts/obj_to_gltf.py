import bpy
import os
import shutil
from PIL import Image

MODEL_NAMES = [
    "2023-07-19_19",
    "2023-07-20_01",
    "2023-07-20_07",
    "2023-07-20_13_final",
]


def convert(input_dir: str, output_dir: str, name: str):
    bpy.ops.import_scene.obj(filepath=os.path.join(input_dir, f"{name}.obj"))
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(output_dir, f"{name}.gltf"),
        use_selection=True,
        export_format="GLTF_EMBEDDED",
    )


def main():
    for name in MODEL_NAMES[-2:]:
        input_dir = os.path.join(
            os.path.abspath("../data/models/obj/reduced_processed"),
            name,
        )
        output_dir = os.path.abspath("../tr-web/public/db/gltf_auto")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        convert(input_dir, output_dir, name)


if __name__ == "__main__":
    main()
