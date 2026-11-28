import time
from pathlib import Path
import shutil
import coords
from click import *
from checker import *

file_b3d_path = r"C:\Users\Airat\Documents\shared_test\model\abc\bazis\Шкаф.b3d"
file_obj_path = r"C:\Users\Airat\Documents\shared_test\model\abc\blender\shkaf.obj"

def convert_b3d_to_obj(file_b3d_path: str, file_obj_path: str):
    click(coords.BAZIS_EXE)
    wait_until(coords.BAZIS_IS_OPENED_ICON_REGION, coords.BAZIS_IS_OPENED_ICON_RGB)
    print("Bazis is opened")

    wait_until(coords.BAZIS_IS_READY_REGION, coords.BAZIS_IS_READY_RGB)
    print("Bazis is ready")

    click(coords.BAZIS_OPEN_FILE)
    wait_until(coords.BAZIS_ENTER_FILE_NAME_REGION, coords.BAZIS_ENTER_FILE_NAME_RGB)

    ctrlV(file_b3d_path)
    enter()

    wait_until(coords.BAZIS_IS_MODEL_OPENED_REGION, coords.BAZIS_IS_MODEL_OPENED_RGB)
    print("Is model opened")

    # time.sleep(5)
    click(coords.BAZIS_EXPORT_FILE)
    wait_until(coords.BAZIS_EXPORT_FILE_REGION, coords.BAZIS_EXPORT_FILE_RGB)

    click(coords.BAZIS_EXPORT)
    wait_until(coords.BAZIS_EXPORT_REGION, coords.BAZIS_EXPORT_RGB)

    click(coords.BAZIS_EXPORT_3D_MODEL)

    ctrlV(file_obj_path)
    enter()
    wait_until_not(coords.BAZIS_EXPORT_REGION, coords.BAZIS_EXPORT_RGB)

    click(coords.BAZIS_CLOSE_MODEL)

# convert_b3d_to_obj(file_b3d_path, file_obj_path)

for i in range(10):
    print("__Create dir")
    Path(r"C:\Users\Airat\Documents\shared_test\model\abc\blender").mkdir(parents=True, exist_ok=True)

    print("__Run bazis")
    convert_b3d_to_obj(file_b3d_path, file_obj_path)

    print("__Remove dir")
    shutil.rmtree(r"C:\Users\Airat\Documents\shared_test\model\abc\blender")

    click(coords.BAZIS_EXE)