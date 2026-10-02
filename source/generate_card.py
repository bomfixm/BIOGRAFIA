"""Render the original, code-drawn @bomfixm TV profile card.

Requires Python 3, Pillow and NumPy. No external image assets or network calls.
The geometry and beige/green palette follow the user's TV portfolio reference.
"""
from pathlib import Path
import math
import json
import zipfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
W, H = 960, 650
BG = (7, 14, 10)
S = .85
TX, TY = 138, 24
GREEN = (201, 249, 174)
LIME = (183, 245, 56)
FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf'

GLYPHS = {
 'A': ['01110','11011','11011','11111','11011','11011','11011'],
 'B': ['11110','11011','11011','11110','11011','11011','11110'],
 'E': ['11111','11000','11000','11110','11000','11000','11111'],
 'F': ['11111','11000','11000','11110','11000','11000','11000'],
 'I': ['11111','01110','01110','01110','01110','01110','11111'],
 'M': ['11011','11111','11111','11011','11011','11011','11011'],
 'O': ['01110','11011','11011','11011','11011','11011','01110'],
 'S': ['01111','11000','11000','01110','00011','00011','11110'],
 'T': ['11111','01110','01110','01110','01110','01110','01110'],
 'U': ['11011','11011','11011','11011','11011','11011','01110'],
}

def font(size, bold=False):
    path = FONT_BOLD if bold else FONT_PATH
    return ImageFont.truetype(path, size)

def rect(draw, xy, fill, radius=0, outline=None, width=1):
    if radius:
        draw.rounded_rectangle(xy, radius, fill, outline, width)
    else:
        draw.rectangle(xy, fill, outline, width)

def gradient_shape(image, xy, colors, radius, horizontal=False, texture=0, seed=11):
    x0,y0,x1,y1 = map(round,xy)
    ww,hh=x1-x0+1,y1-y0+1
    axis = np.linspace(0,1,ww if horizontal else hh)
    stops=np.linspace(0,1,len(colors))
    channels=np.stack([np.interp(axis,stops,[c[k] for c in colors]) for k in range(3)],axis=-1)
    arr=np.broadcast_to(channels[None,:,:] if horizontal else channels[:,None,:],(hh,ww,3)).copy()
    if texture:
        rng=np.random.default_rng(seed)
        arr+=rng.normal(0,texture,(hh,ww,1))
    tile=Image.fromarray(np.uint8(np.clip(arr,0,255)), 'RGB')
    mask=Image.new('L',(ww,hh))
    ImageDraw.Draw(mask).rounded_rectangle((0,0,ww-1,hh-1),radius=radius,fill=255)
    image.paste(tile,(x0,y0),mask)

def make_tv():
    # Render the physical frame at 2x for smooth bevels, then downsample once.
    tv=Image.new('RGBA',(1608,1380))
    def box(x,y,w,h):return tuple(round(v*2) for v in (x,y,x+w,y+h))
    gradient_shape(tv,box(246,624,312,38),[(81,64,43),(157,129,89)],0)
    gradient_shape(tv,box(196,650,412,36),[(228,207,174),(192,164,126),(136,113,81)],18,texture=1.5)
    d=ImageDraw.Draw(tv)
    rect(d,box(204,652,396,5),(241,226,200,210),5)
    gradient_shape(tv,box(2,2,800,626),[(239,224,199),(223,202,171),(207,184,148)],68,texture=2.2)
    d=ImageDraw.Draw(tv)
    d.rounded_rectangle(box(3,3,798,624),radius=66,outline=(79,61,37,230),width=4)
    d.rounded_rectangle(box(6,6,792,618),radius=60,outline=(255,247,226,200),width=3)
    d.line([(56,10),(1550,10)], fill=(255,247,226,130),width=3)
    gradient_shape(tv,box(52,44,700,494),[(149,123,89),(188,161,124),(215,194,159),(242,229,204)],72,texture=1.5)
    d=ImageDraw.Draw(tv)
    d.rounded_rectangle(box(51,43,702,496),radius=74,outline=(128,104,72,200),width=3)
    d.rounded_rectangle(box(68,60,668,462),radius=60,fill=(17,17,11),outline=(88,76,56),width=3)
    d.rounded_rectangle(box(72,64,660,454),radius=58,outline=(2,7,4),width=9)
    for y in (557,566,575,584,593,602):
        rect(d,box(104,y,198,5),(77,63,45),5)
        rect(d,box(106,y+4.2,194,1.3),(255,246,228,165),1)
    for x in (558,626):
        d.ellipse(box(x-17,586-17,34,34),fill=(105,86,60))
        d.ellipse(box(x-16.5,584-16.5,33,33),fill=(122,103,80))
        d.ellipse(box(x-14.5,584-14.5,29,29),fill=(218,197,163),outline=(249,236,211),width=2)
        d.arc(box(x-13,584-13,26,26),35,175,fill=(163,135,95),width=3)
        d.line([(x*2,573*2),(x*2,581*2)],fill=(103,84,57),width=3)
    d.ellipse(box(515,579,10,10),outline=(109,92,69),width=3)
    for a in range(0,360,45):
        a=math.radians(a)
        d.line([(2*(520+8*math.cos(a)),2*(584+8*math.sin(a))),
                (2*(520+11*math.cos(a)),2*(584+11*math.sin(a)))],fill=(109,92,69),width=3)
    d.arc(box(622,548,12,12),45,330,fill=(109,92,69),width=3)
    d.line([(1268,1097),(1268,1106),(1259,1106)],fill=(109,92,69),width=3)
    d.ellipse(box(659.5,575.5,17,17),fill=(58,50,34))
    rect(d,box(694,566,72,38),(90,73,54),10)
    gradient_shape(tv,box(697,568,66,32),[(229,208,176),(191,164,127)],8)
    d=ImageDraw.Draw(tv)
    d.arc(box(723.4,580,13.2,13.2),-45,225,fill=(109,92,69),width=3)
    d.line([(1460,1157),(1460,1170)],fill=(109,92,69),width=3)
    return tv.resize((round(804*S),round(690*S)),Image.Resampling.LANCZOS)

