import streamlit as st

# 페이지 설정
st.set_page_config(page_title="Missile VFX Code", layout="centered")

st.title("🚀 미사일 발사 & 폭발 이펙트 (코드 구현)")
st.write("아래 화면을 **한 번 클릭한 후**, **스페이스바**를 눌러 미사일을 발사해보세요!")

# --- HTML5 Canvas + JS 기반 VFX 엔진 주입 ---
game_html = """
<div id="vfx-container" tabindex="0" style="outline:none; text-align:center; cursor:pointer;">
    <canvas id="vfxCanvas" width="700" height="500" style="background-color:#050510; border:3px solid #4a5568; border-radius: 12px;"></canvas>
    <div style="color: #cbd5e1; margin-top: 8px; font-family: sans-serif; font-size: 14px;">
        🎮 클릭 후 스페이스바를 눌러 미사일을 발사하세요
    </div>
</div>

<script>
const canvas = document.getElementById('vfxCanvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('vfx-container');

// 포커스 자동 잡기
container.focus();

// 상태 정의
let player = { x: 350, y: 450 };
let missiles = [];
let explosions = [];
let particles = [];

// 키 입력 상태 추적
let spacePressed = false;
window.addEventListener('keydown', e => {
    if (e.key === " ") {
        spacePressed = true;
        e.preventDefault(); // 스크롤 방지
    }
});
window.addEventListener('keyup', e => {
    if (e.key === " ") spacePressed = false;
});

// 공격 딜레이 제어
let lastShotTime = 0;
const shotCooldown = 150; // ms

function fireMissile() {
    const now = Date.now();
    if (now - lastShotTime < shotCooldown) return;
    lastShotTime = now;

    missiles.push({
        x: player.x,
        y: player.y - 20,
        speed: 8,
        life: 1.0 // 미사일 수명
    });
}

function createExplosion(x, y, color) {
    explosions.push({
        x: x,
        y: y,
        life: 1.0, // 폭발 수명
        maxRadius: 30 + Math.random() * 20,
        color: color || '#ff4500'
    });

    // 파티클 추가
    for (let i = 0; i < 20; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 6,
            vy: (Math.random() - 0.5) * 6,
            size: Math.random() * 3 + 1,
            life: 1.0,
            color: color || '#ffca00'
        });
    }
}

// 루프 업데이트
function update() {
    if (spacePressed) fireMissile();

    // 미사일 업데이트
    missiles.forEach((m, index) => {
        m.y -= m.speed;
        m.life -= 0.01; // 수명 감소

        // 화면 밖으로 나가거나 수명이 다하면 폭발 생성
        if (m.y < 50 || m.life <= 0) {
            createExplosion(m.x, m.y);
            missiles.splice(index, 1);
        }
    });

    // 폭발 업데이트
    explosions.forEach((e, index) => {
        e.life -= 0.02;
        if (e.life <= 0) {
            explosions.splice(index, 1);
        }
    });

    // 파티클 업데이트
    particles.forEach((p, index) => {
        p.x += p.vx;
        p.y += p.vy;
        p.life -= 0.03;
        if (p.life <= 0) {
            particles.splice(index, 1);
        }
    });
}

// 그리기 (Canvas Rendering)
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. 미사일 발사대 (간단한 형태)
    ctx.fillStyle = "#e2e8f0";
    ctx.fillRect(player.x - 10, player.y - 10, 20, 20);

    // 2. 미사일 그리기
    missiles.forEach(m => {
        ctx.save();
        ctx.translate(m.x, m.y);
        
        // 미사일 본체
        ctx.fillStyle = "#cbd5e1";
        ctx.fillRect(-2, -10, 4, 15);

        // 발사 화염 (글로우 효과 포함)
        ctx.shadowBlur = 10;
        ctx.shadowColor = "#ffca00";
        ctx.fillStyle = "#ff4500";
        ctx.beginPath();
        ctx.moveTo(-2, 5);
        ctx.lineTo(0, 15 + Math.random() * 5);
        ctx.lineTo(2, 5);
        ctx.fill();
        ctx.restore();
    });

    // 3. 폭발 효과 그리기
    explosions.forEach(e => {
        ctx.save();
        ctx.translate(e.x, e.y);
        
        // 폭발 글로우
        ctx.shadowBlur = 20 * e.life;
        ctx.shadowColor = e.color;
        
        // 폭발 원 (수명에 따라 크기와 투명도 조절)
        ctx.globalAlpha = e.life;
        ctx.fillStyle = e.color;
        ctx.beginPath();
        ctx.arc(0, 0, e.maxRadius * (1 - e.life), 0, Math.PI * 2);
        ctx.fill();
        
        ctx.restore();
    });

    // 4. 파티클 그리기
    particles.forEach(p => {
        ctx.save();
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
        ctx.restore();
    });
}

// 메인 루프 실행
function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

loop();
</script>
"""

# HTML 컴포넌트 실행
st.components.v1.html(game_html, height=550)
