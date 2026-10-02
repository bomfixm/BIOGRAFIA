"""Draw the animated profile pass and place it below the approved TV.

Uses the original portrait supplied by the user's portfolio. Typography,
geometry and animation are code-native; no generated photograph is involved.
Python 3, Pillow and NumPy are required only to regenerate the assets.
"""
from pathlib import Path
from hashlib import sha256
import math
import zipfile
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageChops

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'
WIDTH,HEIGHT=960,520
CW,CH=744,422
BG=(7,14,10)
INK=(28,35,22)
BLUE=(66,80,178)
LIME=(183,245,56)
SCALE=2

def font(size,kind='mono'):
    paths={
      'mono':'/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
      'bold':'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
      'sans':'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
      'signature':'/usr/share/fonts/opentype/urw-base35/Z003-MediumItalic.otf',
    }
    return ImageFont.truetype(paths[kind],round(size*SCALE))

def xy(values):return tuple(round(v*SCALE) for v in values)

def star(draw,cx,cy,r,points=5):
    p=[]
    for i in range(points*2):
        a=-math.pi/2+i*math.pi/points
        rr=r if i%2==0 else r*.42
        p.append((SCALE*(cx+math.cos(a)*rr),SCALE*(cy+math.sin(a)*rr)))
    draw.polygon(p,fill=LIME,outline=(111,134,43))

def text(d,position,value,size=16,kind='mono',fill=INK):
    d.text(xy(position),value,font=font(size,kind),fill=fill)

def title(d,position,value,size=42):
    # Compact display type, matching the credential's condensed headline.
    f=font(size,'bold')
    bbox=f.getbbox(value)
    tile=Image.new('RGBA',(bbox[2]+5*SCALE,(bbox[3]-bbox[1])+4*SCALE))
    ImageDraw.Draw(tile).text((0,-bbox[1]),value,font=f,fill=INK)
    tile=tile.resize((round(tile.width*.89),tile.height),Image.Resampling.LANCZOS)
    d._image.alpha_composite(tile,xy(position))

