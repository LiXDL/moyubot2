import textwrap

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def drawing(text: dict, outname: str):
    resource_dir = Path(__file__).resolve().parent / "resource"
    out_path = resource_dir / "out"
    font = resource_dir / "FZYHK.TTF"
    img: Image.Image = Image.open(resource_dir / "hoshimi_frame.png")
    draw = ImageDraw.Draw(img)

    quote, by = text["quote"], text["by"]
    multiline_quote = textwrap.fill(quote, width=14)

    rx1, ry1, rx2, ry2 = draw.multiline_textbbox(
        xy=(270, 220),
        text=multiline_quote,
        anchor="mm",
        direction="ltr",
        spacing=12,
        font=ImageFont.truetype(str(font), 28)
    )

    #   Draw quote
    #   Center is moved upward by 1/4 of the textbox height
    draw.text(
        xy=(270, 220 - int((ry2 - ry1) / 4)),
        text=multiline_quote,
        fill="#323232",
        anchor="mm",
        direction="ltr",
        spacing=12,
        stroke_width=3,
        stroke_fill="#F5F5F5",
        font=ImageFont.truetype(str(font), 28)
    )
    #   Draw person
    draw.text(
        xy=(420, ry2 + 48),
        text=by + "  ———",
        fill="#323232",
        anchor="rm",
        direction="rtl",
        spacing=12,
        stroke_width=3,
        stroke_fill="#F5F5F5",
        font=ImageFont.truetype(str(font), 24)
    )

    img.save(out_path / outname)
    return out_path / outname
