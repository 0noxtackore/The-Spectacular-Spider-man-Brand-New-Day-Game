import pygame
import sys
import os

from webcompat import IS_WEB, load_gif_frames as _wg_frames

if not IS_WEB:
    import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE_DIR, "images-game", "costumes-section")
ORIG_W, ORIG_H = 1920, 1080

try:
    import asset_manager  # desktop compatibility only
except Exception:
    asset_manager = None


def load_png(path, w, h, do_scale=True):
    try:
        img = pygame.image.load(os.path.join(ASSETS, path)).convert_alpha()
        if do_scale and img.get_size() != (w, h):
            img = pygame.transform.scale(img, (w, h))
        return img
    except:
        surf = pygame.Surface((w, h) if do_scale else (ORIG_W, ORIG_H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        return surf


def crop_content(surf):
    try:
        import pygame
    except Exception:
        return surf, None
    if IS_WEB:
        from webcompat import bbox_pygame_mask
        bb = bbox_pygame_mask(surf)
        if not bb:
            return surf, None
        left, top, right, bottom = bb
        w, h = surf.get_size()
        if left < 0:
            left = 0
        if top < 0:
            top = 0
        if right > w:
            right = w
        if bottom > h:
            bottom = h
        cw, ch = max(1, right - left), max(1, bottom - top)
        subs = surf.subsurface((left, top, cw, ch)).copy()
        return subs, (left, top, right, bottom)
    w, h = surf.get_size()
    raw = pygame.image.tobytes(surf, "RGBA")
    try:
        from PIL import Image
    except Exception:
        return surf, None
    pil_img = Image.frombytes("RGBA", (w, h), raw)
    bbox = pil_img.getbbox()
    if not bbox:
        return surf, None
    cropped = pil_img.crop(bbox)
    raw2 = cropped.tobytes()
    return pygame.image.frombuffer(raw2, cropped.size, "RGBA"), bbox


def _load_gif_frames(gif_path, target_w, target_h, speed=1.0):
    frames, durs = _wg_frames(gif_path, target_size=(target_w, target_h))
    if speed != 1.0 and durs:
        nd = []
        for d in durs:
            nd.append(max(int(d * speed), 1))
        durs = nd
    return frames, durs


SUIT_BBOXES = {
    1: (105, 225, 243, 1069), 2: (174, 227, 305, 1078),
    3: (238, 227, 369, 1078), 4: (314, 226, 445, 1078),
    5: (385, 227, 509, 1077), 6: (447, 228, 590, 1078),
    7: (527, 227, 659, 1079), 8: (583, 228, 753, 1080),
    9: (707, 226, 839, 1079), 10: (794, 227, 918, 1069),
    11: (851, 227, 985, 1067), 12: (930, 229, 1054, 1067),
    13: (1003, 224, 1127, 1064), 14: (1079, 228, 1203, 1054),
    15: (1158, 227, 1293, 1053), 16: (1201, 229, 1368, 1055),
    17: (1309, 227, 1438, 1077), 18: (1373, 227, 1497, 1077),
}

_assets = {}
_load_event = None
if not IS_WEB:
    try:
        _load_event = threading.Event()
    except Exception:
        _load_event = None
else:
    _load_event = None


def load_fast(screen, w, h):
    global _assets
    if not pygame.font.get_init():
        pygame.font.init()
    sx = w / ORIG_W
    sy = h / ORIG_H
    crops = {}
    for i in range(1, 19):
        full = load_png("suits/{}.png".format(i), ORIG_W, ORIG_H, do_scale=False)
        cropped, _ = crop_content(full)
        crops[i] = cropped
    keys = {}
    for name in ["left", "right", "x", "z", "p", "a", "esc"]:
        p = os.path.join(BASE_DIR, "images-game", "key button", name + ".png")
        try:
            keys[name] = pygame.image.load(p).convert_alpha()
        except:
            keys[name] = pygame.Surface((40, 40), pygame.SRCALPHA)
    arrows = {i: load_png("arrow/{}.png".format(i), w, h) for i in range(1, 19)}
    spidey_path = os.path.join(BASE_DIR, "images-game", "notification-icon", "spidey-icon.png")
    try:
        spidey = pygame.image.load(spidey_path).convert_alpha()
    except:
        spidey = pygame.Surface((64, 64), pygame.SRCALPHA)
    sfx_dir = os.path.join(BASE_DIR, "sound-game", "costumes")

    def ls(name):
        try:
            return pygame.mixer.Sound(os.path.join(sfx_dir, name + ".mp3"))
        except:
            return None

    sfx = {"move": ls("move-costume"), "quit": ls("quit-game"), "select": ls("select-costume"), "other": ls("other")}
    bg = load_png("backgroung.png", w, h)

    displays = {}
    big_surfs = {}
    for i in range(1, 19):
        bx1, by1, bx2, by2 = SUIT_BBOXES[i]
        ow = bx2 - bx1
        oh = by2 - by1
        dw = max(1, int(ow * sx))
        dh = max(1, int(oh * sy))
        scaled = pygame.transform.scale(crops[i], (dw, dh))
        displays[i] = {"surf": scaled, "x": int(bx1 * sx), "y": int(by1 * sy), "w": dw, "h": dh}
        bw = max(1, int(dw * 1.15))
        bh = max(1, int(dh * 1.15))
        big_surfs[i] = pygame.transform.scale(scaled, (bw, bh))
    cf = pygame.font.SysFont("arial", 16, bold=True)
    ctrl = []
    for label_text, key_name in [("QUIT", "esc"), ("BACK", "a"), ("LEFT", "left"), ("RIGHT", "right"), ("SELECT", "x"), ("MAP", "z"), ("SWING TIME", "p")]:
        ki = keys[key_name]
        kw = ki.get_width()
        kh = ki.get_height()
        ks = pygame.transform.smoothscale(ki, (48, int(48 * kh / kw)))
        lb = cf.render(label_text, True, (255, 255, 255))
        lsh = cf.render(label_text, True, (0, 0, 0))
        ctrl.append((lb, lsh, ks, lb.get_width() + 6 + ks.get_width()))
    tw = sum(d[3] for d in ctrl) + 20 * (len(ctrl) - 1)
    qf = pygame.font.SysFont("arial", 24, bold=True)
    qt = qf.render("ARE YOU SURE YOU WANT TO QUIT?", True, (255, 255, 255))
    of = pygame.font.SysFont("arial", 22, bold=True)
    icon = pygame.transform.smoothscale(spidey, (100, 100))
    _assets = {
        "sx": sx, "sy": sy, "bg": bg,
        "bg_suit": displays[18]["surf"],
        "displays": displays, "big_surfs": big_surfs, "arrows": arrows,
        "ctrl_data": ctrl, "cx": w - 20 - tw, "cy": h - 20,
        "qf": qf, "qt": qt, "of": of, "icon": icon, "sfx": sfx,
    }
    if _load_event is not None:
        try:
            _load_event.set()
        except Exception:
            pass


def load_assets(screen, w, h):
    load_fast(screen, w, h)


def _load_shadow(w, h, suit_num=1):
    cache_key = "shadow_frames_noir" if suit_num == 18 else "shadow_frames"
    dcache_key = "shadow_durs_noir" if suit_num == 18 else "shadow_durs"
    if cache_key in _assets:
        return _assets[cache_key], _assets[dcache_key]
    name = "shadow-noir.gif" if suit_num == 18 else "shadow.gif"
    shadow_path = os.path.join(ASSETS, name)
    frames, durs = _load_gif_frames(shadow_path, w, h, speed=1.5)
    _assets[cache_key] = frames
    _assets[dcache_key] = durs
    return frames, durs


def _load_pose(suit_num, w, h):
    key = "pose_frames_{}".format(suit_num)
    dkey = "pose_durs_{}".format(suit_num)
    if key in _assets:
        return _assets[key], _assets[dkey]
    pose_path = os.path.join(ASSETS, "suit-pose", "{}.gif".format(suit_num))
    frames, durs = _load_gif_frames(pose_path, w, h, speed=1.5)
    _assets[key] = frames
    _assets[dkey] = durs
    return frames, durs


def _render_pose_overlay(screen, shadow_frames, pose_frames, shadow_idx, pose_idx):
    if not pose_frames or not shadow_frames:
        return
    cycle = len(shadow_frames)
    sf = shadow_frames[shadow_idx % cycle]
    white_shadow = pygame.Surface(sf.get_size(), pygame.SRCALPHA)
    white_shadow.fill((255, 255, 255, 255))
    white_shadow.blit(sf, (0, 0))
    screen.blit(white_shadow, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    pf = pose_frames[pose_idx % cycle]
    screen.blit(pf, (0, 0))


def main_loop(screen, screen_width, screen_height):
    global _assets
    if _load_event is not None:
        try:
            _load_event.wait()
        except Exception:
            pass
    a = _assets
    w, h = screen_width, screen_height

    current_suit = 1
    active_pose_suit = 1
    clock = pygame.time.Clock()
    running = True
    show_quit_modal = False
    modal_choice = 0

    shadow_frames = []
    pose_frames = []
    shared_durs = []
    shared_idx = 0
    shared_timer = 0

    def activate_pose_for_suit(suit_num):
        nonlocal active_pose_suit, shadow_frames, pose_frames, shared_durs, shared_idx, shared_timer
        active_pose_suit = suit_num
        shadow_frames, shadow_durs = _load_shadow(w, h, suit_num)
        pose_frames, _ = _load_pose(active_pose_suit, w, h)
        shared_durs = shadow_durs
        shared_idx = 0
        shared_timer = 0

    activate_pose_for_suit(active_pose_suit)
    sfx = a["sfx"]
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if show_quit_modal:
                    if event.key == pygame.K_LEFT:
                        modal_choice = 0
                    if event.key == pygame.K_RIGHT:
                        modal_choice = 1
                    if event.key == pygame.K_RETURN:
                        if modal_choice == 0:
                            if sfx["other"]:
                                sfx["other"].play()
                            running = False
                        else:
                            if sfx["other"]:
                                sfx["other"].play()
                            show_quit_modal = False
                    if event.key == pygame.K_ESCAPE:
                        if sfx["other"]:
                            sfx["other"].play()
                        show_quit_modal = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        show_quit_modal = True
                        modal_choice = 0
                        if sfx["quit"]:
                            sfx["quit"].play()
                    if event.key == pygame.K_LEFT:
                        current_suit = 18 if current_suit == 1 else current_suit - 1
                        if sfx["move"]:
                            sfx["move"].play()
                    if event.key == pygame.K_RIGHT:
                        current_suit = 1 if current_suit == 18 else current_suit + 1
                        if sfx["move"]:
                            sfx["move"].play()
                    if event.key == pygame.K_x:
                        activate_pose_for_suit(current_suit)
                        if sfx["select"]:
                            sfx["select"].play()
                    if event.key == pygame.K_RETURN:
                        if sfx["other"]:
                            sfx["other"].play()
                        running = False

        if active_pose_suit > 0 and pose_frames:
            shared_timer += dt
            dur = max(16, int(shared_durs[shared_idx % len(shared_durs)]))
            while shared_timer >= dur:
                shared_timer -= dur
                shared_idx += 1
                dur = max(16, int(shared_durs[shared_idx % len(shared_durs)]))

        screen.fill((0, 0, 0))

        screen.blit(a["bg"], (0, 0))

        if current_suit != 18:
            d18 = a["displays"][18]
            screen.blit(a["bg_suit"], (d18["x"], d18["y"]))

        for i in range(1, 19):
            if i != current_suit:
                d = a["displays"][i]
                screen.blit(d["surf"], (d["x"], d["y"]))

        d = a["displays"][current_suit]
        big = a["big_surfs"][current_suit]
        bx = d["x"] - (big.get_width() - d["w"]) // 2
        by = d["y"] - (big.get_height() - d["h"]) // 2
        screen.blit(big, (bx, by))

        screen.blit(a["arrows"][current_suit], (0, 0))

        if active_pose_suit > 0 and pose_frames:
            _render_pose_overlay(screen, shadow_frames, pose_frames, shared_idx, shared_idx)

        x = a["cx"]
        for lbl, lbl_shadow, k_scaled, seg_w in a["ctrl_data"]:
            lh = lbl.get_height()
            kh = k_scaled.get_height()
            center_y = a["cy"] - max(lh, kh) // 2
            text_y = center_y - lh // 2
            key_y = center_y - kh // 2
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                screen.blit(lbl_shadow, (x + dx, text_y + dy))
            screen.blit(lbl, (x, text_y))
            screen.blit(k_scaled, (x + lbl.get_width() + 6, key_y))
            x += seg_w + 20

        if show_quit_modal:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            modal_w = 500
            modal_h = 280
            mx = (screen_width - modal_w) // 2
            my = (screen_height - modal_h) // 2
            pygame.draw.rect(screen, (20, 20, 40), (mx, my, modal_w, modal_h), border_radius=12)
            pygame.draw.rect(screen, (100, 100, 180), (mx, my, modal_w, modal_h), 3, border_radius=12)
            ix = mx + (modal_w - 100) // 2
            iy = my + 20
            screen.blit(a["icon"], (ix, iy))
            qx = mx + (modal_w - a["qt"].get_width()) // 2
            qy = iy + 115
            screen.blit(a["qt"], (qx, qy))
            opt_spacing = 120
            opt_center_x = mx + modal_w // 2
            opt_y = qy + 45
            for idx, text in enumerate(["YES", "NO"]):
                color = (255, 50, 50) if idx == modal_choice else (180, 180, 180)
                label = a["of"].render(text, True, color)
                lx = opt_center_x - opt_spacing // 2 + idx * opt_spacing - label.get_width() // 2
                screen.blit(label, (lx, opt_y))
                if idx == modal_choice:
                    underline = pygame.Surface((label.get_width() + 10, 3))
                    underline.fill((255, 50, 50))
                    screen.blit(underline, (lx - 5, opt_y + label.get_height() + 4))

        pygame.display.flip()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Spider-Man - Costumes")
    main_loop(screen, sw, sh)
    pygame.quit()
    sys.exit()
