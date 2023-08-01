import os
import shutil

import pandas as pd

from constants import (
    RAW_OUTPUTS_DIRPATH,
    IMAGE_DATA_FILEPATH,
    RAW_IMAGES_DIRPATH,
    TEMP_OUTPUTS_DIRPATH,
)

# TODO: Only return names of dirs that actually have content


def get_names(dirpath: str = RAW_OUTPUTS_DIRPATH):
    names = []
    for _, dirs, _ in os.walk(dirpath):
        for d in dirs:
            # Model names should be along the lines of '0_2023-07-31_19'
            if len(d.split("_")) == 3:
                names.append(d)

    return names


def get_capture_names():
    images_df = pd.read_csv(IMAGE_DATA_FILEPATH)
    return images_df["capture_name"].unique().tolist()


def get_images_from_capture(capture_name: str):
    images_df = pd.read_csv(IMAGE_DATA_FILEPATH)
    matches = images_df.loc[images_df["capture_name"] == capture_name]
    return matches["name"].tolist()


def remove_empty_names():
    names = get_names()
    for name in names:
        dirpath = os.path.join(RAW_OUTPUTS_DIRPATH, name)
        if len(os.listdir(dirpath)) == 0:
            try:
                os.rmdir(dirpath)
                print(f"Removed empty: {name}")
            except:
                print(f"Failed to remove empty: {name}")


# Yikes! Dangerous territory
def wipe_temp():
    # Hardcoding this here to make absolutely sure it doesn't get passed something weird
    temp_dirpath = "/Volumes/T7/turning_rose/outputs/temp"
    if os.path.exists(temp_dirpath):
        shutil.rmtree(temp_dirpath)
        os.makedirs(temp_dirpath)


def copy_to_temp(capture_name):
    wipe_temp()

    image_names = get_images_from_capture(capture_name)
    for image_name in image_names:
        input_filepath = os.path.join(RAW_IMAGES_DIRPATH, image_name)
        output_filepath = os.path.join(TEMP_OUTPUTS_DIRPATH, image_name)

        if os.path.exists(input_filepath):
            shutil.copy2(input_filepath, output_filepath)
        else:
            print("MISSING IMAGE", image_name)


def copy_assets(
    input_base,
    output_base,
    names=None,
    include_obj=False,
    include_img=False,
    use_jpg=False,
):
    if names == None:
        names = get_names()
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
