import os

from constants import NAMES, BLENDER_EXPORT_BASE, PREPARED_BASE
from utils import copy_assets


def remove_lines_smoothing_normals_watermark(dirpath, name):
    with open(os.path.join(dirpath, name + ".obj"), "r") as f:
        lines = f.readlines()

    with open(os.path.join(dirpath, name + ".obj"), "w") as f:
        for line in lines:
            # Remove watermark, and everything that comes after
            if line.startswith("o watermark"):
                break
            # Remove normals
            elif line.startswith("vn "):
                continue

            # Remove lines
            elif line.startswith("l "):
                continue

            # Remove smoothing
            elif line.startswith("s "):
                continue

            # Remove normals from faces
            elif line.startswith("f "):
                split_ws = line.split()
                new_verts = []
                for vert in split_ws[1:]:
                    # Third value is the idx of normal
                    new_verts.append("/".join(vert.split("/")[:-1]))
                new_line = f"f {' '.join(new_verts)}\n"
                f.write(new_line)
            else:
                f.write(line)


# NOTE: Files are processed in place
def process_assets(input_base: str, output_base: str, names: list[str]):
    print("PREPARING ASSETS")
    copy_assets(
        input_base,
        output_base,
        names,
        include_obj=True,
        include_img=True,
    )
    for name in names:
        dirpath = os.path.join(output_base, name)
        os.makedirs(dirpath, exist_ok=True)
        remove_lines_smoothing_normals_watermark(dirpath, name)  # Modifies in place


if __name__ == "__main__":
    process_assets(BLENDER_EXPORT_BASE, PREPARED_BASE, NAMES)
