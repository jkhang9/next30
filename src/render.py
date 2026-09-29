"""A small voxel ray tracer in the MagicaVoxel spirit, plus a film-ish post chain.

Each frame is a dense uint8 grid of material ids sitting on an infinite ground
plane. Every sample traces a primary ray (Amanatides-Woo DDA), a soft sun
shadow ray, one ambient-occlusion ray and one shadow ray per point light.
Voxel faces also get corner-interpolated AO and a fake bevel so they read as
little physical blocks.
"""
import math

import numpy as np
from numba import njit, prange
from scipy import ndimage

# ---- environment parameter layout (float64 vector) ----
E_SUN = 0      # 3  direction towards the sun (unit)
E_SUNC = 3     # 3  sun colour * intensity (linear)
E_SUNR = 6     # 1  sun disc radius (softness of shadows)
E_SKY = 7      # 3  ambient light from above
E_GND = 10     # 3  ambient light bounced from below
E_BGT = 13     # 3  backdrop top
E_BGM = 16     # 3  backdrop middle
E_BGB = 19     # 3  backdrop bottom
E_BGMP = 22    # 1  where the middle colour sits (0..1)
E_FLOOR = 23   # 3  ground plane albedo
E_FOG0 = 26    # 1  ground starts fading into the backdrop at this radius
E_FOG1 = 27    # 1  ...and is fully faded here
E_STARS = 28   # 1  star density (0 = none)
E_STARB = 29   # 1  star brightness
E_MOON = 30    # 3  moon direction
E_MOONS = 33   # 1  moon angular size (0 = none)
E_MOONC = 34   # 3  moon colour
E_SHOOT = 37   # 6  shooting star: az0, el0, az1, el1, progress, brightness
E_AOD = 43     # 1  AO ray length
E_AOS = 44     # 1  AO ray strength
E_CX = 45      # 2  fog centre (x, z)
E_SEAM = 47    # 1  darkening of seams between blocks
E_BEVEL = 48   # 1  bevel normal strength
E_T1 = 49      # 3  sun tangent 1 (filled in by make_env)
E_T2 = 52      # 3  sun tangent 2
E_EL0 = 55     # 1  elevation (rad) where the backdrop shows its bottom colour
E_EL1 = 56     # 1  elevation where it reaches the top colour
E_SIZE = 57

AO_TABLE = (0.40, 0.62, 0.81, 1.0)


@njit(inline='always', fastmath=True)
def hash32(n):
    n = n & 0xFFFFFFFF
    n = (((n >> 16) ^ n) * 0x45D9F3B) & 0xFFFFFFFF
    n = (((n >> 16) ^ n) * 0x45D9F3B) & 0xFFFFFFFF
    return (n >> 16) ^ n


@njit(inline='always', fastmath=True)
def rnd(state):
    state = (state + 0x9E3779B9) & 0xFFFFFFFF
    return state, hash32(state) * (1.0 / 4294967296.0)


@njit(inline='always')
def occ(grid, x, y, z):
    if y < 0:
        return 1
    if x < 0 or z < 0 or x >= grid.shape[0] or y >= grid.shape[1] or z >= grid.shape[2]:
        return 0
    return 1 if grid[x, y, z] != 0 else 0


