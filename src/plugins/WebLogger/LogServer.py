from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

import asyncio
import nonebot

app: FastAPI = nonebot.get_app()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
log_path = Path.cwd() / "logs"
log_file = "info.log"


async def log_reader(n: int = 10) -> list[str]:
    log_lines = []

    with open(log_path / log_file) as f:
        for line in f.readlines()[-n:]:
            line = line.strip()
            if line.__contains__("ERROR"):
                log_lines.append(f'<span class="text-red-400">{line}</span><br/>')
            elif line.__contains__("WARNING"):
                log_lines.append(f'<span class="text-orange-300">{line}</span><br/>')
            elif line.__contains__("SUCCESS"):
                log_lines.append(f'<span class="text-lime-500">{line}</span><br/>')
            else:
                log_lines.append(f'<span class="text-neutral-50">{line}</span><br/>')

    return log_lines


@app.get("/log")
async def get(request: Request):
    context = {
        "title": "Nonebot Running Log Viewer over FastAPI WebSocket"
    }
    return templates.TemplateResponse("log_view.html", {"request": request, "context": context})


@app.websocket("/ws/log")
async def websocket_endpoint_log(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            await asyncio.sleep(10)
            logs = await log_reader(100)
            await ws.send_json(logs)
    except Exception as e:
        pass
    finally:
        await ws.close()