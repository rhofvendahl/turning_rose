import os
import math

from PIL import Image
import numpy as np
import bpy
import bmesh

from constants import NAMES, DECIMATED_BASE, CLEANED_BASE


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
    h_new = int((hsv[0] / 360.0) * 255)
    s_new = int((hsv[1] / 100.0) * 255)
    v_new = int((hsv[2] / 100.0) * 255)

    return [h_new, s_new, v_new]


def filter_texture(input_dirpath, output_dirpath, lower_bound, upper_bound):
    lower_bound = scale_hsv(lower_bound)
    upper_bound = scale_hsv(upper_bound)

    img = Image.open(os.path.join(input_dirpath, "texgen_2.png")).convert("RGBA")
    img_np = np.array(img)

    # Convert to hsv
    img_hsv = np.array(img.convert("HSV"))

    # Find pixels in range and set alpha channel to 0 (transparent)
    in_range = np.all((img_hsv >= lower_bound) & (img_hsv <= upper_bound), axis=-1)
    img_np[in_range] = (0, 0, 0, 0)

    output_img = Image.fromarray(img_np)
    output_img.save(os.path.join(output_dirpath, "texgen_2.png"))


def remove_outer_points(input_dirpath, output_dirpath, name, radius):
    bpy.ops.import_scene.obj(filepath=os.path.join(input_dirpath, name + ".obj"))

    obj = bpy.context.selected_objects[0]

    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(obj.data)

    verts_to_remove = [
        v for v in bm.verts if math.sqrt(v.co.x**2 + v.co.z**2) > radius
    ]

    bmesh.ops.delete(bm, geom=verts_to_remove, context="VERTS")
    bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.export_scene.obj(
        filepath=os.path.join(output_dirpath, name + ".obj"), use_selection=True
    )


def clean_model(
    input_base_dir: str,
    output_base_dir: str,
    names: list[str],
    new_size: int = None,
):
    print("CLEANING")
    for i, name in enumerate(names):
        print(i, name)
        input_dirpath = os.path.join(input_base_dir, name)
        output_dirpath = os.path.join(output_base_dir, name)
        os.makedirs(output_dirpath, exist_ok=True)

        lower_bound = [180, 0, 0]
        upper_bound = [290, 30, 55]
        filter_texture(input_dirpath, output_dirpath, lower_bound, upper_bound)

        if new_size:
            resize_image(input_dirpath, output_dirpath, name, new_size)

        remove_outer_points(input_dirpath, output_dirpath, name, 0.5)


if __name__ == "__main__":
    # TODO: Definitely time for a new approach to stage dirs
    clean_model(DECIMATED_BASE, CLEANED_BASE, NAMES[:-1], 256)
    clean_model(DECIMATED_BASE, CLEANED_BASE, NAMES[-1:], 1024)
