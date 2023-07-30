import os
from PIL import Image

from constants import NAMES, BLENDER_EXPORT_BASE, PROCESSED_BASE
from utils import copy_assets


def process_image(dirpath: str, name: str, new_size: int = None, to_jpg=True):
    img = Image.open(os.path.join(dirpath, "texgen_2.png"))
    if new_size:
        img = img.resize((new_size, new_size))
    if to_jpg:
        img = img.convert("RGB")
        img.save(os.path.join(dirpath, "texgen_2.jpg"), "JPEG")
    else:
        img.save(os.path.join(dirpath, "texgen_2.png"), "PNG")

    mtl_filepath = os.path.join(dirpath, f"{name}.mtl")
    with open(mtl_filepath, "r") as f:
        lines = f.readlines()

    with open(mtl_filepath, "w") as f:
        for line in lines:
            if to_jpg and line.startswith("map_"):
                line = line.replace(".png", ".jpg")
            if "/" in line:
                # Replace absolute path with relative
                parts = line.split("/")
                line = parts[0] + parts[-1]
            f.write(line)


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
def process_assets(base_dir: str, names: list[str]):
    print("PROCESSING")
    for name in names:
        dirpath = os.path.join(base_dir, name)
        os.makedirs(dirpath, exist_ok=True)
        remove_lines_smoothing_normals_watermark(dirpath, name)  # Modifies in place
        process_image(dirpath, name)


if __name__ == "__main__":
    copy_assets(
        BLENDER_EXPORT_BASE,
        PROCESSED_BASE,
        NAMES,
        include_obj=True,
        include_img=True,
        use_jpg=False,
    )
    process_assets(PROCESSED_BASE, NAMES)
