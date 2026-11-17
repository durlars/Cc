import numpy as np
from PIL import Image, ImageDraw
import sys, os

W = H = 128
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

def hx(s):
    s = s.lstrip("#"); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)

P = {
    "out":   hx("15131f"),
    "void":  hx("0a0910"),
    "robe0": hx("1f2430"), "robe1": hx("2c3342"), "robe2": hx("3d4758"), "robe3": hx("55617a"),
    "cape0": hx("2a2036"), "cape1": hx("3a2c4a"), "cape2": hx("4f3d63"), "cape3": hx("6b557f"),
    "mant0": hx("1c1a26"), "mant1": hx("2a2636"), "mant2": hx("3a344a"), "mant3": hx("4f4762"),
    "red0":  hx("4f1a20"), "red1": hx("7a2a2e"), "red2": hx("a33d38"),
    "bone0": hx("6e6858"), "bone1": hx("9c957f"), "bone2": hx("c8c0a4"), "bone3": hx("e8e1c8"),
    "wood0": hx("2e1f1a"), "wood1": hx("4a3226"), "wood2": hx("6b4a34"),
    "gold0": hx("7a5526"), "gold1": hx("b8893e"), "gold2": hx("e5b660"),
    "glow0": hx("2f6a5a"), "glow1": hx("4fae86"), "glow2": hx("9be8b8"), "glow3": hx("e4ffe9"),
}

img = np.zeros((H, W, 4), np.uint8)
owner = np.full((H, W), -1, int)   # layer id per pixel, for interior outlines

def mask_poly(pts):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0

def mask_line(pts, w=1):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).line(pts, fill=255, width=w)
    return np.array(m) > 0

def mask_ell(box):
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse(box, fill=255)
    return np.array(m) > 0

def shift(m, dx, dy):
    r = np.zeros_like(m)
    ys, ye = max(dy, 0), H + min(dy, 0)
    xs, xe = max(dx, 0), W + min(dx, 0)
    r[ys:ye, xs:xe] = m[ys - dy:ye - dy, xs - dx:xe - dx]
    return r

def put(m, col):
    img[m] = col

LID = [0]
def layer(m, ramp, shadow_w=3, deep_w=1, hl=True, sel=True):
    """Fill a mask with a 3-4 tone ramp; light comes from the upper left."""
    LID[0] += 1; lid = LID[0]
    base = ramp[-2] if len(ramp) >= 3 else ramp[-1]
    put(m, base)
    # broad shadow band on the right / bottom side
    sh = m & ~shift(m, -shadow_w, -1)
    put(sh, ramp[1] if len(ramp) > 2 else ramp[0])
    deep = m & ~shift(m, -deep_w, 0)
    put(deep, ramp[0])
    if hl and len(ramp) >= 4:
        h = m & ~shift(m, 1, 1) & ~sh
        put(h, ramp[-1])
    owner[m] = lid
    if sel:  # selective interior outline where this layer overlaps something else
        edge = m & (shift(owner != lid, 1, 0) | shift(owner != lid, -1, 0) |
                    shift(owner != lid, 0, 1) | shift(owner != lid, 0, -1))
        edge &= shift(owner >= 0, 1, 0) | shift(owner >= 0, -1, 0) | shift(owner >= 0, 0, 1) | shift(owner >= 0, 0, -1)
        # only darken where the neighbour is opaque but another layer
        nb_other = np.zeros_like(m)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            o = shift(owner, dx, dy) if False else None
        put(edge & ~(m & ~shift(m, 1, 0) & ~shift(m, -1, 0)), ramp[0])
    return lid

def px(x, y, col):
    img[y, x] = col;

def pxs(pts, col):
    for x, y in pts: px(x, y, col)

R = lambda n: [P[f"{n}{i}"] for i in range(4) if f"{n}{i}" in P]

# ---------------------------------------------------------------- robe (long coat, hunched)
robe = mask_poly([(44, 40), (70, 38), (77, 48), (79, 64), (82, 84), (86, 104), (90, 120),
                  (84, 121), (80, 118), (76, 122), (70, 119), (65, 123), (60, 119), (54, 122),
                  (49, 118), (44, 122), (38, 119), (33, 122), (35, 104), (38, 84), (40, 62), (41, 50)])
layer(robe, R("robe"), shadow_w=6, deep_w=2, sel=False)
# long folds
for (x0, y0, x1, y1) in [(50, 66, 46, 118), (60, 70, 60, 117), (70, 72, 74, 116)]:
    put(mask_line([(x0, y0), (x1, y1)]) & robe, P["robe1"])
for (x0, y0, x1, y1) in [(51, 70, 47, 116), (61, 74, 61, 114)]:
    put(mask_line([(x0, y0), (x1, y1)]) & robe, P["robe3"])
# dithered darkening toward the hem (nods to the checker dither in the backgrounds)
yy, xx = np.mgrid[0:H, 0:W]
put(robe & (yy > 108) & ((xx + yy) % 2 == 0) & (img[..., 0] > P["robe1"][0]), P["robe1"])

