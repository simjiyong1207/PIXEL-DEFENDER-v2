
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="PIXEL DEFENDER",
    page_icon="👾",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
.stApp {
    background: #090d1b;
    color: #e8f1ff;
}
h1 {
    font-family: 'Press Start 2P', monospace !important;
    color: #73fbd3;
}
.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("PIXEL DEFENDER")
st.caption("BOSS UPDATE · 픽셀 우주 슈팅")

st.markdown("""
**조작법**

- ← → 또는 A / D : 이동
- SPACE : 발사
- P : 일시정지
- R : 다시 시작

적을 처치해 아이템을 얻고 무기를 강화하세요.
3레벨마다 강력한 보스가 등장합니다.
""")

game_html = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #090d1b;
    color: #e8f1ff;
    font-family: monospace;
}

.wrap {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 9px;
}

.hud {
    width: min(720px, 100%);
    display: flex;
    justify-content: space-between;
    gap: 6px;
    flex-wrap: wrap;
    color: #73fbd3;
    font-weight: bold;
    font-size: 13px;
}

canvas {
    width: min(720px, 100%);
    height: auto;
    image-rendering: pixelated;
    border: 3px solid #33466f;
    background: #070b18;
}

.controls {
    display: flex;
    gap: 8px;
    width: min(720px, 100%);
    justify-content: center;
    flex-wrap: wrap;
}

button {
    background: #172444;
    color: #e8f1ff;
    border: 2px solid #5474ad;
    padding: 11px 16px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 15px;
    touch-action: none;
}

button:active {
    background: #28518a;
}

.hint {
    color: #9fb0d6;
    font-size: 12px;
    text-align: center;
}
</style>
</head>

<body>

<div class="wrap">

<div class="hud">
    <span id="score">SCORE 0000</span>
    <span id="best">BEST 0000</span>
    <span id="lives">LIVES ♥♥♥</span>
    <span id="weapon">WEAPON 1</span>
</div>

<canvas id="game" width="480" height="560"></canvas>

<div class="controls">
    <button id="left">◀</button>
    <button id="fire">FIRE</button>
    <button id="right">▶</button>
    <button id="pause">Ⅱ</button>
    <button id="restart">↻</button>
</div>

<div class="hint">
← → / A D 이동 · SPACE 발사 · P 일시정지 · R 재시작
</div>

</div>

