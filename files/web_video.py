import os
import sys

IS_WEB = sys.platform == "emscripten"

if not IS_WEB:
    try:
        from ffpyplayer.player import MediaPlayer as _FFPlayer
    except Exception:
        _FFPlayer = None
else:
    _FFPlayer = None

_player = None
_last_frame = None
_loop = False
_eof = False
_video_dom = None


def _make_surface(frame):
    try:
        import pygame
        img, pts = frame
        data = img.to_bytearray()[0]
        w, h = img.get_size()
        return pygame.image.frombuffer(data, (w, h), "RGB")
    except Exception:
        return None


def open_video(path, loop=True):
    global _player, _last_frame, _loop, _eof, _video_dom
    close_video()
    _loop = loop
    _eof = False
    _last_frame = None
    if not IS_WEB:
        if _FFPlayer is None:
            return
        try:
            _player = _FFPlayer(path)
            for _ in range(15):
                frame, val = _player.get_frame()
                if frame:
                    _last_frame = _make_surface(frame)
                    break
                time_sleep(0.015)
        except Exception:
            _player = None
        return
    try:
        import platform
        window = getattr(platform, "window", None)
        if window is None:
            return
        vid = window.document.createElement("video")
        vid.src = path.replace("\\", "/")
        vid.setAttribute("preload", "auto")
        vid.setAttribute("muted", "muted")
        vid.setAttribute("playsinline", "true")
        vid.style.position = "absolute"
        vid.style.left = "0px"
        vid.style.top = "0px"
        vid.style.width = "0px"
        vid.style.height = "0px"
        vid.style.opacity = "0"
        vid.style.pointerEvents = "none"
        if _loop:
            vid.loop = True
        vid.autoplay = True
        window.document.body.appendChild(vid)
        def on_ended(evt):
            global _eof
            _eof = True
        try:
            vid.addEventListener("ended", on_ended)
        except Exception:
            pass
        try:
            vid.play()
        except Exception:
            pass
        _video_dom = vid
    except Exception:
        _video_dom = None


def is_eof():
    global _eof
    if IS_WEB and _video_dom is not None:
        try:
            if getattr(_video_dom, "ended", False):
                _eof = True
        except Exception:
            pass
    return _eof


def get_frame(w, h):
    global _last_frame, _eof
    if not IS_WEB:
        if _player is None:
            return None
        if _eof and not _loop:
            return _last_frame
        try:
            frame, val = _player.get_frame()
        except Exception:
            frame, val = None, None
        if val == "eof":
            _eof = True
            if _loop:
                try:
                    _player.seek(0, relative=False)
                    _eof = False
                    frame, val = _player.get_frame()
                except Exception:
                    frame, val = None, None
            else:
                return _last_frame
        if frame is None:
            return _last_frame
        surf = _make_surface(frame)
        if surf is None:
            return _last_frame
        try:
            if surf.get_size() != (w, h):
                surf = pygame.transform.scale(surf, (w, h))
        except Exception:
            pass
        _last_frame = surf
        return surf
    return None


def close_video():
    global _player, _last_frame, _eof, _video_dom
    if not IS_WEB:
        if _player is not None:
            try:
                _player.close_player()
            except Exception:
                pass
        _player = None
    else:
        if _video_dom is not None:
            try:
                vid = _video_dom
                try:
                    vid.pause()
                except Exception:
                    pass
                try:
                    vid.src = ""
                except Exception:
                    pass
                par = vid.parentNode
                if par is not None:
                    par.removeChild(vid)
            except Exception:
                pass
        _video_dom = None
    _last_frame = None
    _eof = False


def time_sleep(v):
    try:
        import time
        time.sleep(v)
    except Exception:
        pass


try:
    import pygame
except Exception:
    pygame = None
