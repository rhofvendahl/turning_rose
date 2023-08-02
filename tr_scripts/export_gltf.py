import os
import json
import shutil

import bpy

from constants import (
    INTERMEDIATE_OUTPUTS_DIRPATH,
    COMPLETE_OUTPUTS_DIRPATH,
    WEBAPP_GLTF_DIRPATH,
    WEBAPP_INDEX_FILEPATH,
    OBJ_FILENAME,
)
from utils import get_names


def convert_to_gltf(source_filepath: str, dest_filepath: str):
    bpy.ops.import_scene.obj(filepath=source_filepath)
    bpy.ops.export_scene.gltf(
        filepath=dest_filepath,
        use_selection=True,
        export_format="GLTF_EMBEDDED",
        export_normals=False,
    )


def export_gltf(
    names: list[str] = None,
    source_base_dirpath: str = INTERMEDIATE_OUTPUTS_DIRPATH,
    dest_dirpath: str = COMPLETE_OUTPUTS_DIRPATH,
    index_filepath: str = WEBAPP_INDEX_FILEPATH,
    copy_to_webapp: bool = False,
):
    os.makedirs(dest_dirpath, exist_ok=True)
    if copy_to_webapp:
        os.makedirs(WEBAPP_GLTF_DIRPATH, exist_ok=True)
    if names == None:
        names = get_names()

    print("EXPORTING")
    for i, name in enumerate(names):
        print(i, name)
        source_dirpath = os.path.join(source_base_dirpath, name)
        source_filepath = os.path.join(source_dirpath, OBJ_FILENAME)
        dest_filepath = os.path.join(dest_dirpath, f"{name}.gltf")
        convert_to_gltf(source_filepath, dest_filepath)

        if copy_to_webapp:
            webapp_source_filepath = os.path.join(dest_dirpath, f"{name}.gltf")
            webapp_dest_filepath = os.path.join(WEBAPP_GLTF_DIRPATH, f"{name}.gltf")
            shutil.copy2(webapp_source_filepath, webapp_dest_filepath)

    if index_filepath:
        os.makedirs(os.path.dirname(index_filepath), exist_ok=True)
        index = [f"{name}.gltf" for name in names]
        with open(index_filepath, "w") as file:
            json.dump(index, file, indent=2)


if __name__ == "__main__":
    export_gltf()
