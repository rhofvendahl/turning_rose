RAW_IMAGES_DIRPATH = (
    "/Volumes/T7/turning_rose/raw_images/2023_06_15_evening_to_2023_07_20_noon"
)
RAW_IMAGES_DARKER_DIRPATH = "/Volumes/T7/turning_rose/raw_images/2023-07-20_13_darker"
RAW_OUTPUTS_DIRPATH = "/Volumes/T7/turning_rose/outputs/raw"
INTERMEDIATE_OUTPUTS_DIRPATH = "/Volumes/T7/turning_rose/outputs/intermediate"
COMPLETE_OUTPUTS_DIRPATH = "/Volumes/T7/turning_rose/outputs/complete"
METADATA_OUTPUTS_DIRPATH = "/Volumes/T7/turning_rose/outputs/metadata"
# Also hardcoded in utils.py, to be absolutely sure the wrong dir doesn't get wiped
TEMP_OUTPUTS_DIRPATH = "/Volumes/T7/turning_rose/outputs/temp"
IMAGE_DATA_FILEPATH = "/Volumes/T7/turning_rose/outputs/metadata/image_data.csv"

# Useful for webapp
WEBAPP_GLTF_DIRPATH = "../tr-web/public/db/gltf"
WEBAPP_INDEX_FILEPATH = "../tr-web/public/db/json/modelNames.json"


# NOTE: Capture indices start at 0 and go to 132 (including final darker), for a total of 133 frames
# So, starting at capture 57 (with no subsequent blacklisted) makes for 76 frames
# (there's a big jump between 56/57 where the rose was damaged and trimmed, and 56 was a bad capture anyway)
START_AT: str = "57_2023-07-01_13"
BLACKLIST = [
    # This capture only included 80 frames and is pretty messed up
    "56_2023-07-01_13",
]

OBJ_FILENAME = "baked_mesh.obj"
MTL_FILENAME = "baked_mesh.mtl"
TEXTURE_FILENAME = "baked_mesh_tex0.png"

# Recommended order (after get_image_data and compile_from_images):
# python prepare_assets.py
# python align_models.py
# python process_models.py
# python process_textures.py
# python export_gltf.py

# All together: python prepare_assets.py && python align_models.py && python process_models.py && python process_textures.py && python export_gltf.py
