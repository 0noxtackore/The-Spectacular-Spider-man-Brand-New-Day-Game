# Plan: Spider-Man BND → juego ejecutable en interfaz web (Pygbag)

## Objetivo

Ejecutar el juego completo (intro → menú → costumes → gameplay) en el navegador como una app web, usando **pygbag** (Python/Pygame → WebAssembly), de modo que en la web **no se dependa de librerías de Python para cargar imágenes/videos**: el navegador carga PNG/GIF/MP4/OGG nativamente y la lógica Python solo referencia rutas.

**Regla de oro: el juego de escritorio (los `.bat`) no cambia de comportamiento.** Todo lo web se aísla tras `IS_WEB = sys.platform == "emscripten"`; los caminos desktop conservan PIL/ffpyplayer/threads tal cual.

## Hallazgos clave (verificados)

- Código runtime: 16 .py en `files/` (~2.800 líneas). `test-player.py` (1.331 líneas) **corre todo al importarse** (loop en nivel módulo L1097, sin guard `__main__`, `sys.exit()` al final).
- PIL se usa para: 20 GIFs de personaje + 20 GIFs de costumes (spritesheets), resize de PNG-sequence, y `GaussianBlur` (blur=1.5 en punch/swing/air-attack).
- **Race de blur**: el thread preload (blur=0) siempre sobrescribe al lazy (blur=1.5) → en escritorio el resultado efectivo final es **sin blur**. En web: precargar sin blur, eliminar la rama lazy blur ⇒ resultado determinista equivalente.
- ffpyplayer: solo `intro.py` + `asset_manager.py`. `costumes.py:11` importa `asset_manager` sin usarlo (arrastra ffpyplayer a todos los entry points) → eliminar ese import.
- Threads: preload en `start.py:64`, `_preload_all_animations` en `test-player.py:260`, `threading.Event` en `costumes.py` (`main_loop` espera con `.wait()` bloqueante en L190) → todos deben ser async en web (pygbag no tiene `_thread`).
- Gameplay: **no usa fondo** (`screen.fill(RED)`), no toca `main-game/` salvo `videos-composites/*.mp4` (menús).
- Audios: solo `main-theme.mp3`, `city/web/laught.mp3` y `sound-game/costumes/*.mp3` (4) se usan. pygbag **rechaza MP3** → convertir a OGG en build.
- Assets huérfanos que NO entran al bundle: `main-game/{videos,sun,night,spider-effect,spider-man,shadow,light,spritesheets,_tmp_frames}`, `art-loading/`, `ui-branding/`, `characters/Shocker/`, `climb/up-down/`, 6/7 soundtrack, `key button` sin usar, GIFs no referenciados (`punch.gif`, `surf-*`, `f-ii`).
- `tests/test_asset_manager.py` ya está roto (spec obsoleta: espera `preload_fase_menu_async`/`_frame_cache`). `tests/test_costumes.py` y `verify_costumes.py` llaman `costumes.load_fast()` **síncrono** → mantener `load_fast` síncrona (versión desktop) y crear `load_fast_async` aparte.
- `SysFont("arial")` se crea **cada frame** en `test-player.py:1066` → cachear; en web `arial` no existe (fallback a fuente por defecto de pygame → freesansbold).
- Vídeos: intro (6,8MB) + 4 composites de menú (~4,9MB) = ~11,7MB — perfectos para `<video>` nativo del navegador.

## Decisiones de arquitectura

1. **pygbag 0.9.x** (solo dependencia de build, no runtime). App folder = `webapp/` ensamblado por un script (nunca empaquetar `.git/`, tools, tests).
2. **Vídeo = elemento `<video>` del DOM** controlado desde Python vía `platform.window` (API pygbag), **sin decodificar frames en Python**. Estrategia de composición se decide en el spike (ver Paso 0).
3. **GIF → spritesheet PNG + JSON** en build (herramienta existente `convert_gifs_to_spritesheets.py`, extendida), con **test de paridad frame-a-frame vs PIL** antes de confiar.
4. **Audio MP3 → OGG** en build con `imageio_ffmpeg` (ya en el toolchain del repo).
5. **Bucles `while` → `async def` + `await` pacing** en TODOS los módulos (desktop los ejecuta con `asyncio.run`, que no altera el comportamiento; web los necesita sí o sí).
6. **Resolución lógica web = 1280×720** (la del gameplay) escalada por CSS al tamaño de ventana; los menús ya escalan por `sx/sy = w/1920`.
7. Tras costumes (Enter) → gameplay **solo en la entrada web** (escritorio intacto: run-game termina en costumes como hoy).