<script>
(() => {

const c = document.getElementById('game');
const g = c.getContext('2d');

const W = 480;
const H = 560;

g.imageSmoothingEnabled = false;

const $ = id => document.getElementById(id);

let keys = {};

let score = 0;
let best = Number(localStorage.getItem('pixelDefenderBest') || 0);

let lives = 3;
let level = 1;

let state = 'title';
let paused = false;
let frame = 0;

let player;
let shots;
let foeShots;
let enemies;
let drops;
let particles;
let boss;

let fireTick;
let enemyDir;

function reset() {

    score = 0;
    lives = 3;
    level = 1;
    frame = 0;

    paused = false;
    state = 'playing';
    boss = null;

    player = {
        x: W / 2 - 12,
        y: H - 55,
        w: 24,
        h: 20,
        speed: 4,
        inv: 0,
        weapon: 1
    };

    shots = [];
    foeShots = [];
    enemies = [];
    drops = [];
    particles = [];

    fireTick = 0;
    enemyDir = 1;

    wave();
    hud();
}

function wave() {

    enemies = [];
    boss = null;

    const count = Math.min(5 + level, 12);

    for (let i = 0; i < count; i++) {

        const type = (i + level) % 3;

        enemies.push({
            x: 25 + (i % 6) * 72,
            y: 55 + Math.floor(i / 6) * 48,
            w: type === 1 ? 28 : 24,
            h: 20,
            type: type,
            hp: type === 2 ? 2 : 1,
            phase: Math.random() * 6.28
        });
    }
}

function makeBoss() {

    boss = {
        x: W / 2 - 48,
        y: 55,
        w: 96,
        h: 54,
        hp: 18 + level * 3,
        max: 18 + level * 3,
        dir: 1,
        fire: 0
    };
}

function hud() {

    $('score').textContent =
        'SCORE ' + String(score).padStart(4, '0');

    $('best').textContent =
        'BEST ' + String(best).padStart(4, '0');

    $('lives').textContent =
        'LIVES ' +
        '♥'.repeat(lives) +
        '♡'.repeat(3 - lives);

    $('weapon').textContent =
        'WEAPON ' + player.weapon;
}

function rect(x, y, w, h, col) {

    g.fillStyle = col;

    g.fillRect(
        Math.round(x),
        Math.round(y),
        w,
        h
    );
}

function ship(x, y) {

    rect(x + 8, y, 8, 4, '#73fbd3');
    rect(x + 4, y + 4, 16, 4, '#73fbd3');
    rect(x, y + 8, 24, 8, '#73fbd3');

    rect(x + 4, y + 16, 5, 4, '#f8d66d');
    rect(x + 15, y + 16, 5, 4, '#f8d66d');

    rect(x + 9, y + 8, 6, 5, '#173d5a');
}

function enemyDraw(e) {

    const colors = [
        '#ff6b8a',
        '#b58cff',
        '#ffad5c'
    ];

    const col = colors[e.type];

    const x = e.x;
    const y = e.y + Math.sin(frame / 12 + e.phase) * 2;

    rect(x + 4, y, 16, 4, col);
    rect(x, y + 4, e.w, 8, col);

    rect(x + 4, y + 12, 5, 5, col);
    rect(x + e.w - 9, y + 12, 5, 5, col);

    rect(x + 5, y + 6, 4, 4, '#fff');
    rect(x + e.w - 9, y + 6, 4, 4, '#fff');

    rect(x + 6, y + 7, 2, 2, '#18213c');
    rect(x + e.w - 8, y + 7, 2, 2, '#18213c');

    if (e.hp > 1) {
        rect(x + 7, y - 5, 10, 2, '#f8d66d');
    }
}

function bossDraw() {

    if (!boss) return;

    const b = boss;

    rect(b.x + 18, b.y, 60, 8, '#9c66ff');
    rect(b.x + 5, b.y + 8, 86, 10, '#c17bff');

    rect(b.x, b.y + 18, 96, 22, '#8d4bd6');

    rect(b.x + 10, b.y + 40, 18, 14, '#8d4bd6');
    rect(b.x + 68, b.y + 40, 18, 14, '#8d4bd6');

    rect(b.x + 20, b.y + 18, 14, 10, '#fff');
    rect(b.x + 62, b.y + 18, 14, 10, '#fff');

    rect(b.x + 24, b.y + 21, 6, 6, '#18213c');
    rect(b.x + 66, b.y + 21, 6, 6, '#18213c');

    rect(90, 18, 300, 7, '#28365a');

    rect(
        90, 18,
        300 * (b.hp / b.max),
        7,
        '#ff6b8a'
    );

    g.fillStyle = '#f2d9ff';
    g.font = '12px monospace';
    g.textAlign = 'center';
    g.fillText('BOSS', W / 2, 13);
}

function burst(x, y, col) {

    for (let i = 0; i < 9; i++) {

        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            life: 22,
            col: col
        });
    }
}

function drop(x, y) {

    if (Math.random() < 0.28) {

        drops.push({
            x: x,
            y: y,
            w: 12,
            h: 12,
            kind: Math.random() < 0.7
                ? 'weapon'
                : 'life',
            vy: 1.5
        });
    }
}

function fire() {

    if (
        fireTick > 0 ||
        state !== 'playing' ||
        paused
    ) return;

    const mid = player.x + 11;

    if (player.weapon === 1) {

        shots.push({
            x: mid,
            y: player.y - 8,
            w: 3,
            h: 10,
            d: 1
        });

    } else if (player.weapon === 2) {

        shots.push(
            {
                x: mid - 7,
                y: player.y - 8,
                w: 3,
                h: 10,
                d: 1
            },
            {
                x: mid + 7,
                y: player.y - 8,
                w: 3,
                h: 10,
                d: 1
            }
        );

    } else {

        shots.push(
            {
                x: mid,
                y: player.y - 8,
                w: 3,
                h: 10,
                d: 2
            },
            {
                x: mid - 9,
                y: player.y,
                w: 3,
                h: 8,
                d: 1
            },
            {
                x: mid + 9,
                y: player.y,
                w: 3,
                h: 8,
                d: 1
            }
        );
    }

    fireTick = player.weapon === 3 ? 9 : 12;
}

function damagePlayer() {

    if (player.inv > 0) return;

    lives--;

    player.inv = 80;

    burst(
        player.x + 12,
        player.y,
        '#73fbd3'
    );

    hud();

    if (lives <= 0) {

        state = 'over';

        best = Math.max(best, score);

        localStorage.setItem(
            'pixelDefenderBest',
            best
        );

        hud();
    }
}

function overlap(a, b) {

    return (
        a.x < b.x + b.w &&
        a.x + a.w > b.x &&
        a.y < b.y + b.h &&
        a.y + a.h > b.y
    );
}

