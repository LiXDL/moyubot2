from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

import asyncio
import aiofiles
import nonebot

app: FastAPI = nonebot.get_app()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
log_path = Path.cwd().resolve() / "logs"
log_file = "info.log"


async def log_reader(n: int = 5) -> list[str]:
    async with aiofiles.open(log_path / log_file) as af:
        lines = await af.readlines()
        return lines[-n:]


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(str(Path(__file__).resolve().parent / "favicon.ico"))


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
        print(e)
    finally:
        await ws.close()