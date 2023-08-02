import os
import shutil


from constants import (
    RAW_OUTPUTS_DIRPATH,
    INTERMEDIATE_OUTPUTS_DIRPATH,
    TEXTURE_FILENAME,
    OBJ_FILENAME,
    MTL_FILENAME,
)
from utils import get_names


def process_mtl(mtl_filepath: str, texture_filepath):
    with open(mtl_filepath, "r") as f:
        lines = f.readlines()

    with open(mtl_filepath, "w") as f:
        for line in lines:
            if line.startswith("map_Kd "):
                new_line = f"map_Kd {texture_filepath}\n"
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
    dest_base_dirpath: str = INTERMEDIATE_OUTPUTS_DIRPATH,
):
    # If no specific names are specified use the list of all names
    if names == None:
        names = get_names()

    for i, name in enumerate(names):
        print(i, name)
        source_dirpath = os.path.join(source_base_dirpath, name)
        dest_dirpath = os.path.join(dest_base_dirpath, name)
        os.makedirs(dest_dirpath, exist_ok=True)

        if include_obj:
            source_filepath = os.path.join(source_dirpath, OBJ_FILENAME)
            dest_filepath = os.path.join(dest_dirpath, OBJ_FILENAME)
            shutil.copy(source_filepath, dest_filepath)

            source_filepath = os.path.join(source_dirpath, MTL_FILENAME)
            dest_filepath = os.path.join(dest_dirpath, MTL_FILENAME)
            shutil.copy(source_filepath, dest_filepath)
            process_mtl(dest_filepath, os.path.join(dest_dirpath, TEXTURE_FILENAME))

        if include_texture:
            source_filepath = os.path.join(source_dirpath, TEXTURE_FILENAME)
            dest_filepath = os.path.join(dest_dirpath, TEXTURE_FILENAME)
            shutil.copy(source_filepath, dest_filepath)


if __name__ == "__main__":
    prepare_assets()