def star(draw,cx,cy,r,color,points=8):
    p=[]
    for i in range(points*2):
        a=-math.pi/2+i*math.pi/points
        rr=r if i%2==0 else r*.35
        p.append((cx+math.cos(a)*rr,cy+math.sin(a)*rr))
    draw.polygon(p,fill=color)

def paper(checker=False):
    im=Image.new('RGBA',(182,200))
    d=ImageDraw.Draw(im)
    rng=np.random.default_rng(8 if checker else 7)
    p=[(8+int(rng.integers(-4,5)),y) for y in range(8,193,9)]
    p += [(x,192+int(rng.integers(-4,5))) for x in range(8,175,9)]
    p += [(174+int(rng.integers(-4,5)),y) for y in range(192,7,-9)]
    p += [(x,8+int(rng.integers(-4,5))) for x in range(174,7,-9)]
    d.polygon(p,fill=(236,233,220))
    mask=Image.new('L',im.size)
    md=ImageDraw.Draw(mask)
    p2=[(91+(x-91)*.94,100+(y-100)*.94) for x,y in p]
    md.polygon(p2,fill=255)
    tile=Image.new('RGBA',im.size,(55,68,219))
    td=ImageDraw.Draw(tile)
    if checker:
        for y in range(0,200,23):
            for x in range(0,182,23):
                td.rectangle((x,y,x+22,y+22),fill=(20,24,20) if ((x//23+y//23)%2) else (217,218,205))
    else:
        star(td,87,106,62,(228,229,223),points=8)
    im.paste(tile,(0,0),mask)
    return im.rotate(9 if not checker else -8,Image.Resampling.BICUBIC,expand=True)

def cursor():
    # A small white, pixel-shaped arrow, drawn as native geometry.
    im=Image.new('RGBA',(90,106))
    d=ImageDraw.Draw(im)
    p=[(8,6),(8,81),(27,66),(40,95),(55,88),(41,60),(67,60)]
    d.line(p+[p[0]],fill=(232,231,220),width=12,joint='curve')
    d.polygon(p,fill=(231,232,222),outline=(11,18,13))
    d.line(p+[p[0]],fill=(12,16,12),width=5,joint='curve')
    return im.rotate(8,Image.Resampling.NEAREST,expand=True)

TV=make_tv()
BLUE=paper(False)
CHECK=paper(True)
POINTER=cursor().resize((69,83),Image.Resampling.NEAREST)
SCREEN_X=round(TX+74*S)
SCREEN_Y=round(TY+66*S)
SW,SH=round(656*S),round(450*S)

def base(t):
    im=Image.new('RGBA',(W,H),BG+(255,))
    # Only two paper fragments and one small cursor surround the TV.
    phase=2*math.pi*t/8.4
    im.alpha_composite(BLUE,(83,100+round(3*math.sin(phase))))
    im.alpha_composite(CHECK,(699+round(2*math.sin(phase)),151+round(4*math.sin(phase+1))))
    d=ImageDraw.Draw(im)
    star(d,123,458+round(3*math.sin(phase-1)),36,LIME,points=8)
    d.line([(80,510),(92,489),(100,517),(115,491)],fill=(228,225,211),width=3)
    im.alpha_composite(TV,(TX,TY))
    im.alpha_composite(POINTER,(772,393+round(2*math.cos(phase))))
    return im

yy,xx=np.mgrid[0:SH,0:SW]
rad=np.clip(1-(((xx-SW*.5)/(SW*.69))**2+((yy-SH*.48)/(SH*.75))**2),0,1)
scan=np.where(yy%3==0,.82,1.)
screen_array=np.stack([(3+rad*4)*scan,(12+rad*19)*scan,(7+rad*8)*scan],axis=-1)
SCREEN=Image.fromarray(np.uint8(screen_array),'RGB').convert('RGBA')
SMASK=Image.new('L',(SW,SH))
ImageDraw.Draw(SMASK).rounded_rectangle((0,0,SW-1,SH-1),radius=23,fill=255)

def pixel_title(draw,text,cy,size=10):
    width=(len(text)*6-1)*size
    left=(SW-width)//2
    for k,ch in enumerate(text):
        for row,line in enumerate(GLYPHS[ch]):
            for col,bit in enumerate(line):
                if bit=='1':
                    x=left+k*6*size+col*size
                    y=cy+row*size
                    # A dot matrix within each 5x7 letter gives a CRT display.
                    for dx in (0,3,6):
                        for dy in (0,3,6):
                            draw.rectangle((x+dx,y+dy,x+dx+1,y+dy+1),fill=GREEN)

def text_center(draw,text,y,size,color=GREEN):
    f=font(size)
    width=draw.textlength(text,font=f)
    draw.text(((SW-width)/2,y),text,font=f,fill=color)

def content(t,alpha=1):
    out=Image.new('RGBA',(SW,SH))
    d=ImageDraw.Draw(out)
    f=font(20)
    d.text((30,39),'@bomfixm',font=f,fill=(152,203,128))
    if int(t*2)%2==0:
        d.rectangle((149,43,157,59),fill=LIME)
    d.text((SW-109,43),'CH. 01',font=font(13),fill=(106,148,94))
    pixel_title(d,'MATEUS',99)
    pixel_title(d,'BOMFIM',187)
    d.line([(SW/2-32,285),(SW/2+32,285)],fill=(130,186,108),width=1)
    text_center(d,'Engenharia de Software · FIAP',304,18,(168,214,145))
    text_center(d,'Desenvolvimento Web & IA',335,17,(130,177,116))
    glow=out.filter(ImageFilter.GaussianBlur(2.1))
    glow.putalpha(glow.getchannel('A').point(lambda a:int(a*.3)))
    merged=Image.alpha_composite(glow,out)
    if alpha<1:
        merged.putalpha(merged.getchannel('A').point(lambda a:int(a*alpha)))
    return merged

def screen(t):
    # Full text on the first frame. One soft power-on sequence per loop.
    level=1.
    alpha=1.
    if .72<=t<1.04:
        level=max(.015,1-(t-.72)/.32)
        alpha=level
    elif 1.04<=t<1.2:
        level=.007
        alpha=0
    elif 1.2<=t<1.76:
        level=max(.007,(t-1.2)/.56)
        alpha=0
    elif 1.76<=t<2.16:
        alpha=(t-1.76)/.4
    sc=SCREEN.copy()
    sc.alpha_composite(content(t,alpha))
    if level<1:
        dark=Image.new('RGBA',(SW,SH),(2,7,4,255))
        hh=max(2,round(SH*level))
        shrunk=sc.resize((SW,hh),Image.Resampling.BILINEAR)
        dark.alpha_composite(shrunk,(0,(SH-hh)//2))
        if hh<7:
            dd=ImageDraw.Draw(dark)
            dd.line([(12,SH//2),(SW-12,SH//2)],fill=(109,167,78),width=2)
        sc=dark
    # Brief, small horizontal displacement. No whole-screen flashes.
    glitches={40:1,41:2,42:1,68:1,69:2,70:1,93:1,94:1}
    idx=round(t/.08)
    strength=glitches.get(idx,0)
    if strength:
        for y,h,dx in ((121,8,6),(204,12,-8),(269,5,3)):
            stripe=sc.crop((0,y,SW,y+h))
            sc.alpha_composite(stripe,(dx*strength,y))
        d=ImageDraw.Draw(sc)
        d.line([(18,269),(SW-22,269)],fill=(56,94,69,150),width=1)
    # Restrained moving phosphor band, with no random frame noise.
    if level>.95:
        band_y=round((t/8.4)*SH)
        band=Image.new('RGBA',(SW,SH))
        bd=ImageDraw.Draw(band)
        for k in range(-6,7):
            if 0<=band_y+k<SH:
                bd.line([(0,band_y+k),(SW,band_y+k)],fill=(143,214,114,max(0,5-abs(k)//2)))
        sc.alpha_composite(band)
    return sc,level

def render(t):
    im=base(t)
    sc,level=screen(t)
    im.paste(sc,(SCREEN_X,SCREEN_Y),SMASK)
    led=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(led)
    cx,cy=round(TX+668*S),round(TY+584*S)
    bright=level>.1
    d.ellipse((cx-7,cy-7,cx+7,cy+7),fill=LIME+(75,) if bright else (22,34,12,255))
    if bright:
        im.alpha_composite(led.filter(ImageFilter.GaussianBlur(4)))
        ImageDraw.Draw(im).ellipse((cx-4,cy-4,cx+4,cy+4),fill=(143,229,67))
        ImageDraw.Draw(im).ellipse((cx-1,cy-2,cx+1,cy),fill=(209,255,144))
    return im.convert('RGB')

if __name__=='__main__':
    poster=render(0)
    poster.save(ASSETS/'bomfixm-tv.png')
    frames=[render(i*.08) for i in range(105)]
    palette=Image.new('RGB',(W*4,H))
    for i,n in enumerate((0,15,41,69)):
        palette.paste(frames[n],(i*W,0))
    palette=palette.quantize(colors=192,method=Image.Quantize.MEDIANCUT)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/'bomfixm-tv.gif',save_all=True,append_images=frames[1:],duration=80,
                   loop=0,optimize=True,disposal=1)
    (ROOT/'README.md').write_text(
      '<p align="center">\n'
      '  <img src="assets/bomfixm-tv.gif" width="960" '
      'alt="TV retrô animada de Mateus Bomfim (@bomfixm). '
      'Engenharia de Software na FIAP; Desenvolvimento Web e IA.">\n'
      '</p>\n',encoding='utf-8')
    (ROOT/'COMO_USAR.txt').write_text(
      'CARD ANIMADO — @bomfixm\n\n'
      '1. Extraia este pacote.\n'
      '2. No GitHub, crie (ou abra) o repositório público chamado bomfixm.\n'
      '   Ele precisa pertencer à conta bomfixm para aparecer no perfil.\n'
      '3. Envie o README.md e a pasta assets para a raiz desse repositório.\n'
      '   Se já existir um README, substitua seu conteúdo somente se desejar.\n'
      '4. Confirme o envio com Commit changes.\n\n'
      'O README exibe apenas a TV animada. Não tem link para o portfólio.\n'
      'A pasta source contém o desenho editável em Python. Não precisa enviá-la.\n'
      'O PNG em assets é uma alternativa estática. O README usa o GIF.\n\n'
      'Animação: ciclo de 8,4 segundos, TV ligando, luz verde, cursor piscando,\n'
      'colagens com movimento discreto e falhas breves na imagem.\n',encoding='utf-8')
    # Inspect the encoded output, including palette and frame timing.
    gif=Image.open(ASSETS/'bomfixm-tv.gif')
    durations=[]
    for i in range(gif.n_frames):
        gif.seek(i)
        durations.append(gif.info.get('duration',0))
    report={'size':gif.size,'frames':gif.n_frames,'duration_ms':sum(durations),
            'loop':gif.info.get('loop'),'bytes':(ASSETS/'bomfixm-tv.gif').stat().st_size}
    print(json.dumps(report))
    # A small QA sheet is an intermediate file, excluded from delivery.
    sheet=Image.new('RGB',(960,975),BG)
    for k,t in enumerate((0,.88,1.12,1.52,3.28,6.0)):
        tile=render(t).resize((480,325),Image.Resampling.LANCZOS)
        sheet.paste(tile,((k%2)*480,(k//2)*325))
    sheet.save(ROOT.parent/'bomfixm-tv-qa.png')
    with zipfile.ZipFile(ROOT.parent/'bomfixm-github-tv.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(ROOT))
