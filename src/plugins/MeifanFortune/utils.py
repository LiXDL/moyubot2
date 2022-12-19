import textwrap

from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from pathlib import Path
import random
try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .config import fortune_config

def get_copywriting() -> tuple[str, str]:
    '''
        Read the copywriting.json, choice a luck with a random content
    '''
    _p: Path = fortune_config.fortune_path / "fortune" / "copywriting.json"

    with open(_p, "r", encoding="utf-8") as f:
        content = json.load(f).get("copywriting")
        
    luck = random.choice(content)
    
    title: str = luck.get("good-luck")
    text: str = random.choice(luck.get("content"))

    return title, text

def randomBasemap(theme: str, spec_path: Optional[str] = None) -> Path:
    if isinstance(spec_path, str):
        p: Path = fortune_config.fortune_path / "img" / spec_path
        return p

    if theme == "random":
        __p: Path = fortune_config.fortune_path / "img"
        
        # Each dir is a theme, remember add _flag after the names of themes
        themes: list[str] = [f.name for f in __p.iterdir() if f.is_dir() and themes_flag_check(f.name)]
        picked: str = random.choice(themes)

        _p: Path = __p / picked
        
        # Each file is a posix path of images directory
        images_dir: list[Path] = [i for i in _p.iterdir() if i.is_file()]
        p: Path = random.choice(images_dir)
    else:
        _p: Path = fortune_config.fortune_path / "img" / theme
        images_dir: list[Path] = [i for i in _p.iterdir() if i.is_file()]
        p: Path = random.choice(images_dir)
    
    return p

def drawing(gid: str, uid: str, theme: str, spec_path: Optional[str] = None) -> Path:
    # 1. Random choice a base image
    imgPath: Path = randomBasemap(theme, spec_path)
    img: Image.Image = Image.open(imgPath)
    draw = ImageDraw.Draw(img)
    
    # 2. Random choice a luck text with title
    title, text = get_copywriting()
    
    # 3. Draw
    fontPath = {
        "title": f"{fortune_config.fortune_path}/font/Mamelon.otf",
        "text": f"{fortune_config.fortune_path}/font/FZYHK.TTF",
    }

    #   Title
    draw.text(
        xy=(175, 800),
        text=title,
        fill="#F5F5F5",
        anchor="mm",
        direction="ttb",
        font=ImageFont.truetype(fontPath["title"], 60)
    )
    #   Texts
    draw.text(
        xy=(625, 800),
        text=textwrap.fill(text, width=10),
        fill="#323232",
        anchor="mm",
        direction="ltr",
        spacing=20,
        stroke_width=3,
        stroke_fill="#F5F5F5",
        font=ImageFont.truetype(fontPath["text"], 40)
    )
    
    # Save
    outPath: Path = exportFilePath(imgPath, gid, uid)
    img.save(outPath)
    return outPath

def exportFilePath(originalFilePath: Path, gid: str, uid: str) -> Path:
    dirPath: Path = fortune_config.fortune_path / "out"
    if not dirPath.exists():
        dirPath.mkdir(exist_ok=True, parents=True)

    outPath: Path = originalFilePath.parent.parent.parent / "out" / f"{gid}_{uid}.png" 
    return outPath


def themes_flag_check(theme: str) -> bool:
    '''
        Read the config json, return the status of a theme
    '''
    flags_config_path: Path = fortune_config.fortune_path / "fortune_config.json"
    
    with flags_config_path.open("r", encoding="utf-8") as f:
        data: dict[str, bool] = json.load(f)
    
        return data.get((theme + "_flag"), False)