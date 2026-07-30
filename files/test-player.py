import pygame
import sys
import os
import math
import random
from PIL import Image, ImageFilter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_path(path):
    if not path:
        return path
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(BASE_DIR, path))

# Initialization
pygame.init()
pygame.mixer.init()

# Windowed mode (not fullscreen)
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Spider-Man - Player Test")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 149, 0)
DARK_RED = (139, 0, 0)

# Animation paths
ANIMATION_PATHS = {
    "idle-right": "images-game/characters/Spider-man/idle-right.gif",
    "idle-left": "images-game/characters/Spider-man/idle-left.gif",
    "run-right": "images-game/characters/Spider-man/run-right.gif",
    "run-left": "images-game/characters/Spider-man/run-left.gif",
    "entry-right": "images-game/characters/Spider-man/entry-right.png",
    "entry-left": "images-game/characters/Spider-man/entry-left.png",
    "jump-right": "images-game/characters/Spider-man/jump-right.gif",
    "jump-left": "images-game/characters/Spider-man/jump-left.gif",
    "sit-right": "images-game/characters/Spider-man/sit-right.png",
    "sit-left": "images-game/characters/Spider-man/sit-left.png",
    "sit-center": "images-game/characters/Spider-man/sit-center.png",
    "sit-back": "images-game/characters/Spider-man/sit-back.png",
    "climb-right": "images-game/characters/Spider-man/climb/right/climb.gif",
    "climb-left": "images-game/characters/Spider-man/climb/left/climb.gif",
    "pch-right": "images-game/characters/Spider-man/punch/right",
    "pch-left": "images-game/characters/Spider-man/punch/left",
    "punch-right": "images-game/characters/Spider-man/punch/right",
    "punch-left": "images-game/characters/Spider-man/punch/left",
    "swing-right": "images-game/characters/Spider-man/swing/right",
    "swing-left": "images-game/characters/Spider-man/swing/left",
    "wsh-right": "images-game/characters/Spider-man/wsh-right.gif",
    "wsh-left": "images-game/characters/Spider-man/wsh-left.gif",
    "shield-right": "images-game/characters/Spider-man/sh-right.png",
    "shield-left": "images-game/characters/Spider-man/sh-left.png",
    "flip-right": "images-game/characters/Spider-man/flip/right/f-i.png",
    "flip-left": "images-game/characters/Spider-man/flip/left/f-i.png",
    "stealth": "images-game/characters/Spider-man/hf.png"
}

HEALTH_ICON_PATH = "images-game/health-character/Spider-man.png"

# Load GIF with PIL
def load_gif_frames(path, scale_factor=1.0):
    """Load GIF frames using PIL with transparency and uniform sizing"""
    frames = []
    path = resolve_path(path)
    if not os.path.exists(path):
        print(f"Not found: {path}")
        return frames
    
    try:
        gif = Image.open(path)
        
        # Get first frame dimensions as reference
        gif.seek(0)
        ref_frame = gif.convert('RGBA')
        ref_w = int(ref_frame.width * scale_factor)
        ref_h = int(ref_frame.height * scale_factor)
        
        for frame_num in range(gif.n_frames):
            gif.seek(frame_num)
            # Convert to RGBA to preserve transparency
            frame_rgba = gif.convert('RGBA')
            frame_resized = frame_rgba.resize((ref_w, ref_h), Image.Resampling.BILINEAR)
            frame_data = frame_resized.tobytes()
            frame_surface = pygame.image.fromstring(frame_data, (ref_w, ref_h), 'RGBA')
            frames.append(frame_surface)
        print(f"Loaded: {path} ({len(frames)} frames, {ref_w}x{ref_h})")
    except Exception as e:
        print(f"Error loading {path}: {e}")
    
    return frames

def load_single_image(path, scale_factor=1.0):
    """Load a single PNG/JPG image"""
    path = resolve_path(path)
    if not os.path.exists(path):
        print(f"Not found: {path}")
        return None
    
    try:
        img = pygame.image.load(path).convert_alpha()
        new_w = int(img.get_width() * scale_factor)
        new_h = int(img.get_height() * scale_factor)
        return pygame.transform.smoothscale(img, (new_w, new_h))
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

def load_png_sequence_from_dir(dir_path, scale_factor=1.0, blur_radius=0):
    """Load all PNGs from a directory in alphabetical order, with optional blur"""
    frames = []
    dir_path = resolve_path(dir_path)
    if not os.path.exists(dir_path):
        print(f"Directory not found: {dir_path}")
        return frames

    try:
        png_files = sorted([f for f in os.listdir(dir_path) if f.lower().endswith('.png')])
        for png_file in png_files:
            path = os.path.join(dir_path, png_file)
            pil_img = Image.open(path).convert('RGBA')
            if blur_radius > 0:
                pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            new_w = int(pil_img.width * scale_factor)
            new_h = int(pil_img.height * scale_factor)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            frame = pygame.image.fromstring(pil_img.tobytes(), (new_w, new_h), 'RGBA')
            frames.append(frame)
        print(f"Cargado: {dir_path} ({len(frames)} frames)")
    except Exception as e:
        print(f"Error cargando {dir_path}: {e}")

    return frames

def load_specific_pngs(dir_path, filenames, scale_factor=1.0, blur_radius=0):
    """Carga PNGs específicos de un directorio, con blur opcional."""
    frames = []
    dir_path = resolve_path(dir_path)
    for fname in filenames:
        path = os.path.join(dir_path, fname)
        if not os.path.exists(path):
            print(f"No encontrado: {path}")
            continue
        try:
            pil_img = Image.open(path).convert('RGBA')
            if blur_radius > 0:
                pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            new_w = int(pil_img.width * scale_factor)
            new_h = int(pil_img.height * scale_factor)
            pil_img = pil_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            frame = pygame.image.fromstring(pil_img.tobytes(), (new_w, new_h), 'RGBA')
            frames.append(frame)
        except Exception as e:
            print(f"Error cargando {path}: {e}")
    if frames:
        print(f"Cargados {len(frames)} frames desde {dir_path}: {filenames}")
    return frames

# Air attack specific file
AIR_ATTACK_FILES = ["p-t-ii.png"]

# Swing flat frame sequence: sw-vii, sw-viii, sw-vi, sw-i, sw-viii, sw-vi, sw-v, sw-iv, sw-v
SWING_SEQUENCE = [6, 7, 5, 0, 7, 5, 4, 3, 4]

K_ROMAN = ["i", "ii", "iii", "iv", "v"]


