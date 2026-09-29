"""NEXT30: a 15 second voxel stop-motion. My next thirty years, 2026 -> 2056.

    python film.py --frame 20              # one preview frame -> out/preview_0020.png
    python film.py --frames 0,40,80        # several previews
    python film.py --all                   # every frame, then out/next30.mp4 (+ gif)

One diorama on one plinth, rebuilt block by block every few years.
"""
import argparse
import math
import os
import subprocess
import time

import numpy as np
from PIL import Image, ImageDraw

import render as R
from props import (P, M, FL, CX, CZ, DESK, plinth, terrain_wood, terrain_tiles, terrain_grass,
                   grass_tufts, person, spark, spark_light, cat, desk, chair, laptop, mug,
                   potted_plant, bookshelf, floor_lamp, cloud, lab_bench, monitor, microscope,
                   test_tubes, flask, dna, pedestal, tree, flowers, turbine, pond, watering_can,
                   bird, rocket_sprite, launch_pad, tower, flame, smoke_puff, park_bench,
                   lamp_post, telescope, stone_path, pixel_heart)
from vox import Vox, GX, GY, GZ, WORLD_HASH, text_bitmap

FPS = 12
SCENE_LEN = 36          # 3 seconds per era
TR = 6                  # frames spent rebuilding the diorama at the start of an era
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out')

hx = R.hexcol


def ease(i, a, b):
    return float(np.clip((i - a) / float(b - a), 0.0, 1.0))


