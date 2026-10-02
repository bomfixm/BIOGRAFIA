// Render the image-edited artwork with a precise native QR component and animation.
// Requires Node.js, @napi-rs/canvas and FFmpeg. No network calls.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const require=createRequire(import.meta.url);
const canvasModule=require.resolve('@napi-rs/canvas',{
  paths:[process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES||'',process.cwd()]
});
const {createCanvas,loadImage}=require(canvasModule);
const source=path.dirname(fileURLToPath(import.meta.url));
const root=path.dirname(source);
const assets=path.join(root,'assets');
const temporary=path.join(path.dirname(root),'bomfixm-pastel-frames');
fs.mkdirSync(temporary,{recursive:true});
const art=await loadImage(path.join(source,'pass-art.png'));
const qr=await loadImage(path.join(source,'github-qr.png'));
const portrait=await loadImage(path.join(source,'portrait-original.jpg'));
const composed=createCanvas(art.width,art.height);
const cc=composed.getContext('2d');
cc.drawImage(art,0,0);
// Insert the actual uploaded photograph as a native image component.
// Only cropping, scaling and the small tilt of the printed photo frame apply.
// No generated portrait, retouch, facial reconstruction or color filter is used.
cc.save();
cc.beginPath();
cc.moveTo(99,100);
cc.lineTo(347,107);
cc.lineTo(336,451);
cc.lineTo(88,444);
cc.closePath();
cc.clip();
const pw=248,ph=344;
cc.transform(1,7/pw,-11/ph,1,99,100);
const cropHeight=portrait.height*.88;
const cropWidth=cropHeight*pw/ph;
const cropX=(portrait.width-cropWidth)/2;
const cropY=portrait.height*.06;
cc.drawImage(portrait,cropX,cropY,cropWidth,cropHeight,0,0,pw,ph);
cc.restore();
// Keep the existing foreground labels on top of the original photograph.
for(const points of [
  [[136,407],[410,398],[410,468],[136,457]],
  [[47,441],[133,428],[158,518],[78,532]],
  [[337,369],[387,369],[387,425],[337,425]]
]){
  cc.save();
  cc.beginPath();
  points.forEach(([x,y],i)=>i?cc.lineTo(x,y):cc.moveTo(x,y));
  cc.closePath();
  cc.clip();
  cc.drawImage(art,0,0);
  cc.restore();
}
// Real encoded QR data, with a quiet zone and square pixels.
cc.imageSmoothingEnabled=false;
cc.drawImage(qr,364,825,410,410);
cc.imageSmoothingEnabled=true;
fs.writeFileSync(path.join(assets,'bomfixm-card-roxo.png'),composed.toBuffer('image/png'));
const width=900;
const scale=width/art.width;
const height=Math.round(art.height*scale);
for(let i=0;i<84;i++){
  const t=i/10;
  const frame=createCanvas(width,height);
  const ctx=frame.getContext('2d');
  ctx.scale(scale,scale);
  ctx.drawImage(composed,0,0);
  // Soft gloss moves across the paper; the portrait and QR stay fixed.
  const p=(t-2.0)/2.4;
  if(p>0 && p<1){
    ctx.save();
    ctx.beginPath();
    ctx.roundRect(42,66,1036,623,40);
    ctx.rect(75,95,280,360);
    ctx.roundRect(49,728,1018,625,40);
    ctx.rect(364,825,410,410);
    ctx.clip('evenodd');
    const x=-260+p*1640;
    const gradient=ctx.createLinearGradient(x-150,0,x+150,0);
    gradient.addColorStop(0,'rgba(255,255,255,0)');
    gradient.addColorStop(.5,'rgba(255,255,255,0.12)');
    gradient.addColorStop(1,'rgba(255,255,255,0)');
    ctx.fillStyle=gradient;
    ctx.fillRect(x-150,65,300,1290);
    ctx.restore();
  }
  const pulse=.03+.035*(.5+.5*Math.sin(2*Math.PI*t/4.2));
  for(const [x,y] of [[643,131],[1026,196],[1030,867],[205,1080]]){
    const radial=ctx.createRadialGradient(x,y,0,x,y,40);
    radial.addColorStop(0,`rgba(255,255,233,${pulse})`);
    radial.addColorStop(1,'rgba(255,255,233,0)');
    ctx.fillStyle=radial;
    ctx.fillRect(x-40,y-40,80,80);
  }
  fs.writeFileSync(path.join(temporary,`frame-${String(i).padStart(3,'0')}.png`),frame.toBuffer('image/png'));
}
const encoded=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-y','-framerate','10',
  '-i',path.join(temporary,'frame-%03d.png'),
  '-filter_complex','[0:v]split[a][b];[a]palettegen=stats_mode=full:max_colors=256[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle',
  '-loop','0',path.join(assets,'bomfixm-card-roxo.gif')],{stdio:'inherit'});
if(encoded.status!==0)throw new Error(`GIF encoding failed: ${encoded.status}`);
fs.writeFileSync(path.join(root,'README.md'),`<p align="center">\n  <img src="assets/bomfixm-tv.gif" width="960" alt="TV retrô animada de Mateus Bomfim (@bomfixm). Engenharia de Software na FIAP; Desenvolvimento Web e IA.">\n  <br>\n  <img src="assets/bomfixm-card-roxo.gif" width="780" alt="Passe criativo animado de Mateus Bomfim: frente e verso em lavanda pastel. GitHub @bomfixm, Engenharia de Software na FIAP e QR para seu perfil no GitHub.">\n</p>\n`);
fs.writeFileSync(path.join(root,'COMO_USAR.txt'),`TV + PASSE PASTEL — @bomfixm\n\n1. Extraia este pacote.\n2. No GitHub, crie (ou abra) o repositório público chamado bomfixm, na conta bomfixm.\n3. Envie o README.md e a pasta assets para a raiz desse repositório. Se já usa a versão anterior, atualize o README e os arquivos bomfixm-card-roxo.gif e bomfixm-card-roxo.png.\n4. Confirme o envio com Commit changes.\n\nO passe aparece abaixo da TV. A arte traz frente e verso, com cores pastel e detalhes de código/design.\nAnimação: brilho suave no papel e nos adesivos. A foto e os textos permanecem legíveis.\nA foto original foi aplicada diretamente, apenas com recorte e ajuste ao enquadramento.\nO QR é gerado com os dados https://github.com/bomfixm.\nOs PNGs são alternativas estáticas. O README usa os GIFs.\nNão é preciso enviar a pasta source para o GitHub.\n\nA arte-base foi editada a partir da referência e personalizada com os dados profissionais fornecidos.\nPara regenerar o passe: Node.js, @napi-rs/canvas e FFmpeg; execute source/render_pass.mjs.\n`);
console.log(JSON.stringify({width,height,frames:84,duration_ms:8400,bytes:fs.statSync(path.join(assets,'bomfixm-card-roxo.gif')).size}));