@njit(inline='always', fastmath=True)
def trace(grid, ox, oy, oz, dx, dy, dz, tlim):
    """First solid voxel along the ray. Returns (t, x, y, z, axis); t < 0 on a miss."""
    GX = grid.shape[0]
    GY = grid.shape[1]
    GZ = grid.shape[2]
    if abs(dx) < 1e-12:
        dx = 1e-12
    if abs(dy) < 1e-12:
        dy = 1e-12
    if abs(dz) < 1e-12:
        dz = 1e-12
    idx = 1.0 / dx
    idy = 1.0 / dy
    idz = 1.0 / dz
    tx0 = -ox * idx
    tx1 = (GX - ox) * idx
    if tx0 > tx1:
        tx0, tx1 = tx1, tx0
    ty0 = -oy * idy
    ty1 = (GY - oy) * idy
    if ty0 > ty1:
        ty0, ty1 = ty1, ty0
    tz0 = -oz * idz
    tz1 = (GZ - oz) * idz
    if tz0 > tz1:
        tz0, tz1 = tz1, tz0
    tn = tx0
    ax = 0
    if ty0 > tn:
        tn = ty0
        ax = 1
    if tz0 > tn:
        tn = tz0
        ax = 2
    tf = min(tx1, min(ty1, tz1))
    if tf < 0.0 or tn > tf or tn > tlim:
        return -1.0, 0, 0, 0, -1
    if tn < 0.0:
        tn = 0.0
        ax = -1
    t = tn
    x = int(math.floor(ox + dx * t))
    y = int(math.floor(oy + dy * t))
    z = int(math.floor(oz + dz * t))
    x = min(max(x, 0), GX - 1)
    y = min(max(y, 0), GY - 1)
    z = min(max(z, 0), GZ - 1)
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1
    sz = 1 if dz > 0 else -1
    tdx = abs(idx)
    tdy = abs(idy)
    tdz = abs(idz)
    tmx = ((x + 1 if sx > 0 else x) - ox) * idx
    tmy = ((y + 1 if sy > 0 else y) - oy) * idy
    tmz = ((z + 1 if sz > 0 else z) - oz) * idz
    while True:
        if grid[x, y, z] != 0:
            return t, x, y, z, ax
        if tmx < tmy and tmx < tmz:
            t = tmx
            x += sx
            tmx += tdx
            ax = 0
            if x < 0 or x >= GX:
                return -1.0, 0, 0, 0, -1
        elif tmy < tmz:
            t = tmy
            y += sy
            tmy += tdy
            ax = 1
            if y < 0 or y >= GY:
                return -1.0, 0, 0, 0, -1
        else:
            t = tmz
            z += sz
            tmz += tdz
            ax = 2
            if z < 0 or z >= GZ:
                return -1.0, 0, 0, 0, -1
        if t > tlim:
            return -1.0, 0, 0, 0, -1


