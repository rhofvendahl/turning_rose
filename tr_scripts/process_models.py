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


# TODO: Combine this with editing mtl img path, editing mtl to be jpg, creating jpg, deleting png, reducing tex size
def reduce_tex_size(filepath: str, new_size: int = None):
    pass


# TODO: Explore jpg compression
def process_image(dirpath: str, name: str, new_size: int = None):
    img = Image.open(os.path.join(dirpath, "texgen_2.png"))
    img = img.convert("RGB")
    if new_size:
        img = img.resize((new_size, new_size))
    img.save(os.path.join(dirpath, "texgen_2.jpg"), "JPEG")

    mtl_filepath = os.path.join(dirpath, f"{name}.mtl")
    with open(mtl_filepath, "r") as f:
        lines = f.readlines()

    with open(mtl_filepath, "w") as f:
        for line in lines:
            if line.startswith("map_"):
                line = line.replace(".png", ".jpg")
            if "/" in line:
                # Replace absolute path with relative, and .png with .jpg
                parts = line.split("/")
                line = parts[0] + parts[-1]
            f.write(line)


# Decimate leaves a few lines between verticies, which apparently mess up obj files for some purposes. It's likely possible
# to not create those lines, but easier IMO to just edit the obj.
# NOTE: This modifies in place, after rest of pipeliene, so it doesn't overwrite it by copying over again
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


def run_pipeline(input_base, output_base, names, decimate_ratio=None, new_size=None):
    for name in names:
        input_dir = os.path.join(input_base, name)
        output_dir = os.path.join(output_base, name)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        decimate_obj(input_dir, output_dir, name, decimate_ratio)
        remove_lines_smoothing_normals_watermark(output_dir, name)  # Modifies in place
        process_image(output_dir, name, new_size)


# TODO: Refactor below (DRY it up)
def main():
    input_base = os.path.abspath("../data/models/obj/reduced")  # Has blender 3.5.1
    # output_base = os.path.abspath("../data/models/obj/reduced_decp2_256")
    # run_pipeline(input_base, output_base, MODEL_NAMES[:-1], 0.2, 256)

    # output_base = os.path.abspath("../data/models/obj/reduced_decp5_512")
    # run_pipeline(input_base, output_base, MODEL_NAMES[-1:], 0.5, 512)

    # empty processing = blender 3.5.1 (copied from "/reduced")
    output_base = os.path.abspath("../data/models/obj/reduced_processed")
    run_pipeline(input_base, output_base, MODEL_NAMES[-2:], 0.5, 1600)


if __name__ == "__main__":
    main()
