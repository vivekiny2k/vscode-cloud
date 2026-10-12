import base64
import hashlib
import hmac
import json
from pathlib import Path

from aiohttp import web

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

_DIR = Path(__file__).resolve().parent
_LOGIN = _DIR / "login.html"
_CREDS_PATH = _DIR / "credentials.json"
_COOKIE = "comfy_session"
_OPEN_PATHS = {"/login", "/logout"}


def _load_creds():
    data = json.loads(_CREDS_PATH.read_text(encoding="utf-8"))
    user = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not user or not password:
        raise RuntimeError("comfyui-auth: credentials.json is missing username or password")
    return user, password


def _same(left, right):
    return hmac.compare_digest(
        hashlib.sha256(str(left).encode("utf-8")).digest(),
        hashlib.sha256(str(right).encode("utf-8")).digest(),
    )


def _token(user, password):
    digest = hmac.new(password.encode("utf-8"), user.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{user}:{digest}"


def _valid_token(value, user, password):
    expected = _token(user, password)
    return isinstance(value, str) and hmac.compare_digest(value, expected)


def _valid_basic(header, user, password):
    if not header or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode("utf-8")
        got_user, got_pass = decoded.split(":", 1)
    except Exception:
        return False
    return _same(got_user, user) and _same(got_pass, password)


def _authorized(request, user, password):
    if _valid_token(request.cookies.get(_COOKIE), user, password):
        return True
    return _valid_basic(request.headers.get("Authorization", ""), user, password)


def _secure_cookie(request):
    proto = request.headers.get("X-Forwarded-Proto", request.scheme)
    return proto == "https"


def _install():
    user, password = _load_creds()

    from server import PromptServer

    app = PromptServer.instance.app
    if getattr(app, "_comfyui_basic_auth", False):
        return

    @web.middleware
    async def require_login(request, handler):
        if request.method == "OPTIONS" or request.path in _OPEN_PATHS:
            return await handler(request)
        if _authorized(request, user, password):
            return await handler(request)
        accept = request.headers.get("Accept", "")
        if request.method == "GET" and "text/html" in accept:
            raise web.HTTPFound("/login")
        return web.Response(
            status=401,
            text="Unauthorized",
            headers={"WWW-Authenticate": 'Basic realm="ComfyUI"'},
        )

    async def login_page(_request):
        return web.FileResponse(_LOGIN, headers={"Cache-Control": "no-store"})

    async def login_submit(request):
        form = await request.post()
        got_user = (form.get("username") or "").strip()
        got_pass = form.get("password") or ""
        if _same(got_user, user) and _same(got_pass, password):
            response = web.HTTPFound("/")
            response.set_cookie(
                _COOKIE,
                _token(user, password),
                httponly=True,
                secure=_secure_cookie(request),
                samesite="Lax",
                path="/",
                max_age=60 * 60 * 24 * 30,
            )
            return response
        raise web.HTTPFound("/login?error=1")

    async def logout(_request):
        response = web.HTTPFound("/login")
        response.del_cookie(_COOKIE, path="/")
        return response

    app.middlewares.insert(0, require_login)
    PromptServer.instance.routes.get("/login")(login_page)
    PromptServer.instance.routes.post("/login")(login_submit)
    PromptServer.instance.routes.get("/logout")(logout)
    app._comfyui_basic_auth = True


try:
    _install()
except Exception as exc:
    print(f"[comfyui-auth] not installed: {exc}")
