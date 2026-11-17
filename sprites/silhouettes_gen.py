from PIL import Image, ImageDraw, ImageFont
W = 128
def canvas():
    m = Image.new("L", (W, W), 0); return m, ImageDraw.Draw(m)
def P(d, pts): d.polygon(pts, fill=255)
def C(d, pts): d.polygon(pts, fill=0)          # cut (negative space)
def L(d, pts, w=1): d.line(pts, fill=255, width=w)

def body(d):
    # slim, stooped figure: long legs, thigh-length coat with ragged split tails
    P(d, [(50,36),(44,38),(39,46),(36,58),(36,70),(34,80),(28,92),(22,102),(30,100),(34,94),(40,100),(44,90),(50,96),
          (54,86),(60,94),(66,84),(70,90),(72,78),(70,64),(72,54),(70,44),(64,38),(58,36)])
    P(d, [(44,86),(52,86),(53,100),(51,112),(49,119),(42,119),(44,108),(43,96)])
    P(d, [(58,86),(66,86),(68,98),(70,110),(72,119),(64,119),(62,108),(59,96)])
    P(d, [(38,117),(50,117),(55,121),(57,125),(36,125),(35,120)])
    P(d, [(60,117),(72,117),(80,122),(84,125),(58,125)])
    C(d, [(55,70),(57,70),(58,88),(55,88)])                       # coat front opening
    P(d, [(64,40),(72,42),(82,54),(88,60),(89,67),(84,68),(78,62),(68,52)])   # arm
    P(d, [(84,58),(95,58),(97,62),(97,70),(93,72),(84,72)])                    # blocky hand
    C(d, [(94,62),(97,62),(97,63),(94,63)]); C(d, [(94,66),(97,66),(97,67),(94,67)])

def pole(d, top=4):
    P(d, [(88,top),(91,top),(91,120),(89,127),(88,120)])
    for y in (50, 54, 84): P(d, [(86,y),(93,y),(93,y+2),(86,y+2)])

def lantern(d, x, y):
    L(d, [(x+5,y-6),(x+5,y)], 2)
    P(d, [(x+5,y-8),(x+8,y-4),(x+2,y-4)])
    P(d, [(x,y),(x+10,y),(x+9,y+3),(x+1,y+3)])
    P(d, [(x+1,y+3),(x+9,y+3),(x+10,y+17),(x,y+17)])
    C(d, [(x+3,y+6),(x+7,y+6),(x+7,y+14),(x+3,y+14)])
    P(d, [(x+4,y+6),(x+6,y+6),(x+6,y+14),(x+4,y+14)])
    P(d, [(x-1,y+17),(x+11,y+17),(x+9,y+20),(x+1,y+20)])

def charms(d, x, y):
    for dx, ln in ((-4, 12), (3, 17)):
        cx = x + dx
        L(d, [(cx, y), (cx, y+ln-8)], 1)
        top = y + ln - 8
        P(d, [(cx-2,top),(cx+2,top),(cx+2,top+4),(cx+1,top+8),(cx-1,top+8),(cx-2,top+4)])
        P(d, [(cx-3,top+7),(cx-1,top+7),(cx-1,top+10),(cx-3,top+10)]); P(d, [(cx+1,top+7),(cx+3,top+7),(cx+3,top+10),(cx+1,top+10)])

def belt_bell(d):
    L(d, [(69,64),(69,68)], 1)
    P(d, [(65,68),(73,68),(74,73),(77,79),(61,79),(64,73)])
    P(d, [(67,79),(71,79),(69,83)])

def net(d):
    P(d, [(40,44),(32,52),(24,66),(18,84),(12,102),(8,122),(16,118),(21,124),(28,115),(34,122),(38,110),(40,94),(42,76),(42,58)])
    for cx, cy in ((29,66),(24,80),(30,90),(20,96),(27,104),(15,112),(32,110),(23,116),(36,98)):
        C(d, [(cx,cy-3),(cx+2,cy),(cx,cy+3),(cx-2,cy)])

