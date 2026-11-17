import numpy as np, sys, os
from PIL import Image, ImageDraw
W, H = 48, 82
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
hx = lambda s: tuple(int(s.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) + (255,)
RAMP = {
 "oil":  ["141f29","22323f","34495a","5a7a8c"],
 "coat": ["1e1b2a","302c42","443e5c","625b7c"],
 "legs": ["1d2434","2e384e","45516c","687b9e"],
 "boot": ["0f121a","1b212e","2c3549","4d5b80"],
 "bone": ["5c5646","8a826c","b9b095","e3dcc0"],
 "wood": ["1f1712","352519","52392a","75553d"],
 "iron": ["11151b","222934","3a4655","6a7a8e"],
 "brass":["5e4220","8f6830","c79a4a","f0cf86"],
 "red":  ["34121a","5e2228","8c3633","b8534a"],
 "glow": ["1e4a40","2f8266","6fd6a2","b9f5d0","effff2"],
}
R = {k: [hx(c) for c in v] for k, v in RAMP.items()}
img = np.zeros((H, W, 4), np.uint8)
yy, xx = np.mgrid[0:H, 0:W]
def mk(fn):
    m = Image.new("L", (W, H), 0); fn(ImageDraw.Draw(m)); return np.array(m) > 0
poly = lambda pts: mk(lambda d: d.polygon(pts, fill=255))
line = lambda pts, w=1: mk(lambda d: d.line(pts, fill=255, width=w))
def rect(x0, y0, x1, y1): m = np.zeros((H, W), bool); m[y0:y1+1, x0:x1+1] = True; return m
def shift(m, dx, dy):
    r = np.zeros_like(m); ys, ye = max(dy, 0), H + min(dy, 0); xs, xe = max(dx, 0), W + min(dx, 0)
    r[ys:ye, xs:xe] = m[ys-dy:ye-dy, xs-dx:xe-dx]; return r
dil = lambda m: m | shift(m,1,0) | shift(m,-1,0) | shift(m,0,1) | shift(m,0,-1)
def part(m, ramp, spec=False, inner=True):
    prior = img[..., 3] > 0
    img[m] = ramp[1]
    tl = m & ~shift(m, 1, 1);  img[tl] = ramp[3] if spec else ramp[2]
    br = m & ~shift(m, -1, -1) & ~tl; img[br] = ramp[0]
    if inner: img[m & dil(prior & ~m) & ~tl] = ramp[0]
    return m

# ---------------------------------------------------------------- geometry at the real in-game scale (hat top y=8, soles y=77, pole top y=0)
coat  = poly([(18,22),(14,23),(11,26),(10,31),(11,36),(10,42),(7,48),(4,55),(9,52),(11,47),(14,50),(16,46),(19,49),(21,44),(24,46),(26,42),(27,36),(28,30),(29,26),(27,23),(22,21)])
legB  = poly([(14,44),(18,44),(18,54),(16,64),(14,72),(11,72),(12,62),(13,54)])
legF  = poly([(20,44),(24,44),(25,54),(26,64),(28,72),(24,72),(22,64),(20,54)])
bootB = poly([(8,71),(15,71),(17,74),(18,77),(7,77),(7,74)])
bootF = poly([(22,71),(27,71),(31,74),(33,77),(21,77)])
arm   = poly([(25,23),(29,24),(31,29),(32,34),(30,36),(27,32),(26,28)])
hand  = poly([(31,34),(35,34),(36,36),(36,38),(34,39),(31,39)])
pole  = rect(33, 0, 34, 76) | poly([(33,76),(34,76),(33,78)])
hook  = poly([(33,5),(34,2),(37,0),(41,1),(43,4),(43,8),(41,10),(39,9),(40,6),(39,3),(37,2),(35,6)])
barb  = poly([(33,8),(30,6),(29,3),(32,5),(33,6)])
crown = poly([(17,16),(17,12),(19,9),(23,8),(26,9),(28,12),(28,16)])
brim  = poly([(10,18),(16,15),(22,14),(29,14),(33,18),(31,20),(25,20),(18,20),(12,20)])
flap  = poly([(14,19),(10,22),(8,27),(7,32),(10,30),(13,26),(15,22)])
LX, LY = 38, 13
lcap  = rect(LX+1, LY, LX+5, LY) | poly([(LX+3,LY-2),(LX+4,LY),(LX+2,LY)])
lbody = rect(LX, LY+1, LX+6, LY+8)
lbase = rect(LX, LY+9, LX+6, LY+9)
lwin  = rect(LX+2, LY+2, LX+4, LY+7)
chain = rect(LX+3, LY-4, LX+3, LY-1)
bell  = poly([(23,37),(26,37),(27,40),(22,40)])

# ---------------------------------------------------------------- paint back to front
part(legB, R["legs"]); part(bootB, R["boot"], spec=True)
part(legF, R["legs"]); part(bootF, R["boot"], spec=True)
part(coat, R["coat"])
img[line([(14,28),(12,44)]) & coat] = R["coat"][2]
img[line([(22,27),(23,44)]) & coat] = R["coat"][0]
belt = poly([(10,33),(28,32),(28,34),(10,35)]) & coat
img[belt] = R["wood"][1]; img[belt & ~shift(belt,0,1)] = R["wood"][2]
img[rect(24,32,26,35)] = R["brass"][2]; img[rect(25,33,25,34)] = R["wood"][0]
img[rect(24,36,24,43)] = R["red"][1]; img[rect(25,36,25,42)] = R["red"][0]
for y in (27, 29): img[y, 20] = R["brass"][2]
img[coat & (yy >= 44) & (((xx + yy) % 3) == 0)] = R["coat"][0]
part(flap, R["oil"], spec=True)
part(bell, R["brass"], spec=True); 
part(arm, R["coat"]); img[rect(29,31,31,31) & arm] = R["red"][1]
part(pole, R["wood"])
for y in (28, 44): part(rect(32, y, 35, y), R["brass"], spec=True, inner=False)
part(hand, R["bone"]); img[hand & (yy >= 37)] = R["bone"][1]
img[rect(32,35,36,35) & hand] = R["bone"][0]; img[rect(32,37,36,37) & hand] = R["bone"][0]
part(hook, R["iron"], spec=True); part(barb, R["iron"], spec=True)
part(chain, R["iron"], spec=True, inner=False)
part(lcap, R["brass"], spec=True); part(lbody, R["brass"], spec=True); part(lbase, R["brass"], spec=True)
img[lwin] = R["glow"][1]; img[rect(LX+3, LY+3, LX+3, LY+6)] = R["glow"][4]; img[rect(LX+2, LY+2, LX+4, LY+2)] = R["glow"][2]
img[rect(LX+2, LY+7, LX+4, LY+7)] = R["glow"][0]
# one bone charm on a cord
img[rect(36, 46, 36, 48)] = R["wood"][2]
part(rect(35, 49, 36, 52), R["bone"], inner=False); img[52, 35] = R["bone"][0]
# hat
part(crown, R["oil"], spec=True)
img[line([(19,9),(18,15)]) & crown] = R["oil"][0]
band = rect(15, 14, 26, 15) & crown; img[band] = R["red"][1]; img[band & ~shift(band,0,1)] = R["red"][2]
part(brim, R["oil"], spec=True)
face = poly([(23,18),(30,17),(33,19),(31,22),(25,22)]) & (brim | coat)
img[face] = hx("05040a"); img[face & (yy <= 18)] = R["oil"][0]
img[20, 30] = R["glow"][2]
# lantern glow on nearby surfaces (small, sparse)
cx, cy = LX + 3, LY + 5
solid = img[..., 3] > 0
d = np.hypot(xx - cx, yy - cy); lit = solid & (d < 14) & ~(lcap|lbody|lbase|lwin|chain|pole|hook|barb) & (((xx + yy) % 2) == 0) & ~shift(solid, -1, 0)
g = np.array(R["glow"][2][:3], float); rgb = img[..., :3].astype(float); rgb[lit] = rgb[lit]*0.62 + g*0.38; img[..., :3] = rgb.astype(np.uint8)
# soft outline: cool dark for cool parts, warm dark for warm parts (no pure black, no new hues)
cool = np.array([R[k][0][:3] for k in ("oil", "coat", "legs", "boot", "iron")], float)
warm = np.array([R[k][0][:3] for k in ("wood", "red", "brass")], float)
solid = img[..., 3] > 0; ring = ~solid & dil(solid)
for y, x in zip(*np.where(ring)):
    nb = [img[y+dy, x+dx][:3].astype(float) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)) if 0 <= y+dy < H and 0 <= x+dx < W and img[y+dy, x+dx, 3] > 0]
    m = np.mean(nb, axis=0); cands = warm if (m[0] > m[2] + 25) else cool
    c = cands[np.argmin(((cands - m) ** 2).sum(1))]
    img[y, x] = (*c.astype(np.uint8), 255)
for x, y, k in [(45,6,1),(46,12,2),(44,24,0),(40,27,1)]: img[y, x] = R["glow"][k+1]
os.makedirs(OUT, exist_ok=True)
sp = Image.fromarray(img, "RGBA"); sp.save(os.path.join(OUT, "ferryman_native.png"))
ys, xs = np.where(img[..., 3] > 0); print("bbox", xs.min(), xs.max(), ys.min(), ys.max(), "colours", len(np.unique(img.reshape(-1,4), axis=0)))
