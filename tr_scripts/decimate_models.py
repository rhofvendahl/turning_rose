import bpy
import os

from constants import ALIGNED_BASE, DECIMATED_BASE, NAMES

# from utils import copy_assets


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


def decimate_models(
    input_base: str,
    output_base: str,
    names: list[str],
    decimate_ratio: float,
):
    print("DECIMATING")
    for i, name in enumerate(names):
        print(i, name)
        input_dirpath = os.path.join(input_base, name)
        output_dirpath = os.path.join(output_base, name)
        os.makedirs(output_dirpath, exist_ok=True)

        decimate_obj(input_dirpath, output_dirpath, name, decimate_ratio)
    print()


if __name__ == "__main__":
    decimate_models(ALIGNED_BASE, DECIMATED_BASE, NAMES, 0.5)
    # copy_assets(ALIGNED_BASE, DECIMATED_BASE, NAMES)
