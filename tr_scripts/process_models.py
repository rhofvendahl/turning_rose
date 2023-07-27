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


# NOTE: Apparently this does something needed by align even without decimate_ratio. I'm letting decimate
# be optional for now, but some renaming/restructuring is in order, if there's gonna be a plain processing step.
def decimate_obj(
    input_dir: str, output_dir: str, name: str, decimate_ratio: float = None
):
    # Load object
    bpy.ops.import_scene.obj(filepath=os.path.join(input_dir, f"{name}.obj"))
    obj = bpy.context.selected_objects[0]

    if decimate_ratio != None:
        # Apply decimate modifier
        modifier: bpy.types.DecimateModifier = obj.modifiers.new("decimate", "DECIMATE")
        modifier.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    # Export object
    bpy.ops.export_scene.obj(
        filepath=os.path.join(output_dir, f"{name}.obj"), use_selection=True
    )

    # Export diffuse texture (NOTE: Pretty sure this'll have to change with full pipeline, but idk how)
    for node in obj.active_material.node_tree.nodes:
        if node.type == "TEX_IMAGE":
            tex_node: bpy.types.ShaderNodeTexImage = node
            tex_filepath = tex_node.image.filepath
            if os.path.isfile(tex_filepath):
                # tex_filename = os.path.basename(tex_filepath)
                shutil.copy(
                    tex_filepath,
                    output_dir,
                )

    # Replace absolute path with relative (not ideal but I expect a lot will change when I implement the full pipeline)
    mtl_filepath = os.path.join(output_dir, f"{name}.mtl")
    with open(mtl_filepath, "r") as file:
        content = file.read()
    content = content.replace(input_dir + "/", "")
    with open(mtl_filepath, "w") as file:
        file.write(content)


def reduce_tex_size(filepath: str, new_size: int = None):
    pass


# I'm not entirely sure this is necessary, but a lot of this stuff can't handle alpha channel so can't hurt
def create_jpg(dirpath: str):
    img = Image.open(os.path.join(dirpath, "texgen_2.png"))
    rgb_img = img.convert("RGB")
    rgb_img.save(os.path.join(dirpath, "texgen_2.jpg"), "JPEG")


# Decimate leaves a few lines between verticies, which apparently mess up obj files for some purposes. It's likely possible
# to not create those lines, but easier IMO to just edit the obj.
# NOTE: This should eventually happen before reduce_filesize.py, after photogrammetry, along with conversion usdz to obj
def remove_lines_smoothing_watermark(input_dir, output_dir, name):
    with open(os.path.join(input_dir, name + ".obj"), "r") as f:
        lines = f.readlines()

    with open(os.path.join(output_dir, name + ".obj"), "w") as f:
        for line in lines:
            if line.startswith("o watermark"):
                break
            is_line = line.startswith("l ")
            # NOTE: I'm removing smoothing because it causes problems in some places, but might be something I want elsewhere
            # So, keep in mind
            is_smoothing = line.startswith("s ")
            if not is_line and not is_smoothing:
                f.write(line)


def run_pipeline(input_base, output_base, names, decimate_ratio=None, new_size=None):
    for name in names:
        input_dir = os.path.join(input_base, name)
        output_dir = os.path.join(output_base, name)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        decimate_obj(input_dir, output_dir, name, decimate_ratio)
        remove_lines_smoothing_watermark(input_dir, output_dir, name)
        reduce_tex_size(os.path.join(output_dir, "texgen_2.png"), new_size)
        create_jpg(output_dir)


# TODO: Refactor below (DRY it up)
def main():
    input_base = os.path.abspath("../data/models/obj/reduced")
    # output_base = os.path.abspath("../data/models/obj/reduced_decp2_256")
    # run_pipeline(input_base, output_base, MODEL_NAMES[:-1], 0.2, 256)

    # output_base = os.path.abspath("../data/models/obj/reduced_decp5_512")
    # run_pipeline(input_base, output_base, MODEL_NAMES[-1:], 0.5, 512)

    output_base = os.path.abspath("../data/models/obj/reduced_same")
    run_pipeline(input_base, output_base, MODEL_NAMES[-2:])


if __name__ == "__main__":
    main()
