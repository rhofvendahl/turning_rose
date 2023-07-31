import os
from PIL import Image
import numpy as np

from constants import NAMES, DECIMATED_BASE, RETEXTURED_BASE


def resize_image(
    input_dirpath: str,
    output_dirpath: str,
    name: str,
    new_size: int = None,
):
    img = Image.open(os.path.join(input_dirpath, "texgen_2.png"))
    img = img.resize((new_size, new_size))
    img.save(os.path.join(output_dirpath, "texgen_2.png"), "PNG")

    with open(os.path.join(input_dirpath, name + ".mtl"), "r") as f:
        lines = f.readlines()

    with open(os.path.join(output_dirpath, name + ".mtl"), "w") as f:
        for line in lines:
            if "/" in line:
                # Replace absolute path with relative
                parts = line.split("/")
                line = parts[0] + parts[-1]
            f.write(line)


def scale_hsv(hsv):
    h_new = int((hsv[0] / 360) * 255)
    s_new = int((hsv[1] / 100) * 255)
    v_new = int((hsv[2] / 100) * 255)

    return [h_new, s_new, v_new]


def filter_texture(input_dirpath, output_dirpath, lower_bound, upper_bound):
    lower_bound = scale_hsv(lower_bound)
    upper_bound = scale_hsv(upper_bound)

    img = Image.open(os.path.join(input_dirpath, "texgen_2.png")).convert("RGBA")
    img_np = np.array(img)

    # Convert to hsv
    img_hsv = np.array(img.convert("RGB"))

    # Find pixels in range and set alpha channel to 0 (transparent)
    in_range = np.all((img_hsv >= lower_bound) & (img_hsv <= upper_bound), axis=-1)
    img_np[in_range] = (0, 0, 0, 0)

    output_img = Image.fromarray(img_np)
    output_img.save(os.path.join(output_dirpath, "texgen_2.png"))


# NOTE: Files are processed in place
def clean_model(
    input_base_dir: str,
    output_base_dir: str,
    names: list[str],
    new_size: int = None,
):
    print("PROCESSING")
    for i, name in enumerate(names):
        print(i, name)
        input_dirpath = os.path.join(input_base_dir, name)
        output_dirpath = os.path.join(output_base_dir, name)
        os.makedirs(output_dirpath, exist_ok=True)

        lower_bound = [0, 0, 0]
        upper_bound = [360, 50, 50]
        filter_texture(input_dirpath, output_dirpath, lower_bound, upper_bound)

        if new_size:
            resize_image(input_dirpath, output_dirpath, name)


if __name__ == "__main__":
    # TODO: Definitely time for a new approach to stage dirs
    clean_model(DECIMATED_BASE, RETEXTURED_BASE, NAMES, 1024)
