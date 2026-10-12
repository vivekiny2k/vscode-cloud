import asyncio
import re
from pathlib import Path

from aiohttp import web

WEB_DIRECTORY = "."
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_INDEX = Path(__file__).resolve().parent / "index.html"
_SAFE_NAME = re.compile(r"^[\w.\-]+$")
_SAFE_SUB = re.compile(r"^[\w.\-/]*$")
_MAX_CLIPS = 16


def _output_dir():
    import folder_paths

    return Path(folder_paths.get_output_directory()).resolve()


def _resolve_output(clip, output_dir):
    name = str(clip.get("filename") or "")
    sub = str(clip.get("subfolder") or "").replace("\\", "/").strip("/")
    typ = str(clip.get("type") or "output")
    if typ != "output" or not _SAFE_NAME.match(name) or ".." in name:
        raise ValueError("invalid clip")
    if sub and (not _SAFE_SUB.match(sub) or ".." in sub):
        raise ValueError("invalid clip")
    path = (output_dir / sub / name if sub else output_dir / name).resolve()
    if output_dir not in path.parents and path != output_dir:
        raise ValueError("invalid clip")
    if not path.is_file():
        raise FileNotFoundError(name)
    return path


def _next_mp4(dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        dest = dest_dir / f"i2v_{n:05d}_.mp4"
        if not dest.exists():
            return dest
        n += 1


try:
    from server import PromptServer

    @PromptServer.instance.routes.get("/i2v")
    async def i2v_ui(_request):
        return web.FileResponse(_INDEX, headers={"Cache-Control": "no-store"})

    @PromptServer.instance.routes.get("/i2v/")
    async def i2v_ui_slash(_request):
        return web.FileResponse(_INDEX, headers={"Cache-Control": "no-store"})

    @PromptServer.instance.routes.post("/i2v/concat")
    async def i2v_concat(request):
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid json"}, status=400)
        clips = data.get("clips") or []
        if not isinstance(clips, list) or not clips or len(clips) > _MAX_CLIPS:
            return web.json_response({"error": "need 1–16 clips"}, status=400)
        if not all(isinstance(c, dict) for c in clips):
            return web.json_response({"error": "clips must be files"}, status=400)
        try:
            output_dir = _output_dir()
            paths = [_resolve_output(c, output_dir) for c in clips]
        except (ValueError, FileNotFoundError) as exc:
            return web.json_response({"error": str(exc)}, status=400)

        dest = _next_mp4(output_dir / "video")
        if len(paths) == 1:
            proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-y",
                "-i",
                str(paths[0]),
                "-an",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-r",
                "16",
                "-movflags",
                "+faststart",
                str(dest),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        else:
            args = ["ffmpeg", "-y"]
            filters = []
            labels = []
            for i, path in enumerate(paths):
                args.extend(["-i", str(path)])
                if i == 0:
                    filters.append(f"[{i}:v]fps=16,setsar=1,format=yuv420p[v{i}]")
                else:
                    filters.append(
                        f"[{i}:v]trim=start_frame=1,setpts=PTS-STARTPTS,fps=16,setsar=1,format=yuv420p[v{i}]"
                    )
                labels.append(f"[v{i}]")
            filters.append("".join(labels) + f"concat=n={len(paths)}:v=1:a=0:unsafe=1[outv]")
            args.extend(
                [
                    "-filter_complex",
                    ";".join(filters),
                    "-map",
                    "[outv]",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-r",
                    "16",
                    "-movflags",
                    "+faststart",
                    str(dest),
                ]
            )
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        _out, err = await proc.communicate()
        if proc.returncode != 0 or not dest.is_file():
            return web.json_response(
                {"error": (err or b"").decode("utf-8", "replace")[-1500:] or "ffmpeg failed"},
                status=500,
            )
        return web.json_response(
            {"filename": dest.name, "subfolder": "video", "type": "output"}
        )
except Exception:
    pass