# ---------------------------------------------------------------- red sash with bone charms
sash = mask_poly([(40, 70), (79, 66), (80, 71), (40, 75)])
layer(sash, R("red"), shadow_w=2, sel=False)
tail = mask_poly([(44, 73), (48, 73), (47, 92), (45, 95), (42, 92)])
layer(tail, R("red"), shadow_w=1, sel=False)
put(mask_line([(45, 76), (44, 92)]) & tail, P["red0"])
# gold buckle
buck = mask_poly([(74, 66), (78, 66), (78, 72), (74, 72)])
layer(buck, R("gold"), shadow_w=1, sel=False)
put(mask_poly([(75, 68), (76, 68), (76, 70), (75, 70)]), P["gold0"])
# dangling finger bones on cords
for cx, ln in ((54, 10), (60, 14), (66, 8)):
    put(mask_line([(cx, 74), (cx, 74 + ln)]), P["wood1"])
    b = mask_poly([(cx - 1, 74 + ln), (cx + 1, 74 + ln), (cx + 1, 78 + ln), (cx, 79 + ln), (cx - 1, 78 + ln)])
    put(b, P["bone2"]); px(cx + 1, 76 + ln, P["bone1"]); px(cx + 1, 77 + ln, P["bone1"]); px(cx - 1, 74 + ln, P["bone3"])

# ---------------------------------------------------------------- shoulder mantle (tattered)
cape = mask_poly([(42, 38), (72, 37), (78, 46), (80, 54), (75, 56), (72, 60), (68, 55), (63, 61),
                  (58, 55), (53, 62), (48, 55), (43, 59), (38, 53), (40, 44)])
layer(cape, R("mant"), shadow_w=4, deep_w=1, sel=False)
for (x0, y0, x1, y1) in [(53, 44, 53, 60), (63, 44, 63, 58)]:
    put(mask_line([(x0, y0), (x1, y1)]) & cape, P["mant1"])

# ---------------------------------------------------------------- hood
hood = mask_poly([(48, 22), (55, 15), (64, 13), (72, 15), (78, 21), (81, 29), (80, 37), (74, 41),
                  (62, 43), (50, 42), (45, 36)])
htail = mask_poly([(49, 21), (42, 22), (36, 27), (33, 34), (36, 33), (42, 30), (46, 34)])
hood_all = hood | htail
layer(hood_all, R("cape"), shadow_w=4, deep_w=1, sel=False)
hb = hood_all & ~shift(hood_all, 0, -1) & cape
put(hb | (shift(hb, 0, 1) & cape), P["cape0"])
# hood rim highlight & face opening
opening = mask_poly([(68, 21), (76, 22), (80, 28), (80, 37), (74, 40), (68, 38), (66, 30)])
put(opening, P["cape0"])
face = mask_poly([(70, 23), (76, 24), (79, 29), (79, 36), (74, 38), (70, 36), (68, 30)])
put(face, P["void"])
# pale skull jaw hint catching glow
pxs([(76, 35), (77, 35), (78, 34)], P["bone0"])
pxs([(77, 36)], P["bone1"])
# glowing eye (single visible eye, like the reference character)
pxs([(74, 28), (75, 28), (74, 29), (75, 29)], P["glow2"])
px(75, 28, P["glow3"])
pxs([(73, 28), (76, 29), (74, 30), (75, 27)], P["glow0"])
# hood seam
put(mask_line([(56, 17), (52, 30), (50, 40)]) & hood, P["cape1"])

# ---------------------------------------------------------------- staff (behind hand, in front of robe)
staff = mask_line([(92, 30), (92, 124)], w=2)
layer(staff, R("wood"), shadow_w=1, deep_w=1, sel=False)
for y in (52, 53, 92, 93):  # gold ferrule bands
    px(91, y, P["gold2"]); px(92, y, P["gold1"])
px(91, 123, P["gold1"]); px(92, 123, P["gold0"]); px(91, 122, P["gold2"]); px(92, 122, P["gold1"])
# crook arm reaching forward to hang a lantern
crook = mask_line([(92, 31), (94, 26), (98, 23), (103, 23), (106, 26)], w=2)
layer(crook, R("wood"), shadow_w=1, sel=False)

# ---------------------------------------------------------------- skull mounted at staff top
skull = mask_ell((86, 14, 98, 26)) | mask_poly([(90, 24), (97, 24), (96, 30), (90, 30)])
layer(skull, R("bone"), shadow_w=3, deep_w=1, sel=False)
pxs([(92, 18), (93, 18), (94, 18), (92, 19), (93, 19), (94, 19), (95, 19), (93, 20), (94, 20)], P["void"])
px(93, 19, P["glow2"]); px(94, 19, P["glow1"])
pxs([(88, 17), (89, 16), (90, 15)], P["bone3"])
pxs([(89, 22), (90, 23)], P["bone0"])                                                 # ember in socket
pxs([(96, 24), (97, 24), (96, 23)], P["void"])                         # nasal
pxs([(91, 27), (93, 27), (95, 27), (91, 28), (93, 28), (95, 28)], P["bone0"])  # teeth gaps
put(mask_line([(90, 26), (96, 26)]), P["bone1"])
# rag strips tied under the skull
for x0, ln in ((89, 7), (91, 10)):
    put(mask_line([(x0, 31), (x0 - 1, 31 + ln)]), P["red1"])
    px(x0 - 1, 31 + ln, P["red0"])

