from pydantic import BaseModel, Extra
from pathlib import Path
from enum import Enum
from collections import OrderedDict


ELEMENT: list[str] = ["", "花", "风", "雪", "月", "宙", "云", "梦", "日", "星"]
ATTACK_TYPE: list[str] = ["", "通常", "特殊"]
ATTRIBUTES: OrderedDict[str, str] = OrderedDict([("total", "综合力"), ("atk", "ACT Power"), ("hp", "HP"), ("agi", "速度"), ("mdef", "特防"), ("pdef", "物防")])
ROLE: dict[str, str] = {"front": "前排", "middle": "中排", "back": "后排"}


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


class LOCALE(str, Enum):
    JP = "ja"
    CN = "zh_hant"
    EN = "en"
    KR = "ko"


class Config(BaseModel, extra=Extra.ignore):
    resource_path: Path = Path(__file__).parent / "resource"
    json_storage: Path = resource_path / "json"
    image_storage: Path = resource_path / "image"

    dress_image: Path = image_storage / "dress"
    dress_json: Path = json_storage / "dress"

    other_image: Path = image_storage / "other"

    card_alias = resource_path / "alias.json"

    api_source: str = "https://karth.top/api"
    api_dress: str = api_source + "/dress"
    api_image: str = "https://cdn.karth.top/api/assets/dlc/res/dress/cg"