function update() {

    if (state !== 'playing' || paused) return;

    frame++;

    if (keys.ArrowLeft || keys.a || keys.A) {
        player.x -= player.speed;
    }

    if (keys.ArrowRight || keys.d || keys.D) {
        player.x += player.speed;
    }

    player.x = Math.max(
        4,
        Math.min(W - player.w - 4, player.x)
    );

    if (keys[' '] || keys.Space || keys.fire) {
        fire();
    }

    if (fireTick > 0) fireTick--;

    if (player.inv > 0) player.inv--;

    shots.forEach(s => s.y -= 8);
    shots = shots.filter(s => s.y > -15);

    foeShots.forEach(s => s.y += s.vy || 3);
    foeShots = foeShots.filter(s => s.y < H + 15);

    drops.forEach(d => d.y += d.vy);
    drops = drops.filter(d => d.y < H + 10);

    let edge = false;

    enemies.forEach(e => {

        e.x += enemyDir *
            (0.5 + level * 0.08) *
            (e.type === 1 ? 1.35 : 1);

        if (e.x < 5 || e.x + e.w > W - 5) {
            edge = true;
        }
    });

    if (edge) {

        enemyDir *= -1;

        enemies.forEach(e => e.y += 12);
    }

    if (
        frame % Math.max(35, 95 - level * 3) === 0 &&
        enemies.length
    ) {

        const e = enemies[
            Math.floor(Math.random() * enemies.length)
        ];

        foeShots.push({
            x: e.x + e.w / 2,
            y: e.y + e.h,
            w: 4,
            h: 9,
            vy: e.type === 1 ? 4 : 3
        });
    }

    for (let i = enemies.length - 1; i >= 0; i--) {

        const e = enemies[i];

        if (e.y + e.h >= player.y) {

            enemies.splice(i, 1);
            damagePlayer();
            continue;
        }

        for (let j = shots.length - 1; j >= 0; j--) {

            if (overlap(shots[j], e)) {

                e.hp -= shots[j].d;

                shots.splice(j, 1);

                if (e.hp <= 0) {

                    enemies.splice(i, 1);

                    score += e.type === 2 ? 20 : 10;

                    burst(
                        e.x + 12,
                        e.y,
                        '#ff6b8a'
                    );

                    drop(e.x + 8, e.y);

                    hud();
                }

                break;
            }
        }
    }

    if (boss) {

        boss.x += boss.dir * 1.5;

        if (
            boss.x < 5 ||
            boss.x + boss.w > W - 5
        ) {
            boss.dir *= -1;
        }

        boss.fire++;

        if (boss.fire > 48) {

            boss.fire = 0;

            foeShots.push(
                {
                    x: boss.x + 20,
                    y: boss.y + 48,
                    w: 6,
                    h: 12,
                    vy: 3.8
                },
                {
                    x: boss.x + 70,
                    y: boss.y + 48,
                    w: 6,
                    h: 12,
                    vy: 3.8
                }
            );
        }

        for (let j = shots.length - 1; j >= 0; j--) {

            if (overlap(shots[j], boss)) {

                boss.hp -= shots[j].d;

                shots.splice(j, 1);

                if (boss.hp <= 0) {

                    score += 150;

                    burst(
                        boss.x + 48,
                        boss.y + 25,
                        '#c17bff'
                    );

                    drop(
                        boss.x + 42,
                        boss.y + 40
                    );

                    boss = null;

                    level++;

                    wave();

                    hud();
                }

                break;
            }
        }

        if (boss && boss.y + boss.h >= player.y) {
            damagePlayer();
        }
    }

    foeShots.forEach(s => {

        if (overlap(s, player)) {

            s.y = H + 20;

            damagePlayer();
        }
    });

    for (let i = drops.length - 1; i >= 0; i--) {

        if (overlap(drops[i], player)) {

            const d = drops[i];

            if (d.kind === 'weapon') {

                player.weapon = Math.min(
                    3,
                    player.weapon + 1
                );

            } else {

                lives = Math.min(5, lives + 1);
            }

            burst(
                d.x,
                d.y,
                d.kind === 'weapon'
                    ? '#f8d66d'
                    : '#73fbd3'
            );

            drops.splice(i, 1);

            hud();
        }
    }

    if (enemies.length === 0 && !boss) {

        if (level % 3 === 0) {

            makeBoss();

        } else {

            level++;

            wave();

            hud();
        }
    }

    particles.forEach(p => {

        p.x += p.vx;
        p.y += p.vy;
        p.life--;
    });

    particles = particles.filter(p => p.life > 0);
}