def make_pass():
    rng=np.random.default_rng(31)
    yy,xx=np.mgrid[0:CH*SCALE,0:CW*SCALE]
    # Pale yellow paper with restrained mint/lilac holographic shapes.
    blend=np.clip(xx/(CW*SCALE),0,1)
    start=np.array([240,236,185.])
    end=np.array([227,236,201.])
    arr=start[None,None,:]*(1-blend[:,:,None])+end[None,None,:]*blend[:,:,None]
    arr=arr+rng.normal(0,.8,(CH*SCALE,CW*SCALE,1))
    im=Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB').convert('RGBA')
    art=Image.new('RGBA',im.size)
    ad=ImageDraw.Draw(art)
    ad.polygon([xy(p) for p in [(158,0),(206,0),(458,422),(403,422)]],fill=(129,197,154,47))
    ad.polygon([xy(p) for p in [(554,0),(623,0),(710,422),(650,422)]],fill=(131,134,228,37))
    ad.polygon([xy(p) for p in [(0,320),(0,287),(452,121),(491,143)]],fill=(180,212,156,45))
    ad.arc(xy((101,263,418,517)),189,334,fill=(91,165,161,37),width=40*SCALE)
    im=Image.alpha_composite(im,art)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle(xy((1.5,1.5,CW-1.5,CH-1.5)),22*SCALE,outline=(51,62,41),width=4*SCALE)
    d.rounded_rectangle(xy((6,6,CW-6,CH-6)),17*SCALE,outline=(255,253,216),width=1*SCALE)

    # Photo is reused as-is, fitted to a simple white photograph border.
    photo=Image.open(ROOT/'source/portrait.webp').convert('RGB')
    photo=ImageOps.fit(photo,(196*SCALE,245*SCALE),method=Image.Resampling.LANCZOS)
    photo_frame=Image.new('RGBA',(214*SCALE,265*SCALE),(248,247,229))
    photo_frame.alpha_composite(photo.convert('RGBA'),(9*SCALE,9*SCALE))
    photo_frame=photo_frame.rotate(1.8,Image.Resampling.BICUBIC,expand=True)
    sh=Image.new('RGBA',photo_frame.size,(0,0,0,0))
    sh.putalpha(photo_frame.getchannel('A').point(lambda a:round(a*.2)))
    im.alpha_composite(sh,xy((29,39)))
    im.alpha_composite(photo_frame,xy((24,32)))
    d=ImageDraw.Draw(im)

    title(d,(268,35),'CREATIVE',42)
    text(d,(269,86),'DEVELOPER PASS',23,'bold')
    text(d,(654,29),'code:',14,fill=BLUE)
    text(d,(663,49),'#01',21,'mono',BLUE)
    text(d,(535,42),'code.',11,fill=BLUE)
    text(d,(535,56),'edit.',11,fill=BLUE)
    text(d,(535,70),'design.',11,fill=BLUE)
    star(d,713,92,11)
    star(d,32,19,10)

    # Field boxes keep the profile easy to read below the animated TV.
    grid=Image.new('RGBA',im.size)
    gd=ImageDraw.Draw(grid)
    gd.rectangle(xy((267,137,714,358)),fill=(244,245,212,95),outline=(95,111,80,220),width=1*SCALE)
    for y in (188,251,311):
        gd.line([xy((267,y)),xy((714,y))],fill=(95,111,80,210),width=1*SCALE)
    gd.line([xy((498,311)),xy((498,358))],fill=(95,111,80,210),width=1*SCALE)
    im=Image.alpha_composite(im,grid)
    d=ImageDraw.Draw(im)
    text(d,(275,143),'full name:',11,fill=BLUE)
    text(d,(275,161),'MATEUS BOMFIM NASCIMENTO',19,'bold')
    text(d,(275,195),'roles:',11,fill=BLUE)
    text(d,(275,213),'DEVELOPER · VIDEO EDITOR',17,'bold')
    text(d,(275,232),'DESIGNER',17,'bold')
    text(d,(275,258),'signature ( authorised only )',10,fill=BLUE)
    text(d,(277,270),'Mateus',38,'signature')
    text(d,(275,317),'github:',11,fill=BLUE)
    text(d,(275,334),'@bomfixm',16,'bold')
    text(d,(506,317),'education:',11,fill=BLUE)
    text(d,(506,334),'FIAP',16,'bold')

    # The yellow strip and a small circular stamp echo the original pass.
    tag=Image.new('RGBA',(224*SCALE,34*SCALE),(0,0,0,0))
    td=ImageDraw.Draw(tag)
    td.rectangle((0,0,tag.width-1,tag.height-1),fill=(244,193,56))
    td.text((8*SCALE,4*SCALE),'code. edit. design.',font=font(16,'bold'),fill=INK)
    tag=tag.rotate(3,Image.Resampling.BICUBIC,expand=True)
    im.alpha_composite(tag,xy((24,282)))
    d=ImageDraw.Draw(im)
    d.ellipse(xy((126,317,191,357)),fill=(193,161,208,145),outline=(132,103,154),width=1*SCALE)
    text(d,(143,323),'MB',15,'bold',(68,61,88))
    text(d,(135,340),'CREATIVE',8,'mono',(68,61,88))
    star(d,228,334,10)

    # Decorative barcode, derived only from the public GitHub handle.
    bits=''.join(f'{b:08b}' for b in sha256(b'bomfixm').digest())[:115]
    for i,b in enumerate(bits):
        if b=='1':
            x=29+i*1.6
            d.rectangle(xy((x,369,x+.95,397)),fill=INK)
    text(d,(89,400),'bomfixm',8)
    text(d,(269,386),'SOFTWARE ENGINEERING STUDENT @ FIAP',14,'bold',(58,78,175))
    # Mask the paper itself to its rounded outline.
    mask=Image.new('L',im.size)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,im.width-1,im.height-1),22*SCALE,fill=255)
    im.putalpha(mask)
    return im

CARD=make_pass()

