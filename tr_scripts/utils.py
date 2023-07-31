import os
import shutil

from constants import NAMES


# Returns whether hue is within bounds
def check_hue(hue, target, tolerance):
    # NOTE: I don't like this, TODO: change it later
    if target is None:
        return True

    # Hue wraps around, i.e. 0 and 360 are the same shade of red
    bound_1 = (target - tolerance) % 1.0
    bound_2 = (target + tolerance) % 1.0
    # This makes it a bit tricky to tell whether a hue is within these bounds, as one bound may have wrapped around
    if bound_1 <= bound_2:
        within_bounds = bound_1 <= hue <= bound_2
    else:
        within_bounds = hue >= bound_1 or hue <= bound_2
    if within_bounds:
        print("WITHIN BOUNDS")
    return within_bounds


def copy_assets(
    input_base,
    output_base,
    names=None,
    include_obj=False,
    include_img=False,
    use_jpg=False,
):
    if names == None:
        names = NAMES
    img_ext = ".jpg" if use_jpg else ".png"

    for name in names:
        input_dirpath = os.path.join(input_base, name)
        output_dirpath = os.path.join(output_base, name)
        os.makedirs(output_dirpath, exist_ok=True)

        shutil.copy(os.path.join(input_dirpath, name + ".mtl"), output_dirpath)

        if include_img:
            shutil.copy(
                os.path.join(input_dirpath, "texgen_2" + img_ext), output_dirpath
            )
        if include_obj:
            shutil.copy(os.path.join(input_dirpath, name + ".obj"), output_dirpath)
