
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

    particles.forEach(p => {
        rect(p.x, p.y, 3, 3, p.col);
    });

    if (state === 'title') {

        overlay(
            'PIXEL DEFENDER',
            'START 버튼 또는 ENTER를 눌러 시작',
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

    // 오버레이보다 플레이어를 나중에 그려 시작 화면에서도 보이게 함
    if (
        player &&
        (
            player.inv === 0 ||
            Math.floor(frame / 5) % 2 === 0
        )
    ) {
        ship(player.x, player.y);
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
$('start').onclick = reset;

// 게임 화면을 클릭하면 키보드 조작을 받을 수 있도록 포커스
c.setAttribute('tabindex', '0');
c.addEventListener('pointerdown', () => c.focus());

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
