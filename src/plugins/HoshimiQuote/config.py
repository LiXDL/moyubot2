from pydantic import BaseModel, Extra
from pathlib import Path


class Config(BaseModel, extra=Extra.ignore):
    resource_path: Path = Path(__file__).resolve().parent / "resource"
    base_image: Path = resource_path / "hoshimi_frame.png"
    output_path: Path = resource_path / "out"