RAW_IMAGES_DIRPATH = (
    "/Volumes/T7/turning_rose/raw_images/2023_06_15_evening_to_2023_07_20_noon"
)
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


# The number of captures to work with. Useful for dev purposes, set to None to use all names
# NOTE: util.get_captue_names() selects the n latest.
NAMES_CAP: int = 20
