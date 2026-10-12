from pathlib import Path

from aiohttp import web

WEB_DIRECTORY = "."
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_INDEX = Path(__file__).resolve().parent / "index.html"

try:
    from server import PromptServer

    @PromptServer.instance.routes.get("/i2v")
    async def i2v_ui(_request):
        return web.FileResponse(_INDEX, headers={"Cache-Control": "no-store"})

    @PromptServer.instance.routes.get("/i2v/")
    async def i2v_ui_slash(_request):
        return web.FileResponse(_INDEX, headers={"Cache-Control": "no-store"})
except Exception:
    pass