@njit(inline='always', fastmath=True)
def smoothstep(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


@njit(fastmath=True)
def background(env, dx, dy, dz, frame):
    el = math.asin(min(max(dy, -1.0), 1.0))
    el0 = env[E_EL0]
    el1 = env[E_EL1]
    t = min(max((el - el0) / (el1 - el0), 0.0), 1.0)
    mp = env[E_BGMP]
    r = 0.0
    g = 0.0
    b = 0.0
    if t < mp:
        k = t / mp
        r = env[E_BGB] * (1 - k) + env[E_BGM] * k
        g = env[E_BGB + 1] * (1 - k) + env[E_BGM + 1] * k
        b = env[E_BGB + 2] * (1 - k) + env[E_BGM + 2] * k
    else:
        k = (t - mp) / (1.0 - mp)
        r = env[E_BGM] * (1 - k) + env[E_BGT] * k
        g = env[E_BGM + 1] * (1 - k) + env[E_BGT + 1] * k
        b = env[E_BGM + 2] * (1 - k) + env[E_BGT + 2] * k
    az = math.atan2(dx, -dz)
    dens = env[E_STARS]
    if dens > 0.0 and el > el0:
        cs = 0.0048
        i = int(math.floor(az / cs))
        j = int(math.floor(el / cs))
        h = hash32((i * 73856093) ^ (j * 19349663) ^ 0x5bd1e995)
        if (h & 0xFFFF) * (1.0 / 65536.0) < dens:
            fu = az / cs - i
            fv = el / cs - j
            cu = 0.3 + 0.4 * ((h >> 16) & 0xFF) / 255.0
            cv = 0.3 + 0.4 * ((h >> 24) & 0xFF) / 255.0
            big = ((h >> 20) & 7) == 0
            sz = 0.2 if big else 0.12
            if abs(fu - cu) < sz and abs(fv - cv) < sz:
                tw = hash32(h ^ (frame * 2654435761)) * (1.0 / 4294967296.0)
                s = env[E_STARB] * (0.45 + 0.55 * tw) * (1.6 if big else 1.0) * smoothstep(el0, el0 + 0.12, el)
                r += s
                g += s
                b += s * 1.05
    ms = env[E_MOONS]
    if ms > 0.0:
        mx = env[E_MOON]
        my = env[E_MOON + 1]
        mz = env[E_MOON + 2]
        # local tangent frame around the moon direction
        ux = mz
        uy = 0.0
        uz = -mx
        ul = math.sqrt(ux * ux + uz * uz) + 1e-9
        ux /= ul
        uz /= ul
        vx = my * uz - mz * uy
        vy = mz * ux - mx * uz
        vz = mx * uy - my * ux
        cosang = dx * mx + dy * my + dz * mz
        if cosang > 0.9:
            pu = (dx * ux + dy * uy + dz * uz) / ms
            pv = (dx * vx + dy * vy + dz * vz) / ms
            q = 7.0
            qu = (math.floor(pu * q) + 0.5) / q
            qv = (math.floor(pv * q) + 0.5) / q
            if qu * qu + qv * qv < 1.0 and (qu - 0.5) ** 2 + (qv - 0.25) ** 2 > 0.64:
                r = env[E_MOONC]
                g = env[E_MOONC + 1]
                b = env[E_MOONC + 2]
            else:
                rr = math.sqrt(pu * pu + pv * pv)
                glow = 0.06 * math.exp(-max(rr - 1.0, 0.0) * 1.3)
                r += env[E_MOONC] * glow
                g += env[E_MOONC + 1] * glow
                b += env[E_MOONC + 2] * glow
    sb = env[E_SHOOT + 5]
    p = env[E_SHOOT + 4]
    if sb > 0.0 and p >= 0.0 and p <= 1.0:
        a0 = env[E_SHOOT]
        e0 = env[E_SHOOT + 1]
        a1 = env[E_SHOOT + 2]
        e1 = env[E_SHOOT + 3]
        hx = a0 + (a1 - a0) * p
        hy = e0 + (e1 - e0) * p
        ddx = a1 - a0
        ddy = e1 - e0
        ln = math.sqrt(ddx * ddx + ddy * ddy) + 1e-9
        ddx /= ln
        ddy /= ln
        tail = 0.16 * min(p * 4.0, 1.0)
        qx = az - hx
        qy = el - hy
        along = -(qx * ddx + qy * ddy)
        perp = abs(qx * ddy - qy * ddx)
        if along > -0.003 and along < tail and perp < 0.0016 * (1.0 - along / (tail + 1e-6)) + 0.0004:
            k = sb * (1.0 - along / (tail + 1e-6))
            r += k
            g += k * 0.95
            b += k * 0.85
    return r, g, b


@njit(inline='always', fastmath=True)
def ao_corner(s1, s2, c):
    if s1 == 1 and s2 == 1:
        return AO_TABLE[0]
    return AO_TABLE[3 - (s1 + s2 + c)]


@njit(fastmath=True)
def shade(grid, env, lights, nl, hx, hy, hz, vx, vy, vz, ax, sgn,
          ar, ag, ab, emis, is_ground, state):
    """Light one surface point. (vx,vy,vz) is the voxel the face belongs to."""
    nx = 0.0
    ny = 0.0
    nz = 0.0
    cx = vx
    cy = vy
    cz = vz
    if ax == 0:
        nx = float(sgn)
        cx = vx + sgn
        ux, uy, uz = 0, 1, 0
        wx, wy, wz = 0, 0, 1
        fu = min(max(hy - vy, 0.0), 1.0)
        fw = min(max(hz - vz, 0.0), 1.0)
    elif ax == 1:
        ny = float(sgn)
        cy = vy + sgn
        ux, uy, uz = 1, 0, 0
        wx, wy, wz = 0, 0, 1
        fu = min(max(hx - vx, 0.0), 1.0)
        fw = min(max(hz - vz, 0.0), 1.0)
    else:
        nz = float(sgn)
        cz = vz + sgn
        ux, uy, uz = 1, 0, 0
        wx, wy, wz = 0, 1, 0
        fu = min(max(hx - vx, 0.0), 1.0)
        fw = min(max(hy - vy, 0.0), 1.0)

    # corner ambient occlusion (the classic voxel "smooth lighting")
    o_mu = occ(grid, cx - ux, cy - uy, cz - uz)
    o_pu = occ(grid, cx + ux, cy + uy, cz + uz)
    o_mw = occ(grid, cx - wx, cy - wy, cz - wz)
    o_pw = occ(grid, cx + wx, cy + wy, cz + wz)
    a00 = ao_corner(o_mu, o_mw, occ(grid, cx - ux - wx, cy - uy - wy, cz - uz - wz))
    a10 = ao_corner(o_pu, o_mw, occ(grid, cx + ux - wx, cy + uy - wy, cz + uz - wz))
    a01 = ao_corner(o_mu, o_pw, occ(grid, cx - ux + wx, cy - uy + wy, cz - uz + wz))
    a11 = ao_corner(o_pu, o_pw, occ(grid, cx + ux + wx, cy + uy + wy, cz + uz + wz))
    vao = (a00 * (1 - fu) + a10 * fu) * (1 - fw) + (a01 * (1 - fu) + a11 * fu) * fw

    # bevels on convex edges and faint seams between neighbouring blocks
    snx = nx
    sny = ny
    snz = nz
    seam = 1.0
    if not is_ground:
        bw = 0.14
        bu = 0.0
        bv = 0.0
        sw = 0.035
        v_pu = occ(grid, vx + ux, vy + uy, vz + uz)
        v_mu = occ(grid, vx - ux, vy - uy, vz - uz)
        v_pw = occ(grid, vx + wx, vy + wy, vz + wz)
        v_mw = occ(grid, vx - wx, vy - wy, vz - wz)
        if v_pu == 0 and fu > 1 - bw:
            bu += (fu - (1 - bw)) / bw
        if v_mu == 0 and fu < bw:
            bu -= (bw - fu) / bw
        if v_pw == 0 and fw > 1 - bw:
            bv += (fw - (1 - bw)) / bw
        if v_mw == 0 and fw < bw:
            bv -= (bw - fw) / bw
        k = env[E_BEVEL]
        snx = nx + k * (bu * ux + bv * wx)
        sny = ny + k * (bu * uy + bv * wy)
        snz = nz + k * (bu * uz + bv * wz)
        ln = math.sqrt(snx * snx + sny * sny + snz * snz)
        snx /= ln
        sny /= ln
        snz /= ln
        if (v_pu == 1 and fu > 1 - sw) or (v_mu == 1 and fu < sw) or \
           (v_pw == 1 and fw > 1 - sw) or (v_mw == 1 and fw < sw):
            seam = 1.0 - env[E_SEAM]

    eps = 1e-3
    px = hx + nx * eps
    py = hy + ny * eps
    pz = hz + nz * eps

    dr = 0.0
    dg = 0.0
    db = 0.0
    # sun with a soft disc
    state, r1 = rnd(state)
    state, r2 = rnd(state)
    rr = math.sqrt(r1) * env[E_SUNR]
    ph = 6.283185307 * r2
    c1 = rr * math.cos(ph)
    c2 = rr * math.sin(ph)
    lx = env[E_SUN] + c1 * env[E_T1] + c2 * env[E_T2]
    ly = env[E_SUN + 1] + c1 * env[E_T1 + 1] + c2 * env[E_T2 + 1]
    lz = env[E_SUN + 2] + c1 * env[E_T1 + 2] + c2 * env[E_T2 + 2]
    ll = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx /= ll
    ly /= ll
    lz /= ll
    ndl = snx * lx + sny * ly + snz * lz
    if ndl > 0.0 and (nx * lx + ny * ly + nz * lz) > -0.05:
        t, _a, _b, _c, _d = trace(grid, px, py, pz, lx, ly, lz, 1e9)
        if t < 0.0:
            dr += env[E_SUNC] * ndl
            dg += env[E_SUNC + 1] * ndl
            db += env[E_SUNC + 2] * ndl

    # one cosine-weighted AO ray around the true normal
    state, r1 = rnd(state)
    state, r2 = rnd(state)
    phi = 6.283185307 * r1
    sr = math.sqrt(r2)
    a1 = sr * math.cos(phi)
    a2 = sr * math.sin(phi)
    an = math.sqrt(max(0.0, 1.0 - r2))
    ddx = an * nx + a1 * ux + a2 * wx
    ddy = an * ny + a1 * uy + a2 * wy
    ddz = an * nz + a1 * uz + a2 * wz
    aod = env[E_AOD]
    t, _a, _b, _c, _d = trace(grid, px, py, pz, ddx, ddy, ddz, aod)
    vis = 1.0
    if t >= 0.0:
        vis = 0.25 + 0.75 * (t / aod) ** 2
    elif ddy < -1e-6:
        tg = -py / ddy
        if tg < aod:
            vis = 0.25 + 0.75 * (tg / aod) ** 2
    ao = vao * (1.0 - env[E_AOS] * (1.0 - vis))
    up = 0.5 + 0.5 * sny
    amr = (env[E_GND] * (1 - up) + env[E_SKY] * up) * ao
    amg = (env[E_GND + 1] * (1 - up) + env[E_SKY + 1] * up) * ao
    amb = (env[E_GND + 2] * (1 - up) + env[E_SKY + 2] * up) * ao

    # point lights (glowing props)
    for li in range(nl):
        state, j1 = rnd(state)
        state, j2 = rnd(state)
        state, j3 = rnd(state)
        qx = lights[li, 0] + (j1 - 0.5) * 1.2 - px
        qy = lights[li, 1] + (j2 - 0.5) * 1.2 - py
        qz = lights[li, 2] + (j3 - 0.5) * 1.2 - pz
        dist = math.sqrt(qx * qx + qy * qy + qz * qz) + 1e-6
        qx /= dist
        qy /= dist
        qz /= dist
        nd = snx * qx + sny * qy + snz * qz
        if nd > 0.0:
            rng = lights[li, 6]
            att = 1.0 / (1.0 + (dist / rng) ** 2)
            att *= 1.0 - smoothstep(rng * 3.0, rng * 4.0, dist)
            if att > 0.004:
                reach = dist - lights[li, 7]
                hit = False
                if reach > 0.0:
                    t, _a, _b, _c, _d = trace(grid, px, py, pz, qx, qy, qz, reach)
                    hit = t >= 0.0
                if not hit:
                    dr += lights[li, 3] * nd * att
                    dg += lights[li, 4] * nd * att
                    db += lights[li, 5] * nd * att

    r = ar * (dr + amr) * seam + ar * emis
    g = ag * (dg + amg) * seam + ag * emis
    b = ab * (db + amb) * seam + ab * emis
    return r, g, b, state


@njit(parallel=True, fastmath=True, cache=True)
def render_kernel(grid, alb, emi, W, H, spp, frame, cam, env, lights, nl, out, depth):
    ox = cam[0]
    oy = cam[1]
    oz = cam[2]
    fx = cam[3]
    fy = cam[4]
    fz = cam[5]
    rx = cam[6]
    ry = cam[7]
    rz = cam[8]
    ux = cam[9]
    uy = cam[10]
    uz = cam[11]
    th = cam[12]
    asp = cam[13]
    n = int(math.ceil(math.sqrt(spp)))
    fcx = env[E_CX]
    fcz = env[E_CX + 1]
    for py in prange(H):
        for px in range(W):
            state = hash32((px * 73856093) ^ (py * 19349663) ^ (frame * 83492791))
            accr = 0.0
            accg = 0.0
            accb = 0.0
            dsum = 0.0
            for s in range(spp):
                state, j1 = rnd(state)
                state, j2 = rnd(state)
                sx = ((s % n) + j1) / n
                sy = (((s // n) % n) + j2) / n
                u = (2.0 * (px + sx) / W - 1.0) * th * asp
                v = (1.0 - 2.0 * (py + sy) / H) * th
                dx = fx + u * rx + v * ux
                dy = fy + u * ry + v * uy
                dz = fz + u * rz + v * uz
                dl = math.sqrt(dx * dx + dy * dy + dz * dz)
                dx /= dl
                dy /= dl
                dz /= dl
                t, vx, vy, vz, ax = trace(grid, ox, oy, oz, dx, dy, dz, 1e9)
                tg = -1.0
                if dy < -1e-9:
                    tg = -oy / dy
                if t >= 0.0 and ax >= 0 and (tg < 0.0 or t <= tg):
                    m = grid[vx, vy, vz]
                    if ax == 0:
                        sgn = -1 if dx > 0 else 1
                    elif ax == 1:
                        sgn = -1 if dy > 0 else 1
                    else:
                        sgn = -1 if dz > 0 else 1
                    r, g, b, state = shade(grid, env, lights, nl,
                                           ox + dx * t, oy + dy * t, oz + dz * t,
                                           vx, vy, vz, ax, sgn,
                                           alb[m, 0], alb[m, 1], alb[m, 2], emi[m], False, state)
                    dsum += t
                elif tg > 0.0:
                    hx = ox + dx * tg
                    hz = oz + dz * tg
                    r, g, b, state = shade(grid, env, lights, nl, hx, 0.0, hz,
                                           int(math.floor(hx)), -1, int(math.floor(hz)), 1, 1,
                                           env[E_FLOOR], env[E_FLOOR + 1], env[E_FLOOR + 2], 0.0,
                                           True, state)
                    rad = math.sqrt((hx - fcx) ** 2 + (hz - fcz) ** 2)
                    f = smoothstep(env[E_FOG0], env[E_FOG1], rad)
                    br, bgc, bb = background(env, dx, dy, dz, frame)
                    r = r * (1 - f) + br * f
                    g = g * (1 - f) + bgc * f
                    b = b * (1 - f) + bb * f
                    dsum += tg * (1 - f) + 3000.0 * f
                else:
                    r, g, b = background(env, dx, dy, dz, frame)
                    dsum += 3000.0
                accr += r
                accg += g
                accb += b
            out[py, px, 0] = accr / spp
            out[py, px, 1] = accg / spp
            out[py, px, 2] = accb / spp
            depth[py, px] = dsum / spp


# ----------------------------------------------------------------------------
# python side

def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def inv_aces(y):
    """Scene value that the ACES curve below maps to display value y."""
    y = np.clip(np.asarray(y, dtype=np.float64), 0.0, 0.985)
    a = 2.43 * y - 2.51
    b = 0.59 * y - 0.03
    c = 0.14 * y
    return (-b - np.sqrt(b * b - 4 * a * c)) / (2 * a)


def linear_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def hexcol(h):
    h = h.lstrip('#')
    return srgb_to_linear([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])


def normalize(v):
    v = np.asarray(v, dtype=np.float64)
    return v / np.linalg.norm(v)


def look_at(eye, target, fov_deg, aspect):
    eye = np.asarray(eye, dtype=np.float64)
    f = normalize(np.asarray(target, dtype=np.float64) - eye)
    r = normalize(np.cross(f, [0.0, 1.0, 0.0]))
    u = np.cross(r, f)
    th = math.tan(math.radians(fov_deg) / 2)
    return np.concatenate([eye, f, r, u, [th, aspect]]).astype(np.float64)


def make_env(**kw):
    """Pack an environment dict (colours as linear rgb triples) into the kernel vector."""
    e = np.zeros(E_SIZE, dtype=np.float64)
    sun = normalize(kw['sun'])
    e[E_SUN:E_SUN + 3] = sun
    e[E_SUNC:E_SUNC + 3] = kw['sun_col']
    e[E_SUNR] = kw.get('sun_soft', 0.05)
    e[E_SKY:E_SKY + 3] = kw['sky']
    e[E_GND:E_GND + 3] = kw['bounce']
    e[E_BGT:E_BGT + 3] = kw['bg_top']
    e[E_BGM:E_BGM + 3] = kw['bg_mid']
    e[E_BGB:E_BGB + 3] = kw['bg_bot']
    e[E_BGMP] = kw.get('bg_mid_pos', 0.5)
    e[E_FLOOR:E_FLOOR + 3] = kw['floor']
    e[E_FOG0] = kw.get('fog0', 60.0)
    e[E_FOG1] = kw.get('fog1', 170.0)
    e[E_STARS] = kw.get('stars', 0.0)
    e[E_STARB] = kw.get('star_bright', 0.0)
    if kw.get('moon_size', 0.0) > 0:
        e[E_MOON:E_MOON + 3] = normalize(kw['moon'])
        e[E_MOONS] = kw['moon_size']
        e[E_MOONC:E_MOONC + 3] = kw['moon_col']
    e[E_SHOOT:E_SHOOT + 6] = kw.get('shoot', (0, 0, 0, 0, -1, 0))
    e[E_AOD] = kw.get('ao_dist', 9.0)
    e[E_AOS] = kw.get('ao_strength', 0.7)
    e[E_CX:E_CX + 2] = kw.get('center', (36.0, 36.0))
    e[E_SEAM] = kw.get('seam', 0.05)
    e[E_BEVEL] = kw.get('bevel', 0.9)
    helper = np.array([0.0, 1.0, 0.0]) if abs(sun[1]) < 0.95 else np.array([1.0, 0.0, 0.0])
    t1 = normalize(np.cross(sun, helper))
    e[E_T1:E_T1 + 3] = t1
    e[E_T2:E_T2 + 3] = np.cross(sun, t1)
    e[E_EL0] = kw.get('el0', -0.45)
    e[E_EL1] = kw.get('el1', -0.18)
    return e


def render(grid, palette, cam, env, lights, W, H, spp, frame):
    out = np.zeros((H, W, 3), dtype=np.float32)
    depth = np.zeros((H, W), dtype=np.float32)
    lights = np.asarray(lights, dtype=np.float64).reshape(-1, 8)
    if len(lights) == 0:
        lights = np.zeros((1, 8), dtype=np.float64)
        nl = 0
    else:
        nl = len(lights)
    render_kernel(grid, palette.alb, palette.emi, W, H, spp, frame, cam, env, lights, nl, out, depth)
    return out, depth


# ---- post ----

def _blur(img, sigma):
    if sigma <= 0:
        return img
    return ndimage.gaussian_filter(img, sigma=(sigma, sigma, 0), mode='nearest')


def depth_of_field(img, depth, focus, aperture, max_coc):
    """Cheap gather DOF: blend a stack of blurred copies by circle of confusion.

    Blur radii below half a pixel are treated as sharp so the diorama stays crisp and
    only the backdrop and the far edges melt away, like a macro lens on a miniature set.
    """
    coc = aperture * np.abs(1.0 - focus / np.maximum(depth, 1e-3))
    coc = ndimage.gaussian_filter(coc, 1.0)
    sigma = np.clip(coc - 0.5, 0.0, max_coc)
    levels = [0.0, 1.0, 2.0, max(max_coc, 2.5)]
    stack = [img] + [_blur(img, s) for s in levels[1:]]
    out = np.zeros_like(img)
    for i in range(len(levels) - 1):
        lo, hi = levels[i], levels[i + 1]
        w = np.clip((sigma - lo) / (hi - lo), 0.0, 1.0)[..., None]
        m = ((sigma >= lo) & ((sigma < hi) | (i == len(levels) - 2)))[..., None]
        out += np.where(m, stack[i] * (1 - w) + stack[i + 1] * w, 0)
    return out


def bloom(img, threshold, strength, scale):
    lum = img.max(axis=2)
    k = np.clip((lum - threshold) / np.maximum(lum, 1e-4), 0, None)[..., None]
    bright = img * k
    h, w = img.shape[:2]
    small = bright[: h // 4 * 4, : w // 4 * 4].reshape(h // 4, 4, w // 4, 4, 3).mean(axis=(1, 3))
    acc = np.zeros_like(small)
    for s, wgt in ((1.5, 0.5), (4.0, 0.32), (10.0, 0.18)):
        acc += _blur(small, s * scale) * wgt
    up = ndimage.zoom(acc, (h / acc.shape[0], w / acc.shape[1], 1), order=1)
    return img + up[:h, :w] * strength


def aces(x):
    return np.clip((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0, 1)


def finish(img, depth, focus, frame, post):
    """HDR frame -> display-referred float image in [0,1]."""
    H, W = img.shape[:2]
    s = W / 1920.0
    img = img * post.get('exposure', 1.0)
    img = depth_of_field(img, depth, focus, post.get('aperture', 7.0) * s, post.get('max_coc', 4.0) * s)
    img = bloom(img, post.get('bloom_thr', 1.1), post.get('bloom', 0.55), s)
    tint = np.asarray(post.get('tint', (1, 1, 1)), dtype=np.float32)
    img = aces(img * tint)
    img = linear_to_srgb(img).astype(np.float32)
    # gentle s-curve + saturation
    sat = post.get('saturation', 1.08)
    lum = (img * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).sum(axis=2, keepdims=True)
    img = np.clip(lum + (img - lum) * sat, 0, 1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = ((xx / W - 0.5) ** 2 * 1.2 + (yy / H - 0.5) ** 2)
    img *= (1.0 - post.get('vignette', 0.32) * rr * 1.6)[..., None]
    rng = np.random.default_rng(1000 + frame)
    grain = rng.normal(0, post.get('grain', 0.012), (H, W, 1)).astype(np.float32)
    img = np.clip(img + grain, 0, 1)
    return img