def rag(d, x, y):
    P(d, [(x,y),(x+7,y+2),(x+11,y+8),(x+6,y+6),(x+9,y+14),(x+2,y+10),(x,y+12)])

def V1():
    m, d = canvas(); body(d)
    P(d, [(46,30),(47,20),(51,13),(57,9),(63,9),(68,13),(71,20),(72,30)])                       # crown
    P(d, [(34,31),(48,27),(60,27),(72,26),(84,31),(80,34),(64,35),(50,36),(38,36)])            # brim
    P(d, [(47,32),(40,36),(35,46),(33,56),(39,52),(44,46),(48,38)])                             # neck flap
    pole(d)
    P(d, [(88,10),(94,5),(101,5),(107,10),(108,17),(105,23),(100,21),(102,16),(100,11),(96,10),(91,14)])  # hook
    P(d, [(88,22),(81,19),(77,13),(84,16),(89,17)])                                             # barb
    lantern(d, 101, 30)
    charms(d, 90, 88); belt_bell(d)
    return m

def V2():
    m, d = canvas(); body(d)
    P(d, [(47,30),(47,16),(50,8),(68,8),(71,16),(72,30)])                                       # tall crown
    P(d, [(30,30),(42,30),(48,26),(70,26),(86,32),(90,28),(88,37),(74,37),(48,38),(34,37)])    # curled brim
    pole(d, top=14)
    P(d, [(78,22),(102,22),(102,26),(78,26)])                                                   # trident
    P(d, [(78,22),(78,8),(80,2),(82,8),(82,22)]); P(d, [(98,22),(98,8),(100,2),(102,8),(102,22)])
    P(d, [(88,22),(88,6),(90,0),(92,6),(92,22)])
    L(d, [(100,26),(100,32)], 2)
    lantern(d, 96, 38)
    net(d); rag(d, 90, 88)
    return m

def V3():
    m, d = canvas(); body(d)
    P(d, [(46,34),(47,26),(51,16),(56,8),(62,3),(70,0),(79,3),(73,8),(67,14),(68,22),(71,30),(73,36)])   # drooping cowl
    P(d, [(46,36),(40,40),(35,48),(33,56),(39,52),(45,46)])
    pole(d, top=26)
    P(d, [(76,26),(104,26),(104,30),(76,30)])                                                   # bell bar
    P(d, [(84,30),(96,30),(98,42),(104,49),(76,49),(82,42)]); P(d, [(87,49),(93,49),(90,55)])
    P(d, [(87,22),(93,22),(90,15)])
    charms(d, 90, 88)
    L(d, [(32,90),(22,102),(12,112),(3,117)], 2)
    return m

items = [("A1  sou'wester + big hook + lantern", V1()),
         ("A2  captain's hat + trident gaff + net", V2()),
         ("A3  long cowl + bell staff + rope", V3())]
S = 3; pad = 16; lab = 34
sheet = Image.new("RGB", (len(items)*(W*S+pad)+pad, W*S+lab+pad*2+60), (30, 38, 52))
dr = ImageDraw.Draw(sheet); f = ImageFont.load_default(size=15)
import os; os.makedirs("/home/user/Cc/sprites/silhouettes", exist_ok=True)
for i, (name, m) in enumerate(items):
    x = pad + i*(W*S+pad)
    panel = Image.new("RGB", (W, W), (196, 204, 214)); panel.paste((14, 12, 20), mask=m)
    sheet.paste(panel.resize((W*S, W*S), Image.NEAREST), (x, lab))
    dr.text((x, 10), name, fill=(230, 232, 240), font=f)
    sheet.paste(panel.resize((64, 64), Image.NEAREST), (x, lab + W*S + 10))
    dr.text((x + 74, lab + W*S + 30), "64px check", fill=(150, 160, 175), font=f)
    out = Image.new("RGBA", (W, W), (0,0,0,0)); out.paste((14,12,20,255), mask=m)
    out.save(f"/home/user/Cc/sprites/silhouettes/ferryman_b{i+1}.png")
sheet.save("/home/user/Cc/sprites/silhouettes_v3.png")
