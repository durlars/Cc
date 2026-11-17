import numpy as np, sys, os
from PIL import Image, ImageDraw
W = H = 128
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
def hx(s): s = s.lstrip("#"); return tuple(int(s[i:i+2], 16) for i in (0, 2, 4)) + (255,)
RAMP = {
 "oil":  ["0f1c26","1b2f3d","2c4858","4f7585"],
 "coat": ["1a1726","2a263c","3d3756","5a5275"],
 "legs": ["1b2130","2c3547","414d66","60708e"],
 "boot": ["0d0f16","1a1f2c","2b3347","4d5a7e"],
 "bone": ["5c5646","8a826c","b9b095","e3dcc0"],
 "wood": ["1f1712","352519","52392a","75553d"],
 "iron": ["11151b","222934","3a4655","6a7a8e"],
 "brass":["5e4220","8f6830","c79a4a","f0cf86"],
 "red":  ["34121a","5e2228","8c3633","b8534a"],
 "glow": ["1e4a40","2f8266","6fd6a2","b9f5d0","effff2"],
}
R = {k: [hx(c) for c in v] for k, v in RAMP.items()}
OUTL, VOID = hx("0a0910"), hx("05040a")
img = np.zeros((H, W, 4), np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
def mk(fn):
    m = Image.new("L", (W, H), 0); fn(ImageDraw.Draw(m)); return np.array(m) > 0
poly = lambda pts: mk(lambda d: d.polygon(pts, fill=255))
line = lambda pts, w=1: mk(lambda d: d.line(pts, fill=255, width=w))
def shift(m, dx, dy):
    r = np.zeros_like(m); ys, ye = max(dy, 0), H + min(dy, 0); xs, xe = max(dx, 0), W + min(dx, 0)
    r[ys:ye, xs:xe] = m[ys-dy:ye-dy, xs-dx:xe-dx]; return r
def dil(m): return m | shift(m,1,0) | shift(m,-1,0) | shift(m,0,1) | shift(m,0,-1)
B4 = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]) / 16.0
bayer = B4[yy % 4, xx % 4]

def part(m, ramp, spec=False, inner=True, dither_bottom=0):
    """Paint a part: 4-tone ramp, moon rim top-left, shadow bottom-right, outline where it overlaps earlier parts."""
    prior = img[..., 3] > 0
    img[m] = ramp[1]
    tl = m & ~shift(m, 1, 1);  img[tl] = ramp[3] if spec else ramp[2]
    tl2 = m & ~shift(m, 2, 2) & ~tl; img[tl2] = ramp[2]
    br = m & ~shift(m, -2, -3) & ~tl; img[br] = ramp[0]
    if inner:
        edge = m & dil(prior & ~m); img[edge] = ramp[0]
    if dither_bottom:
        d = m & (yy >= dither_bottom) & (((xx + yy) % 2) == 0); img[d] = ramp[0]
    return m

# ----------------------------------------------------------------- geometry (same body as silhouette A1)
coat  = poly([(50,36),(44,38),(39,46),(36,58),(36,70),(34,80),(28,92),(22,102),(30,100),(34,94),(40,100),(44,90),(50,96),
              (54,86),(60,94),(66,84),(70,90),(72,78),(70,64),(72,54),(70,44),(64,38),(58,36)])
legB  = poly([(44,86),(52,86),(53,100),(51,112),(49,119),(42,119),(44,108),(43,96)])
legF  = poly([(58,86),(66,86),(68,98),(70,110),(72,119),(64,119),(62,108),(59,96)])
bootB = poly([(38,117),(50,117),(55,121),(57,125),(36,125),(35,120)])
bootF = poly([(60,117),(72,117),(80,122),(84,125),(58,125)])
arm   = poly([(64,40),(72,42),(82,54),(88,60),(89,67),(84,68),(78,62),(68,52)])
hand  = poly([(84,58),(95,58),(97,62),(97,70),(93,72),(84,72)])
pole  = poly([(88,4),(91,4),(91,120),(89,127),(88,120)])
hook  = poly([(88,10),(94,5),(101,5),(107,10),(108,17),(105,23),(100,21),(102,16),(100,11),(96,10),(91,14)])
barb  = poly([(88,22),(81,19),(77,13),(84,16),(89,17)])
crown = poly([(46,30),(47,20),(51,13),(57,9),(63,9),(68,13),(71,20),(72,30)])
brim  = poly([(34,31),(48,27),(60,27),(72,26),(84,31),(80,34),(64,35),(50,36),(38,36)])
flap  = poly([(47,32),(40,36),(35,46),(33,56),(39,52),(44,46),(48,38)])
LX, LY = 101, 30
chain = line([(LX+5,LY-6),(LX+5,LY)], 2)
lcap  = poly([(LX,LY),(LX+10,LY),(LX+9,LY+3),(LX+1,LY+3)]) | poly([(LX+5,LY-8),(LX+8,LY-4),(LX+2,LY-4)])
lbody = poly([(LX+1,LY+3),(LX+9,LY+3),(LX+10,LY+17),(LX,LY+17)])
lbase = poly([(LX-1,LY+17),(LX+11,LY+17),(LX+9,LY+20),(LX+1,LY+20)])
lwin  = poly([(LX+3,LY+6),(LX+7,LY+6),(LX+7,LY+14),(LX+3,LY+14)])
bell  = poly([(65,68),(73,68),(74,73),(77,79),(61,79),(64,73)]) | poly([(67,79),(71,79),(69,83)])

