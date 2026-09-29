"""Palette and voxel props for NEXT30."""
import math

import numpy as np

from vox import Vox, Palette, facing, text_bitmap

P = Palette()
_C = P.add

# plinth
_C('foot', '#2A2530')
_C('plinth', '#3A3441')
_C('trim', '#4E4659')
_C('digit', '#F6E9D6', 0.22)
# study
_C('wood1', '#C99466')
_C('wood2', '#BB875B')
_C('wood3', '#AE7B51')
_C('wood_joint', '#8C5F3E')
_C('wood_under', '#7A5236')
_C('rug1', '#D9876B')
_C('rug2', '#F2DDBC')
_C('rug3', '#6FA39B')
_C('desk', '#8F5F3D')
_C('desk_top', '#B98457')
_C('handle', '#E8C170')
_C('chair', '#3F4A5C')
_C('chair2', '#57637A')
_C('laptop', '#B4BAC3')
_C('laptop_dark', '#5F6670')
_C('screen', '#CFE8FF', 1.6)
_C('sticker', '#F2A07B')
_C('mug', '#F1ECE4')
_C('coffee', '#4A2C1D')
_C('steam', '#FFFFFF', 0.35)
_C('pot', '#C9714F')
_C('pot2', '#B5613F')
_C('leaf1', '#5FA35A')
_C('leaf2', '#4C8C4A')
_C('leaf3', '#7DBB66')
_C('shelf', '#8A5E3C')
_C('book1', '#D65A4A')
_C('book2', '#E3B04B')
_C('book3', '#4E79A7')
_C('book4', '#6FAF8F')
_C('book5', '#8D6CAB')
_C('book6', '#E9E1D3')
_C('lamp_shade', '#F3E3C3')
_C('metal_dark', '#3B3F4A')
_C('cat', '#8E8C99')
_C('cat_light', '#DAD7E1')
_C('cat_dark', '#6A6876')
_C('cat_pink', '#E89AA6')
# people
_C('skin', '#E8B48F')
_C('blush', '#F09A8A')
_C('eye', '#2B211D')
_C('glasses', '#D4B062')
_C('hair_dark', '#3B2A22')
_C('hair_grey', '#9A928C')
_C('hair_light', '#CFC9C4')
_C('hair_white', '#F2EEEA')
_C('hoodie', '#3F8EA8')
_C('pants', '#3B4660')
_C('shoe', '#2E2E36')
_C('labcoat', '#F5F5F1')
_C('goggles', '#8FD3F0', 0.25)
_C('jacket', '#5C9A5E')
_C('mustard', '#E0A24F')
_C('cardigan', '#B5525E')
_C('scarf', '#F2C14E')
_C('khaki', '#8C7A5B')
# the spark (me)
_C('spark', '#E47B52', 0.55)
_C('spark_tip', '#F9B08B', 1.1)
_C('spark_eye', '#2A1A14')
# lab
_C('tile1', '#C7D2DC')
_C('tile2', '#A7B7C6')
_C('bench', '#F7F7F5')
_C('cabinet', '#B7C8D6')
_C('cabinet2', '#A5B8C8')
_C('steel', '#8E99A4')
_C('steel_dark', '#4B535C')
_C('glass', '#DDF3F7', 0.15)
_C('liq_g', '#7DF0A0', 1.2)
_C('liq_p', '#FF8FB8', 1.2)
_C('liq_b', '#7FC8FF', 1.2)
_C('liq_y', '#FFE07A', 1.2)
_C('bubble', '#EFFFF4', 0.8)
_C('monitor', '#2F3440')
_C('screen_dark', '#16233A', 0.3)
_C('heart', '#FF5C7A', 2.2)
_C('ekg', '#6DFFB0', 2.0)
_C('dna_a', '#FF7A6B', 0.35)
_C('dna_b', '#3CC4B4', 0.35)
_C('rung_a', '#FFD166', 0.2)
_C('rung_b', '#A89BFF', 0.2)
_C('pedestal', '#E9EEF2')
_C('ring', '#7FF3FF', 2.2)
_C('sparkle', '#FFF3B0', 3.0)
# forest
_C('grass1', '#86C25F')
_C('grass2', '#79B455')
_C('grass3', '#97CD6C')
_C('soil', '#8A5A3B')
_C('soil2', '#77492F')
_C('trunk', '#7B5134')
_C('trunk2', '#6A4430')
_C('leafA', '#5DAA55')
_C('leafB', '#4E9A4B')
_C('leafC', '#74BD5E')
_C('leafD', '#8CCB6A')
_C('water', '#5DB7E8', 0.08)
_C('water2', '#86CFF2', 0.15)
_C('lily', '#6DBE5A')
_C('flower_r', '#F2596B')
_C('flower_y', '#FFD34E')
_C('flower_w', '#FFFFFF')
_C('flower_p', '#B98CF2')
_C('turbine', '#F2F4F6')
_C('can', '#3D8FD6')
_C('drop', '#8FD3FF', 0.5)
_C('bird', '#3A3A48')
_C('cloud', '#FFFFFF')
_C('cloud2', '#EEF2F7')
# launch
_C('concrete', '#B3AEA8')
_C('concrete2', '#A29D98')
_C('stripe', '#F2C14E')
_C('rocket', '#F4F2EE')
_C('rocket_red', '#E4572E')
_C('window', '#8FD6FF', 1.2)
_C('nozzle', '#4A4D55')
_C('flame1', '#FFF6C8', 6.0)
_C('flame2', '#FFB347', 4.0)
_C('flame3', '#FF6B3D', 2.6)
_C('smoke1', '#F4F1EC')
_C('smoke2', '#DEDAD4')
_C('smoke3', '#C6C1BA')
_C('tower', '#C9503E')
_C('tower2', '#9E3E31')
_C('beacon', '#FF4A4A', 4.0)
# night
_C('bench_wood', '#A0704A')
_C('bench_dark', '#5E3F2A')
_C('lamp', '#FFD08A', 4.0)
_C('firefly', '#E9FF8A', 5.0)
_C('stone', '#A4A3AE')
_C('stone2', '#908F9A')
_C('telescope', '#ECEAE6')
_C('heart_small', '#FF7A9A', 2.6)