# Combo frame table: (name, duration, boost_y, burst_x, chargeable, charged_boost)
# Order: frames WITHOUT impulse first, then frames WITH impulse
COMBO_FRAMES = [
    ("k-i",     10,    0,  0, False,   0),
    ("k-iii",   10,    0,  0, False,   0),
    ("k-iv",    15,    0,  0, False,   0),
    ("p-t-ii",  15,    0,  0, False,   0),
    ("k-ii",    10,  -12,  0, False,   0),
    ("p-i",     28,  -14,  0,  True, -18),
    ("p-t-i",   15,  -14, 22, False,   0),
    ("sw-p",    18,  -10, 22, False,   0),
    ("w-i",     30,  -24,  0,  True, -28),
    # PCH GIF entries (9-13): auto-play multi-frame GIFs
    ("pch-i-gif",   1,   0,  0, False,   0),
    ("pch-ii-gif",  1,   0,  0, False,   0),
    ("pch-iii-gif", 1,   0,  0, False,   0),
    ("pch-iv-gif",  1,   0,  0, False,   0),
    ("pch-v-gif",   1,   0,  0, False,   0),
]
# Map: position in COMBO_FRAMES → alphabetical PNG index (0=k-i … 8=w-i)
# For GIF entries (9-13) the visual index is unused (animation switches)
COMBO_VISUAL_MAP = [0, 2, 3, 6, 1, 4, 5, 7, 8, 0, 0, 0, 0, 0]

# Ground pattern: three 7-hit phases + 5 pch finisher → 26 frames total
# Each number is the index within COMBO_FRAMES
GROUND_COMBO = [
    0,1,4,2,5,7,6,3,   # k-i, k-iii, k-ii, k-iv, p-i, sw-p, p-t-i, p-t-ii
    1,5,6,4,7,0,2,3,   # k-iii, p-i, p-t-i, k-ii, sw-p, k-i, k-iv, p-t-ii
    5,4,7,6,0,2,1,3,   # p-i, k-ii, sw-p, p-t-i, k-i, k-iv, k-iii, p-t-ii
    9,10,11,12,13,     # pch-i, pch-ii, pch-iii, pch-iv, pch-v
]

# Character scale (smaller for window)
PLAYER_SCALE = 0.3
RUN_SCALE = 0.25  # Smaller scale for run-left and run-right
JUMP_SCALE = 0.25  # Smaller scale for jump-left and jump-right

# Cargar solo las animaciones básicas al inicio para acelerar el arranque
animations = {
    "idle-right": load_gif_frames(ANIMATION_PATHS["idle-right"], PLAYER_SCALE),
    "idle-left": load_gif_frames(ANIMATION_PATHS["idle-left"], PLAYER_SCALE),
    "run-right": load_gif_frames(ANIMATION_PATHS["run-right"], RUN_SCALE),
    "run-left": load_gif_frames(ANIMATION_PATHS["run-left"], RUN_SCALE),
    "entry-right": [load_single_image(ANIMATION_PATHS["entry-right"], PLAYER_SCALE)],
    "entry-left": [load_single_image(ANIMATION_PATHS["entry-left"], PLAYER_SCALE)],
    "jump-right": load_gif_frames(ANIMATION_PATHS["jump-right"], PLAYER_SCALE),
    "jump-left": load_gif_frames(ANIMATION_PATHS["jump-left"], PLAYER_SCALE),
    "sit-right": [load_single_image(ANIMATION_PATHS["sit-right"], PLAYER_SCALE)],
    "sit-left": [load_single_image(ANIMATION_PATHS["sit-left"], PLAYER_SCALE)],
    "sit-center": [load_single_image(ANIMATION_PATHS["sit-center"], PLAYER_SCALE)],
    "sit-back": [load_single_image(ANIMATION_PATHS["sit-back"], PLAYER_SCALE)],
    "shield-right": [load_single_image(ANIMATION_PATHS["shield-right"], PLAYER_SCALE)],
    "shield-left": [load_single_image(ANIMATION_PATHS["shield-left"], PLAYER_SCALE)],
    "flip-right": [load_single_image(ANIMATION_PATHS["flip-right"], PLAYER_SCALE)],
    "flip-left": [load_single_image(ANIMATION_PATHS["flip-left"], PLAYER_SCALE)],
    "stealth": [load_single_image(ANIMATION_PATHS["stealth"], PLAYER_SCALE)],
}

# Carga diferida para animaciones más pesadas
lazy_animations = {}


def ensure_animation(name, loader):
    if name not in lazy_animations and name not in animations:
        lazy_animations[name] = loader()
        animations[name] = lazy_animations[name]
    return animations.get(name, [])


# Load health icon (larger, 0.25 instead of 0.15)
health_icon = load_single_image(HEALTH_ICON_PATH, 0.29)

def _preload_all_animations():
    import threading
    def _worker():
        for side in ["right", "left"]:
            animations[f"climb-{side}"] = load_gif_frames(ANIMATION_PATHS[f"climb-{side}"], PLAYER_SCALE)
            animations[f"wsh-{side}"] = load_gif_frames(ANIMATION_PATHS[f"wsh-{side}"], PLAYER_SCALE)
            animations[f"punch-{side}"] = load_png_sequence_from_dir(ANIMATION_PATHS[f"punch-{side}"], PLAYER_SCALE)
            animations[f"swing-{side}"] = load_png_sequence_from_dir(ANIMATION_PATHS[f"swing-{side}"], PLAYER_SCALE)
            animations[f"air-attack-{side}"] = load_specific_pngs(ANIMATION_PATHS[f"punch-{side}"], AIR_ATTACK_FILES, PLAYER_SCALE)
            for roman in K_ROMAN:
                animations[f"pch-{roman}-{side}"] = load_gif_frames(os.path.join(ANIMATION_PATHS[f"pch-{side}"], f"pch-{roman}.gif"), PLAYER_SCALE)
        animations["pch-right"] = load_png_sequence_from_dir(ANIMATION_PATHS["punch-right"], PLAYER_SCALE)
        animations["pch-left"] = load_png_sequence_from_dir(ANIMATION_PATHS["punch-left"], PLAYER_SCALE)
        print("All animations preloaded.")
    threading.Thread(target=_worker, daemon=True).start()

_preload_all_animations()

