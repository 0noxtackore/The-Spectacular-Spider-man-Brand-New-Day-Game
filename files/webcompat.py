import os
import sys
import time

IS_WEB = sys.platform == "emscripten"

if not IS_WEB:
    import threading as _threading
else:
    _threading = None


def get_clock():
    try:
        import pygame
        return pygame.time.Clock()
    except Exception:
        return None


def frame_pace(clock=None, target_fps=60):
    try:
        import pygame
        import asyncio
    except Exception:
        return 0

    if IS_WEB:
        dt_ms = int(1000 / max(1, target_fps))
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.sleep(0))
        except Exception:
            pass
        if clock is not None:
            try:
                clock.tick(target_fps)
            except Exception:
                pass
        return dt_ms

    if clock is None:
        clock = get_clock()
    if clock is not None:
        try:
            return clock.tick(target_fps)
        except Exception:
            return 16
    return 16


_font_cache = {}


def load_font(size=24, bold=False):
    try:
        import pygame
    except Exception:
        return None
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    try:
        if not IS_WEB:
            font = pygame.font.SysFont("arial", size, bold=bold)
        else:
            font = pygame.font.Font(None, size)
        _font_cache[key] = font
        return font
    except Exception:
        try:
            font = pygame.font.Font(None, size)
            _font_cache[key] = font
            return font
        except Exception:
            return None


def resolve_audio(path):
    if not path:
        return path
    if IS_WEB:
        if path.endswith(".mp3"):
            return path[:-4] + ".ogg"
    return path


def _load_gif_frames_desktop(path, target_size=None, scale=None):
    try:
        from PIL import Image
        import pygame
    except Exception:
        return [], []
    gif = Image.open(path)
    n = getattr(gif, "n_frames", 1)
    frames = []
    durations = []
    for i in range(n):
        try:
            gif.seek(i)
        except EOFError:
            break
        dur = gif.info.get("duration", 40)
        durations.append(max(int(dur), 1))
        frame = gif.convert("RGBA")
        raw = frame.tobytes()
        pw, ph = frame.size
        surf = pygame.image.frombuffer(raw, (pw, ph), "RGBA")
        if scale is not None and scale != 1.0:
            sw = int(pw * scale)
            sh = int(ph * scale)
            surf = pygame.transform.smoothscale(surf, (sw, sh))
        elif target_size and (pw, ph) != target_size:
            surf = pygame.transform.scale(surf, target_size)
        frames.append(surf)
    return frames, durations


def _load_gif_frames_web(path, target_size=None, scale=None):
    import json
    import os
    import pygame
    base = os.path.splitext(path)[0]
    sheet_path = base + "-sheet.png"
    json_path = base + "-sheet.json"
    try:
        sheet = pygame.image.load(sheet_path).convert_alpha()
    except Exception:
        return [], []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception:
        meta = {}
    fw = meta.get("frame_w")
    fh = meta.get("frame_h")
    cols = meta.get("cols", 1)
    rows = meta.get("rows", 1)
    durations = list(meta.get("durations", []))
    if fw is None or fh is None:
        fw = sheet.get_width() // max(1, cols)
        fh = sheet.get_height() // max(1, rows)
    frames = []
    total = cols * rows
    for i in range(total):
        r = i // cols
        c = i % cols
        rect = (c * fw, r * fh, fw, fh)
        f = sheet.subsurface(rect).copy()
        if scale is not None and scale != 1.0:
            sw = int(fw * scale)
            sh = int(fh * scale)
            f = pygame.transform.smoothscale(f, (sw, sh))
        elif target_size and (fw, fh) != target_size:
            f = pygame.transform.scale(f, target_size)
        frames.append(f)
    if len(durations) < len(frames):
        durations = list(durations) + [40] * (len(frames) - len(durations))
    elif len(durations) > len(frames):
        durations = durations[:len(frames)]
    return frames, durations


def load_gif_frames(path, target_size=None, scale=None):
    if IS_WEB:
        return _load_gif_frames_web(path, target_size=target_size, scale=scale)
    return _load_gif_frames_desktop(path, target_size=target_size, scale=scale)


def has_threading():
    return _threading is not None


def threading():
    return _threading


def bbox_pygame_mask(surf):
    try:
        import pygame
        mask = pygame.mask.from_surface(surf, threshold=1)
        rects = mask.get_bounding_rects()
        if not rects:
            return None
        left = min(r.x for r in rects)
        top = min(r.y for r in rects)
        right = max(r.x + r.width for r in rects)
        bottom = max(r.y + r.height for r in rects)
        return (left, top, right, bottom)
    except Exception:
        return None