def M(m):
    """Material spec -> id or [(id, weight)] (accepts names or name lists)."""
    if isinstance(m, str):
        return P[m]
    if isinstance(m, (list, tuple)):
        return [(P[n], w) for n, w in m]
    return m


# world layout
FL = 14                      # first free layer above the plinth's terrain
X0, X1, Z0, Z1 = 8, 64, 8, 64
CX, CZ = 36, 36


# ---------------------------------------------------------------------------
# plinth + terrain

def plinth(v, year):
    v.box(X0 - 1, 0, Z0 - 1, X1 + 1, 2, Z1 + 1, P['foot'])
    v.box(X0, 2, Z0, X1, 12, Z1, P['plinth'])
    v.box(X0, 11, Z0, X1, 12, Z1, P['trim'])
    bm = text_bitmap(str(year), proportional=False, spacing=2)
    h, w = bm.shape
    x0 = CX - w // 2
    for r in range(h):
        for c in range(w):
            if bm[r, c]:
                v.put(x0 + c, 10 - r, Z1, P['digit'])


def terrain_wood(v):
    v.box(X0, 12, Z0, X1, 13, Z1, P['wood_under'])
    rng = np.random.default_rng(11)
    shades = [P['wood1'], P['wood2'], P['wood3']]
    for pz in range(Z0, Z1, 4):
        off = rng.integers(0, 14)
        col = shades[rng.integers(0, 3)]
        v.box(X0, 13, pz, X1, 14, min(pz + 4, Z1), col)
        for x in range(X0 + off, X1, 14):
            v.box(x, 13, pz, x + 1, 14, min(pz + 4, Z1), P['wood_joint'])
    # a striped rug
    for z in range(22, 54):
        band = (z - 22) // 3
        col = [P['rug1'], P['rug2'], P['rug3'], P['rug2']][band % 4]
        v.box(16, 13, z, 56, 14, z + 1, col)
    v.box(16, 13, 22, 56, 14, 23, P['rug1'])
    v.box(16, 13, 53, 56, 14, 54, P['rug1'])


