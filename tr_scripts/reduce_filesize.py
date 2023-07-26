import bpy
import os
import shutil

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


def reduce_tex_size(filepath: str, new_size: int):
    pass


# TODO: Refactor below (DRY it up)
def main():
    input_base = os.path.abspath("../data/models/obj/reduced")
    output_base = os.path.abspath("../data/models/obj/reduced_decp2_256")
    for name in MODEL_NAMES[:-1]:
        input_dir = os.path.join(input_base, name)
        output_dir = os.path.join(output_base, name)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        decimate_obj(input_dir, output_dir, name, 0.2)

        reduce_tex_size(os.path.join(output_dir, "texgen_2.png"), 256)

    output_base = os.path.abspath("../data/models/obj/reduced_decp5_512")
    for name in MODEL_NAMES[-1:]:
        input_dir = os.path.join(input_base, name)
        output_dir = os.path.join(output_base, name)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        decimate_obj(input_dir, output_dir, name, 0.5)

        reduce_tex_size(os.path.join(output_dir, "texgen_2.png"), 512)

    output_base = os.path.abspath("../data/models/obj/reduced_same")
    for name in MODEL_NAMES[-1:]:
        input_dir = os.path.join(input_base, name)
        output_dir = os.path.join(output_base, name)
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        decimate_obj(input_dir, output_dir, name)

        reduce_tex_size(os.path.join(output_dir, "texgen_2.png"), 512)


if __name__ == "__main__":
    main()