def bob(i, amp=1):
    return (0, 0, amp, amp)[(i // 2) % 4]


# ---------------------------------------------------------------------------
# 2026: hello, world

def scene_desk(v, i):
    terrain_wood(v)
    bookshelf(v)
    floor_lamp(v, 58, 13)
    potted_plant(v, 57, FL, 55, size=1.5)
    desk(v)
    chair(v, 30, 28)
    laptop(v, 30, 35)
    mug(v, 26, 37, i)
    potted_plant(v, 23, DESK + 1, 41, size=0.7)
    v.stamp(cat(i), 12, FL, 45)

    lights = [(34.0, 24.5, 39.0, 0.35, 0.55, 0.8, 5.0, 0.8)]
    if i < 16:
        arms, look = ('type', 'type'), (0, 0)
    elif i < 20:
        arms, look = ('forward', 'forward'), (1, 1)
    else:
        arms, look = ('forward', 'wave' if (i // 2) % 2 == 0 else 'wave2'), (1, 1)
    v.stamp(person('sit', top='hoodie', hair='hair_dark', arms=arms, tap=i % 2, look=look,
                   blink=(i == 31)), 30, FL, 28)

    path = {12: (0, 30, 24, 39), 13: (1, 30, 26, 39), 14: (2, 30, 28, 39), 15: (2, 31, 31, 40),
            16: (2, 34, 31, 40), 17: (2, 37, 30, 41), 18: (2, 39, 29, 41)}
    if i >= 12:
        size, x, y, z = path.get(i, (2, 40, 28 + bob(i), 41))
        sp_look = (0, 1) if i < 16 else (-1, 0)
        v.stamp(spark(size, look=sp_look, blink=(i == 26), twinkle=i // 2), x, y, z)
        lights.append(spark_light(x, y, z, 0.25 + 0.2 * min(size, 2), 7.0))
    return {'lights': lights}


# ---------------------------------------------------------------------------
# 2034: helping cure disease

def scene_lab(v, i):
    terrain_tiles(v)
    lab_bench(v)
    monitor(v, i)
    microscope(v, 33, 13)
    test_tubes(v, 36, 16, i)
    flask(v, 14, 16, i)
    pedestal(v, 47, 42)
    g = ease(i, 7, 28)
    h = int(round(30 * g))
    dna(v, 47, 42, FL + 2, h, phase=i * 0.3, grow_top_sparkle=(i >= 28), t=i)
    lights = [(47.0, FL + 3.0, 42.0, 0.25, 0.75, 0.85, 6.0, 1.0)]

    top = FL + 2 + h
    sy = max(FL + 3, top - 5) + bob(i)
    v.stamp(spark(2, look=(-1, 0) if i < 28 else (0, 0), blink=(i == 33), twinkle=i // 2), 54, sy, 40)
    lights.append(spark_light(54, sy, 40, 0.45, 7.0))

    if i < 28:
        arms = ('down', 'forward')
    else:
        arms = ('up', 'up') if (i // 2) % 2 == 0 else ('wave', 'wave')
    v.stamp(person('stand', top='labcoat', collar='hoodie', hair='hair_dark', goggles=True,
                   look=(1, 1), arms=arms, blink=(i == 21)), 23, FL, 32)
    return {'lights': lights}


# ---------------------------------------------------------------------------
# 2041: helping forests grow back

def scene_forest(v, i):
    terrain_grass(v)
    pond(v, 44, 44, 60, 58, i)
    turbine(v, 55, 11, angle=0.3 + i * 0.42)
    tree(v, 13, 13, grow=0.45 + 0.45 * ease(i, 6, 30), seed=1)
    tree(v, 41, 12, grow=0.35 + 0.5 * ease(i, 8, 32), seed=2)
    tree(v, 12, 31, grow=0.3 + 0.45 * ease(i, 10, 30), seed=3)
    tree(v, 13, 53, grow=0.2 + 0.55 * ease(i, 12, 34), seed=4)
    tree(v, 30, 28, grow=0.1 + 0.3 * ease(i, 10, 32), seed=7)       # the one we plant
    flowers(v, 5, 46, t=i, t_start=8, avoid=[(43, 43, 61, 59), (22, 15, 34, 30), (8, 8, 20, 20)])
    grass_tufts(v, 6, 50, avoid=[(43, 43, 61, 59)])

    v.stamp(person('stand', top='jacket', hair=[('hair_dark', 3), ('hair_grey', 2)],
                   arms=('down', 'hold'), look=(1, 0), blink=(i == 24)), 24, FL, 17)
    watering_can(v, 29, 18, 22)
    for k in range(4):
        y = 20 - ((i + k * 2) % 7)
        if y > FL + 1:
            v.put(30, y, 28 + (k % 2), P['drop'])

    sx, sy, sz = 36, FL + 11 + bob(i), 25
    v.stamp(spark(2, look=(-1, -1), blink=(i == 30), twinkle=i // 2), sx, sy, sz)
    rng = np.random.default_rng(300 + i)
    for _ in range(4):
        v.put(int(29 + rng.integers(0, 4)), int(sy - rng.integers(0, 8)), int(27 + rng.integers(0, 3)), P['sparkle'])
    if i >= 6:
        bx = int(4 + (i - 6) * 2.2)
        bird(v, bx, 48 + bob(i), 30, i)
        bird(v, bx - 6, 45 + bob(i + 2), 34, i + 1)
    cloud(v, 14 + i * 0.12, 40, 4, 0.8)
    return {'lights': [spark_light(sx, sy, sz, 0.45, 7.0)]}


# ---------------------------------------------------------------------------
# 2049: reaching for the stars

LIFTOFF = 14
IGNITION = 10


def scene_launch(v, i):
    terrain_grass(v)
    launch_pad(v)
    tree(v, 13, 13, grow=0.95, seed=1)
    tree(v, 12, 31, grow=0.85, seed=3)
    tree(v, 30, 28, grow=0.7, seed=7)
    flowers(v, 5, 30, avoid=[(33, 11, 61, 37), (15, 42, 36, 52)])
    grass_tufts(v, 6, 40, avoid=[(33, 11, 61, 37)])

    yoff = 0 if i < LIFTOFF else int(round(0.12 * (i - LIFTOFF + 1) ** 2))
    tower(v, i, arm=(i < IGNITION))
    v.stamp(rocket_sprite(), 40, FL + yoff, 17)
    lights = [(56.5, 47.5, 22.5, 0.6, 0.05, 0.05, 3.0, 1.0)] if (i // 3) % 2 == 0 else []
    cx, cz = 47.5, 24.5
    if i >= IGNITION:
        size = min(1.0, 0.4 + 0.15 * (i - IGNITION)) * (1.4 if i >= LIFTOFF else 1.0)
        fy = FL + yoff
        if i < LIFTOFF:
            v.cyl(cx, cz, 3.2 + 0.6 * (i % 2), FL + 1, FL + 2, P['flame2'], only_empty=True)
        flame(v, cx, fy, cz, i, size, y_min=FL + 1)
        lights.append((cx, fy - 2.0, cz, 3.2, 1.7, 0.6, 16.0, 3.0))
        age = i - IGNITION
        for k in range(7):
            a = k * 2 * math.pi / 7 + 0.4
            d = 6 + min(age, 10) * 1.0
            r = min(2.2 + age * 0.45, 5.5)
            smoke_puff(v, cx + d * math.cos(a), FL + 1 + r * 0.6, cz + d * math.sin(a), r)
        if i >= LIFTOFF + 1:
            for y in range(FL + 3, fy - 3, 5):
                r = min(1.8 + (fy - y) * 0.06, 4.2)
                smoke_puff(v, cx + math.sin(y * 0.7) * 0.8, y, cz + math.cos(y * 0.5) * 0.8, r)

    cheer = i >= LIFTOFF
    arms = (('up', 'up') if (i // 2) % 2 == 0 else ('wave', 'wave')) if cheer else ('down', 'down')
    v.stamp(person('stand', top='mustard', hair=[('hair_grey', 3), ('hair_light', 2)],
                   arms=arms, look=(1, 1), blink=(i == 9)), 17, FL + (1 if cheer and (i // 2) % 2 == 0 else 0), 45)
    sy = FL + 5 + (bob(i, 2) if cheer else bob(i))
    v.stamp(spark(2, look=(1, 1), twinkle=i // 2, blink=(i == 10)), 27, sy, 46)
    lights.append(spark_light(27, sy, 46, 0.55, 7.0))
    return {'lights': lights}


# ---------------------------------------------------------------------------
# 2056: still curious, still here

FIREFLIES = np.random.default_rng(77).uniform([14, 18, 20], [54, 36, 50], (11, 3))


def scene_night(v, i):
    terrain_grass(v)
    stone_path(v)
    tree(v, 30, 28, grow=1.0, big=True, seed=7)
    tree(v, 12, 13, grow=1.0, seed=1)
    park_bench(v)
    lamp_post(v, 57, 50)
    telescope(v)
    flowers(v, 9, 28, avoid=[(20, 34, 46, 46), (29, 43, 36, 64), (42, 39, 55, 49), (54, 47, 61, 54)])
    grass_tufts(v, 6, 40)

    look = (0, 1) if i < 20 else (1, 0)
    v.stamp(person('sit', top='cardigan', hair='hair_white', glasses=True, scarf='scarf',
                   arms=('down', 'down'), look=look, blink=(i == 27)), 23, FL, 37)
    sp_look = (0, 1) if i < 20 else (-1, 0)
    hop = 1 if 12 <= i < 18 and (i // 2) % 2 == 0 else 0
    v.stamp(spark(2, look=sp_look, twinkle=i // 2, blink=(i == 32)), 33, 18 + hop, 39)
    lights = [(57.5, 38.5, 50.5, 3.4, 2.3, 1.2, 15.0, 2.2),
              spark_light(33, 18 + hop, 39, 1.3, 9.0)]
    rng = np.random.default_rng(900)
    for k, (fx, fy, fz) in enumerate(FIREFLIES):
        wob = rng.uniform(0, 2 * math.pi)
        x = fx + 2.0 * math.sin(i * 0.35 + wob)
        y = fy + 1.5 * math.sin(i * 0.5 + wob * 1.7)
        z = fz + 2.0 * math.cos(i * 0.3 + wob)
        if (i + k) % 7 != 0:
            v.put(int(x), int(y), int(z), P['firefly'], only_empty=True)
    if i >= 22:
        pixel_heart(v, 30, 34 + min(i - 22, 3), 42)
        lights.append((32.5, 32.0 + min(i - 22, 3), 42.5, 0.8, 0.3, 0.4, 5.0, 1.5))
    shoot = (0, 0, 0, 0, -1, 0)
    if 10 <= i <= 17:
        shoot = (-0.03, -0.235, -0.19, -0.29, (i - 10) / 7.0, 7.0)
    return {'lights': lights, 'shoot': shoot}


# ---------------------------------------------------------------------------
# eras

def env_dict(**kw):
    return kw


# Backdrop colours are given as the colour they should *appear* on screen; they are
# pushed back through the tone curve below. The ground plane is then tinted so that,
# once lit, it melts into the foot of the backdrop like a photo-studio sweep.
ENVS = {
    'morning': env_dict(sun=(-0.55, 0.75, 0.5), sun_col=hx('#FFE8CF') * 2.7, sun_soft=0.07,
                        sky=hx('#C3D6EC') * 1.0, bounce=hx('#E6CDB5') * 0.5,
                        bg_top='#78B4E4', bg_mid='#F4D2BE', bg_bot='#F1C7AE', bg_mid_pos=0.5,
                        stars=0.0, star_bright=0.0, moon_size=0.0),
    'lab': env_dict(sun=(-0.35, 0.82, 0.45), sun_col=hx('#FFFBF4') * 2.5, sun_soft=0.07,
                    sky=hx('#CDE7EF') * 1.0, bounce=hx('#E3ECEE') * 0.5,
                    bg_top='#4FB8B0', bg_mid='#B5E2DA', bg_bot='#CFE9E4', bg_mid_pos=0.5,
                    stars=0.0, star_bright=0.0, moon_size=0.0),
    'day': env_dict(sun=(0.3, 0.8, 0.55), sun_col=hx('#FFF0CF') * 2.8, sun_soft=0.07,
                    sky=hx('#BCD8F0') * 1.0, bounce=hx('#D3E2BC') * 0.45,
                    bg_top='#55ABE3', bg_mid='#B8DEF0', bg_bot='#D5EBC2', bg_mid_pos=0.5,
                    stars=0.0, star_bright=0.0, moon_size=0.0),
    'dusk': env_dict(sun=(-0.85, 0.34, 0.42), sun_col=hx('#FF9B5E') * 2.7, sun_soft=0.09,
                     sky=hx('#7A70B6') * 0.8, bounce=hx('#B27E74') * 0.4,
                     bg_top='#23255C', bg_mid='#86507F', bg_bot='#E48C6A', bg_mid_pos=0.5,
                     stars=0.035, star_bright=1.6, moon_size=0.0),
    'night': env_dict(sun=(-0.45, 0.75, 0.35), sun_col=hx('#8EA6FF') * 0.5, sun_soft=0.05,
                      sky=hx('#2B3872') * 0.55, bounce=hx('#1B2142') * 0.35,
                      bg_top='#04060F', bg_mid='#0B1233', bg_bot='#1B2452', bg_mid_pos=0.5,
                      stars=0.045, star_bright=2.0, floor=hx('#1A2140'),
                      moon=(-0.438, -0.274, -0.856), moon_size=0.024, moon_col=hx('#FFF2D2') * 2.4),
}

POSTS = {
    'morning': dict(exposure=1.0, tint=(1.03, 1.0, 0.97), bloom=0.45, saturation=1.08),
    'lab': dict(exposure=0.92, tint=(0.99, 1.01, 1.02), bloom=0.5, saturation=1.06),
    'day': dict(exposure=1.0, tint=(1.01, 1.01, 0.98), bloom=0.45, saturation=1.1),
    'dusk': dict(exposure=1.05, tint=(1.04, 0.98, 1.0), bloom=0.7, saturation=1.1),
    'night': dict(exposure=1.25, tint=(0.97, 0.99, 1.05), bloom=0.9, saturation=1.1),
}


def _lum(c):
    return float(np.dot(c, [0.2126, 0.7152, 0.0722]))


def _display(hexstr):
    return R.srgb_to_linear([int(hexstr[i:i + 2], 16) / 255.0 for i in (1, 3, 5)])


for _name, _e in ENVS.items():
    _exp = POSTS[_name]['exposure']
    _sun = R.normalize(_e['sun'])
    _light = _lum(_e['sun_col']) * max(_sun[1], 0.0) + _lum(_e['sky']) * 0.9
    if 'floor' not in _e:
        _e['floor'] = np.clip(_display(_e['bg_bot']) / _light, 0.0, 0.75)
    for _k in ('bg_top', 'bg_mid', 'bg_bot'):
        _e[_k] = R.inv_aces(_display(_e[_k])) / _exp


SCENES = [
    dict(year=2026, caption='HELLO, WORLD.', build=scene_desk, env='morning'),
    dict(year=2034, caption='HELPING CURE DISEASE', build=scene_lab, env='lab'),
    dict(year=2041, caption='HELPING FORESTS GROW BACK', build=scene_forest, env='day'),
    dict(year=2049, caption='REACHING FOR THE STARS', build=scene_launch, env='dusk'),
    dict(year=2056, caption='STILL CURIOUS. STILL HERE.', build=scene_night, env='night'),
]
N_FRAMES = SCENE_LEN * len(SCENES)
TITLE = 'MY NEXT 30 YEARS  ·  CLAUDE'


def locate(f):
    k = min(f // SCENE_LEN, len(SCENES) - 1)
    return k, f - k * SCENE_LEN


def lerp_dict(a, b, t):
    out = {}
    for key in set(a) | set(b):
        va = a.get(key, b.get(key))
        vb = b.get(key, va)
        if isinstance(va, (tuple, list, np.ndarray)):
            out[key] = np.asarray(va, float) * (1 - t) + np.asarray(vb, float) * t
        else:
            out[key] = va * (1 - t) + vb * t
    return out


def year_at(f):
    k, i = locate(f)
    y1 = SCENES[k]['year']
    if k == 0 or i >= TR:
        return y1
    y0 = SCENES[k - 1]['year']
    return int(round(y0 + (y1 - y0) * (i + 1) / TR))


def caption_at(f):
    """(text, cursor_visible): captions are typed in and backspaced out like a terminal."""
    k, i = locate(f)
    if k > 0 and i < 3:
        prev = SCENES[k - 1]['caption']
        return prev[:int(len(prev) * (1 - (i + 1) / 3.0))], True
    cap = SCENES[k]['caption']
    start = 3
    if i < start:
        return '', (i // 3) % 2 == 0
    n = min(len(cap), int(math.ceil(len(cap) * (i - start + 1) / 5.0)))
    if n < len(cap):
        return cap[:n], True
    return cap, (f // 3) % 2 == 0


def blend(old, new, p):
    """Stop-motion rebuild: the old diorama comes down from the top while the new one goes up."""
    y = np.arange(GY, dtype=np.float32)[None, :, None]
    key = 0.62 * np.clip((y - 12) / 48.0, 0, 1) + 0.38 * WORLD_HASH
    p_old = min(p / 0.62, 1.0)
    p_new = max((p - 0.38) / 0.62, 0.0)
    old_vis = key < (1.0 - p_old) * 1.0001
    new_vis = key < p_new
    return np.where(new_vis & (new != 0), new, np.where(old_vis, old, 0)).astype(np.uint8)


def build_frame(f):
    k, i = locate(f)
    sc = SCENES[k]
    v = Vox()
    info = sc['build'](v, i)
    lights = list(info.get('lights', []))
    env = dict(ENVS[sc['env']])
    post = dict(POSTS[sc['env']])
    if i < TR:
        p = (i + 1) / (TR + 1.0)
        old = Vox()
        if k == 0:
            terrain_wood(old)
            old_lights = []
        else:
            prev = SCENES[k - 1]
            old_info = prev['build'](old, SCENE_LEN - 1)
            old_lights = old_info.get('lights', [])
            s = p * p * (3 - 2 * p)
            env = lerp_dict(ENVS[prev['env']], env, s)
            post = lerp_dict(POSTS[prev['env']], post, s)
        v.g = blend(old.g, v.g, p)
        fade_old = 1.0 - min(p / 0.62, 1.0)
        fade_new = max((p - 0.38) / 0.62, 0.0)
        lights = [l[:3] + tuple(np.asarray(l[3:6]) * fade_new) + l[6:] for l in lights] + \
                 [l[:3] + tuple(np.asarray(l[3:6]) * fade_old) + l[6:] for l in old_lights]
    env['shoot'] = info.get('shoot', (0, 0, 0, 0, -1, 0))
    plinth(v, year_at(f))
    return v, lights, env, post, info


# ---------------------------------------------------------------------------
# camera + overlay

FOV = 20.5


def camera(f, W, H):
    t = f / float(N_FRAMES - 1)
    yaw = math.radians(24.0 - 10.0 * t)
    pitch = math.radians(24.0 - 2.0 * t)
    dist = 245.0 - 10.0 * t
    target = np.array([36.0, 13.5, 36.5])
    rng = np.random.default_rng(f * 7 + 1)
    eye = target + dist * np.array([math.sin(yaw) * math.cos(pitch), math.sin(pitch),
                                    math.cos(yaw) * math.cos(pitch)])
    eye = eye + rng.normal(0, 0.1, 3)
    cam = R.look_at(eye, target + rng.normal(0, 0.05, 3), FOV, W / float(H))
    return cam, float(np.linalg.norm(target - eye))


def draw_pixel_text(draw, s, x, y, cell, fill, shadow, cursor=False, anchor='left'):
    bm = text_bitmap(s)
    if cursor:
        pad = np.zeros((7, 1 if s else 0), bool)
        blk = np.ones((7, 4), bool)
        bm = np.concatenate([bm, pad, blk], axis=1)
    h, w = bm.shape
    if anchor == 'center':
        x = x - (w * cell) // 2
    ys, xs = np.nonzero(bm)
    off = max(1, cell // 2)
    for (r, c) in zip(ys, xs):
        draw.rectangle([x + c * cell + off, y + r * cell + off,
                        x + (c + 1) * cell - 1 + off, y + (r + 1) * cell - 1 + off], fill=shadow)
    for (r, c) in zip(ys, xs):
        draw.rectangle([x + c * cell, y + r * cell, x + (c + 1) * cell - 1, y + (r + 1) * cell - 1], fill=fill)


def overlay(img, f):
    H, W = img.shape[:2]
    s = W / 1920.0
    pil = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).convert('RGBA')
    layer = Image.new('RGBA', pil.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = np.random.default_rng(5000 + f)
    jx, jy = rng.integers(-1, 2, 2) * max(1, int(round(s)))
    draw_pixel_text(d, TITLE, int(56 * s) + jx, int(48 * s) + jy, max(2, int(round(4 * s))),
                    (255, 248, 236, 235), (20, 16, 28, 90))
    text, cur = caption_at(f)
    cell = max(3, int(round(7 * s)))
    draw_pixel_text(d, text, W // 2 + jx, int(H - 112 * s) + jy, cell,
                    (255, 246, 232, 255), (20, 16, 28, 120), cursor=cur, anchor='center')
    return np.asarray(Image.alpha_composite(pil, layer).convert('RGB'))


# ---------------------------------------------------------------------------

def render_frame(f, W, H, spp):
    v, lights, env_kw, post, info = build_frame(f)
    env = R.make_env(center=(CX, CZ), fog0=48.0, fog1=120.0, el0=-0.40, el1=-0.21, **env_kw)
    cam, focus = camera(f, W, H)
    hdr, depth = R.render(v.g, P, cam, env, lights, W, H, spp, f)
    flicker = 1.0 + 0.018 * np.random.default_rng(f + 99).normal()
    post['exposure'] = post.get('exposure', 1.0) * flicker
    img = R.finish(hdr, depth, focus, f, post)
    return overlay(img, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frame', type=int)
    ap.add_argument('--frames', type=str)
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--end', type=int, default=N_FRAMES)
    ap.add_argument('--w', type=int, default=1920)
    ap.add_argument('--h', type=int, default=1080)
    ap.add_argument('--spp', type=int, default=9)
    ap.add_argument('--encode-only', action='store_true')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    frames_dir = os.path.join(OUT, 'frames')
    if a.frame is not None or a.frames:
        todo = [a.frame] if a.frame is not None else [int(x) for x in a.frames.split(',')]
        for f in todo:
            t0 = time.time()
            img = render_frame(f, a.w, a.h, a.spp)
            path = os.path.join(OUT, 'preview_%04d.png' % f)
            Image.fromarray(img).save(path)
            print('frame %d -> %s (%.1fs)' % (f, path, time.time() - t0), flush=True)
        return
    if a.all and not a.encode_only:
        os.makedirs(frames_dir, exist_ok=True)
        t_all = time.time()
        for f in range(a.start, a.end):
            t0 = time.time()
            img = render_frame(f, a.w, a.h, a.spp)
            Image.fromarray(img).save(os.path.join(frames_dir, 'f_%04d.png' % f))
            print('frame %3d/%d  %.1fs' % (f, N_FRAMES, time.time() - t0), flush=True)
        print('rendered in %.1f min' % ((time.time() - t_all) / 60))
    if a.all or a.encode_only:
        encode(frames_dir)


def encode(frames_dir):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mp4 = os.path.join(OUT, 'next30.mp4')
    audio = os.path.join(OUT, 'music.wav')
    cmd = [ff, '-y', '-framerate', str(FPS), '-i', os.path.join(frames_dir, 'f_%04d.png')]
    if os.path.exists(audio):
        cmd += ['-i', audio]
    cmd += ['-vf', 'fps=24,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
            '-movflags', '+faststart']
    if os.path.exists(audio):
        cmd += ['-c:a', 'aac', '-b:a', '160k', '-shortest']
    cmd += [mp4]
    subprocess.run(cmd, check=True, capture_output=True)
    gif = os.path.join(OUT, 'next30.gif')
    pal = os.path.join(OUT, 'palette.png')
    src = ['-framerate', str(FPS), '-i', os.path.join(frames_dir, 'f_%04d.png')]
    scale = 'scale=640:-1:flags=lanczos'
    subprocess.run([ff, '-y'] + src + ['-vf', scale + ',palettegen=max_colors=160:stats_mode=full', pal],
                   check=True, capture_output=True)
    subprocess.run([ff, '-y'] + src + ['-i', pal, '-lavfi',
                                       scale + ' [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=4', gif],
                   check=True, capture_output=True)
    os.remove(pal)
    print('wrote', mp4, 'and', gif)


if __name__ == '__main__':
    main()