---

## Paso 0 — Spike de validación técnica (ANTES de tocar el juego)

Crear `webapp-spike/` mínimo con `main.py` async que pruebe en el navegador:

1. `pip install pygbag` + `py -m pygbag webapp-spike` en Windows.
2. `set_mode((1280,720))`, dibujar texto con `pygame.font.Font(None, ...)`, teclado.
3. Cargar un PNG y **un GIF convertido a spritesheet** (probar la conversión sobre `idle-right.gif`).
4. Reproducir un OGG con `pygame.mixer` (convertir `main-theme.mp3` como prueba).
5. **Vídeo**: crear `<video>` con `platform.window` usando `start-menu-sun.mp4` y validar las dos estrategías de composición del menú (logo+PRESS encima):
   - **A (preferida)**: vídeo **detrás** del canvas + canvas transparente (`set_mode(..., pygame.SRCALPHA)` + clear `(0,0,0,0)`); si el navegador compone bien → toda la UI sigue en pygame, sin mover nada al HTML.
   - **B (fallback)**: vídeo **encima** del canvas + overlay DOM (`<img>` logo + div "PRESS ENTER") controlado desde Python.
   - Intro/action (a pantalla completa, sin UI encima): vídeo encima del canvas siempre, indiferente.
6. Polling de `video.ended` desde Python para secuencias no-loop.
7. **Frame pacing**: medir FPS con `clock.tick(60)` vs `await asyncio.sleep(0)` a 60 y 120 Hz (la física es frame-based: si corre a 120fps el juego va al doble de velocidad). Definir el helper de pacing según lo que se mida.
8. Comprobar resolución de rutas (`BASE_DIR` vía `__file__` en wasm) y `os.listdir`.

**Criterio de salida**: estrategia de vídeo elegida (A o B), pacing a 60fps estable, spritesheet OK, OGG OK.

## Paso 1 — Pipeline de build: `build_web.py` (raíz)

Script que ensambla `webapp/` con la **misma estructura del repo** (`files/`, `images-game/`, `intro-video/`, `sound-game/`, `soundtrack-game/`) solo con lo referenciado, y convierte:

| Transformación | Detalle | Herramienta |
|---|---|---|
| GIFs → spritesheet+JSON | 20 GIFs de `characters/Spider-man/` + `shadow.gif`, `shadow-noir.gif`, `suit-pose/{1..18}.gif`. Extender `convert_gifs_to_spritesheets.py` (cols, `frame_w/h`, duraciones por frame). **Validar disposal/composición de Pillow** | Pillow (solo build) |
| MP3 → OGG | `main-theme`, `city`, `web`, `laught`, `costumes/*` (4) | `imageio_ffmpeg` |
| Copiar código | `files/*.py` (solo runtime: NO `generate_*`, `convert_*`), paths intactos | shutil |
| Copiar assets runtime | según el inventario de arriba; excluir huérfanos, `__pycache__`, GIFs/MP3 originales una vez convertidos | shutil |
| Poda de código | `main.py` nuevo (Paso 3) | — |

- Reporte de tamaño final del bundle (objetivo: ≲100MB; si se pasa, optimizar PNGs/spritesheets).
- Flags: `--serve` (→ `py -m pygbag webapp`, servidor local en :8000), `--archive` (zip para itch.io), `--clean`.

**Verificación**: `webapp/` listo; `build_web.py --serve` arranca; `webapp/files/*.py` importan rutas correctas.

## Paso 2 — Capa de compatibilidad: `files/webcompat.py` + `files/web_video.py`

**`webcompat.py`**
- `IS_WEB = sys.platform == "emscripten"`.
- `async def frame_pace(clock, target_ms=16)` → devuelve `dt` ms (para `costumes` que usa `dt`); desktop: `clock.tick(60)`; web: pacing medido en el spike.
- `load_font(size, bold)` → desktop: `SysFont("arial", ...)`; web: `Font(None, ...)` cacheado (además cachear el `SysFont` de `test-player.py:1066` que hoy se crea por frame).
- `resolve_audio(path)` → `.ogg` en web / `.mp3` en escritorio.
- `load_gif_frames(path, scale)` con rama web: lee spritesheet+JSON con `subsurface` (escritorio conserva PIL intacto).
- `_thread`/`threading` solo se importan si `not IS_WEB`.