def terrain_tiles(v):
    v.box(X0, 12, Z0, X1, 13, Z1, P['steel'])
    x = np.arange(X0, X1)[:, None]
    z = np.arange(Z0, Z1)[None, :]
    chk = (((x - X0) // 4 + (z - Z0) // 4) % 2).astype(bool)
    top = np.where(chk, P['tile2'], P['tile1']).astype(np.uint8)
    v.g[X0:X1, 13, Z0:Z1] = top


def terrain_grass(v, path=False):
    v.box(X0, 12, Z0, X1, 13, Z1, M([('soil', 3), ('soil2', 1)]))
    v.box(X0, 13, Z0, X1, 14, Z1, M([('grass1', 4), ('grass2', 3), ('grass3', 2)]))
    # soil shows on the plinth's upper edge like a cut through the lawn
    v.box(X0, 12, Z1 - 1, X1, 13, Z1, M([('soil', 3), ('soil2', 1)]))


def grass_tufts(v, seed, n=40, avoid=()):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x = int(rng.integers(X0 + 1, X1 - 1))
        z = int(rng.integers(Z0 + 1, Z1 - 1))
        if any(a[0] <= x < a[2] and a[1] <= z < a[3] for a in avoid):
            continue
        v.put(x, FL, z, M([('grass3', 1), ('grass1', 1)]), only_empty=True)


# ---------------------------------------------------------------------------
# characters

def person(pose='stand', top='hoodie', sleeve=None, pants='pants', hair='hair_dark', shoe='shoe',
           look=(0, 0), arms=('down', 'down'), blink=False, tap=0, collar=None, glasses=False,
           goggles=False, scarf=None):
    """A chibi person facing +z. Returns a Vox sprite.

    stand: 8 x 16 x 7 (feet at y=0)     sit: 8 x 17 x 9 (thighs at y=4)
    """
    sleeve = sleeve or top
    top, sleeve, pants, hair, shoe = M(top), M(sleeve), M(pants), M(hair), M(shoe)
    skin = P['skin']
    if pose == 'sit':
        s = Vox((8, 17, 9), seed=3)
        S = 4
        s.box(2, 1, 5, 4, S, 7, pants)
        s.box(4, 1, 5, 6, S, 7, pants)
        s.box(2, 0, 5, 4, 1, 8, shoe)
        s.box(4, 0, 5, 6, 1, 8, shoe)
        s.box(2, S, 1, 4, S + 2, 7, pants)
        s.box(4, S, 1, 6, S + 2, 7, pants)
        ty = S + 1
    else:
        s = Vox((8, 16, 7), seed=3)
        s.box(2, 0, 1, 4, 4, 3, pants)
        s.box(4, 0, 1, 6, 4, 3, pants)
        s.box(2, 0, 1, 4, 1, 4, shoe)
        s.box(4, 0, 1, 6, 1, 4, shoe)
        ty = 4
    s.box(2, ty, 1, 6, ty + 5, 4, top)
    if collar:
        s.box(3, ty + 3, 3, 5, ty + 5, 4, M(collar))
    if scarf:
        s.box(2, ty + 4, 1, 6, ty + 5, 4, M(scarf))
        s.box(4, ty + 2, 3, 5, ty + 4, 4, M(scarf))
    for side, mode in zip((0, 1), arms):
        ax = 1 if side == 0 else 6
        ox = 0 if side == 0 else 7
        if mode == 'down':
            s.box(ax, ty, 1, ax + 1, ty + 5, 3, sleeve)
            s.box(ax, ty, 1, ax + 1, ty + 1, 3, skin)
        elif mode == 'up':
            s.box(ax, ty + 3, 1, ax + 1, ty + 5, 3, sleeve)
            s.box(ox, ty + 4, 1, ox + 1, ty + 9, 3, sleeve)
            s.box(ox, ty + 9, 1, ox + 1, ty + 10, 3, skin)
        elif mode == 'wave':
            s.box(ax, ty + 3, 1, ax + 1, ty + 5, 3, sleeve)
            s.box(ox, ty + 4, 2, ox + 1, ty + 8, 3, sleeve)
            s.box(ox, ty + 8, 2, ox + 1, ty + 10, 3, skin)
        elif mode == 'wave2':
            s.box(ax, ty + 3, 1, ax + 1, ty + 5, 3, sleeve)
            s.box(ox, ty + 4, 2, ox + 1, ty + 7, 3, sleeve)
            nx = min(max(ox + (1 if side else -1), 0), 7)
            s.box(nx, ty + 7, 2, nx + 1, ty + 9, 3, skin)
        elif mode in ('forward', 'type'):
            depth = s.shape[2]
            lift = 0
            if mode == 'type':
                lift = (tap if side == 0 else 1 - tap)
            s.box(ax, ty + 2, 1, ax + 1, ty + 5, 3, sleeve)
            s.box(ax, ty + 2, 3, ax + 1, ty + 3, depth - 2, sleeve)
            s.box(ax, ty + 2 + lift, depth - 2, ax + 1, ty + 3 + lift, depth, skin)
        elif mode == 'hold':
            s.box(ax, ty + 2, 1, ax + 1, ty + 5, 3, sleeve)
            s.box(ax, ty + 2, 3, ax + 1, ty + 3, 5, sleeve)
            s.box(ax, ty + 2, 5, ax + 1, ty + 3, 6, skin)
    hy = ty + 5
    s.box(1, hy, 0, 7, hy + 6, 6, skin)
    s.box(1, hy + 5, 0, 7, hy + 7, 6, hair)
    s.box(1, hy, 0, 7, hy + 6, 1, hair)
    s.box(1, hy + 2, 0, 2, hy + 6, 4, hair)
    s.box(6, hy + 2, 0, 7, hy + 6, 4, hair)
    s.box(1, hy + 4, 5, 3, hy + 5, 6, hair)
    lx, ly = look
    ey = hy + 2 + ly
    if glasses:
        s.box(1, ey, 5, 7, ey + 1, 6, P['glasses'])
    if not blink:
        s.put(min(max(2 + lx, 1), 6), ey, 5, P['eye'])
        s.put(min(max(5 + lx, 1), 6), ey, 5, P['eye'])
    s.put(1, hy + 1, 5, P['blush'])
    s.put(6, hy + 1, 5, P['blush'])
    if goggles:
        s.box(1, hy + 4, 5, 7, hy + 5, 6, P['goggles'])
        s.box(1, hy + 4, 1, 2, hy + 5, 5, P['goggles'])
        s.box(6, hy + 4, 1, 7, hy + 5, 5, P['goggles'])
    return s


def spark(size=2, look=(0, 0), blink=False, twinkle=0):
    """Me: a small glowing orange spark with two eyes. 9 x 9 x 3, facing +z."""
    s = Vox((9, 9, 3), seed=5)
    b, tip = P['spark'], P['spark_tip']
    if size <= 0:
        s.box(4, 4, 1, 5, 5, 2, tip)
        return s
    if size == 1:
        s.box(3, 4, 1, 6, 5, 2, tip)
        s.box(4, 3, 1, 5, 6, 2, tip)
        s.box(4, 4, 0, 5, 5, 3, b)
        return s
    s.box(3, 2, 0, 6, 7, 3, b)
    s.box(2, 3, 0, 7, 6, 3, b)
    for (x, y) in ((4, 7), (4, 1), (7, 4), (1, 4)):
        s.put(x, y, 1, b)
    for (x, y) in ((4, 8), (4, 0), (8, 4), (0, 4)):
        s.put(x, y, 1, tip)
    if twinkle % 2 == 0:
        for (x, y) in ((2, 6), (6, 6), (2, 2), (6, 2)):
            s.put(x, y, 1, tip)
    else:
        for (x, y) in ((1, 7), (7, 7), (1, 1), (7, 1)):
            s.put(x, y, 1, tip)
    if not blink:
        lx, ly = look
        s.put(3 + lx, 4 + ly, 2, P['spark_eye'])
        s.put(5 + lx, 4 + ly, 2, P['spark_eye'])
    return s


def spark_light(x, y, z, strength=1.0, rng=9.0):
    """Point light for the spark sprite placed with its corner at (x, y, z)."""
    c = np.array([1.0, 0.55, 0.32]) * strength
    return (x + 4.5, y + 4.5, z + 1.5, c[0], c[1], c[2], rng, 3.2)


def cat(t=0):
    """A sleeping cat, curled up, 9 x 5 x 7, head towards -x."""
    s = Vox((9, 5, 7), seed=9)
    s.ellipsoid(5.0, 1.0, 3.5, 4.0, 2.6, 3.0, M([('cat', 3), ('cat_dark', 1)]))
    s.ellipsoid(5.0, 0.6, 4.6, 3.0, 1.2, 1.8, P['cat_light'], only_solid=True)
    s.box(0, 0, 2, 3, 3, 6, M([('cat', 3), ('cat_dark', 1)]))
    s.box(0, 3, 2, 1, 4, 3, P['cat'])
    s.box(0, 3, 5, 1, 4, 6, P['cat'])
    s.put(0, 1, 3, P['cat_pink'])
    s.box(0, 2, 2, 1, 3, 3, P['cat_dark'])
    s.box(0, 2, 5, 1, 3, 6, P['cat_dark'])
    # tail wraps round the front and flicks now and then
    s.box(3, 0, 6, 8, 1, 7, P['cat_dark'])
    if t % 12 in (4, 5, 6):
        s.box(2, 1, 6, 3, 3, 7, P['cat_dark'])
    else:
        s.box(2, 0, 6, 3, 1, 7, P['cat_dark'])
    return s


# ---------------------------------------------------------------------------
# study props (2026)

DESK = 20   # desk top layer


def desk(v):
    v.box(22, DESK, 34, 46, DESK + 1, 44, P['desk_top'])
    for x, z in ((22, 34), (44, 34), (22, 42), (44, 42)):
        v.box(x, FL, z, x + 2, DESK, z + 2, P['desk'])
    v.box(38, 16, 34, 46, DESK, 44, P['desk'])
    v.box(39, 17, 44, 45, 19, 45, P['desk_top'])
    v.box(41, 18, 45, 43, 19, 46, P['handle'])


def chair(v, x0, z0):
    v.box(x0, 17, z0, x0 + 8, 18, z0 + 6, P['chair2'])
    for x, z in ((x0, z0), (x0 + 7, z0), (x0, z0 + 5), (x0 + 7, z0 + 5)):
        v.box(x, FL, z, x + 1, 17, z + 1, P['metal_dark'])
    v.box(x0, 18, z0 - 1, x0 + 8, 27, z0, P['chair'])


def laptop(v, x0, z0):
    y = DESK + 1
    v.box(x0, y, z0, x0 + 8, y + 1, z0 + 6, P['laptop'])
    v.box(x0 + 1, y, z0 + 1, x0 + 7, y + 1, z0 + 4, P['laptop_dark'])
    v.box(x0, y + 1, z0 + 5, x0 + 8, y + 6, z0 + 6, P['screen'])
    v.box(x0, y + 1, z0 + 6, x0 + 8, y + 6, z0 + 7, P['laptop'])
    v.box(x0 + 5, y + 3, z0 + 7, x0 + 7, y + 5, z0 + 8, P['sticker'])


def mug(v, x0, z0, t):
    y = DESK + 1
    v.box(x0, y, z0, x0 + 3, y + 3, z0 + 3, P['mug'])
    v.put(x0 + 1, y + 2, z0 + 1, P['coffee'])
    v.put(x0 + 3, y + 1, z0 + 1, P['mug'])
    v.put(x0 + 3, y + 2, z0 + 1, P['mug'])
    for k in range(3):
        ph = (t + k * 3) % 9
        if ph < 7:
            dx = [0, 1, 1, 0, -1, 0, 1][ph]
            v.put(x0 + 1 + dx, y + 4 + ph // 2 + k, z0 + 1, P['steam'])


def potted_plant(v, x0, y0, z0, size=1.0):
    r = int(round(1.5 * size))
    v.box(x0 - r, y0, z0 - r, x0 + r + 1, y0 + int(3 * size), z0 + r + 1, M([('pot', 3), ('pot2', 1)]))
    top = y0 + int(3 * size)
    v.ellipsoid(x0 + 0.5, top + 2.5 * size, z0 + 0.5, 2.8 * size, 3.0 * size, 2.8 * size,
                M([('leaf1', 3), ('leaf2', 2), ('leaf3', 2)]))
    v.put(x0, top, z0, P['soil'])


def bookshelf(v):
    x0, x1, z0, z1 = 10, 24, 10, 14
    v.box(x0, FL, z0, x1, 34, z0 + 1, P['shelf'])
    v.box(x0, FL, z0, x0 + 1, 34, z1, P['shelf'])
    v.box(x1 - 1, FL, z0, x1, 34, z1, P['shelf'])
    for y in (FL, 20, 26, 33):
        v.box(x0, y, z0, x1, y + 1, z1, P['shelf'])
    rng = np.random.default_rng(4)
    books = ['book1', 'book2', 'book3', 'book4', 'book5', 'book6']
    for y in (FL + 1, 21, 27):
        x = x0 + 1
        while x < x1 - 1:
            h = int(rng.integers(3, 6))
            if rng.random() < 0.12:
                x += 1
                continue
            v.box(x, y, z0 + 1, x + 1, y + h, z1, P[books[rng.integers(0, len(books))]])
            x += 1


def floor_lamp(v, x, z, on=False):
    v.box(x - 1, FL, z - 1, x + 2, FL + 1, z + 2, P['metal_dark'])
    v.box(x, FL, z, x + 1, 37, z + 1, P['metal_dark'])
    v.box(x - 2, 37, z - 2, x + 3, 41, z + 3, P['lamp_shade'])
    if on:
        v.box(x - 1, 36, z - 1, x + 2, 37, z + 2, P['lamp'])


def cloud(v, x, y, z, s=1.0):
    v.ellipsoid(x, y, z, 5 * s, 2.4 * s, 3 * s, M([('cloud', 3), ('cloud2', 1)]))
    v.ellipsoid(x - 4 * s, y - 0.8 * s, z, 3.2 * s, 1.8 * s, 2.6 * s, P['cloud'])
    v.ellipsoid(x + 4.5 * s, y - 0.8 * s, z + 0.5, 3.4 * s, 1.8 * s, 2.4 * s, M([('cloud', 3), ('cloud2', 1)]))


# ---------------------------------------------------------------------------
# lab props (2034)

def lab_bench(v):
    v.box(12, FL, 12, 44, 21, 20, M([('cabinet', 3), ('cabinet2', 1)]))
    for x in range(12, 44, 8):
        v.box(x, FL + 1, 20, x + 7, 20, 21, P['cabinet'])
        v.box(x + 3, 18, 21, x + 4, 19, 22, P['steel'])
    v.box(11, 21, 11, 45, 22, 21, P['bench'])


def monitor(v, t):
    x0, x1, y0, y1, z = 15, 31, 23, 33, 12
    v.box(22, 22, 13, 24, 23, 15, P['steel_dark'])
    v.box(x0, y0, z, x1, y1, z + 1, P['monitor'])
    v.box(x0 + 1, y0 + 1, z + 1, x1 - 1, y1 - 1, z + 2, P['screen_dark'])
    heart = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
    big = (t // 3) % 2 == 0
    hx, hy = 16, y1 - 3
    for r, row in enumerate(heart):
        for c, ch in enumerate(row):
            if ch == '#':
                v.put(hx + c, hy - r, z + 2, P['heart'])
    if big:
        v.put(hx + 3, hy + 1, z + 2, P['heart'])
    ekg = [0, 0, 0, 1, 3, -2, 0, 0, 0, 0, 1, 3, -2, 0]
    shift = t % len(ekg)
    for c in range(7):
        k = ekg[(c + shift) % len(ekg)]
        v.put(23 + c, 27 + k, z + 2, P['ekg'])


def microscope(v, x, z):
    v.box(x, 22, z, x + 4, 23, z + 5, P['steel_dark'])
    v.box(x + 1, 23, z, x + 3, 30, z + 2, P['bench'])
    v.box(x + 1, 28, z + 1, x + 3, 30, z + 4, P['bench'])
    v.box(x + 1, 25, z + 3, x + 3, 29, z + 5, P['steel'])
    v.box(x + 1, 24, z + 2, x + 3, 25, z + 5, P['steel_dark'])
    v.box(x + 1, 30, z + 2, x + 3, 32, z + 4, P['steel_dark'])


def test_tubes(v, x, z, t):
    v.box(x, 22, z, x + 9, 24, z + 3, P['steel'])
    for i, liq in enumerate(('liq_g', 'liq_p', 'liq_b', 'liq_y')):
        tx = x + 1 + i * 2
        lvl = 3 + ((t // 2 + i) % 2 if t >= 0 else 0)
        v.box(tx, 23, z + 1, tx + 1, 23 + lvl, z + 2, P[liq])
        v.box(tx, 23 + lvl, z + 1, tx + 1, 29, z + 2, P['glass'])


def flask(v, x, z, t):
    v.sphere(x + 0.5, 25.0, z + 0.5, 2.6, P['glass'])
    v.sphere(x + 0.5, 24.4, z + 0.5, 2.3, P['liq_g'])
    v.box(x, 27, z, x + 1, 31, z + 1, P['glass'])
    for k in range(3):
        ph = (t + k * 2) % 6
        v.put(x + (k % 2), 28 + ph, z + (1 if k == 1 else 0), P['bubble'])


def dna(v, cx, cz, y0, height, phase, grow_top_sparkle=False, t=0):
    """A double helix growing out of the pedestal."""
    r = 4.2
    for k in range(int(height)):
        th = k * (2 * math.pi / 15.0) + phase
        ax, az = cx + r * math.cos(th), cz + r * math.sin(th)
        bx, bz = cx - r * math.cos(th), cz - r * math.sin(th)
        y = y0 + k
        v.sphere(ax, y + 0.5, az, 1.05, P['dna_a'])
        v.sphere(bx, y + 0.5, bz, 1.05, P['dna_b'])
        if k % 3 == 1:
            mx, mz = (ax + bx) / 2, (az + bz) / 2
            v.line((ax, y + 0.5, az), (mx, y + 0.5, mz), P['rung_a'], only_empty=True)
            v.line((mx, y + 0.5, mz), (bx, y + 0.5, bz), P['rung_b'], only_empty=True)
    if grow_top_sparkle and height > 0:
        rng = np.random.default_rng(100 + t)
        for _ in range(5):
            a = rng.random() * 2 * math.pi
            rr = 2 + rng.random() * 5
            v.put(int(cx + rr * math.cos(a)), int(y0 + height + rng.integers(-2, 4)),
                  int(cz + rr * math.sin(a)), P['sparkle'])


def pedestal(v, cx, cz):
    v.cyl(cx, cz, 6.5, FL, FL + 2, P['pedestal'])
    v.cyl(cx, cz, 6.5, FL + 1, FL + 2, P['ring'])
    v.cyl(cx, cz, 5.5, FL + 1, FL + 2, P['pedestal'])


# ---------------------------------------------------------------------------
# nature props (2041+)

def tree(v, x, z, grow=1.0, big=False, seed=0):
    """A tree at (x, z). grow in [0, 1] scales it from sprout to full size."""
    leaves = M([('leafA', 3), ('leafB', 3), ('leafC', 2), ('leafD', 1)])
    if grow <= 0:
        return
    if grow < 0.15:
        v.put(x, FL, z, P['leafC'])
        v.put(x, FL + 1, z, P['leafD'])
        return
    if big:
        th, cr = 18, 9.5
    else:
        th, cr = 9, 5.0
    h = max(2, int(round(th * grow)))
    r = max(1.2, cr * grow)
    tw = 3 if (big and grow > 0.6) else (2 if grow > 0.45 else 1)
    v.box(x - tw // 2, FL, z - tw // 2, x - tw // 2 + tw, FL + h, z - tw // 2 + tw,
          M([('trunk', 3), ('trunk2', 1)]))
    top = FL + h
    rng = np.random.default_rng(seed)
    v.ellipsoid(x + 0.5, top + r * 0.6, z + 0.5, r, r * 0.85, r, leaves)
    if grow > 0.4:
        for _ in range(4 if big else 3):
            ox, oz = rng.uniform(-0.8, 0.8, 2) * r
            oy = rng.uniform(-0.2, 0.5) * r
            rs = r * rng.uniform(0.5, 0.7)
            v.ellipsoid(x + 0.5 + ox, top + r * 0.6 + oy, z + 0.5 + oz, rs, rs * 0.85, rs, leaves)
    if big:
        v.line((x + 0.5, FL + h * 0.6, z + 0.5), (x + 6.5, FL + h * 0.95, z + 3.5), P['trunk'], r=0.8)
        v.line((x + 0.5, FL + h * 0.55, z + 0.5), (x - 5.5, FL + h * 0.9, z - 1.5), P['trunk'], r=0.8)
        v.box(x - 2, FL, z - 1, x + 3, FL + 1, z + 2, P['trunk2'])
        v.box(x - 1, FL, z - 2, x + 2, FL + 1, z + 3, P['trunk2'])


def flowers(v, seed, n, t=None, t_start=0, avoid=()):
    rng = np.random.default_rng(seed)
    cols = ['flower_r', 'flower_y', 'flower_w', 'flower_p']
    for i in range(n):
        x = int(rng.integers(X0 + 1, X1 - 1))
        z = int(rng.integers(Z0 + 1, Z1 - 1))
        appear = t_start + rng.integers(0, 18)
        if t is not None and t < appear:
            continue
        if any(a[0] <= x < a[2] and a[1] <= z < a[3] for a in avoid):
            continue
        if v.g[x, FL, z] != 0:
            continue
        v.put(x, FL, z, P['leafB'])
        v.put(x, FL + 1, z, P[cols[i % 4]])


def turbine(v, x, z, angle):
    v.box(x, FL, z, x + 2, 50, z + 2, P['turbine'])
    v.box(x - 1, 49, z - 1, x + 3, 52, z + 4, P['turbine'])
    hx, hy, hz = x + 1.0, 50.5, z + 4.5
    v.box(x, 50, z + 4, x + 2, 52, z + 5, P['steel'])
    for k in range(3):
        a = angle + k * 2 * math.pi / 3
        ex, ey = hx + 12 * math.cos(a), hy + 12 * math.sin(a)
        v.line((hx, hy, hz), (ex, ey, hz), P['turbine'])
        mx, my = hx + 4 * math.cos(a), hy + 4 * math.sin(a)
        v.line((hx, hy, hz), (mx + 0.8 * math.cos(a + 1.57), my + 0.8 * math.sin(a + 1.57), hz), P['turbine'])


def pond(v, x0, z0, x1, z1, t):
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    rx, rz = (x1 - x0) / 2, (z1 - z0) / 2
    x = np.arange(x0, x1)[:, None]
    z = np.arange(z0, z1)[None, :]
    inside = ((x + 0.5 - cx) / rx) ** 2 + ((z + 0.5 - cz) / rz) ** 2 <= 1.0
    edge = ((x + 0.5 - cx) / (rx + 1.2)) ** 2 + ((z + 0.5 - cz) / (rz + 1.2)) ** 2 <= 1.0
    reg = v.g[x0:x1, 13, z0:z1]
    reg[edge & ~inside] = P['stone']
    wat = np.where(((x * 7 + z * 13 + t // 2 * 5) % 17) == 0, P['water2'], P['water']).astype(np.uint8)
    reg[inside] = wat[inside]
    v.box(int(cx) - 2, 14, int(cz), int(cx), 15, int(cz) + 2, P['lily'])
    v.put(int(cx) - 1, 15, int(cz), P['flower_p'])


def watering_can(v, x, y, z, pour=True):
    v.box(x, y, z, x + 3, y + 3, z + 3, P['can'])
    v.box(x + 1, y + 3, z, x + 2, y + 4, z + 3, P['can'])
    v.line((x + 1.5, y + 1.5, z + 3), (x + 1.5, y + 2.5, z + 6), P['can'])


def bird(v, x, y, z, t):
    v.box(x, y, z, x + 1, y + 1, z + 2, P['bird'])
    if t % 2 == 0:
        v.put(x - 1, y + 1, z, P['bird'])
        v.put(x + 1, y + 1, z, P['bird'])
        v.put(x - 2, y + 2, z, P['bird'])
        v.put(x + 2, y + 2, z, P['bird'])
    else:
        v.put(x - 1, y, z, P['bird'])
        v.put(x + 1, y, z, P['bird'])
        v.put(x - 2, y - 1, z, P['bird'])
        v.put(x + 2, y - 1, z, P['bird'])


# ---------------------------------------------------------------------------
# launch props (2049)

def rocket_sprite():
    s = Vox((15, 34, 15), seed=21)
    c = 7.0
    white = P['rocket']
    red = P['rocket_red']
    s.cyl(c + 0.5, c + 0.5, 3.6, 4, 24, white)
    s.cyl(c + 0.5, c + 0.5, 3.6, 18, 20, red)
    s.cyl(c + 0.5, c + 0.5, 3.6, 5, 6, red)
    for y in range(24, 33):
        r = 3.6 * (1 - (y - 24) / 9.5) ** 0.75
        s.cyl(c + 0.5, c + 0.5, max(r, 0.6), y, y + 1, red)
    s.box(6, 21, 10, 9, 23, 11, P['window'])
    s.cyl(c + 0.5, c + 0.5, 2.2, 1, 4, P['nozzle'])
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for d in range(3, 7):
            top = 11 - (d - 3) * 2
            x = int(c + dx * d)
            z = int(c + dz * d)
            s.box(x, 3 if d > 4 else 4, z, x + 1, top, z + 1, red)
    return s


def launch_pad(v):
    v.box(34, 13, 12, 60, 14, 36, M([('concrete', 3), ('concrete2', 1)]))
    v.box(38, FL, 16, 56, FL + 1, 32, M([('concrete', 3), ('concrete2', 1)]))
    for i in range(38, 56, 3):
        v.put(i, FL, 31, P['stripe'])
        v.put(i, FL, 16, P['stripe'])


def tower(v, t, arm=True):
    x0, z0 = 55, 21
    for (x, z) in ((x0, z0), (x0 + 3, z0), (x0, z0 + 3), (x0 + 3, z0 + 3)):
        v.box(x, FL + 1, z, x + 1, 46, z + 1, P['tower'])
    for y in range(FL + 3, 46, 4):
        v.box(x0, y, z0, x0 + 4, y + 1, z0 + 4, P['tower2'])
    v.box(x0, 46, z0, x0 + 4, 47, z0 + 4, P['tower2'])
    v.put(x0 + 1, 47, z0 + 1, P['beacon'] if (t // 3) % 2 == 0 else P['tower2'])
    if arm:
        v.box(51, 38, z0 + 1, x0, 39, z0 + 3, P['tower2'])


def flame(v, cx, y, cz, t, size=1.0, y_min=0):
    rng = np.random.default_rng(500 + t)
    n = int(6 * size) + 2
    for k in range(n):
        yy = y - k
        if yy < y_min:
            break
        rr = max(0.6, (2.4 - k * 0.22) * size + rng.uniform(-0.4, 0.4))
        mat = 'flame1' if k < 2 else ('flame2' if k < n * 0.6 else 'flame3')
        v.cyl(cx + rng.uniform(-0.4, 0.4), cz + rng.uniform(-0.4, 0.4), rr, yy, yy + 1, P[mat])


def smoke_puff(v, x, y, z, r):
    v.sphere(x, y, z, r, M([('smoke1', 3), ('smoke2', 2), ('smoke3', 1)]), only_empty=True)


# ---------------------------------------------------------------------------
# night props (2056)

def park_bench(v):
    x0, x1 = 22, 44
    v.box(x0, 17, 37, x1, 18, 43, P['bench_wood'])
    for x in range(x0, x1, 3):
        v.box(x, 17, 37, x + 1, 18, 43, P['bench_dark'])
    for x in (x0 + 1, x1 - 2):
        v.box(x, FL, 38, x + 1, 17, 39, P['bench_dark'])
        v.box(x, FL, 41, x + 1, 17, 42, P['bench_dark'])
        v.box(x, 17, 36, x + 1, 25, 37, P['bench_dark'])
    v.box(x0, 20, 36, x1, 22, 37, P['bench_wood'])
    v.box(x0, 23, 36, x1, 25, 37, P['bench_wood'])


def lamp_post(v, x, z):
    v.box(x - 1, FL, z - 1, x + 2, FL + 2, z + 2, P['metal_dark'])
    v.box(x, FL, z, x + 1, 36, z + 1, P['metal_dark'])
    v.box(x - 2, 36, z - 2, x + 3, 37, z + 3, P['metal_dark'])
    v.box(x - 1, 37, z - 1, x + 2, 40, z + 2, P['lamp'])
    v.box(x - 2, 40, z - 2, x + 3, 41, z + 3, P['metal_dark'])
    v.put(x, 41, z, P['metal_dark'])


def telescope(v):
    """A little stargazing telescope on a tripod, aimed up to the right."""
    top = (48.5, 21.5, 44.5)
    for (bx, bz) in ((48, 41), (45, 46), (51, 46)):
        v.line((bx + 0.5, FL + 0.5, bz + 0.5), top, P['metal_dark'])
    for k in range(9):
        x = 45 + k
        y = 21 + int(k * 0.85)
        v.box(x, y, 43, x + 2, y + 2, 45, P['telescope'])
    v.box(44, 20, 43, 46, 22, 45, P['metal_dark'])
    v.box(53, 27, 43, 55, 30, 45, P['metal_dark'])


def stone_path(v):
    rng = np.random.default_rng(8)
    for z in range(44, 64, 3):
        x = 32 + int(rng.integers(-1, 2))
        v.box(x, 13, z, x + 3, 14, z + 2, M([('stone', 2), ('stone2', 1)]))


def pixel_heart(v, x, y, z):
    heart = [".#.#.", "#####", "#####", ".###.", "..#.."]
    for r, row in enumerate(heart):
        for c, ch in enumerate(row):
            if ch == '#':
                v.put(x + c, y - r, z, P['heart_small'])