# ---------------------------------------------------------------- hanging lantern with soul-fire
put(mask_line([(106, 27), (106, 32)]), P["gold0"])
lant = mask_poly([(102, 34), (110, 34), (111, 37), (111, 45), (109, 47), (103, 47), (101, 45), (101, 37)])
put(lant, P["gold0"])
glass = mask_poly([(103, 37), (109, 37), (109, 45), (103, 45)])
put(glass, P["glow1"])
put(mask_poly([(105, 39), (107, 39), (107, 44), (105, 44)]), P["glow2"])
pxs([(106, 40), (106, 41), (105, 42)], P["glow3"])
put(mask_line([(106, 37), (106, 45)]), P["gold0"])
pxs([(102, 34), (103, 33), (109, 33), (110, 34), (104, 33), (108, 33)], P["gold1"])
pxs([(103, 32), (104, 32), (105, 32), (106, 32), (107, 32), (108, 32), (109, 32)], P["gold2"])
pxs([(102, 47), (103, 48), (104, 48), (108, 48), (109, 48), (110, 47)], P["gold1"])

# ---------------------------------------------------------------- arm & skeletal hand gripping staff
sleeve = mask_poly([(64, 44), (72, 43), (80, 52), (88, 58), (89, 64), (84, 66), (75, 60), (66, 54)])
layer(sleeve, R("robe"), shadow_w=3, deep_w=1, sel=False)
cuff = mask_poly([(84, 57), (89, 58), (89, 66), (84, 66)])
layer(cuff, R("cape"), shadow_w=1, sel=False)
put(mask_line([(70, 50), (82, 60)]) & sleeve, P["robe1"])
# bony fingers wrapping the staff
fing = [(90, 59), (91, 59), (93, 59), (94, 60), (90, 61), (91, 61), (93, 61), (94, 62),
        (90, 63), (91, 63), (93, 63), (94, 64), (90, 65), (91, 65), (92, 66)]
pxs(fing, P["bone2"])
pxs([(94, 60), (94, 62), (94, 64), (92, 66)], P["bone1"])
pxs([(90, 59), (90, 61)], P["bone3"])

# ---------------------------------------------------------------- feet peeking out
foot = mask_poly([(80, 119), (88, 120), (92, 122), (92, 124), (80, 124)])
layer(foot, [P["void"], P["robe0"], P["robe1"]], shadow_w=1, sel=False)

# ---------------------------------------------------------------- loose soul wisps
for x, y, c in [(100, 54, "glow1"), (101, 53, "glow2"), (99, 60, "glow0"), (104, 58, "glow1"),
                (84, 74, "glow0"), (86, 72, "glow1"), (108, 51, "glow0"), (24, 30, "glow0"), (28, 26, "glow1")]:
    px(x, y, P[c])

# ---------------------------------------------------------------- outer outline
opaque = img[..., 3] > 0
ring = ~opaque & (shift(opaque, 1, 0) | shift(opaque, -1, 0) | shift(opaque, 0, 1) | shift(opaque, 0, -1))
# don't outline the floating wisps (they should feel like light)
wisp = np.zeros_like(opaque)
for x, y in [(100, 54), (101, 53), (99, 60), (104, 58), (84, 74), (86, 72), (108, 51), (24, 30), (28, 26)]:
    wisp[y, x] = True
solid = opaque & ~wisp
ring = ~opaque & (shift(solid, 1, 0) | shift(solid, -1, 0) | shift(solid, 0, 1) | shift(solid, 0, -1))
img[ring] = P["out"]

# soft glow halo around lantern (single-pixel dither, no outline)
halo = mask_ell((96, 30, 116, 52)) & (img[..., 3] == 0) & ((xx + yy) % 2 == 0)
halo &= ~mask_ell((99, 33, 113, 49)) | True
img[halo] = (79, 174, 134, 70)

os.makedirs(OUT, exist_ok=True)
sprite = Image.fromarray(img, "RGBA")
sprite.save(os.path.join(OUT, "necromancer.png"))
# preview: 4x nearest on a night-harbour backdrop
bg = Image.new("RGBA", (W, H), hx("1b2330"))
bgd = np.array(bg)
bgd[(yy > 118)] = hx("10161f")
bgd[(yy > 100) & (yy <= 118) & ((xx + yy) % 2 == 0)] = hx("222c3b")
bg = Image.fromarray(bgd, "RGBA")
bg.alpha_composite(sprite)
bg.resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(OUT, "necromancer_preview_4x.png"))
print("ok")