# ----------------------------------------------------------------- paint, back to front
part(legB, R["legs"]); part(bootB, R["boot"], spec=True)
part(legF, R["legs"]); part(bootF, R["boot"], spec=True)
part(coat, R["coat"], dither_bottom=82)
# coat details: folds, belt, lining, buttons
img[line([(46,48),(43,86)]) & coat] = R["coat"][2]
img[line([(47,50),(45,84)]) & coat] = R["coat"][2]
img[line([(62,46),(65,82)]) & coat] = R["coat"][0]
img[line([(52,50),(50,70)]) & coat] = R["coat"][0]
img[poly([(55,70),(57,70),(58,88),(55,88)])] = R["red"][1]
img[line([(57,70),(58,88)])] = R["red"][2]
belt = poly([(37,64),(72,63),(72,67),(36,68)]) & coat
img[belt] = R["wood"][1]; img[belt & ~shift(belt,0,1)] = R["wood"][2]; img[belt & ~shift(belt,0,-1)] = R["wood"][0]
img[poly([(59,62),(64,62),(64,69),(59,69)])] = R["brass"][2]; img[poly([(60,64),(63,64),(63,67),(60,67)])] = R["wood"][0]
img[60, 59] = R["brass"][3]; img[62, 59] = R["brass"][3]
for y in (48, 55): img[y, 53] = R["brass"][2]; img[y-1, 53] = R["brass"][3]
# hem: tide-stained, wet
img[coat & (yy >= 94) & (((xx*3 + yy) % 5) == 0)] = R["coat"][0]
part(flap, R["oil"], spec=True)
img[line([(45,36),(36,52)]) & flap] = R["oil"][0]
part(bell, R["brass"], spec=True); img[line([(69,64),(69,68)])] = R["wood"][2]; img[poly([(66,76),(72,76),(73,79),(65,79)])] = R["brass"][0]
part(arm, R["coat"]); img[line([(72,45),(86,62)]) & arm] = R["coat"][2]
# cuff
cuff = poly([(82,60),(90,60),(90,68),(83,67)]) ; img[cuff & arm] = R["red"][1]; img[line([(83,60),(90,61)]) & arm] = R["red"][2]
part(pole, R["wood"])
for y in (50, 54, 84):
    b = poly([(86,y),(93,y),(93,y+2),(86,y+2)]); part(b, R["brass"], spec=True, inner=False)
part(hand, R["bone"])
for yy_ in (62, 66): img[yy_, 85:95] = np.where(hand[yy_, 85:95][:, None], np.array(R["bone"][0]), 0)
for yy_ in (62, 66): img[yy_, 95:98] = (0, 0, 0, 0)
img[hand & (yy >= 69)] = R["bone"][1]
img[poly([(84,61),(88,61),(88,63),(84,63)])] = R["bone"][2]
part(hook, R["iron"], spec=True); part(barb, R["iron"], spec=True)
img[line([(90,12),(97,7)]) & hook] = R["iron"][3]
part(chain, R["iron"], spec=True, inner=False)
part(lcap, R["brass"], spec=True); part(lbody, R["brass"], spec=True); part(lbase, R["brass"], spec=True)
img[lwin] = R["glow"][1]; img[poly([(LX+4,LY+7),(LX+6,LY+7),(LX+6,LY+13),(LX+4,LY+13)])] = R["glow"][3]
img[poly([(LX+3,LY+6),(LX+7,LY+6),(LX+7,LY+8),(LX+3,LY+8)])] = R["glow"][2]
img[LY+9:LY+13, LX+5] = R["glow"][4]; img[LY+13, LX+3:LX+7] = R["glow"][0]
# charms on cords
for cx, ln in ((86, 12), (93, 17)):
    img[line([(cx, 88), (cx, 88+ln-8)]) & ~(coat|pole|hand)] = R["wood"][2]
    top = 88 + ln - 8
    b = poly([(cx-2,top),(cx+2,top),(cx+2,top+4),(cx+1,top+8),(cx-1,top+8),(cx-2,top+4)])
    k1 = poly([(cx-3,top+7),(cx-1,top+7),(cx-1,top+10),(cx-3,top+10)]); k2 = poly([(cx+1,top+7),(cx+3,top+7),(cx+3,top+10),(cx+1,top+10)])
    part(b | k1 | k2, R["bone"], inner=False)
