import streamlit as st

# 페이지 설정
st.set_page_config(page_title="2D Boss Shooting Game with VFX", layout="centered")

st.title("🚀 2D 보스 슈팅 게임 (키보드 조작 & 폭발 이펙트)")
st.write("화면을 **한 번 클릭한 후**, **방향키/WASD**로 이동하고 **스페이스바**로 미사일을 발사하세요!")

# --- HTML5 Canvas + JS 기반 통합 게임 엔진 주입 ---
# 파이썬 재실행 없이 브라우저 내부에서 60fps로 이펙트와 충돌을 처리합니다.
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

// 포커스 자동 잡기
container.focus();

// 게임 기본 상태 정의
let player = { x: 350, y: 420 };
let enemies = [];
let boss = null;
let missiles = [];
let explosions = [];
let particles = [];

// 시스템 변수
let score = 0;
let roundNum = 1;
let weaponLevel = 1;
let enemiesKilled = 0;
let enemiesRequired = 5;
let gameOver = false;

// 키 입력 상태 추적
const keys = {};
window.addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key)) {
        e.preventDefault(); // 웹페이지 스크롤 방지
    }
});
window.addEventListener('keyup', e => {
    keys[e.key.toLowerCase()] = false;
});

// 무기 연사 속도 제어 (ms)
let lastShotTime = 0;
const shotCooldown = 150; 

// 적 스폰 함수
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

// 미사일 발사 로직
function fireBullet() {
    const now = Date.now();
    if (now - lastShotTime < shotCooldown) return;
    lastShotTime = now;

    // 무기 레벨에 따른 다중 미사일 각도 분사 이펙트
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

// 화려한 파티클 폭발 이펙트 생성
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

// 게임 실시간 대전 데이터 업데이트
function update() {
    if (gameOver) {
        if (keys['r']) { // 게임오버 상태에서 R 누르면 재시작
            player = { x: 350, y: 420 };
            enemies = []; boss = null; missiles = []; explosions = []; particles = [];
            score = 0; roundNum = 1; weaponLevel = 1; enemiesKilled = 0; enemiesRequired = 5;
            gameOver = false;
        }
        return;
    }

    // 1. 플레이어 이동 처리
    if (keys['arrowleft'] || keys['a']) player.x = Math.max(30, player.x - 5);
    if (keys['arrowright'] || keys['d']) player.x = Math.min(620, player.x + 5);
    if (keys['arrowup'] || keys['w']) player.y = Math.max(220, player.y - 5);
    if (keys['arrowdown'] || keys['s']) player.y = Math.min(430, player.y - 5);
    if (keys[' ']) fireBullet();

    // 2. 미사일 이동 및 적 피격 판정
    missiles.forEach((m, mIdx) => {
        m.x += m.vx;
        m.y += m.vy;

        // 화면 밖 제거
        if (m.y < 0 || m.x < 0 || m.x > 700) {
            missiles.splice(mIdx, 1);
            return;
        }

        // 보스 피격 검사
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

        // 일반 적 피격 검사
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

    // 3. 일반 적 우주선 이동 및 충돌 검사
    enemies.forEach((enemy, index) => {
        enemy.y += enemy.speedY;
        enemy.x += enemy.speedX;

        if (enemy.x < 50 || enemy.x > 650) enemy.speedX *= -1;

        // 충돌 조건 (게임오버 트리거)
        if (enemy.y >= player.y && enemy.y <= player.y + 40 && enemy.x >= player.x && enemy.x <= player.x + 50) {
            gameOver = true;
        }
        // 화면 하단 이탈 시 패널티 제거 후 리스폰 유도
        if (enemy.y > 500) enemies.splice(index, 1);
    });

    // 4. 보스 우주선 이동 및 스폰 제어
    if (boss) {
        boss.x += 2.5 * boss.dir;
        if (boss.x <= 50 || boss.x >= 510) boss.dir *= -1;
    } else if (enemiesKilled >= enemiesRequired && enemies.length === 0) {
        // 보스 스폰 조건 충족시 리얼 생성
        boss = { x: 280, y: 50, hp: roundNum * 6, maxHp: roundNum * 6, dir: 1 };
    }

    // 5. 이펙트 및 파티클 수명 차감 업데이트
    explosions.forEach((e, index) => {
        e.life -= 0.04;
        if (e.life <= 0) explosions.splice(index, 1);
    });
    particles.forEach((p, index) => {
        p.x += p.vx; p.y += p.vy;
        p.life -= 0.03;
        if (p.life <= 0) particles.splice(index, 1);
    });

    // 주기적인 몹 리스폰 가동
    if (Math.random() < 0.02) spawnEnemy();
}

// 그래픽 화면 그리기 (Canvas Engine)
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 상단 UI 텍스트 출력
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
        ctx.textAlign = "left"; // 정렬 초기화
        return;
    }

    // 1. 플레이어 그리기 (기존 SVG 스타일 완벽 이식)
    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.fillStyle = "#ff4500"; // 화염
    ctx.beginPath(); ctx.moveTo(25, 45); ctx.lineTo(35, 60); ctx.lineTo(45, 45); ctx.fill();
    ctx.fillStyle = "#e2e8f0"; // 몸체
    ctx.strokeStyle = "#4a5568"; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(35, 0); ctx.lineTo(15, 40); ctx.lineTo(55, 40); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#00ffff"; // 조종석
    ctx.beginPath(); ctx.ellipse(35, 25, 6, 12, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // 2.
