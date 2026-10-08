import pygame
import os
import sys
import time

from webcompat import IS_WEB
if not IS_WEB:
    from ffpyplayer.player import MediaPlayer
else:
    MediaPlayer = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.path.join(BASE_DIR, "intro-video", "intro-0noxtackore.mp4")

def play_intro():
    return _play_intro_sync()

def _play_intro_sync():
    screen = pygame.display.get_surface()
    if screen is None:
        pygame.init()
        pygame.mixer.init()
        info = pygame.display.Info()
        sw, sh = info.current_w, info.current_h
        screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Spider-Man - Brand New Day")
    else:
        sw, sh = screen.get_size()

    if IS_WEB:
        try:
            import platform
            w = getattr(platform, "window", None)
            if w is not None:
                vid = w.document.createElement("video")
                vid.src = VIDEO.replace("\\", "/")
                vid.setAttribute("preload", "auto")
                vid.setAttribute("muted", "muted")
                vid.setAttribute("playsinline", "true")
                vid.style.position = "absolute"
                vid.style.left = "0"
                vid.style.top = "0"
                vid.style.width = "100vw"
                vid.style.height = "100vh"
                vid.style.objectFit = "cover"
                vid.style.zIndex = "10"
                vid.autoplay = True
                w.document.body.appendChild(vid)
                _dom_vid = vid

                def _wait():
                    import asyncio
                    loop = asyncio.get_event_loop()
                    while not getattr(vid, "ended", False):
                        loop.run_until_complete(asyncio.sleep(0.016))
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                                try:
                                    vid.pause()
                                    vid.src = ""
                                    w.document.body.removeChild(vid)
                                except Exception:
                                    pass
                                return
                    try:
                        vid.pause()
                        w.document.body.removeChild(vid)
                    except Exception:
                        pass

                _wait()
                return screen
        except Exception:
            pass

    player = MediaPlayer(VIDEO)
    player.set_pause(False)
    time.sleep(0.1)

    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                player.close_player()
                return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                player.close_player()
                return None

        frame, val = player.get_frame()
        if val == 'eof':
            break
        if frame is not None:
            img, pts = frame
            data = img.to_bytearray()[0]
            w, h = img.get_size()
            surf = pygame.image.frombuffer(data, (w, h), "RGB")
            surf = pygame.transform.scale(surf, (sw, sh))
            screen.blit(surf, (0, 0))
            pygame.display.flip()

        clock.tick(30)

    player.close_player()
    return screen

if __name__ == "__main__":
    pygame.init()
    info = pygame.display.Info()
    scr = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Spider-Man - Brand New Day")
    play_intro()
    pygame.quit()
    sys.exit()
