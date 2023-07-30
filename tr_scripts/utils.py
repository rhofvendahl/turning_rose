import os
import shutil

from constants import NAMES


def copy_assets(
    input_base,
    output_base,
    names=None,
    include_obj=False,
    include_img=False,
    use_jpg=True,
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