**`web_video.py`** — interfaz única `open(path, loop) / eof() / close()`:
- Escritorio: backend ffpyplayer **idéntico al actual** (`asset_manager`/`intro` llaman a esto o se quedan como están — se decide por menor diff).
- Web: crea/gestiona `<video>` DOM (src, loop, play, poll `ended`), según estrategia del spike.

**Verificación**: tests nuevos (ver Paso 5) + import limpio de `webcompat` en wasm.

## Paso 3 — Migrar intro, menú y costumes a async + entrada web

| Archivo | Cambios |
|---|---|
| `files/intro.py` | `async def play_intro()`; sin `time.sleep`; en web: vídeo DOM a pantalla completa (ESC/`ended` salen); desktop: ffpyplayer como hoy |
| `files/asset_manager.py` | import ffpyplayer condicional (`if not IS_WEB`); rama web: `open_menu_sun/night/action` cambian `src` del `<video>`, `get_frame() → None` (el canvas queda oculto detrás del vídeo o transparente según spike), `is_eof()` = poll `ended`; `time.sleep` solo desktop |
| `files/start.py` | `async def main_loop` + `await frame_pace`; hilo de precarga de costumes **solo desktop**, en web `await costumes.load_fast_async(...)` al inicio; `screen.fill(BLACK)` → `(0,0,0,0)` cuando hay vídeo detrás (estrategia A); si B → mostrar/ocultar overlay DOM; devuelve `None` en web (sin saved_frame — run-game web lo tolera, costumes pinta su propio fondo) |
| `files/costumes.py` | **eliminar `import asset_manager`** (L11, sin uso); `async def main_loop` + pacing; `if not IS_WEB: import threading` (Event solo desktop; en web `load_fast_async` se awaiting ANTES del loop, L190 no se alcancha sin setear); `crop_content` → rama web con `pygame.mask.from_surface(surf, threshold=1).get_bounding_rects()` (paridad con PIL getbbox verificada por test); `tostring/fromstring` → `tobytes/frombytes` (válidos en ambas versiones); `_load_gif_frames` → spritesheet en web; `load_fast` **sigue síncrona** (tests/verify) + nueva `async def load_fast_async` chunked (`await asyncio.sleep(0)` cada 1-2 trajes) |
| `files/run-game.py` | envolver `intro/start/costumes` en `async def` + `asyncio.run` (desktop). Sin cambios de flujo |
| **`webapp/main.py`** (nuevo) | entrada web: init 1280×720 → `await play_intro()` → `await start.main_loop(...)` → `await costumes.main_loop(...)` → (Paso 4) gameplay → `location.reload()` al terminar para reiniciar |

**Verificación**: desktop `run-game.bat` idéntico al actual; `py -m pygbag webapp` muestra intro→menú→costumes en navegador.

## Paso 4 — Migrar gameplay: `files/test-player.py`

1. **Estructura**: extraer a funciones `init_display()`, `preload_basic()` y `async def run()`; loop L1097-1328 dentro de `run()` (con `global` para `player`, `cam_y`, etc.); al final: `if not IS_WEB: pygame.quit(); sys.exit()` — en web solo `return`. Guard `__main__` con `asyncio.run(run())`.
2. **Loaders con rama web** (`IS_WEB`):
   - `load_gif_frames` → spritesheet (web) / PIL (desktop, intacto).
   - `load_png_sequence_from_dir` / `load_specific_pngs` → `pygame.image.load` + `smoothscale` en web (sin PIL; **sin blur**: la rama blur=1.5 se omite en web — ver race condition, el resultado desktop efectivo es sin blur).