function overlay(title, line1, line2) {

    rect(0, 0, W, H, '#070b18dd');

    g.textAlign = 'center';

    g.fillStyle = '#73fbd3';
    g.font = 'bold 24px monospace';

    g.fillText(
        title,
        W / 2,
        H / 2 - 36
    );

    g.fillStyle = '#e8f1ff';
    g.font = '14px monospace';

    g.fillText(
        line1,
        W / 2,
        H / 2 + 2
    );

    g.fillText(
        line2,
        W / 2,
        H / 2 + 28
    );
}

function draw() {

    g.clearRect(0, 0, W, H);

    for (let i = 0; i < 55; i++) {

        let x = (i * 97) % W;
        let y = (i * 139 + frame * 0.35) % H;

        rect(x, y, 2, 2, '#24385e');
    }

    for (let y = H - 110; y < H; y += 18) {
        rect(0, y, W, 1, '#111d39');
    }

    shots.forEach(s => {

        rect(s.x, s.y, s.w, s.h, '#f8d66d');
        rect(s.x + 1, s.y + 2, 1, 4, '#fff');
    });

    foeShots.forEach(s => {
        rect(s.x, s.y, s.w, s.h, '#ff795e');
    });

    enemies.forEach(enemyDraw);

    bossDraw();

    drops.forEach(d => {

        rect(
            d.x,
            d.y,
            12,
            12,
            d.kind === 'weapon'
                ? '#f8d66d'
                : '#73fbd3'
        );

        g.fillStyle = '#101a32';
        g.font = '10px monospace';
        g.textAlign = 'center';

        g.fillText(
            d.kind === 'weapon' ? 'W' : '+',
            d.x + 6,
            d.y + 10
        );
    });

    if (
        player &&
        (
            player.inv === 0 ||
            Math.floor(frame / 5) % 2 === 0
        )
    ) {
        ship(player.x, player.y);
    }

    particles.forEach(p => {
        rect(p.x, p.y, 3, 3, p.col);
    });

    if (state === 'title') {

        overlay(
            'PIXEL DEFENDER',
            'ENTER 또는 START 버튼을 눌러 시작',
            '적 처치 · 아이템 획득 · 보스 격파'
        );
    }

    if (state === 'over') {

        overlay(
            'GAME OVER',
            'SCORE ' + score + '   BEST ' + best,
            'R 또는 RESTART로 다시 도전'
        );
    }

    if (paused && state === 'playing') {

        overlay(
            'PAUSED',
            'P 또는 Ⅱ 버튼으로 계속',
            ''
        );
    }
}

function loop() {

    update();
    draw();

    requestAnimationFrame(loop);
}

function bind(id, key) {

    const el = $(id);

    const down = e => {
        e.preventDefault();
        keys[key] = true;
    };

    const up = e => {
        e.preventDefault();
        keys[key] = false;
    };

    el.addEventListener('pointerdown', down);
    el.addEventListener('pointerup', up);
    el.addEventListener('pointerleave', up);
    el.addEventListener('pointercancel', up);
}

bind('left', 'ArrowLeft');
bind('right', 'ArrowRight');
bind('fire', 'fire');

$('pause').onclick = () => {

    if (state === 'playing') {
        paused = !paused;
    }
};

$('restart').onclick = reset;

window.addEventListener('keydown', e => {

    if (
        ['ArrowLeft', 'ArrowRight', ' ', 'Space'].includes(e.key)
    ) {
        e.preventDefault();
    }

    keys[e.key] = true;

    if (e.key === 'Enter' && state !== 'playing') {
        reset();
    }

    if (
        (e.key === 'p' || e.key === 'P') &&
        state === 'playing'
    ) {
        paused = !paused;
    }

    if (e.key === 'r' || e.key === 'R') {
        reset();
    }
});

window.addEventListener('keyup', e => {
    keys[e.key] = false;
});

player = {
    x: W / 2 - 12,
    y: H - 55,
    w: 24,
    h: 20,
    speed: 4,
    inv: 0,
    weapon: 1
};

shots = [];
foeShots = [];
enemies = [];
drops = [];
particles = [];
boss = null;

hud();
loop();

})();
</script>

</body>
</html>
"""

components.html(
    game_html,
    height=690,
    scrolling=False
)

with st.expander("📦 게임 기능 안내"):

    st.markdown("""
    - 보스 몬스터: 3레벨마다 등장
    - 무기 업그레이드: 최대 3단계
    - 아이템 드롭: 무기 및 회복
    - 적 종류: 기본형, 빠른 적, 내구력 높은 적
    - 게임 시작 및 종료 화면
    - 최고 점수: 브라우저 localStorage 저장
    """)

st.caption(
    "PIXEL DEFENDER v2 · Streamlit + HTML Canvas"
)
