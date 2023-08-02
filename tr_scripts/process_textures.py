import os

from PIL import Image
import numpy as np

from constants import INTERMEDIATE_OUTPUTS_DIRPATH, TEXTURE_FILENAME
from utils import get_names


def resize_image(
    source_dirpath: str,
    dest_dirpath: str,
    image_name: str,
    new_size: int = None,
):
    img = Image.open(os.path.join(source_dirpath, image_name))
    img = img.resize((new_size, new_size))
    img.save(os.path.join(dest_dirpath, image_name), "PNG")


def scale_hsv(hsv):
    h_new = int((hsv[0] / 360.0) * 255)
    s_new = int((hsv[1] / 100.0) * 255)
    v_new = int((hsv[2] / 100.0) * 255)

    return [h_new, s_new, v_new]


def filter_texture(input_dirpath, output_dirpath, lower_bound, upper_bound):
    lower_bound = scale_hsv(lower_bound)
    upper_bound = scale_hsv(upper_bound)

    img = Image.open(os.path.join(input_dirpath, TEXTURE_FILENAME)).convert("RGBA")
    img_np = np.array(img)

    # Convert to hsv
    img_hsv = np.array(img.convert("HSV"))

    # Find pixels in range and set alpha channel to 0 (transparent)
    in_range = np.all((img_hsv >= lower_bound) & (img_hsv <= upper_bound), axis=-1)
    img_np[in_range] = (0, 0, 0, 0)

    output_img = Image.fromarray(img_np)
    output_img.save(os.path.join(output_dirpath, TEXTURE_FILENAME))


def process_textures(
    names: list[str] = None,
    new_size: int = None,
    source_base_dir: str = INTERMEDIATE_OUTPUTS_DIRPATH,
    dest_base_dir: str = INTERMEDIATE_OUTPUTS_DIRPATH,
):
    if names == None:
        names = get_names()

    print("PROCESSING TEXTURES")
    for i, name in enumerate(names):
        print(i, name)
        source_dirpath = os.path.join(source_base_dir, name)
        dest_dirpath = os.path.join(dest_base_dir, name)
        os.makedirs(dest_dirpath, exist_ok=True)

        # Filtering texure takes a while, and takes a lot longer for higher resolutions.
        # Lowering resolution first would make this step go faster, but I suspect that filtering out
        # pixels in a 256x256 image would result in a "choppier" look than filtering at 2048x2048
        # and resizing, as (haven't rly checked but) I suspect this averages "transparent" and "not transparent"
        # pixels to make a semitransparent value that I believe is desirable in a texture.
        # As a compromise, since resizing is a fast operation we are first resizing down to 1024
        # (unless new size is higher) once, then again after filtering.
        if new_size and new_size < 1024:
            resize_image(source_dirpath, dest_dirpath, TEXTURE_FILENAME, 1024)

        lower_bound = [180, 0, 0]
        upper_bound = [290, 30, 55]
        filter_texture(source_dirpath, dest_dirpath, lower_bound, upper_bound)

        if new_size:
            resize_image(source_dirpath, dest_dirpath, TEXTURE_FILENAME, new_size)


if __name__ == "__main__":
    names = get_names()
    process_textures(names[:-1], 256)
    process_textures(names[-1:], 1024)