3. **Preload**: `_preload_all_animations` (thread) → desktop conserva thread; web: `async def preload_rest()` chunked con awaits, llamado **antes** del loop (evita `os.listdir`/fetch HTTP en pleno gameplay). `os.listdir` de dirs de PNGs en web = peticiones HTTP → por eso se precarga todo.
4. **Loop**: `dt = await frame_pace(...)` sustituye `clock.tick(60)`; el resto de la lógica (física, combos, cámara, input) **no se toca**.
5. Fuente: `SysFont("arial")` cacheada → `load_font()`.
6. Tras `costumes.main_loop` en `webapp/main.py`: `await test_player.run()`. (Fuera de alcance: que el traje elegido afecte al gameplay — hoy no existe esa integración.)

**Verificación**: desktop `excecute-test-player.bat` idéntico (mismas animaciones, mismo comportamiento); web: gameplay completo a 60fps.

## Paso 5 — Verificación y tests

**Desktop (regresión, obligatorio)**
- `run-game.bat`, `execute-start-game.bat`, `excecute-test-player.bat`, `excecute-costumes.bat` → comportamiento visual idéntico.
- `python -m unittest discover tests` (sabemos de antemano que `test_asset_manager.py` ya está roto por spec obsoleta → reescribirlo mínimo contra la API real de `asset_manager`, o marcarlo como skip documentado).

**Tests nuevos**
- `tests/test_spritesheet_parity.py`: para cada GIF convertido, comparar frames PIL vs recortes del spritesheet (exacto o con tolerancia documentada si Pillow compone disposal distinto → corregir el converter).
- `tests/test_crop_parity.py`: `crop_content` PIL vs `pygame.mask` con `threshold=1` sobre las 18 suits → si es idéntico, se puede unificar; si no, rama web aislada.
- Rutas de audio (`.ogg` web / `.mp3` desktop).

**Web (checklist en navegador)**
- Intro: reproduce, ESC salta, no congela la pestaña.
- Menú: vídeo loop, TAB/5s cambia tema, logo+PRESS ENTER visibles, ENTER → transición action vídeo → `ended` → costumes.
- Costumes: ←/→, X (pose GIF), ESC (modal), ENTER sale; SFX suenan.
- Gameplay: todos los controles de las instrucciones (mov, salto, combo L, PCH K, heavy P, swing I, web O, shield M, stealth H, daño/cura 1/2), salud, cámara.
- Audio: música de menú + city loop + SFX (después del gesto de click inicial de pygbag).
- Rendimiento: ~60fps estables en gameplay; tiempo de primera carga; tamaño del zip.

## Paso 6 — Entrega

- `run-web.bat` → `python build_web.py --serve` (abre el juego en el navegador en local).
- `python build_web.py --archive` → `dist/*.zip` listo para itch.io/web.
- README: sección "Jugar en el navegador".
- Actualizar `run-game.html` para enlazar/embeber el build local (hoy solo dice "ejecuta el .bat").

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Canvas no compone alfa sobre `<video>` (estrategia A falla) | Fallback B (overlay DOM de logo/PRESS) ya previsto en el spike |
| Física frame-based a 120Hz va al doble de velocidad | Helper de pacing con throttle a ~16,7ms medido en el spike |
| pygame-ce (wasm) ≠ pygame clásico (APIs) | Unificar a `tobytes/frombytes`; spike valida `mixer`, `mask`, `SCALPHA` |
| Paridad de spritesheets vs PIL (disposal de GIF) | Test de paridad frame-a-frame antes de activar la rama web |
| Tamaño del bundle | Poda agresiva de assets huérfanos; solo 5 MP4 (~12MB); reporte de tamaño en build |
| `threading`/`subprocess` inexistentes en wasm | Imports condicionales `if not IS_WEB`; `protect_assets` ya está en try/except |
| `load_fast` async rompería tests/verify | Se mantiene `load_fast` síncrona; `load_fast_async` es una capa nueva |
| Fetch HTTP de cientos de PNGs en gameplay | Preload asíncrono completo antes del loop |

## Archivos

- **Nuevos**: `webapp/main.py`, `build_web.py`, `files/webcompat.py`, `files/web_video.py`, `run-web.bat`, `tests/test_spritesheet_parity.py`, `tests/test_crop_parity.py`, `webapp-spike/` (temporal, se puede borrar al final).
- **Modificados**: `files/{intro,start,costumes,asset_manager,run-game,test-player}.py` (ramas `IS_WEB` + async; desktop intacto), `README.md`, `run-game.html`.
- **No se toca**: tools de build offline (`convert_*`, `generate_*`), `.bat` desktop, assets originales.