class Player:
    def __init__(self):
        self.x = screen_width // 2
        self.y = screen_height - 150
        self.width = 60
        self.height = 90
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = 4    # Velocidad base
        self.max_speed = 25    # Velocidad maxima (con tecla)
        self.current_speed = 4   # Velocidad actual (interpolada)
        self.acceleration = 0.8  # Suavidad de aceleracion
        self.gravity = 0.6
        self.jump_power = -30
        self.on_ground = False
        
        # Animation
        self.current_animation = "idle-right"
        self.frame_index = 0
        self.frame_delay = 4
        self.frame_counter = 0
        self.facing_right = True
        
        # Jump (no-loop jump animation)
        self.is_jumping = False
        self.jump_phase = None    # None | "descend"
        self.is_air_attacking = False
        
        # Landing animation (sit -> idle)
        self.is_sitting = False
        self.sit_timer = 0
        self.sit_duration = 4  # frames for sit animation (< 1s at 60fps)
        
        # Turn transition
        self.is_turning = False
        self.turn_timer = 0
        self.turn_duration = 8  # frames for entry animation
        
        # Punch attack — sequential order 0→1→2→...→8
        self.is_punching = False
        self.combo_step = 0
        self.combo_timer = 0
        self.combo_timeout = 45
        self.punch_display_timer = 0
        self.total_combo_frames = len(GROUND_COMBO)
        self.frame_data = None      # tupla de COMBO_FRAMES del frame actual
        self.charge_timer = 0
        self.was_charged = False
        self.input_buffer = 0
        self.shake_timer = 0
        
        # Combo GIF auto-play
        self.combo_gif_active = False
        self.combo_gif_frame = 0
        self.combo_gif_counter = 0
        self.combo_gif_speed = 2
        self.combo_gif_total = 0

        # K punch — ciclo pch-i → pch-v
        self.is_k_punch = False
        self.k_step = 0
        self.k_frame_counter = 0

        # Web-shooter
        self.is_web_shooting = False
        self.wsh_prev_animation = ""
        self.wsh_prev_frame = 0

        # Swing (pendulum)
        self.is_swinging = False
        self.swing_pivot_x = 0
        self.swing_pivot_y = 0
        self.swing_length = 500
        self.swing_angle = 0
        self.swing_angular_vel = 0
        self.swing_damping = 0.997
        self.swing_max_angle = 1.5
        self.swing_seq_pos = 0
        self.swing_pump = 0.02
        self.swing_input_override = False
        self.swing_wobble_timer = 0
        self.swing_launched = False
        self.swing_hop_timer = 0
        self.swing_hop_angular_vel = 0

        # Crouching (sit-left/sit-right held)
        self.is_crouching = False
        self.crouch_turning = False  # For sit-center/sit-back transition
        self.crouch_turn_timer = 0
        self.crouch_turn_duration = 6

        # Shield / Block
        self.is_blocking = False

        # Double jump / Somersault (turn-based: odd=normal, even=flip)
        self.is_somersaulting = False
        self.somersault_angle = 0
        self.jump_turn = 0
        self.space_was_held = False
        self.j_air_used = False

        # Stealth / Ceiling hang (automatic rising)
        self.is_stealth = False
        self.stealth_rising = False

        # Health
        self.max_health = 100
        self.health = 100
        
        # Ground Y (invisible floor position)
        self.ground_y = screen_height - 40
    
    def update(self, keys):
        # Horizontal movement
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        moving_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        moving_up = keys[pygame.K_UP]

        # Stealth mode: automatic ceiling rise, no manual controls
        if self.is_stealth:
            if self.stealth_rising:
                self.vel_y = -8
                self.y += self.vel_y
                self.vel_x = 0
            self.current_animation = "stealth"
            self.space_was_held = keys[pygame.K_SPACE]
            self.update_animation()
            return

        # Priority: if both pressed, keep current direction (stand still)
        if moving_right and moving_left:
            self.vel_x = 0
            # Keep idle/jump animation based on state
            if not self.is_turning and not self.is_sitting and not self.is_crouching:
                if not self.on_ground:
                    self.current_animation = "jump-right" if self.facing_right else "jump-left"
                else:
                    self.current_animation = "idle-right" if self.facing_right else "idle-left"
            # Don't return here to allow physics to continue
        
        # Shield active (toggle) — keep vel_x = 0 and force animation
        if self.is_blocking:
            self.vel_x = 0
            self.current_animation = "shield-right" if self.facing_right else "shield-left"
        
        # Handle crouch animation
        if self.is_crouching:
            # Crouch turn transition
            if self.crouch_turning:
                self.vel_x = 0
                self.crouch_turn_timer -= 1
                if self.crouch_turn_timer <= 0:
                    self.crouch_turning = False
                    # After transition, go to sit animation
                    self.current_animation = "sit-right" if self.facing_right else "sit-left"
                    self.frame_index = 0
            else:
                # Detect direction change while crouching (only if one direction is pressed)
                if moving_right and not moving_left and not self.facing_right:
                    # Turn left to right
                    self.crouch_turning = True
                    self.crouch_turn_timer = self.crouch_turn_duration
                    self.current_animation = "sit-back"
                    self.facing_right = True
                    self.frame_index = 0
                elif moving_left and not moving_right and self.facing_right:
                    # Turn right to left
                    self.crouch_turning = True
                    self.crouch_turn_timer = self.crouch_turn_duration
                    self.current_animation = "sit-center"
                    self.facing_right = False
                    self.frame_index = 0
                else:
                    # Horizontal movement while crouching (climb animation)
                    if moving_right and not moving_left and self.facing_right:
                        self.vel_x = 20
                        if self.current_animation != "climb-right":
                            self.current_animation = "climb-right"
                            self.frame_index = 0
                    elif moving_left and not moving_right and not self.facing_right:
                        self.vel_x = -20
                        if self.current_animation != "climb-left":
                            self.current_animation = "climb-left"
                            self.frame_index = 0
                    else:
                        self.vel_x = 0
                        self.current_animation = "sit-right" if self.facing_right else "sit-left"
        
        # Handle turn animation
        if self.is_turning:
            self.vel_x = 0
            self.turn_timer -= 1
            if self.turn_timer <= 0:
                self.is_turning = False
                # After turn, determine next animation
                if self.facing_right:
                    self.current_animation = "run-right" if moving_right else "idle-right"
                else:
                    self.current_animation = "run-left" if moving_left else "idle-left"
        
        # Down key to crouch (only on ground, not jumping)
        if moving_down and self.on_ground and not self.is_jumping and not self.is_crouching:
            self.is_crouching = True
            self.crouch_turning = False
            # Select animation based on current direction
            self.current_animation = "sit-right" if self.facing_right else "sit-left"
            self.frame_index = 0
        
        # Up key to uncrouch (only up arrow)
        moving_up = keys[pygame.K_UP]
        if self.is_crouching and moving_up:
            self.is_crouching = False
            self.crouch_turning = False
            self.current_animation = "idle-right" if self.facing_right else "idle-left"
            self.frame_index = 0
        
        # K punch — velocidad y re-aplicar animacion si fue pisada
        if self.is_k_punch:
            if moving_right and not moving_left:
                self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                self.vel_x = self.current_speed
            elif moving_left and not moving_right:
                self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                self.vel_x = -self.current_speed
            else:
                self.current_speed += (self.base_speed - self.current_speed) * self.acceleration
                self.vel_x = 0
            if not (self.current_animation.startswith("pch-") and (self.current_animation.endswith("-right") or self.current_animation.endswith("-left"))):
                roman = K_ROMAN[(self.k_step - 1) % 5]
                self.current_animation = f"pch-{roman}-right" if self.facing_right else f"pch-{roman}-left"
                self.frame_index = 0
        
        # Normal movement
        if not self.is_crouching and not self.is_turning and not self.is_sitting and not self.is_blocking and not self.is_k_punch:
            if self.is_punching:
                if self.frame_data and self.frame_data[3]:
                    self.vel_x = self.frame_data[3] if self.facing_right else -self.frame_data[3]
                elif moving_right:
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = self.current_speed
                elif moving_left:
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = -self.current_speed
                else:
                    self.current_speed += (self.base_speed - self.current_speed) * self.acceleration
                    self.vel_x = 0
            elif not self.is_jumping and not self.is_sitting and self.on_ground:
                if moving_right and not moving_left:
                    # Accelerate toward max speed
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = self.current_speed
                    if not self.facing_right:
                        # Turn left to right
                        self.is_turning = True
                        self.turn_timer = self.turn_duration
                        self.current_animation = "entry-right"
                        self.facing_right = True
                    else:
                        self.current_animation = "run-right"
                elif moving_left and not moving_right:
                    # Accelerate toward max speed
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = -self.current_speed
                    if self.facing_right:
                        # Turn right to left
                        self.is_turning = True
                        self.turn_timer = self.turn_duration
                        self.current_animation = "entry-left"
                        self.facing_right = False
                    else:
                        self.current_animation = "run-left"
                else:
                    # No movement - decelerate toward base speed
                    self.current_speed += (self.base_speed - self.current_speed) * self.acceleration
                    self.vel_x = 0
                    self.current_animation = "idle-right" if self.facing_right else "idle-left"
            elif self.is_air_attacking:
                self.vel_x = 0
            else:
                # In air: update velocity and detect direction change
                if moving_right and not moving_left:
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = self.current_speed
                    if not self.facing_right:
                        self.facing_right = True
                        self.current_animation = "jump-right"
                        self.frame_index = 0
                elif moving_left and not moving_right:
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = -self.current_speed
                    if self.facing_right:
                        self.facing_right = False
                        self.current_animation = "jump-left"
                        self.frame_index = 0
                else:
                    if not self.swing_launched:
                        self.vel_x = 0
        
        # Jump (SPACE) — turn-based: odd turn = normal jump, even turn = flip somersault
        space_held = keys[pygame.K_SPACE]
        space_just_pressed = space_held and not self.space_was_held
        self.space_was_held = space_held
        if space_just_pressed and self.on_ground and not self.is_punching and not self.is_k_punch and not self.is_swinging and not self.is_blocking:
            if self.is_sitting:
                self.is_sitting = False
                self.sit_timer = 0
            self.jump_turn += 1
            self.vel_y = self.jump_power
            self.on_ground = False
            self.is_jumping = True
            self.jump_phase = "descend"
            self.frame_index = 0
            if self.jump_turn % 2 == 1:
                # Odd turn: normal jump animation
                self.is_somersaulting = False
                self.current_animation = "jump-right" if self.facing_right else "jump-left"
            else:
                # Even turn: flip somersault
                self.is_somersaulting = True
                self.somersault_angle = 0
                self.current_animation = "jump-right" if self.facing_right else "jump-left"
        
        # Swing physics (pendulum) — replaces gravity and normal position
        if self.is_swinging:
            self._update_swing(keys)
        else:
            # Apply gravity
            self.vel_y += self.gravity

            # Fast fall during air attack
            if self.is_air_attacking:
                self.vel_y = max(self.vel_y, 18)
                self.vel_x = 0

            # Update position
            self.x += self.vel_x
            self.y += self.vel_y
        
        # Invisible floor collision
        if self.y + self.height > self.ground_y:
            self.y = self.ground_y - self.height
            self.vel_y = 0
            was_in_air = not self.on_ground
            self.on_ground = True
            self.j_air_used = False
            if was_in_air and self.is_swinging:
                self.is_swinging = False
                self.swing_launched = False
                self.swing_hop_timer = 0
                vx = self.swing_length * math.cos(self.swing_angle) * self.swing_angular_vel
                self.vel_x = vx * 0.3
                self.current_animation = "idle-right" if self.facing_right else "idle-left"
                self.frame_index = 0
            if was_in_air and self.is_air_attacking:
                self.is_air_attacking = False
                self.current_animation = "idle-right" if self.facing_right else "idle-left"
                self.frame_index = 0
            if was_in_air and self.is_somersaulting:
                self.is_somersaulting = False
                self.somersault_angle = 0
            if was_in_air and self.is_punching:
                self.combo_timer = self.combo_timeout
            elif was_in_air and 0 < self.combo_step < self.total_combo_frames:
                self.combo_timer = self.combo_timeout
                if self.on_ground and not self.is_sitting:
                    self.current_animation = "idle-right" if self.facing_right else "idle-left"
                    self.frame_index = 0
            if was_in_air and self.is_jumping:
                self.is_jumping = False
                self.jump_phase = None
                self.is_air_attacking = False
                self.swing_launched = False
                self.swing_hop_timer = 0
                if not self.is_blocking:
                    moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
                    moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
                    
                    # If running, go directly to run, otherwise sit -> idle
                    if moving_right:
                        self.current_animation = "run-right"
                        self.facing_right = True
                    elif moving_left:
                        self.current_animation = "run-left"
                        self.facing_right = False
                    else:
                        # Not running, start sit -> idle animation
                        self.is_sitting = True
                        self.sit_timer = self.sit_duration
                        self.current_animation = "sit-right" if self.facing_right else "sit-left"
                        self.frame_index = 0
        
        # Limitar a pantalla
        if self.x < 0:
            self.x = 0
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
        
        # Carga durante golpe
        self.handle_charge(keys)
        # Input buffer — si hay F pendiente, avanza al siguiente frame
        if self.input_buffer > 0:
            self.input_buffer -= 1
            if self.input_buffer == 0 and self.is_punching and self.combo_step < self.total_combo_frames:
                self.start_combo_frame(self.combo_step)
                self.combo_step += 1
        
        # Combo GIF auto-advance
        if self.is_punching and self.combo_gif_active:
            self.combo_gif_counter += 1
            if self.combo_gif_counter >= self.combo_gif_speed:
                self.combo_gif_counter = 0
                self.combo_gif_frame += 1
                if self.combo_gif_frame >= self.combo_gif_total:
                    self.combo_gif_active = False
                    if self.combo_step < self.total_combo_frames:
                        self.input_buffer = 1
                else:
                    self.frame_index = self.combo_gif_frame

        # Punch display timer
        if self.is_punching:
            self.punch_display_timer -= 1
            if self.punch_display_timer <= 0:
                self.is_punching = False
                if self.was_charged and self.frame_data:
                    charged = self.frame_data[5]
                    if charged:
                        self.vel_y = charged
                        self.on_ground = False
                if self.on_ground:
                    self.current_animation = "idle-right" if self.facing_right else "idle-left"
                else:
                    self.current_animation = "jump-right" if self.facing_right else "jump-left"
                self.frame_index = 0
        
        # Decaimiento del shake
        if self.shake_timer > 0:
            self.shake_timer -= 1

        # Auto re-swing after a hop
        if self.swing_hop_timer > 0:
            self.swing_hop_timer -= 1
            if self.swing_hop_timer == 0 and not self.is_swinging and not self.on_ground:
                self.is_swinging = True
                center_y = self.y + self.height // 2
                self.swing_pivot_x = self.x + self.width // 2
                self.swing_pivot_y = center_y - self.swing_length
                self.swing_angle = 0
                self.swing_angular_vel = self.swing_hop_angular_vel
                self.current_animation = "swing-right" if self.facing_right else "swing-left"
                self.frame_index = SWING_SEQUENCE[self.swing_seq_pos]
                self.swing_launched = False

        # Temporizador de combo (memoria entre golpes)
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_step = 0

        # Somersault: continuous spin while double-jumping (loops until landing)
        if self.is_somersaulting:
            self.somersault_angle = (self.somersault_angle + 9) % 360
        
        # Update animation
        self.update_animation()
    
    def update_animation(self):
        # Web-shoot: handle based on flag
        if self.is_web_shooting:
            if self.current_animation not in ["wsh-right", "wsh-left"]:
                if self.is_punching:
                    # Punch overrides wsh — cancel web-shoot
                    self.is_web_shooting = False
                else:
                    # Re-apply wsh animation (movement code may have overridden it)
                    self.current_animation = "wsh-right" if self.facing_right else "wsh-left"
            if self.is_web_shooting:
                if self.current_animation in ["wsh-right", "wsh-left"] and not animations.get(self.current_animation):
                    animations[self.current_animation] = load_gif_frames(ANIMATION_PATHS[self.current_animation], PLAYER_SCALE)
                anim_frames = animations.get(self.current_animation, [])
                if self.frame_index < len(anim_frames) - 1:
                    self.frame_index += 1
                    return
                else:
                    self.is_web_shooting = False
                    if self.on_ground and not self.is_jumping and not self.is_sitting:
                        self.current_animation = "idle-right" if self.facing_right else "idle-left"
                    elif self.is_jumping or not self.on_ground:
                        self.current_animation = "jump-right" if self.facing_right else "jump-left"
                    self.frame_index = 0
                    return
        
        # Somersault animation is handled entirely by draw() with rotation — skip update
        if self.is_somersaulting:
            return
        
        # K punch auto-play (2 ticks per frame = 2x speed)
        if self.is_k_punch and (self.current_animation.startswith("pch-") and (self.current_animation.endswith("-right") or self.current_animation.endswith("-left"))):
            if not animations.get(self.current_animation):
                side = "right" if self.facing_right else "left"
                roman = self.current_animation.split("-")[1]
                animations[self.current_animation] = load_gif_frames(os.path.join(ANIMATION_PATHS[f"pch-{side}"], f"pch-{roman}.gif"), PLAYER_SCALE)
            anim_frames = animations.get(self.current_animation, [])
            if not anim_frames:
                self.is_k_punch = False
                return
            self.k_frame_counter += 1
            speed = 1 if "pch-ii-" in self.current_animation else 2
            if self.k_frame_counter >= speed:
                self.k_frame_counter = 0
                if self.frame_index < len(anim_frames) - 1:
                    self.frame_index += 1
                else:
                    self.is_k_punch = False
                    if self.on_ground and not self.is_jumping and not self.is_sitting:
                        self.current_animation = "idle-right" if self.facing_right else "idle-left"
                    elif self.is_jumping or not self.on_ground:
                        self.current_animation = "jump-right" if self.facing_right else "jump-left"
                    self.frame_index = 0
            return
        
        if self.current_animation in ["climb-right", "climb-left", "punch-right", "punch-left", "swing-right", "swing-left", "air-attack-right", "air-attack-left", "wsh-right", "wsh-left"] and not animations.get(self.current_animation):
            if self.current_animation in ["climb-right", "climb-left"]:
                animations[self.current_animation] = load_gif_frames(ANIMATION_PATHS[self.current_animation], PLAYER_SCALE)
            elif self.current_animation in ["punch-right", "punch-left"]:
                animations[self.current_animation] = load_png_sequence_from_dir(ANIMATION_PATHS[self.current_animation], PLAYER_SCALE, blur_radius=1.5)
            elif self.current_animation in ["swing-right", "swing-left"]:
                animations[self.current_animation] = load_png_sequence_from_dir(ANIMATION_PATHS[self.current_animation], PLAYER_SCALE, blur_radius=1.5)
            elif self.current_animation in ["air-attack-right", "air-attack-left"]:
                side = "right" if self.current_animation.endswith("right") else "left"
                animations[self.current_animation] = load_specific_pngs(ANIMATION_PATHS[f"punch-{side}"], AIR_ATTACK_FILES, PLAYER_SCALE, blur_radius=1.5)
            elif self.current_animation in ["wsh-right", "wsh-left"]:
                animations[self.current_animation] = load_gif_frames(ANIMATION_PATHS[self.current_animation], PLAYER_SCALE)

        anim_frames = animations.get(self.current_animation, [])
        if not anim_frames:
            return
        
        # Punch is handled by update() (combo GIF auto-advance or KEYDOWN) — don't touch frame_index
        if self.is_punching:
            return
        
        self.frame_counter += 1
        delay = 2 if self.current_animation in ("run-right", "run-left") else self.frame_delay
        if self.frame_counter >= delay:
            self.frame_counter = 0
            
            # Handle crouching animation (sit-center/sit-back transitions)
            if self.is_crouching:
                # Solo manejar transiciones de volteo en crouch
                if self.crouch_turning:
                    self.crouch_turn_timer -= 1
                    if self.crouch_turn_timer <= 0:
                        self.crouch_turning = False
                        # After transition, go to sit animation
                        self.current_animation = "sit-right" if self.facing_right else "sit-left"
                        self.frame_index = 0
                    return
                # Climb animations loop normally (advance frames)
                if self.current_animation not in ["climb-right", "climb-left"]:
                    return
            
            # Handle sit animation (sit -> idle)
            if self.is_sitting:
                self.sit_timer -= 1
                if self.sit_timer <= 0:
                    self.is_sitting = False
                    # After sit, go to idle
                    self.current_animation = "idle-right" if self.facing_right else "idle-left"
                    self.frame_index = 0
                # Sit animations are static (single frame)
                return

            # Jump animation (original GIF: falling)
            if self.current_animation in ["jump-right", "jump-left"]:
                if self.frame_index < len(anim_frames) - 1:
                    self.frame_index += 1
                return

            # Air attack animation (single frame, no advance)
            if self.current_animation in ["air-attack-right", "air-attack-left"]:
                return

            # Swing animation (controlled by pendulum physics)
            if self.current_animation in ["swing-right", "swing-left"]:
                return

            # Shield animation (static, single frame)
            if self.current_animation in ["shield-right", "shield-left"]:
                return

            # Stealth animation (static, single frame)
            if self.current_animation == "stealth":
                return

            # Other animations loop normally
            self.frame_index = (self.frame_index + 1) % len(anim_frames)
    
    def _apply_frame_data(self, combo_idx):
        self.frame_data = COMBO_FRAMES[combo_idx]
        dur = self.frame_data[1]
        boost_y = self.frame_data[2]
        burst_x = self.frame_data[3]
        self.frame_index = COMBO_VISUAL_MAP[combo_idx]
        self.frame_counter = 0
        self.punch_display_timer = dur
        self.combo_timer = self.combo_timeout
        self.charge_timer = 0
        self.was_charged = False
        self.input_buffer = 0
        if boost_y:
            self.vel_y = boost_y
            self.on_ground = False
            self.shake_timer = 6
        if burst_x:
            self.vel_x = burst_x if self.facing_right else -burst_x
            self.shake_timer = max(self.shake_timer, 4)

    def _update_swing(self, keys):
        # Gentle pump with movement keys
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.swing_angular_vel += self.swing_pump
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.swing_angular_vel -= self.swing_pump

        # Pendulum equation: α = -(2g / L) * sin(θ) - damping
        angular_acc = -(self.gravity * 2 / self.swing_length) * math.sin(self.swing_angle)
        self.swing_angular_vel += angular_acc
        self.swing_angular_vel *= self.swing_damping
        self.swing_angle += self.swing_angular_vel

        # Max angle limit
        if abs(self.swing_angle) > self.swing_max_angle:
            self.swing_angle = math.copysign(self.swing_max_angle, self.swing_angle)
            self.swing_angular_vel *= -0.3

        # Position from pendulum
        cx = self.swing_pivot_x + self.swing_length * math.sin(self.swing_angle)
        cy = self.swing_pivot_y + self.swing_length * math.cos(self.swing_angle)
        self.x = cx - self.width // 2
        self.y = cy - self.height // 2

        # One frame per step in sequence, with wobble
        self.swing_wobble_timer += 1

        # Lateral movement: gentle pump + direction change only with keys
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.swing_input_override = moving_left or moving_right
        if moving_left and not moving_right:
            self.facing_right = False
        elif moving_right and not moving_left:
            self.facing_right = True
        self.frame_index = SWING_SEQUENCE[self.swing_seq_pos]
        self.current_animation = "swing-right" if self.facing_right else "swing-left"

    def start_combo_frame(self, step):
        cidx = GROUND_COMBO[step]
        name = COMBO_FRAMES[cidx][0]
        if name.endswith("-gif"):
            gif_n = cidx - 8  # 9→1, 10→2, ..., 13→5
            side = "right" if self.facing_right else "left"
            roman = K_ROMAN[gif_n - 1]
            gif_name = f"pch-{roman}-{side}"
            gif_frames = animations.get(gif_name, [])
            if not gif_frames:
                self.combo_gif_active = False
                return
            self.combo_gif_active = True
            self.combo_gif_frame = 0
            self.combo_gif_counter = 0
            self.combo_gif_speed = COMBO_FRAMES[cidx][1]
            self.combo_gif_total = len(gif_frames)
            self.current_animation = gif_name
            self.frame_index = 0
            self.frame_data = COMBO_FRAMES[cidx]
            self.punch_display_timer = len(gif_frames) * self.combo_gif_speed + 10
            self.combo_timer = self.combo_timeout
            self.input_buffer = 0
        else:
            self._apply_frame_data(cidx)

    def start_special_frame(self, combo_idx):
        """Activa un frame específico por índice de COMBO_FRAMES (fuera del patrón)."""
        self._apply_frame_data(combo_idx)

    def handle_charge(self, keys):
        if not self.is_punching:
            self.charge_timer = 0
            self.was_charged = False
            return
        chargeable = self.frame_data[4] if self.frame_data else False
        if not chargeable:
            self.charge_timer = 0
            return
        if keys[pygame.K_l]:
            self.charge_timer += 1
            if self.charge_timer >= 12:
                self.punch_display_timer = max(self.punch_display_timer, 4)
        else:
            if self.charge_timer >= 12:
                self.was_charged = True
            self.charge_timer = 0

    def teleport_from_stealth(self):
        """Sale del sigilo: teletransporta el eje X según facing y cae desde arriba."""
        self.is_stealth = False
        self.stealth_rising = False
        offset = random.randint(1000, 1500)
        if self.facing_right:
            self.x += offset
        else:
            self.x -= offset
        self.x = max(0, min(screen_width - self.width, self.x))
        self.y = -self.height * 2
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.is_jumping = False
        self.jump_phase = "descend"
        self.current_animation = "jump-right" if self.facing_right else "jump-left"
        self.frame_index = 0

    def draw(self, surface, shake_ox=0, shake_oy=0, cam_y=0):
        # Stealth: display hf.png at ceiling position
        if self.is_stealth:
            base = "stealth"
            base_frames = animations.get(base, [])
            if not base_frames:
                animations[base] = [load_single_image(ANIMATION_PATHS["stealth"], PLAYER_SCALE)]
                base_frames = animations[base]
            if not base_frames:
                return
            frame = base_frames[0]
            frame_rect = frame.get_rect()
            frame_rect.centerx = int(self.x + self.width // 2) + shake_ox
            frame_rect.centery = int(self.y + self.height // 2 + cam_y) + shake_oy
            surface.blit(frame, frame_rect)
            return

        # Somersault: use flip frame with rotation
        if self.is_somersaulting:
            base = "flip-right" if self.facing_right else "flip-left"
            base_frames = animations.get(base, [])
            if not base_frames:
                animations[base] = [load_single_image(ANIMATION_PATHS[base], PLAYER_SCALE)]
                base_frames = animations[base]
            if not base_frames:
                return
            frame = base_frames[self.frame_index % len(base_frames)]
            frame = pygame.transform.rotate(frame, self.somersault_angle)
        else:
            anim_frames = animations.get(self.current_animation, [])
            if not anim_frames or len(anim_frames) == 0:
                return
            frame = anim_frames[self.frame_index % len(anim_frames)]
        # Gentle wobble during swing
        wobble_shake = (0, 0)
        if self.is_swinging and self.current_animation in ["swing-right", "swing-left"]:
            t = self.swing_wobble_timer * 0.15
            wx = int(math.sin(t * 1.3) * 2)
            wy = int(math.sin(t * 0.9 + 1) * 1.5)
            wobble_shake = (wx, wy)
        frame_rect = frame.get_rect()
        frame_rect.centerx = int(self.x + self.width // 2) + shake_ox + wobble_shake[0]
        frame_rect.bottom = int(self.y + self.height + cam_y) + shake_oy + wobble_shake[1]
        surface.blit(frame, frame_rect)
    
    def draw_health(self, surface):
        # Health bar config
        bar_width = 320
        bar_height = 20
        
        # Icon on left, bar beside it centered vertically
        if health_icon:
            icon_x = 10
            icon_y = 15
            surface.blit(health_icon, (icon_x, icon_y))
            # Bar beside icon, centered vertically
            icon_center_y = icon_y + health_icon.get_height() // 2
            bar_x = icon_x + health_icon.get_width()  # Right next to icon
            bar_y = icon_center_y - bar_height // 2  # Vertically centered with icon
        else:
            bar_x = 60
            bar_y = 25
        
        # Bar background (black)
        pygame.draw.rect(surface, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        
        # Health bar - color by percentage
        health_width = int((self.health / self.max_health) * bar_width)
        health_percent = self.health / self.max_health
        
        if health_percent >= 0.5:
            bar_color = ORANGE
        else:
            bar_color = RED  
        
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, health_width, bar_height))
        
        # SPIDER-MAN text with dynamic contrast effect
        font = pygame.font.SysFont("arial", 16, bold=True)
        text_str = "SPIDER-MAN"
        
        # Render two versions of the text
        text_white = font.render(text_str, True, WHITE)
        text_black = font.render(text_str, True, BLACK)
        
        text_x = bar_x + bar_width // 2 - text_white.get_width() // 2
        text_y = bar_y + bar_height // 2 - text_white.get_height() // 2
        
        # A. Draw WHITE version first (visible where there's no health bar)
        surface.blit(text_white, (text_x, text_y))
        
        # B. Draw BLACK version clipped inside the current health bar area
        current_bar_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
        surface.set_clip(current_bar_rect)
        surface.blit(text_black, (text_x, text_y))
        
        # C. Reset clip
        surface.set_clip(None)

# Instantiate player
player = Player()

# Vertical camera
cam_y = 0

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Teclas para ajustar vida (testing)
            if event.key == pygame.K_1:
                player.health = max(0, player.health - 10)
            if event.key == pygame.K_2:
                player.health = min(player.max_health, player.health + 10)
            # Golpe (F) — secuencia ordenada 0→1→2→...→8
            if event.key == pygame.K_l and not player.is_crouching and not player.is_swinging and not player.is_blocking and not player.is_stealth and not player.is_k_punch and not player.is_web_shooting and not player.is_air_attacking:
                if player.is_punching:
                    if player.combo_step >= player.total_combo_frames:
                        continue
                    cidx = GROUND_COMBO[player.combo_step]
                    _, _, _, _, chargeable, _ = COMBO_FRAMES[cidx]
                    if chargeable and player.charge_timer > 0:
                        continue
                    cur_dur = player.frame_data[1] if player.frame_data else 0
                    if player.punch_display_timer > cur_dur // 3:
                        player.input_buffer = 3
                        continue
                elif player.on_ground and not player.is_jumping:
                    if player.combo_timer <= 0 or player.combo_step >= player.total_combo_frames:
                        player.combo_step = 0
                    player.is_punching = True
                    player.current_animation = "punch-right" if player.facing_right else "punch-left"
                else:
                    # L en el aire → p-t-ii air attack
                    player.is_air_attacking = True
                    player.current_animation = "air-attack-right" if player.facing_right else "air-attack-left"
                    player.frame_index = 0
                    continue
                player.start_combo_frame(player.combo_step)
                player.combo_step += 1
            
            # K: ciclo pch-i → pch-v (GIF completo auto-play)
            if event.key == pygame.K_k and not player.is_crouching and not player.is_swinging and not player.is_blocking and not player.is_stealth and not player.is_punching and not player.is_k_punch and not player.is_web_shooting and not player.is_air_attacking:
                if player.on_ground:
                    player.is_k_punch = True
                    player.frame_index = 0
                    player.k_frame_counter = 0
                    roman = K_ROMAN[player.k_step]
                    player.current_animation = f"pch-{roman}-right" if player.facing_right else f"pch-{roman}-left"
                    player.k_step = (player.k_step + 1) % 5
            
            # G: w-i (golpe pesado especial)
            if event.key == pygame.K_p and player.on_ground and not player.is_crouching and not player.is_swinging and not player.is_blocking and not player.is_stealth and not player.is_k_punch and not player.is_web_shooting and not player.is_air_attacking and player.combo_step < player.total_combo_frames:
                if not player.is_punching:
                    player.is_punching = True
                    player.current_animation = "punch-right" if player.facing_right else "punch-left"
                player.start_special_frame(8)
                player.combo_step += 1

            # R: Web-shooter
            if event.key == pygame.K_o and player.on_ground and not player.is_punching and not player.is_swinging and not player.is_crouching and not player.is_web_shooting and not player.is_blocking and not player.is_stealth and not player.is_k_punch and not player.is_air_attacking:
                player.is_web_shooting = True
                player.frame_index = 0
                player.current_animation = "wsh-right" if player.facing_right else "wsh-left"

            # H: Stealth — automatic ceiling rise + teleport (no revert)
            if event.key == pygame.K_h and player.on_ground and not player.is_stealth and not player.is_punching and not player.is_k_punch and not player.is_swinging and not player.is_web_shooting and not player.is_crouching and not player.is_blocking and not player.is_turning and not player.is_sitting and not player.is_air_attacking and not player.is_somersaulting:
                    # Activate stealth rising
                    player.is_stealth = True
                    player.stealth_rising = True
                    player.y -= 70
                    player.vel_x = 0
                    player.vel_y = 0
                    player.current_animation = "stealth"
                    player.frame_index = 0

            # C: Shield toggle
            if event.key == pygame.K_m:
                if player.is_blocking:
                    player.is_blocking = False
                    if player.on_ground:
                        player.current_animation = "idle-right" if player.facing_right else "idle-left"
                    else:
                        player.current_animation = "jump-right" if player.facing_right else "jump-left"
                elif not player.is_punching and not player.is_k_punch and not player.is_swinging and not player.is_web_shooting and not player.is_crouching and not player.is_sitting and not player.is_turning and not player.is_stealth:
                    player.is_blocking = True
                    player.vel_x = 0
                    player.current_animation = "shield-right" if player.facing_right else "shield-left"
                    player.frame_index = 0

            # E: Swing — advance frame; if already swinging, hop + re-swing
            if event.key == pygame.K_i and not player.is_crouching and not player.is_punching and not player.is_k_punch and not player.is_blocking and not player.is_stealth and not player.is_web_shooting and not player.is_air_attacking and player.swing_hop_timer == 0:
                player.swing_seq_pos = (player.swing_seq_pos + 1) % len(SWING_SEQUENCE)
                frame_idx = SWING_SEQUENCE[player.swing_seq_pos]
                player.frame_index = frame_idx
                player.swing_wobble_timer = 0
                if player.is_swinging:
                    # Hop: lanzar momentum angular como velocidad lineal
                    vx = player.swing_length * math.cos(player.swing_angle) * player.swing_angular_vel
                    vy = -player.swing_length * math.sin(player.swing_angle) * player.swing_angular_vel
                    player.vel_x = vx
                    player.vel_y = vy
                    player.is_swinging = False
                    player.on_ground = False
                    player.is_jumping = True
                    player.jump_phase = "descend"
                    player.current_animation = "jump-right" if player.facing_right else "jump-left"
                    player.swing_launched = True
                    # Guardar velocidad angular para re-swing
                    dir_sign = 1 if player.facing_right else -1
                    angular_boost = (vx * dir_sign + abs(vy) * 0.3) / player.swing_length * 2.0
                    player.swing_hop_angular_vel = max(0.06, abs(angular_boost)) * dir_sign
                    player.swing_hop_timer = 12
                else:
                    player_center_y = player.y + player.height // 2
                    player.is_swinging = True
                    player.is_air_attacking = False
                    player.is_somersaulting = False
                    player.somersault_angle = 0
                    player.swing_pivot_x = player.x + player.width // 2
                    player.swing_pivot_y = player_center_y - player.swing_length
                    player.swing_angle = 0
                    player.swing_angular_vel = 0.12 if player.facing_right else -0.12
                    player.vel_x = 0
                    player.vel_y = 0
                    player.on_ground = False
                    player.is_jumping = False
                    player.jump_phase = None

            # J: reservado para uso futuro

            # SPACE durante balanceo → soltar
            if event.key == pygame.K_SPACE and player.is_swinging and not player.is_stealth:
                player.is_swinging = False
                vx = player.swing_length * math.cos(player.swing_angle) * player.swing_angular_vel
                vy = -player.swing_length * math.sin(player.swing_angle) * player.swing_angular_vel
                player.vel_x = vx
                player.vel_y = vy
                player.on_ground = False
                player.is_jumping = True
                player.jump_phase = "descend"
                player.current_animation = "jump-right" if player.facing_right else "jump-left"
                player.frame_index = 0
    
    # Obtener teclas presionadas
    keys = pygame.key.get_pressed()
    
    # Update player
    player.update(keys)
    
    # Vertical camera: 100% follow (paused during stealth rising)
    if not (player.is_stealth and player.stealth_rising):
        player_center_y = player.y + player.height // 2
        target_cam_y = screen_height * 0.38 - player_center_y
        if target_cam_y > cam_y:
            cam_y += (target_cam_y - cam_y) * 0.25  # fast ascent
        else:
            cam_y += (target_cam_y - cam_y) * 0.12  # smooth descent
        # Limit: ground never moves above 85% of screen
        cam_y = max(cam_y, -(player.ground_y - screen_height * 0.85))

    # Stealth rising off-screen → teleport
    if player.is_stealth and player.stealth_rising:
        screen_top = player.y + cam_y
        if screen_top + player.height < 0:
            player.teleport_from_stealth()

    # Screen shake
    shake_ox, shake_oy = 0, 0
    if player.shake_timer > 0:
        intensity = max(1, player.shake_timer // 2)
        tick = pygame.time.get_ticks()
        rng = intensity * 2 + 1
        shake_ox = (tick % rng) - intensity
        shake_oy = ((tick + 997) % rng) - intensity
    
    # Dibujar
    screen.fill(RED)
    
    pygame.draw.line(screen, WHITE, (0, player.ground_y + cam_y), (screen_width, player.ground_y + cam_y), 2)
    
    player.draw(screen, shake_ox, shake_oy, cam_y)
    player.draw_health(screen)
    
    # Instrucciones
    font_small = pygame.font.SysFont("arial", 16)
    instructions = [
        "[←→] or [A][D]  Move",
        "[SPACE]  Jump / Release swing",
        "[L]  Combo (suelo)  |  [L] en aire = Air attack",
        "[K]  PCH combo (suelo)  |  [P]  w-i (heavy)",
        "[I]  Swing  |  [O]  Web-shooter  |  [M]  Shield",
        "[H]  Stealth  |  [ESC]  Exit",
        "[1]  Damage  |  [2]  Heal"
    ]
    for i, text in enumerate(instructions):
        surf = font_small.render(text, True, WHITE)
        screen.blit(surf, (10, screen_height - 100 + i * 20))
    
    # HUD de combate
    debug_font = pygame.font.SysFont("arial", 14)
    if player.is_punching:
        cur = player.combo_step - 1
        if 0 <= cur < len(GROUND_COMBO):
            cidx = GROUND_COMBO[cur]
            name, _, boost_y, burst_x, chargeable, _ = COMBO_FRAMES[cidx]
            parts = [f"[{name}]"]
            if boost_y:
                parts.append("LAUNCH")
            if burst_x:
                parts.append("BURST")
            if chargeable and player.charge_timer > 0:
                pct = min(player.charge_timer / 12 * 100, 100)
                parts.append(f"CHARGE {pct:.0f}%")
            tag = " | ".join(parts)
        else:
            tag = "-"
    else:
        tag = "-"
    swing_tag = ""
    if player.is_swinging:
        ang_deg = math.degrees(player.swing_angle)
        swing_tag = f" | SWING θ={ang_deg:.0f}° ω={player.swing_angular_vel:.3f}"
    hud_text = f"{tag} | Step {player.combo_step}/{len(GROUND_COMBO)} | VelY: {player.vel_y:.1f}{swing_tag}"
    hud_surf = debug_font.render(hud_text, True, WHITE)
    screen.blit(hud_surf, (10, screen_height - 30))
    
    # Jump turn counter
    turn_label = f"Jump turn: {player.jump_turn}"
    turn_surf = debug_font.render(turn_label, True, WHITE)
    screen.blit(turn_surf, (10, screen_height - 50))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
