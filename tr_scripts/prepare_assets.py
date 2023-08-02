import os
import shutil


from constants import (
    RAW_OUTPUTS_DIRPATH,
    INTERMEDIATE_OUTPUTS_DIRPATH,
    TEXTURE_OUTPUTS_DIRPATH,
)
from utils import get_capture_names


def process_mtl(mtl_filepath: str, texture_filepath):
    with open(mtl_filepath, "r") as f:
        lines = f.readlines()

    with open(mtl_filepath, "w") as f:
        for line in lines:
            if line.startswith("map_Kd "):
                new_line = f"map_Kd {texture_filepath}"
                f.write(new_line)
            # Don't include normal map
            elif line.startswith("norm "):
                continue
            # Don't include ambient occlusion map
            elif line.startswith("map_ao "):
                continue
            else:
                f.write(line)


def prepare_assets(
    names: list[str] = None,
    include_obj: bool = True,
    include_texture: bool = True,
    source_base_dirpath: str = RAW_OUTPUTS_DIRPATH,
    obj_dest_base_dirpath: str = INTERMEDIATE_OUTPUTS_DIRPATH,
    texture_dest_base_dirpath: str = TEXTURE_OUTPUTS_DIRPATH,
):
    # If no specific names are specified use the list of all names
    if names == None:
        names = get_capture_names()

    for i, name in enumerate(names):
        print(i, name)
        source_dirpath = os.path.join(source_base_dirpath, name)

        if include_obj:
            dest_dirpath = os.path.join(obj_dest_base_dirpath, name)
            os.makedirs(dest_dirpath, exist_ok=True)

            filename = "baked_mesh.obj"
            source_filepath = os.path.join(source_dirpath, filename)
            dest_filepath = os.path.join(dest_dirpath, filename)
            shutil.copy(source_filepath, dest_filepath)

            filename = "baked_mesh.mtl"
            source_filepath = os.path.join(source_dirpath, filename)
            dest_filepath = os.path.join(dest_dirpath, filename)
            shutil.copy(source_filepath, dest_filepath)
            process_mtl(dest_filepath)

        if include_texture:
            dest_dirpath = os.path.join(texture_dest_base_dirpath, name)
            os.makedirs(dest_dirpath, exist_ok=True)

            filename = "baked_mesh_tex0.png"
            source_filepath = os.path.join(source_dirpath, filename)
            dest_filepath = os.path.join(dest_dirpath, filename)
            shutil.copy(source_filepath, dest_filepath)


if __name__ == "__main__":
    prepare_assets()
