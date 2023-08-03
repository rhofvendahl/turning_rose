import os
import math

import bpy
import bmesh

from constants import INTERMEDIATE_OUTPUTS_DIRPATH, OBJ_FILENAME
from utils import get_names


# Presence/absence of decimate_ratio and radius indicate whether those operations should be performed
def perform_blender_operations(
    source_dirpath,
    dest_dirpath,
    filename,
    decimate_ratio=None,
    radius=None,
):
    bpy.ops.import_scene.obj(filepath=os.path.join(source_dirpath, filename))
    obj = bpy.context.selected_objects[0]

    if decimate_ratio != None:
        modifier: bpy.types.DecimateModifier = obj.modifiers.new("decimate", "DECIMATE")
        modifier.ratio = decimate_ratio
        bpy.ops.object.modifier_apply(modifier=modifier.name)

    if radius != None:
        bpy.ops.object.mode_set(mode="EDIT")

        bm = bmesh.from_edit_mesh(obj.data)
        verts_to_remove = [
            v for v in bm.verts if math.sqrt(v.co.x**2 + v.co.z**2) > radius
        ]
        bmesh.ops.delete(bm, geom=verts_to_remove, context="VERTS")
        bmesh.update_edit_mesh(obj.data)

        bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.export_scene.obj(
        filepath=os.path.join(dest_dirpath, filename), use_selection=True
    )


def process_models(
    names: list[str] = None,
    decimate_ratio: float = None,
    source_base_dirpath: str = INTERMEDIATE_OUTPUTS_DIRPATH,
    dest_base_dirpath: str = INTERMEDIATE_OUTPUTS_DIRPATH,
    decimate: bool = True,
    remove_outer: bool = True,
):
    decimate_ratio = decimate_ratio if decimate_ratio != None and decimate else None
    radius = 0.5 if remove_outer else None

    print("PROCESSING MODELS")
    for i, name in enumerate(names):
        print(i, name)
        source_dirpath = os.path.join(source_base_dirpath, name)
        dest_dirpath = os.path.join(dest_base_dirpath, name)
        os.makedirs(dest_dirpath, exist_ok=True)

        perform_blender_operations(
            source_dirpath,
            dest_dirpath,
            OBJ_FILENAME,
            decimate_ratio,
            radius,
        )
    print()


if __name__ == "__main__":
    names = get_names()
    process_models(names[:-1], 0.5)
    process_models(names[-1:], 0.5)
