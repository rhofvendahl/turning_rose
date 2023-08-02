import os
import shutil

import pandas as pd

from constants import (
    RAW_OUTPUTS_DIRPATH,
    IMAGE_DATA_FILEPATH,
    TEMP_OUTPUTS_DIRPATH,
    START_AT,
    BLACKLIST,
)


def get_names(
    dirpath: str = RAW_OUTPUTS_DIRPATH,
    include_darker=True,
    include_blacklist=False,
    ignore_start_at=False,
):
    names: list[str] = []
    for _, dirs, _ in os.walk(dirpath):
        for d in dirs:
            # Model names should be along the lines of '0_2023-07-31_19'
            # UPDATE: They can now be '0_2023-07-20_13_darker' as well, hence this kludge...
            if len(d.split("_")) >= 3:
                names.append(d)

    if not ignore_start_at and START_AT is not None:
        start_index = names.index(START_AT)
        names = names[start_index:]

    if not include_darker:
        print("Excluding darker capture")
        names = [name for name in names if "darker" not in name]

    if not include_blacklist and BLACKLIST is not None:
        names = [name for name in names if name not in BLACKLIST]

    return names


def get_all_names():
    images_df = pd.read_csv(IMAGE_DATA_FILEPATH)
    return images_df["capture_name"].unique().tolist()


def get_image_filepaths(capture_name: str):
    images_df = pd.read_csv(IMAGE_DATA_FILEPATH)
    matches = images_df.loc[images_df["capture_name"] == capture_name]
    return matches["filepath"].tolist()


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

    source_filepaths = get_image_filepaths(capture_name)
    for source_filepath in source_filepaths:
        filename = source_filepath.split("/")[-1]
        dest_filepath = os.path.join(TEMP_OUTPUTS_DIRPATH, filename)

        if os.path.exists(source_filepath):
            shutil.copy2(source_filepath, dest_filepath)
        else:
            print("MISSING IMAGE", filename)