def render(t):
    card=CARD.copy()
    # A subtle gloss sweep every loop; text and identity never change.
    phase=(t-2.0)/1.6
    if 0<phase<1:
        gloss=Image.new('RGBA',card.size)
        gd=ImageDraw.Draw(gloss)
        center=(-160+(CW+280)*phase)*SCALE
        for k in range(-100,101,4):
            alpha=round(11*max(0,1-abs(k)/100))
            gd.polygon([(center+k*SCALE,0),(center+(k+4)*SCALE,0),
                        (center+(k-168)*SCALE,CH*SCALE),(center+(k-172)*SCALE,CH*SCALE)],
                       fill=(247,251,255,alpha))
        gloss.putalpha(ImageChops.multiply(gloss.getchannel('A'),card.getchannel('A')))
        card=Image.alpha_composite(card,gloss)
    # A small green status marker is a visual detail, not a live indicator.
    cd=ImageDraw.Draw(card)
    if int(t*2)%2==0:
        cd.rectangle(xy((478,339,484,346)),fill=(126,171,57))
    card=card.rotate(1.05,Image.Resampling.BICUBIC,expand=True)
    card=card.resize((card.width//SCALE,card.height//SCALE),Image.Resampling.LANCZOS)
    shadow=Image.new('RGBA',card.size)
    shadow.putalpha(card.getchannel('A').point(lambda a:round(a*.33)))
    out=Image.new('RGBA',(WIDTH,HEIGHT),BG+(255,))
    px=(WIDTH-card.width)//2
    py=37+round(2*math.sin(2*math.pi*t/8.4))
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)),(px+6,py+8))
    out.alpha_composite(card,(px,py))
    return out.convert('RGB')

def package():
    (ROOT/'README.md').write_text(
      '<p align="center">\n'
      '  <img src="assets/bomfixm-tv.gif" width="960" '
      'alt="TV retrô animada de Mateus Bomfim (@bomfixm). '
      'Engenharia de Software na FIAP; Desenvolvimento Web e IA.">\n'
      '  <br>\n'
      '  <img src="assets/bomfixm-pass.gif" width="960" '
      'alt="Passe criativo animado de Mateus Bomfim Nascimento: '
      'Developer, Video Editor e Designer. GitHub @bomfixm. '
      'Estudante de Engenharia de Software na FIAP.">\n'
      '</p>\n',encoding='utf-8')
    (ROOT/'COMO_USAR.txt').write_text(
      'TV + CARD ANIMADOS — @bomfixm\n\n'
      '1. Extraia este pacote.\n'
      '2. No GitHub, crie (ou abra) o repositório público chamado bomfixm.\n'
      '   Ele precisa pertencer à conta bomfixm para aparecer no perfil.\n'
      '3. Envie o README.md e a pasta assets para a raiz desse repositório.\n'
      '   Se já usa a versão anterior, atualize o README e envie os novos arquivos do card.\n'
      '4. Confirme o envio com Commit changes.\n\n'
      'O README já exibe o card abaixo da TV. Ambos são GIFs em loop.\n'
      'Não há link para o portfólio e não é preciso adicionar outras seções.\n'
      'Os PNGs em assets são alternativas estáticas. O README usa os GIFs.\n'
      'A pasta source contém o desenho editável e a foto original do passe.\n'
      'Não precisa enviá-la para o GitHub.\n\n'
      'Para regenerar: Python 3, Pillow e NumPy.\n'
      'Execute source/generate_card.py para a TV e source/generate_pass.py para o card.\n',encoding='utf-8')
    with zipfile.ZipFile(ROOT.parent/'bomfixm-github-tv.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ROOT.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                z.write(p,p.relative_to(ROOT))

if __name__=='__main__':
    poster=render(0)
    poster.save(ASSETS/'bomfixm-pass.png')
    frames=[render(i*.08) for i in range(105)]
    palette=Image.new('RGB',(WIDTH*3,HEIGHT))
    for j,k in enumerate((0,32,39)):
        palette.paste(frames[k],(j*WIDTH,0))
    palette=palette.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    frames=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
    frames[0].save(ASSETS/'bomfixm-pass.gif',save_all=True,append_images=frames[1:],
                   duration=80,loop=0,disposal=1,optimize=True)
    gif=Image.open(ASSETS/'bomfixm-pass.gif')
    total=0
    for i in range(gif.n_frames):
        gif.seek(i)
        total+=gif.info.get('duration',0)
    print(json.dumps({'size':gif.size,'frames':gif.n_frames,'duration_ms':total,
                      'loop':gif.info.get('loop'),'bytes':(ASSETS/'bomfixm-pass.gif').stat().st_size}))
    package()
    tv=Image.open(ASSETS/'bomfixm-tv.png').convert('RGB')
    preview=Image.new('RGB',(WIDTH,tv.height+poster.height),BG)
    preview.paste(tv,(0,0))
    preview.paste(poster,(0,tv.height))
    preview.save(ROOT.parent/'bomfixm-profile-preview.png')
