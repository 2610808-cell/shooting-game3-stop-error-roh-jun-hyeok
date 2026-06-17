import streamlit as st

# 페이지 설정
st.set_page_config(page_title="2D Boss Shooting Game with VFX", layout="centered")

st.title("🚀 2D 보스 슈팅 게임 (키보드 조작 & 폭발 이펙트)")
st.write("화면을 **한 번 클릭한 후**, **방향키/WASD**로 이동하고 **스페이스바**로 미사일을 발사하세요!")

# --- HTML5 Canvas + JS 기반 통합 게임 엔진 주입 ---
game_html = """
<div id="game-container" tabindex="0" style="outline:none; text-align:center; cursor:pointer;">
    <canvas id="gameCanvas" width="700" height="500" style="background-color:#050510; border:3px solid #4a5568; border-radius: 12px;"></canvas>
    <div style="color: #cbd5e1; margin-top: 8px; font-family: sans-serif; font-size: 14px;">
        🎮 이동: 방향키 또는 WASD | 공격: 스페이스바 (연사 가능)
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('game-container');

container.focus();

let player = { x: 350, y: 420 };
let enemies = [];
let boss = null;
let missiles = [];
let explosions = [];
let particles = [];

let score = 0;
let roundNum = 1;
let weaponLevel = 1;
let enemiesKilled = 0;
let enemiesRequired = 5;
let gameOver = false;

const keys = {};
window.addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key)) {
        e.preventDefault();
    }
});
window.addEventListener('keyup', e => {
    keys[e.key.toLowerCase()] = false;
});

let lastShotTime = 0;
const shotCooldown = 150; 

function spawnEnemy() {
    if (!boss && enemies.length < 4 && enemiesKilled < enemiesRequired) {
        enemies.push({
            x: Math.random() * 550 + 70,
            y: Math.random() * 50 + 30,
            speedX: (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 1.5 + 1),
            speedY: Math.random() * 0.4 + 0.6,
            hp: roundNum
        });
    }
}

function fireBullet() {
    const now = Date.now();
    if (now - lastShotTime < shotCooldown) return;
    lastShotTime = now;

    if (weaponLevel === 1) {
        missiles.push({ x: player.x + 25, y: player.y, vx: 0, vy: -7, damage: 1 });
    } else if (weaponLevel === 2) {
        missiles.push({ x: player.x + 15, y: player.y, vx: -1, vy: -7, damage: 1 });
        missiles.push({ x: player.x + 35, y: player.y, vx: 1, vy: -7, damage: 1 });
    } else {
        missiles.push({ x: player.x + 25, y: player.y, vx: 0, vy: -8, damage: 2 });
        missiles.push({ x: player.x + 10, y: player.y, vx: -2, vy: -7, damage: 1 });
        missiles.push({ x: player.x + 40, y: player.y, vx: 2, vy: -7, damage: 1 });
    }
}

function createExplosion(x, y, isBoss) {
    let pCount = isBoss ? 40 : 15;
    let radius = isBoss ? 55 : 25;
    let color = isBoss ? '#7928ca' : '#ff4500';

    explosions.push({
        x: x, y: y, life: 1.0, maxRadius: radius, color: color
    });

    for (let i = 0; i < pCount; i++) {
        particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * (isBoss ? 10 : 6),
            vy: (Math.random() - 0.5) * (isBoss ? 10 : 6),
            size: Math.random() * 3 + 1,
            life: 1.0,
            color: isBoss ? (Math.random() > 0.5 ? '#00ffff' : '#7928ca') : '#ffca00'
        });
    }
}

function update() {
    if (gameOver) {
        if (keys['r']) {
            player = { x: 350, y: 420 };
            enemies = []; boss = null; missiles = []; explosions = []; particles = [];
            score = 0; roundNum = 1; weaponLevel = 1; enemiesKilled = 0; enemiesRequired = 5;
            gameOver = false;
        }
        return;
    }

    if (keys['arrowleft'] || keys['a']) player.x = Math.max(30, player.x - 5);
    if (keys['arrowright'] || keys['d']) player.x = Math.min(620, player.x + 5);
    if (keys['arrowup'] || keys['w']) player.y = Math.max(220, player.y - 5);
    if (keys['arrowdown'] || keys['s']) player.y = Math.min(430, player.y - 5);
    if (keys[' ']) fireBullet();

    missiles.forEach((m, mIdx) => {
        m.x += m.vx;
        m.y += m.vy;

        if (m.y < 0 || m.x < 0 || m.x > 700) {
            missiles.splice(mIdx, 1);
            return;
        }

        if (boss && m.y <= boss.y + 60 && m.y >= boss.y && m.x >= boss.x && m.x <= boss.x + 140) {
            boss.hp -= m.damage;
            createExplosion(m.x, m.y, false);
            missiles.splice(mIdx, 1);

            if (boss.hp <= 0) {
                createExplosion(boss.x + 70, boss.y + 30, true);
                boss = null;
                roundNum++;
                enemiesKilled = 0;
                enemiesRequired += 3;
                if (weaponLevel < 3) weaponLevel++;
                score += 500;
            }
            return;
        }

        enemies.forEach((e, eIdx) => {
            if (Math.abs(m.x - e.x) < 25 && Math.abs(m.y - e.y) < 20) {
                e.hp -= m.damage;
                createExplosion(e.x, e.y, false);
                missiles.splice(mIdx, 1);

                if (e.hp <= 0) {
                    enemies.splice(eIdx, 1);
                    enemiesKilled++;
                    score += 100;
                }
            }
        });
    });

    enemies.forEach((enemy, index) => {
        enemy.y += enemy.speedY;
        enemy.x += enemy.speedX;

        if (enemy.x < 50 || enemy.x > 650) enemy.speedX *= -1;

        if (enemy.y >= player.y && enemy.y <= player.y + 40 && enemy.x >= player.x && enemy.x <= player.x + 50) {
            gameOver = true;
        }
        if (enemy.y > 500) enemies.splice(index, 1);
    });

    if (boss) {
        boss.x += 2.5 * boss.dir;
        if (boss.x <= 50 || boss.x >= 510) boss.dir *= -1;
    } else if (enemiesKilled >= enemiesRequired && enemies.length === 0) {
        boss = { x: 280, y: 50, hp: roundNum * 6, maxHp: roundNum * 6, dir: 1 };
    }

    explosions.forEach((e, index) => {
        e.life -= 0.04;
        if (e.life <= 0) explosions.splice(index, 1);
    });
    particles.forEach((p, index) => {
        p.x += p.vx; p.y += p.vy;
        p.life -= 0.03;
        if (p.life <= 0) particles.splice(index, 1);
    });

    if (Math.random() < 0.02) spawnEnemy();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = "#cbd5e1";
    ctx.font = "bold 16px sans-serif";
    ctx.fillText(`STAGE: ${roundNum}`, 20, 30);
    ctx.fillText(`WEAPON: LV ${weaponLevel}`, 150, 30);
    ctx.fillText(`SCORE: ${score}`, 280, 30);
    if (!boss) {
        ctx.fillText(`🎯 NEXT BOSS: ${Math.max(0, enemiesRequired - enemiesKilled)} REMAIN`, 500, 30);
    } else {
        ctx.fillStyle = "#ff3366";
        ctx.fillText(`⚠️ BOSS EMERGENCY!`, 500, 30);
    }

    if (gameOver) {
        ctx.fillStyle = "#ff3366";
        ctx.font = "bold 40px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("💥 GAME OVER", canvas.width / 2, canvas.height / 2);
        ctx.font = "18px sans-serif";
        ctx.fillStyle = "#ffffff";
        ctx.fillText(`최종 점수: ${score}점 | 재시작하려면 키보드 [ R ] 키를 누르세요`, canvas.width / 2, canvas.height / 2 + 50);
        ctx.textAlign = "left";
        return;
    }

    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.fillStyle = "#ff4500";
    ctx.beginPath(); ctx.moveTo(25, 45); ctx.lineTo(35, 60); ctx.lineTo(45, 45); ctx.fill();
    ctx.fillStyle = "#e2e8f0";
    ctx.strokeStyle = "#4a5568"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(35, 0); ctx.lineTo(15, 40); ctx.lineTo(55, 40); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#00ffff";
    ctx.beginPath(); ctx.ellipse(35, 25, 6, 12, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    missiles.forEach(m => {
        ctx.save();
        ctx.translate(m.x, m.y);
        ctx.shadowBlur = 8; ctx.shadowColor = "#ffca00";
        ctx.fillStyle = "#00ffff";
        ctx.fillRect(-2, -8, 4, 10);
        ctx.restore();
    });

    enemies.forEach(enemy => {
        ctx.save();
        ctx.translate(enemy.x - 20, enemy.y - 10);
        ctx.fillStyle = "#ff3366";
        ctx.beginPath();
        ctx.moveTo(0, 10); ctx.quadraticCurveTo(20, -10, 40, 10);
        ctx.quadraticCurveTo(30, 30, 20, 20); ctx.quadraticCurveTo(10, 30, 0, 10);
        ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(13, 10, 3, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(27, 10, 3, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
    });

    if (boss) {
        ctx.save();
        ctx.translate(boss.x, boss.y);
        ctx.fillStyle = "#44337a"; ctx.strokeStyle = "#7928ca"; ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(0, 20); ctx.lineTo(70, 0); ctx.lineTo(140, 20); ctx.lineTo(120, 60); ctx.lineTo(20, 60);
        ctx.closePath(); ctx.fill(); ctx.stroke();
        ctx.fillStyle = "#00ffff";
        ctx.beginPath(); ctx.arc(70, 55, 10, 0, Math.PI * 2); ctx.fill();
        
        ctx.fillStyle = "#1a202c"; ctx.fillRect(0, -15, 140, 6);
        ctx.fillStyle = "#00f0ff"; ctx.fillRect(0, -15, (boss.hp / boss.maxHp) * 140, 6);
        ctx.restore();
    }

    explosions.forEach(e => {
        ctx.save();
        ctx.translate(e.x, e.y);
        ctx.shadowBlur = 25 * e.life; ctx.shadowColor = e.color;
        ctx.globalAlpha = e.life;
        ctx.fillStyle = e.color;
        ctx.beginPath();
        ctx.arc(0, 0, e.maxRadius * (1 - e.life), 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    });

    particles.forEach(p => {
        ctx.save();
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.fillRect(p.x, p.y, p.size, p.size);
        ctx.restore();
    });
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

spawnEnemy();
loop();
</script>
"""

# 완전 통합본 게임 플레이 프레임 주입
st.components.v1.html(game_html, height=560)
