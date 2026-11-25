
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="PIXEL DEFENDER", page_icon="👾", layout="wide")

st.markdown("""
<style>
.stApp{background:#090d1b;color:#e8f1ff}
h1{color:#73fbd3}
.block-container{max-width:1000px;padding-top:2rem}
</style>
""",unsafe_allow_html=True)

st.title("PIXEL DEFENDER")
st.caption("INFINITE BOSS UPDATE · VERSION 6")

st.markdown("""
**조작법**
- WASD / 방향키: 이동
- SPACE: 발사
- Q: 궁극기 (15초 대기시간)
- P: 일시정지
- R: 다시 시작
""")

game_html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
*{box-sizing:border-box}
body{margin:0;background:#090d1b;color:#e8f1ff;font-family:monospace}
.wrap{width:100%;display:flex;flex-direction:column;align-items:center;gap:9px}
.hud{width:min(720px,100%);display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;color:#73fbd3;font-weight:bold;font-size:13px}
.life-display{background:#172444;color:#ff6b8a;border:2px solid #ff6b8a;border-radius:8px;padding:8px 12px;font-size:16px;font-weight:bold}
.ult-display{background:#30204d;color:#d9a5ff;border:2px solid #bd75ff;border-radius:8px;padding:8px 12px;font-size:13px;font-weight:bold}
canvas{width:min(720px,100%);height:auto;image-rendering:pixelated;border:3px solid #5474ad;background:#070b18;outline:none}
.controls{display:flex;gap:8px;width:min(720px,100%);justify-content:center;flex-wrap:wrap}
button{background:#172444;color:#e8f1ff;border:2px solid #5474ad;padding:11px 16px;border-radius:8px;font-weight:bold;font-size:15px;touch-action:none}
button:active{background:#28518a}
.hint{color:#9fb0d6;font-size:12px;text-align:center}
</style>
</head>
<body>
<div class="wrap">
<div class="hud">
<span id="score">SCORE 0000</span>
<span id="best">BEST 0000</span>
<span id="level">LEVEL 1</span>
<span id="lives" class="life-display">❤️ ❤️ ❤️ LIVES: 3</span>
<span id="weapon">WEAPON 1/5</span>
<span id="ult" class="ult-display">ULT READY (Q)</span>
</div>

<canvas id="game" width="480" height="560" tabindex="0"></canvas>

<div class="controls">
<button id="start">START</button>
<button id="left">◀</button>
<button id="up">▲</button>
<button id="fire">FIRE</button>
<button id="down">▼</button>
<button id="right">▶</button>
<button id="pause">Ⅱ</button>
<button id="restart">↻</button>
</div>
<div class="hint">WASD / 방향키 이동 · SPACE 발사 · Q 궁극기 · P 일시정지 · R 재시작</div>
</div>

<script>
(()=>{
const c=document.getElementById('game');
const g=c.getContext('2d');
const W=480,H=560;
g.imageSmoothingEnabled=false;
const $=id=>document.getElementById(id);

const MAX_LIVES=5;
const ULT_COOLDOWN=900;
const TRANSITION_TIME=90;

let keys={},score=0;
let best=Number(localStorage.getItem('pixelDefenderBest')||0);
let lives=3,level=1,state='title',paused=false,frame=0;
let player,shots=[],foeShots=[],enemies=[],drops=[],particles=[];
let boss=null,fireTick=0,enemyDir=1,shake=0;
let ultCooldown=0,ultEffect=0,transitionTimer=0;
let transitionText='';

function reset(){
 score=0;lives=3;level=1;frame=0;
 paused=false;state='playing';
 player={x:W/2-15,y:H-65,w:30,h:30,speed:5,inv:0,weapon:1};
 shots=[];foeShots=[];enemies=[];drops=[];particles=[];
 boss=null;fireTick=0;enemyDir=1;shake=0;
 ultCooldown=0;ultEffect=0;transitionTimer=0;
 wave();hud();c.focus();
}

function wave(){
 enemies=[];boss=null;
 const count=Math.min(6+level*2,24);
 for(let i=0;i<count;i++){
  const type=(i+level)%3;
  enemies.push({
   x:20+(i%6)*74,
   y:30+Math.floor(i/6)*32,
   w:type===1?28:24,h:20,type,
   hp:type===2?2+Math.floor(level/4):1+Math.floor(level/18),
   phase:Math.random()*6.28
  });
 }
}

function makeBoss(){
 const hp=35+level*9+Math.floor(level*level*.12);
 boss={x:W/2-48,y:48,w:96,h:54,hp,max:hp,dir:1,fire:0};
}

function nextLevel(){
 level++;
 enemies=[];
 boss=null;
 shots=[];
 foeShots=[];
 transitionTimer=TRANSITION_TIME;
 transitionText='LEVEL '+level;
 hud();
}

function startLevel(){
 if(level%3===0)makeBoss();
 else wave();
}

function hud(){
 $('score').textContent='SCORE '+String(score).padStart(4,'0');
 $('best').textContent='BEST '+String(best).padStart(4,'0');
 $('level').textContent='LEVEL '+level;
 $('lives').textContent='❤️ '.repeat(Math.max(0,lives))+' LIVES: '+lives;
 $('weapon').textContent='WEAPON '+player.weapon+'/5';
 $('ult').textContent=ultCooldown<=0?'ULT READY (Q)':'ULT '+Math.ceil(ultCooldown/60)+'s';
}

function rect(x,y,w,h,col){
 g.fillStyle=col;
 g.fillRect(Math.round(x),Math.round(y),w,h);
}

function ship(x,y){
 rect(x+13,y,4,5,'#ffffff');
 rect(x+10,y+5,10,5,'#9ffff0');
 rect(x+6,y+10,18,7,'#48e6d0');
 rect(x+2,y+17,26,7,'#20b9c5');
 rect(x,y+21,7,8,'#f8d66d');
 rect(x+23,y+21,7,8,'#f8d66d');
 rect(x+10,y+17,10,8,'#eaffff');
 rect(x+12,y+18,6,5,'#2873a8');
 rect(x+5,y+25,5,5,'#ff9b54');
 rect(x+20,y+25,5,5,'#ff9b54');
 const flame=4+(frame%6<3?4:0);
 rect(x+7,y+29,4,flame,'#ffcf5c');
 rect(x+19,y+29,4,flame,'#ffcf5c');
}

function enemyDraw(e){
 const colors=['#ff6b8a','#b58cff','#ffad5c'];
 const col=colors[e.type];
 const x=e.x,y=e.y+Math.sin(frame/12+e.phase)*2;
 rect(x+4,y,16,4,col);
 rect(x,y+4,e.w,8,col);
 rect(x+4,y+12,5,5,col);
 rect(x+e.w-9,y+12,5,5,col);
 rect(x+5,y+6,4,4,'#fff');
 rect(x+e.w-9,y+6,4,4,'#fff');
 rect(x+6,y+7,2,2,'#18213c');
 rect(x+e.w-8,y+7,2,2,'#18213c');
 if(e.hp>1)rect(x+7,y-5,10,2,'#f8d66d');
}

function bossDraw(){
 if(!boss)return;
 const b=boss;
 rect(b.x+18,b.y,60,8,'#9c66ff');
 rect(b.x+5,b.y+8,86,10,'#c17bff');
 rect(b.x,b.y+18,96,22,'#8d4bd6');
 rect(b.x+10,b.y+40,18,14,'#8d4bd6');
 rect(b.x+68,b.y+40,18,14,'#8d4bd6');
 rect(b.x+20,b.y+18,14,10,'#fff');
 rect(b.x+62,b.y+18,14,10,'#fff');
 rect(b.x+24,b.y+21,6,6,'#18213c');
 rect(b.x+66,b.y+21,6,6,'#18213c');
 rect(90,18,300,7,'#28365a');
 rect(90,18,300*(b.hp/b.max),7,'#ff6b8a');
 g.fillStyle='#f2d9ff';
 g.font='12px monospace';
 g.textAlign='center';
 g.fillText('BOSS',W/2,13);
}

function burst(x,y,col,amount=20){
 for(let i=0;i<amount;i++){
  const a=Math.random()*Math.PI*2,s=1+Math.random()*5;
  particles.push({
   x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,
   life:20+Math.random()*25,
   size:2+Math.random()*3,
   col:Math.random()<.25?'#fff':col
  });
 }
}

function drop(x,y){
 if(Math.random()<.20){
  drops.push({x,y,w:12,h:12,kind:Math.random()<.7?'weapon':'life',vy:1.5});
 }
}

function fire(){
 if(fireTick>0||state!=='playing'||paused||transitionTimer>0)return;
 const mid=player.x+player.w/2;

 const patterns={
  1:[{x:0,d:1}],
  2:[{x:-7,d:1},{x:7,d:1}],
  3:[{x:-10,d:1},{x:0,d:2},{x:10,d:1}],
  4:[{x:-16,d:1},{x:-8,d:1},{x:0,d:2},{x:8,d:1},{x:16,d:1}],
  5:[{x:-20,d:1},{x:-13,d:1},{x:-6,d:2},{x:0,d:3},{x:6,d:2},{x:13,d:1},{x:20,d:1}]
 };

 patterns[player.weapon].forEach(s=>{
  shots.push({x:mid+s.x-1,y:player.y-8,w:3,h:10,d:s.d});
 });

 fireTick=player.weapon>=4?7:11;
}

function useUltimate(){
 if(state!=='playing'||paused||ultCooldown>0||transitionTimer>0)return;

 ultCooldown=ULT_COOLDOWN;
 ultEffect=55;
 shake=13;

 foeShots=[];

 for(let i=enemies.length-1;i>=0;i--){
  const e=enemies[i];
  burst(e.x+e.w/2,e.y+e.h/2,'#73fbd3',35);
  score+=e.type===2?20:10;
  enemies.splice(i,1);
 }

 if(boss){
  burst(boss.x+boss.w/2,boss.y+boss.h/2,'#c17bff',55);
  boss.hp-=Math.max(50,Math.floor(boss.max*.30));

  if(boss.hp<=0){
   score+=150;
   burst(boss.x+48,boss.y+25,'#c17bff',80);
   drop(boss.x+42,boss.y+40);
   nextLevel();
  }
 }

 hud();

 if(enemies.length===0&&!boss&&transitionTimer===0){
  nextLevel();
 }
}

function damagePlayer(){
 if(player.inv>0||state!=='playing'||transitionTimer>0)return;
 lives--;
 player.inv=75;
 shake=9;
 burst(player.x+15,player.y+15,'#73fbd3',32);
 hud();

 if(lives<=0){
  burst(player.x+15,player.y+15,'#ff9b54',90);
  state='over';
  best=Math.max(best,score);
  localStorage.setItem('pixelDefenderBest',best);
  hud();
 }
}

function overlap(a,b){
 return a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y;
}

function enemyShoot(){
 if(!enemies.length)return;
 const shooters=Math.min(enemies.length,1+Math.floor(level/3));
 const bulletCount=1+Math.floor(level/5);
 const spread=Math.min(.16+level*.003,.42);

 for(let n=0;n<shooters;n++){
  const e=enemies[Math.floor(Math.random()*enemies.length)];
  for(let k=0;k<bulletCount;k++){
   const lane=k-(bulletCount-1)/2;
   foeShots.push({
    x:e.x+e.w/2-2,y:e.y+e.h,w:5,h:11,
    vx:lane*spread*5,
    vy:(e.type===1?4.8:4)+level*.10
   });
  }
 }
}

function update(){
 if(state!=='playing'||paused){
  if(state==='over'){
   particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.life--});
   particles=particles.filter(p=>p.life>0);
  }
  return;
 }

 frame++;

 if(ultCooldown>0){
  ultCooldown--;
  if(ultCooldown%60===0)hud();
 }
 if(ultEffect>0)ultEffect--;

 if(transitionTimer>0){
  transitionTimer--;
  particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.life--});
  particles=particles.filter(p=>p.life>0);

  if(transitionTimer===0){
   startLevel();
   hud();
  }
  return;
 }

 if(keys.ArrowLeft||keys.a||keys.A)player.x-=player.speed;
 if(keys.ArrowRight||keys.d||keys.D)player.x+=player.speed;
 if(keys.ArrowUp||keys.w||keys.W)player.y-=player.speed;
 if(keys.ArrowDown||keys.s||keys.S)player.y+=player.speed;

 player.x=Math.max(4,Math.min(W-player.w-4,player.x));
 player.y=Math.max(H*.43,Math.min(H-player.h-8,player.y));

 if(keys[' ']||keys.Space||keys.fire)fire();
 if(fireTick>0)fireTick--;
 if(player.inv>0)player.inv--;

 shots.forEach(s=>s.y-=8);
 shots=shots.filter(s=>s.y>-15);

 foeShots.forEach(s=>{s.x+=s.vx||0;s.y+=s.vy||3});
 foeShots=foeShots.filter(s=>s.y<H+15&&s.x>-20&&s.x<W+20);

 drops.forEach(d=>d.y+=d.vy);
 drops=drops.filter(d=>d.y<H+10);

 // 적들은 좌우로만 이동하고, 가장자리에 닿아도 아래로 내려오지 않음
 let edge=false;
 enemies.forEach(e=>{
  e.x+=enemyDir*(.9+level*.18+Math.pow(level,1.15)*.035)*(e.type===1?1.35:1);
  if(e.x<5||e.x+e.w>W-5)edge=true;
 });

 if(edge){
  enemyDir*=-1;
 }

 const fireInterval=Math.max(7,48-level*2);
 if(frame%fireInterval===0)enemyShoot();

 for(let i=enemies.length-1;i>=0;i--){
  const e=enemies[i];

  if(overlap(e,player)||e.y+e.h>=player.y){
   burst(e.x+e.w/2,e.y+e.h/2,'#ff6b8a',24);
   enemies.splice(i,1);
   damagePlayer();
   continue;
  }

  for(let j=shots.length-1;j>=0;j--){
   if(overlap(shots[j],e)){
    e.hp-=shots[j].d;
    shots.splice(j,1);

    if(e.hp<=0){
     enemies.splice(i,1);
     score+=e.type===2?20:10;
     burst(e.x+12,e.y,'#ff6b8a');
     drop(e.x+8,e.y);
     hud();
    }
    break;
   }
  }
 }

 if(boss){
  boss.x+=boss.dir*(2+level*.12);
  if(boss.x<5||boss.x+boss.w>W-5)boss.dir*=-1;

  boss.fire++;
  if(boss.fire>Math.max(8,30-level*1.2)){
   boss.fire=0;
   const count=3+Math.floor(level/3);

   for(let k=0;k<count;k++){
    const lane=k-(count-1)/2;
    foeShots.push({
     x:boss.x+boss.w/2-3,y:boss.y+boss.h-4,w:6,h:13,
     vx:lane*Math.min(.45+level*.018,2.2),
     vy:4.5+level*.12
    });
   }
  }

  for(let j=shots.length-1;j>=0;j--){
   if(overlap(shots[j],boss)){
    boss.hp-=shots[j].d;
    shots.splice(j,1);

    if(boss.hp<=0){
     score+=150;
     burst(boss.x+48,boss.y+25,'#c17bff',70);
     drop(boss.x+42,boss.y+40);
     nextLevel();
    }
    break;
   }
  }

  if(boss&&overlap(boss,player))damagePlayer();
 }

 foeShots.forEach(s=>{
  if(overlap(s,player)){
   s.y=H+20;
   damagePlayer();
  }
 });

 for(let i=drops.length-1;i>=0;i--){
  if(overlap(drops[i],player)){
   const d=drops[i];

   if(d.kind==='weapon'){
    player.weapon=Math.min(5,player.weapon+1);
   }else{
    lives=Math.min(MAX_LIVES,lives+1);
   }

   burst(d.x,d.y,d.kind==='weapon'?'#f8d66d':'#73fbd3');
   drops.splice(i,1);
   hud();
  }
 }

 if(enemies.length===0&&!boss&&transitionTimer===0){
  nextLevel();
 }

 particles.forEach(p=>{p.x+=p.vx;p.y+=p.vy;p.life--});
 particles=particles.filter(p=>p.life>0);
}

function overlay(title,line1,line2){
 rect(0,0,W,H,'#070b18dd');
 g.textAlign='center';
 g.fillStyle='#73fbd3';
 g.font='bold 24px monospace';
 g.fillText(title,W/2,H/2-36);
 g.fillStyle='#e8f1ff';
 g.font='14px monospace';
 g.fillText(line1,W/2,H/2+2);
 g.fillText(line2,W/2,H/2+28);
}

function drawUltimate(){
 if(ultEffect<=0)return;

 const progress=1-ultEffect/55;
 const radius=progress*390;
 const alpha=1-progress;

 g.save();
 g.globalAlpha=alpha;
 g.strokeStyle='#73fbd3';
 g.lineWidth=9-progress*6;
 g.shadowColor='#73fbd3';
 g.shadowBlur=30;

 g.beginPath();
 g.arc(player.x+15,player.y+15,radius,0,Math.PI*2);
 g.stroke();

 g.strokeStyle='#d9a5ff';
 g.lineWidth=4;
 g.beginPath();
 g.arc(player.x+15,player.y+15,radius*.78,0,Math.PI*2);
 g.stroke();

 g.restore();

 if(ultEffect>43){
  rect(0,0,W,H,'#b9fff4');
 }
}

function draw(){
 g.save();

 if(shake>0){
  g.translate((Math.random()-.5)*shake,(Math.random()-.5)*shake);
  shake--;
 }

 g.clearRect(-10,-10,W+20,H+20);

 for(let i=0;i<65;i++){
  const x=(i*97)%W,y=(i*139+frame*.45)%H;
  rect(x,y,2,2,'#24385e');
 }

 for(let y=H-110;y<H;y+=18)rect(0,y,W,1,'#111d39');

 shots.forEach(s=>{
  rect(s.x,s.y,s.w,s.h,'#f8d66d');
  rect(s.x+1,s.y+2,1,4,'#fff');
 });

 foeShots.forEach(s=>{
  rect(s.x,s.y,s.w,s.h,'#ff795e');
  rect(s.x+1,s.y+2,Math.max(2,s.w-2),4,'#ffd0a8');
 });

 enemies.forEach(enemyDraw);
 bossDraw();

 drops.forEach(d=>{
  rect(d.x,d.y,12,12,d.kind==='weapon'?'#f8d66d':'#73fbd3');
  g.fillStyle='#101a32';
  g.font='10px monospace';
  g.textAlign='center';
  g.fillText(d.kind==='weapon'?'W':'+',d.x+6,d.y+10);
 });

 particles.forEach(p=>rect(p.x,p.y,p.size,p.size,p.col));

 drawUltimate();

 if(state==='title'){
  overlay('PIXEL DEFENDER','START 또는 ENTER로 시작','Q: 궁극기 / 무기 최대 5단계');
 }

 if(state==='over'){
  overlay('GAME OVER','SCORE '+score+' BEST '+best,'R 또는 RESTART로 다시 도전');
 }

 if(paused&&state==='playing'){
  overlay('PAUSED','P 버튼으로 계속','');
 }

 if(transitionTimer>0&&state==='playing'){
  rect(0,0,W,H,'#070b18bb');

  g.textAlign='center';
  g.shadowColor='#73fbd3';
  g.shadowBlur=22;
  g.fillStyle='#73fbd3';
  g.font='bold 38px monospace';
  g.fillText(transitionText,W/2,H/2-20);

  g.shadowBlur=0;
  g.fillStyle='#ffffff';
  g.font='16px monospace';
  g.fillText('GET READY!',W/2,H/2+20);

  g.fillStyle='#b9c8e8';
  g.font='13px monospace';
  g.fillText('ENEMIES IN '+(transitionTimer/60).toFixed(1)+'s',W/2,H/2+48);
 }

 if(player&&(player.inv===0||Math.floor(frame/5)%2===0)){
  ship(player.x,player.y);
  g.strokeStyle='#b8fff4';
  g.lineWidth=2;
  g.strokeRect(player.x-2,player.y-2,player.w+4,player.h+5);
  g.shadowColor='#73fbd3';
  g.shadowBlur=12;
  g.strokeRect(player.x-1,player.y-1,player.w+2,player.h+2);
  g.shadowBlur=0;
 }

 g.restore();
}

function loop(){
 update();
 draw();
 requestAnimationFrame(loop);
}

function bind(id,key){
 const el=$(id);
 const down=e=>{e.preventDefault();keys[key]=true};
 const up=e=>{e.preventDefault();keys[key]=false};

 el.addEventListener('pointerdown',down);
 el.addEventListener('pointerup',up);
 el.addEventListener('pointerleave',up);
 el.addEventListener('pointercancel',up);
}

bind('left','ArrowLeft');
bind('right','ArrowRight');
bind('up','ArrowUp');
bind('down','ArrowDown');
bind('fire','fire');

$('start').onclick=reset;
$('restart').onclick=reset;
$('pause').onclick=()=>{if(state==='playing')paused=!paused};

c.addEventListener('pointerdown',()=>c.focus());

window.addEventListener('keydown',e=>{
 if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown',' ','Space'].includes(e.key)){
  e.preventDefault();
 }

 keys[e.key]=true;

 if(e.key==='Enter'&&state!=='playing')reset();
 if((e.key==='p'||e.key==='P')&&state==='playing')paused=!paused;
 if((e.key==='q'||e.key==='Q')&&!e.repeat)useUltimate();
 if(e.key==='r'||e.key==='R')reset();
});

window.addEventListener('keyup',e=>{keys[e.key]=false});

player={x:W/2-15,y:H-65,w:30,h:30,speed:5,inv:0,weapon:1};

shots=[];foeShots=[];enemies=[];drops=[];particles=[];
boss=null;

hud();
loop();
})();
</script>
</body>
</html>
"""

components.html(game_html,height=900,scrolling=False)

with st.expander("📦 게임 기능 안내"):
    st.markdown("""
    - 보스: 3레벨마다 등장
    - 무기: 최대 5단계
    - Q 궁극기: 에너지 파동 애니메이션, 일반 적과 탄환 제거, 보스 피해
    - 궁극기 재사용 대기시간: 15초
    - 레벨 전환: 중앙 레벨 표시 후 1.5초 뒤 적 생성
    - 체력: 기본 3개, 회복으로 최대 5개
    - 아이템: 무기 업그레이드 및 회복
    - 적 종류: 기본형, 빠른 적, 내구력 높은 적
    - 최고 점수: 브라우저 localStorage 저장
    """)

st.caption("PIXEL DEFENDER v6 · Streamlit + HTML Canvas")
