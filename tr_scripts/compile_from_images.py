import subprocess
import os
import time
from datetime import datetime

import pandas as pd

from constants import RAW_OUTPUTS_DIRPATH, TEMP_OUTPUTS_DIRPATH
from utils import (
    get_names,
    get_all_names,
    get_images_from_capture,
    copy_to_temp,
    remove_empty_names,
)


def compile_from_images():
    remove_empty_names()
    so_far = get_names()
    all = get_all_names()
    for capture_name in all:
        if capture_name in so_far:
            print("Skipping", capture_name)
            continue
        start = datetime.now()
        print()
        print("COMPILING", capture_name)

        copy_to_temp(capture_name)

        input_dirpath = TEMP_OUTPUTS_DIRPATH
        output_dirpath = os.path.join(RAW_OUTPUTS_DIRPATH, capture_name)
        os.makedirs(output_dirpath)

        # Values: preview, reduced, medium, full, raw
        detail = "reduced"

        cmd = f"../tr_photogrammetry/build/Build/Products/Debug/tr_photogrammetry {input_dirpath} {output_dirpath} -d {detail} -o sequential"

        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(f"ERROR: Command failed with return code {process.returncode}")
            print(f"STD ERR:\n{stderr.decode()}")
            continue

        if stdout:
            print(f"STD OUT:\n{stdout.decode()}")

        elapsed = int((datetime.now() - start).total_seconds())
        minutes, seconds = divmod(elapsed, 60)
        so_far_now = get_names()
        print(
            f"COMPILED in {minutes}mins {seconds}s. {len(so_far_now)} down, {len(all) - len(so_far_now)} to go!"
        )


if __name__ == "__main__":
    compile_from_images()
