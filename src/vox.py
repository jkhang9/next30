"""Voxel modelling helpers: palette, grid drawing primitives and a 5x7 pixel font."""
import numpy as np

from render import hexcol

GX, GY, GZ = 72, 100, 72


class Palette:
    def __init__(self):
        self.alb = np.zeros((256, 3), np.float32)
        self.emi = np.zeros(256, np.float32)
        self.ids = {}
        self.n = 1

    def add(self, name, hx, emit=0.0):
        i = self.n
        self.n += 1
        self.alb[i] = hexcol(hx)
        self.emi[i] = emit
        self.ids[name] = i
        return i

    def __getitem__(self, name):
        return self.ids[name]


def _hash_field(shape, seed):
    return np.random.default_rng(seed).random(shape).astype(np.float32)


# one static noise value per world cell, so textures stay put from frame to frame
WORLD_HASH = _hash_field((GX, GY, GZ), 7)


class Vox:
    """A dense block of voxels. Used both for the world and for small sprites."""

    def __init__(self, shape=(GX, GY, GZ), hash_field=None, seed=1):
        self.g = np.zeros(shape, np.uint8)
        self.shape = shape
        if hash_field is None:
            hash_field = WORLD_HASH if shape == (GX, GY, GZ) else _hash_field(shape, seed)
        self.h = hash_field

    # -- internal --------------------------------------------------------
    def _slices(self, x0, y0, z0, x1, y1, z1):
        X, Y, Z = self.shape
        a = (max(int(x0), 0), max(int(y0), 0), max(int(z0), 0))
        b = (min(int(x1), X), min(int(y1), Y), min(int(z1), Z))
        if a[0] >= b[0] or a[1] >= b[1] or a[2] >= b[2]:
            return None
        return a, b

    def _pick(self, h, m):
        """m is a material id or a list of (id, weight) pairs picked by noise."""
        if isinstance(m, (int, np.integer)):
            return np.full(h.shape, m, np.uint8)
        ids = np.array([p[0] for p in m], np.uint8)
        w = np.cumsum([p[1] for p in m], dtype=np.float64)
        w /= w[-1]
        return ids[np.searchsorted(w, h, side='right').clip(0, len(ids) - 1)]

    def _write(self, a, b, mask, m, only_empty=False, only_solid=False):
        sl = (slice(a[0], b[0]), slice(a[1], b[1]), slice(a[2], b[2]))
        region = self.g[sl]
        if mask is None:
            mask = np.ones(region.shape, bool)
        if only_empty:
            mask = mask & (region == 0)
        if only_solid:
            mask = mask & (region != 0)
        vals = self._pick(self.h[sl], m)
        region[mask] = vals[mask]

    # -- primitives (half-open ranges) ---------------------------------------
    def box(self, x0, y0, z0, x1, y1, z1, m, **kw):
        s = self._slices(x0, y0, z0, x1, y1, z1)
        if s:
            self._write(s[0], s[1], None, m, **kw)

    def put(self, x, y, z, m, **kw):
        self.box(x, y, z, x + 1, y + 1, z + 1, m, **kw)

    def clear(self, x0, y0, z0, x1, y1, z1):
        s = self._slices(x0, y0, z0, x1, y1, z1)
        if s:
            a, b = s
            self.g[a[0]:b[0], a[1]:b[1], a[2]:b[2]] = 0

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, m, **kw):
        s = self._slices(cx - rx - 1, cy - ry - 1, cz - rz - 1, cx + rx + 1, cy + ry + 1, cz + rz + 1)
        if not s:
            return
        a, b = s
        x, y, z = np.ogrid[a[0]:b[0], a[1]:b[1], a[2]:b[2]]
        mask = (((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 + ((z + 0.5 - cz) / rz) ** 2) <= 1.0
        self._write(a, b, mask, m, **kw)

    def sphere(self, cx, cy, cz, r, m, **kw):
        self.ellipsoid(cx, cy, cz, r, r, r, m, **kw)

    def cyl(self, cx, cz, r, y0, y1, m, **kw):
        """Vertical cylinder centred on (cx, cz) in continuous coordinates."""
        s = self._slices(cx - r - 1, y0, cz - r - 1, cx + r + 1, y1, cz + r + 1)
        if not s:
            return
        a, b = s
        x, y, z = np.ogrid[a[0]:b[0], a[1]:b[1], a[2]:b[2]]
        mask = ((x + 0.5 - cx) ** 2 + (z + 0.5 - cz) ** 2 + 0 * y) <= r * r
        self._write(a, b, mask, m, **kw)

    def line(self, p0, p1, m, r=0.0, **kw):
        p0 = np.asarray(p0, float)
        p1 = np.asarray(p1, float)
        n = int(np.ceil(np.abs(p1 - p0).max() * 2)) + 1
        for t in np.linspace(0, 1, n):
            p = p0 + (p1 - p0) * t
            if r <= 0.5:
                self.put(int(np.floor(p[0])), int(np.floor(p[1])), int(np.floor(p[2])), m, **kw)
            else:
                self.sphere(p[0], p[1], p[2], r, m, **kw)

    def stamp(self, spr, x, y, z, only_empty=False):
        """Copy the solid voxels of a sprite (Vox or array) with its corner at (x, y, z)."""
        src = spr.g if isinstance(spr, Vox) else spr
        X, Y, Z = self.shape
        sx, sy, sz = src.shape
        x, y, z = int(x), int(y), int(z)
        a = (max(x, 0), max(y, 0), max(z, 0))
        b = (min(x + sx, X), min(y + sy, Y), min(z + sz, Z))
        if a[0] >= b[0] or a[1] >= b[1] or a[2] >= b[2]:
            return
        part = src[a[0] - x:b[0] - x, a[1] - y:b[1] - y, a[2] - z:b[2] - z]
        dst = self.g[a[0]:b[0], a[1]:b[1], a[2]:b[2]]
        mask = part != 0
        if only_empty:
            mask &= dst == 0
        dst[mask] = part[mask]


def facing(arr, direction):
    """Rotate a sprite built facing +z so it faces another horizontal direction."""
    k = {'+z': 0, '+x': 1, '-z': 2, '-x': 3}[direction]
    return np.ascontiguousarray(np.rot90(arr, k, axes=(2, 0)))


# ---------------------------------------------------------------------------
# 5x7 pixel font (used for the voxel year on the plinth and the captions)

_FONT_SRC = {
    '0': ".###. #...# #..## #.#.# ##..# #...# .###.",
    '1': "..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.",
    '2': ".###. #...# ....# ...#. ..#.. .#... #####",
    '3': "##### ...#. ..#.. ...#. ....# #...# .###.",
    '4': "...#. ..##. .#.#. #..#. ##### ...#. ...#.",
    '5': "##### #.... ####. ....# ....# #...# .###.",
    '6': "..##. .#... #.... ####. #...# #...# .###.",
    '7': "##### ....# ...#. ..#.. .#... .#... .#...",
    '8': ".###. #...# #...# .###. #...# #...# .###.",
    '9': ".###. #...# #...# .#### ....# ...#. .##..",
    'A': ".###. #...# #...# #...# ##### #...# #...#",
    'B': "####. #...# #...# ####. #...# #...# ####.",
    'C': ".###. #...# #.... #.... #.... #...# .###.",
    'D': "###.. #..#. #...# #...# #...# #..#. ###..",
    'E': "##### #.... #.... ####. #.... #.... #####",
    'F': "##### #.... #.... ####. #.... #.... #....",
    'G': ".###. #...# #.... #.### #...# #...# .####",
    'H': "#...# #...# #...# ##### #...# #...# #...#",
    'I': ".###. ..#.. ..#.. ..#.. ..#.. ..#.. .###.",
    'J': "..### ...#. ...#. ...#. ...#. #..#. .##..",
    'K': "#...# #..#. #.#.. ##... #.#.. #..#. #...#",
    'L': "#.... #.... #.... #.... #.... #.... #####",
    'M': "#...# ##.## #.#.# #.#.# #...# #...# #...#",
    'N': "#...# #...# ##..# #.#.# #..## #...# #...#",
    'O': ".###. #...# #...# #...# #...# #...# .###.",
    'P': "####. #...# #...# ####. #.... #.... #....",
    'Q': ".###. #...# #...# #...# #.#.# #..#. .##.#",
    'R': "####. #...# #...# ####. #.#.. #..#. #...#",
    'S': ".#### #.... #.... .###. ....# ....# ####.",
    'T': "##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..",
    'U': "#...# #...# #...# #...# #...# #...# .###.",
    'V': "#...# #...# #...# #...# #...# .#.#. ..#..",
    'W': "#...# #...# #...# #.#.# #.#.# #.#.# .#.#.",
    'X': "#...# #...# .#.#. ..#.. .#.#. #...# #...#",
    'Y': "#...# #...# #...# .#.#. ..#.. ..#.. ..#..",
    'Z': "##### ....# ...#. ..#.. .#... #.... #####",
    '.': "..... ..... ..... ..... ..... .##.. .##..",
    ',': "..... ..... ..... ..... .##.. ..#.. .#...",
    '!': "..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..",
    '?': ".###. #...# ....# ...#. ..#.. ..... ..#..",
    ':': "..... .##.. .##.. ..... .##.. .##.. .....",
    '-': "..... ..... ..... ##### ..... ..... .....",
    "'": ".##.. ..#.. .#... ..... ..... ..... .....",
    '/': "....# ...#. ...#. ..#.. .#... .#... #....",
    '&': ".##.. #..#. #.#.. .#... #.#.# #..#. .##.#",
    '·': "..... ..... ..... ..#.. ..... ..... .....",
    ' ': "..... ..... ..... ..... ..... ..... .....",
}

FONT = {}
for _ch, _src in _FONT_SRC.items():
    rows = _src.split()
    FONT[_ch] = np.array([[c == '#' for c in r] for r in rows], bool)  # [row(top->bottom), col]


def glyph(ch, proportional=True):
    g = FONT.get(ch.upper(), FONT['?'])
    if ch == ' ':
        return g[:, :3]
    if proportional:
        cols = np.where(g.any(axis=0))[0]
        if len(cols):
            g = g[:, cols[0]:cols[-1] + 1]
    return g


def text_bitmap(s, proportional=True, spacing=1):
    """Render a string to a boolean bitmap [rows, cols] (row 0 = top)."""
    parts = []
    for i, ch in enumerate(s):
        g = glyph(ch, proportional)
        parts.append(g)
        if i != len(s) - 1:
            parts.append(np.zeros((7, spacing), bool))
    return np.concatenate(parts, axis=1) if parts else np.zeros((7, 0), bool)