img[line([(90,86),(90,90)]) & ~pole] = R["red"][1]
# hat: crown, red band, brim; face hidden in the shadow under the brim
part(crown, R["oil"], spec=True)
img[line([(52,13),(50,28)]) & crown] = R["oil"][0]; img[line([(58,10),(59,27)]) & crown] = R["oil"][2]
band = poly([(46,26),(72,25),(72,29),(46,30)]) & crown
img[band] = R["red"][1]; img[band & ~shift(band,0,1)] = R["red"][2]; img[band & ~shift(band,0,-1)] = R["red"][0]
part(brim, R["oil"], spec=True)
face = poly([(60,31),(78,30),(80,33),(76,37),(64,37)]) & (brim | coat | crown)
img[face] = VOID
img[face & ~shift(face,0,-1) & (yy < 33)] = R["oil"][0]
img[33, 73] = R["glow"][2]; img[33, 74] = R["glow"][1]
img[line([(36,35),(46,33)]) & brim] = R["oil"][3]       # waxy rim light on brim edge
# ----------------------------------------------------------------- lantern light: dithered green falloff, strongest on right-facing edges
cx, cy = LX + 5, LY + 10
dist = np.hypot(xx - cx, (yy - cy) * 0.9)
inten = np.clip(1 - dist / 40.0, 0, 1)
solid = img[..., 3] > 0
facing = (~shift(solid, -1, 0) | ~shift(solid, -2, 0) | ~shift(solid, -3, 0))   # right-facing edges
isglow = lcap | lbody | lbase | lwin | chain
w = inten * np.where(facing, 1.15, 0.55)
def tint(mask, k):
    rgb = img[..., :3].astype(float); g = np.array(R["glow"][2][:3], float)
    rgb[mask] = rgb[mask] * (1 - k) + g * k; img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
lit2 = solid & ~isglow & (w > 0.50 + (bayer - 0.5) * 0.3)
lit1 = solid & ~isglow & (w > 0.28 + (bayer - 0.5) * 0.3) & ~lit2
tint(lit1, 0.22); tint(lit2, 0.42)
# ----------------------------------------------------------------- outline
solid = img[..., 3] > 0
ring = ~solid & dil(solid)
img[ring] = OUTL
# soul-fire halo and drifting specks (no outline)
halo = (np.hypot(xx - cx, (yy - cy)) < 17) & (img[..., 3] == 0) & (bayer < 0.22 + 0.0)
img[halo] = (79, 174, 134, 60)
for x, y, k in [(113,25,1),(116,17,2),(114,9,0),(120,29,1),(119,40,0),(112,52,1),(117,47,2),(109,60,0)]:
    img[y, x] = R["glow"][k+1]
os.makedirs(OUT, exist_ok=True)
sprite = Image.fromarray(img, "RGBA"); sprite.save(os.path.join(OUT, "ferryman.png"))
bg = np.zeros((H, W, 4), np.uint8); bg[:] = hx("17202c")
bg[yy < 40] = hx("141b27"); bg[(yy > 96)] = hx("0c1118")
bg[(yy > 92) & (yy <= 100) & ((xx + yy) % 2 == 0)] = hx("1d2837")
bg[(yy > 100) & (yy % 6 == 0) & (xx % 8 < 5)] = hx("1a2433")
bgim = Image.fromarray(bg, "RGBA"); bgim.alpha_composite(sprite)
bgim.resize((W*4, H*4), Image.NEAREST).save(os.path.join(OUT, "ferryman_preview_4x.png"))
print("ok", len(np.unique(img.reshape(-1,4), axis=0)), "colours")
