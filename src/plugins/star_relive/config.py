from pydantic import BaseModel, Extra
from pathlib import Path
from typing import Union


DownloadCofig: dict[str, list[int]] = {
    "school": list(range(1, 5+1)),
    "max_character": list(range(1, 10+1)),
    "limit": list(range(1, 50+1)),
    "special_event": [
        9010001, 
        9020001, 
        9030001
    ]
}


class Config(BaseModel, extra=Extra.ignore):
    resource_path: Path = Path(__file__).parent / "resource"
    json_storage: Path = resource_path / "json"
    image_storage: Path = resource_path / "image"
    dress_image: Path = image_storage / "dress"

    api_source: str = "https://karth.top/api"
    api_dress: str = api_source + "/dress"
    api_image: str = "https://cdn.karth.top/api/assets/dlc/res/dress/cg"