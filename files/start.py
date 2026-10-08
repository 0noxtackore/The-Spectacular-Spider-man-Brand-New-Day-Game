import pygame
import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    import protect_assets
    protect_assets.protect_all()
except Exception:
    pass

import asset_manager
from webcompat import IS_WEB, frame_pace, load_font

ORIG_W, ORIG_H = 1920, 1080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WHITE, BLACK = (255, 255, 255), (0, 0, 0)


def _img(path):
    full_path = os.path.join(BASE_DIR, path)
    try:
        return pygame.image.load(full_path).convert_alpha()
    except:
        return pygame.Surface((1, 1))


def main_loop(s, sw, sh):
    screen = s
    w, h = sw, sh

    logo = _img("images-game/game-logo/logo.png")
    blur = _img("images-game/game-logo/blur.png")
    enter_key = _img("images-game/key button/enter.png")
    try:
        pygame.display.set_icon(_img("images-game/game-icon/icon.png"))
    except:
        pass
    font = load_font(24, bold=True) or pygame.font.SysFont("arial", 24, bold=True)
    press_surf = font.render("PRESS ", True, WHITE)
    to_surf = font.render(" TO START", True, WHITE)
    key_scaled = pygame.transform.scale(enter_key, (100, 46))

    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "soundtrack-game", "main-theme.mp3"))
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        c = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound-game", "city.mp3"))
        c.set_volume(0.5)
        c.play(-1)
        web_snd = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound-game", "web.mp3"))
        web_snd.set_volume(0.6)
        laugh_snd = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound-game", "laught.mp3"))
        laugh_snd.set_volume(0.6)
    except Exception:
        web_snd = laugh_snd = None

    try:
        import costumes
        if not IS_WEB:
            import threading
            threading.Thread(target=costumes.load_fast, args=(screen, w, h), daemon=True).start()
        else:
            try:
                import asyncio
                async def _pre():
                    costumes.load_fast(screen, w, h)
                try:
                    asyncio.get_event_loop().run_until_complete(_pre())
                except Exception:
                    costumes.load_fast(screen, w, h)
            except Exception:
                costumes.load_fast(screen, w, h)
    except Exception:
        pass

    theme = "sun"
    asset_manager.open_menu_sun(w, h)

    started = False
    last_theme_swap = pygame.time.get_ticks()
    web_played = False
    laugh_played = False
    clock = pygame.time.Clock()
    running = True

    while running:
        now = pygame.time.get_ticks()
        dt = frame_pace(clock, target_fps=60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                asset_manager.close_video()
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    asset_manager.close_video()
                    return None
                if e.key == pygame.K_RETURN and not started:
                    started = True
                    asset_manager.open_action(w, h, theme)
                if e.key == pygame.K_TAB and not started:
                    theme = "night" if theme == "sun" else "sun"
                    last_theme_swap = now
                    if theme == "sun":
                        asset_manager.open_menu_sun(w, h)
                    else:
                        asset_manager.open_menu_night(w, h)

        if not started and now - last_theme_swap > 5000:
            theme = "night" if theme == "sun" else "sun"
            last_theme_swap = now
            if theme == "sun":
                asset_manager.open_menu_sun(w, h)
            else:
                asset_manager.open_menu_night(w, h)

        screen.fill(BLACK)

        frame = asset_manager.get_frame(w, h)
        if frame:
            screen.blit(frame, (0, 0))

        if not started:
            log_w = int(w * 0.45)
            log_h = int(logo.get_height() * (log_w / logo.get_width()))
            s_scaled = pygame.transform.scale(logo, (log_w, log_h))
            r = s_scaled.get_rect(centerx=w // 2 + 40, top=40)
            if theme == "night" and blur:
                screen.blit(pygame.transform.scale(blur, (log_w, log_h)), r)
            screen.blit(s_scaled, r)
            pw, kw, tw = press_surf.get_width(), 100, to_surf.get_width()
            sx = w // 2 - (pw + kw + tw) // 2
            cy = h - 120
            for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                screen.blit(font.render("PRESS ", True, BLACK), (sx + dx, cy - press_surf.get_height() // 2 + dy))
                ks = pygame.Surface((kw, 46))
                ks.fill(BLACK)
                ks.set_alpha(160)
                screen.blit(ks, (sx + pw + dx, cy - 23 + dy))
                screen.blit(font.render(" TO START", True, BLACK), (sx + pw + kw + dx, cy - to_surf.get_height() // 2 + dy))
            screen.blit(press_surf, (sx, cy - press_surf.get_height() // 2))
            screen.blit(key_scaled, (sx + pw, cy - 23))
            screen.blit(to_surf, (sx + pw + kw, cy - to_surf.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

        if started:
            if not web_played and web_snd:
                web_snd.play()
                web_played = True
            if not laugh_played and laugh_snd:
                laugh_snd.play()
                laugh_played = True
            if asset_manager.is_eof():
                saved = screen.copy()
                asset_manager.close_video()
                return saved

    asset_manager.close_video()
    return None


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    info = pygame.display.Info()
    scr = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Spider-Man - Brand New Day")
    r = main_loop(scr, info.current_w, info.current_h)
    pygame.quit()
    sys.exit()
