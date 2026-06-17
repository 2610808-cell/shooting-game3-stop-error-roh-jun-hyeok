import streamlit as st
import random

# 페이지 설정
st.set_page_config(page_title="2D Boss Shooting Game", layout="centered")

st.title("🚀 2D 보스 슈팅 게임 (키보드 조작 완벽 지원)")
st.write("아래 게임 화면을 **한 번 클릭한 후**, 키보드 **방향키(또는 WASD)**와 **스페이스바(공격)**로 조작하세요!")

# --- 게임 상태 초기화 ---
if "weapon_level" not in st.session_state:
    st.session_state.weapon_level = 1
    st.session_state.round_num = 1
    st.session_state.score = 0

# 파이썬 측 점수 및 스테이지 리셋 함수 (상단 UI 업데이트용)
def reset_game():
    st.session_state.weapon_level = 1
    st.session_state.round_num = 1
    st.session_state.score = 0

# --- 게임 정보 상단 표시 ---
col1, col2, col3 = st.columns(3)
col1.metric("STAGE", f"STAGE {st.session_state.round_num}")
col2.metric("WEAPON", f"LV {st.session_state.weapon_level}")
col3.metric("SCORE", f"{st.session_state.score}점")

if st.button("🔄 게임 초기화 (Reset)", use_container_width=True):
    reset_game()
    st.rerun()

# --- HTML5 + JS 기반 통합 게임 엔진 주입 ---
game_html = """
<div id="game-container" tabindex="0" style="outline:none; text-align:center; cursor:pointer;">
    <canvas id="gameCanvas" width="700" height="500" style="background-color:#050510; border:3px solid #4a5568; border-radius: 12px;"></canvas>
    <div style="color: #cbd5e1; margin-top: 8px; font-family: sans-serif; font-size: 14px;">
        🎮 클릭 후 조작: 이동(방향키 / WASD) | 공격(스페이스바)
    </div>
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const container = document.getElementById('game-container');

// 포커스 자동 잡기
container.focus();

// 게임 상태 정의
let player = { x: 350, y: 420, size: 40 };
let enemies = [];
let boss = null;
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
        e.preventDefault(); // 스크롤 방지
    }
});
window.addEventListener('keyup', e => {
    keys[e.key.toLowerCase()] = false;
});

// 공격 딜레이 제어
let lastShotTime = 0;
const shotCooldown = 200; // ms

function spawnEnemy() {
    if (!boss && enemies.length < 4 && enemiesKilled < enemiesRequired) {
        enemies.push({
            x: Math.random() * (600) + 50,
            y: Math.random() * 50 + 30,
            speedX: (Math.random() > 0.5 ? 1 : -1) * (Math.random() * 2 + 1),
            speedY: Math.random() * 0.5 + 0.5,
            hp: roundNum
        });
    }
}

function fireBullet() {
    const now = Date.now();
    if (now - lastShotTime < shotCooldown) return;
    lastShotTime = now;

    if (boss) {
        let damage = weaponLevel * 2;
        boss.hp -= damage;
        if (boss.hp <= 0) {
            boss = null;
            roundNum++;
            enemiesKilled = 0;
            enemiesRequired += 3;
            if (weaponLevel < 3) weaponLevel++;
            score += 500;
        }
    } else if (enemies.length > 0) {
        let targets = Math.min(enemies.length, weaponLevel);
        for (let i = 0; i < targets; i++) {
            enemies.shift();
            enemiesKilled++;
            score += 100;
        }
    }
    
    // 보스 스폰 조건 체크
    if (!boss && enemiesKilled >= enemiesRequired && enemies.length === 0) {
        boss = { x: 280, y: 50, hp: roundNum * 5, maxHp: roundNum * 5, dir: 1 };
    }
}

// 게임 루프 업데이트
function update() {
    if (gameOver) return;

    // 플레이어 이동 조작
    if (keys['arrowleft'] || keys['a']) player.x = Math.max(50, player.x - 5);
    if (keys['arrowright'] || keys['d']) player.x = Math.min(610, player.x + 5);
    if (keys['arrowup'] || keys['w']) player.y = Math.max(250, player.y - 5);
    if (keys['arrowdown'] || keys['s']) player.y = Math.min(430, player.y - 5);
    if (keys[' ']) fireBullet();

    // 적 이동 및 충돌
    enemies.forEach((enemy, index) => {
        enemy.y += enemy.speedY;
        enemy.x += enemy.speedX;

        if (enemy.x < 50 || enemy.x > 650) enemy.speedX *= -1;

        // 플레이어와 충돌 판정
        if (enemy.y >= player.y - 20 && Math.abs(enemy.x - player.x) < 35) {
            gameOver = true;
        }
    });

    // 보스 이동
    if (boss) {
        boss.x += 2 * boss.dir;
        if (boss.x <= 100 || boss.x >= 500) boss.dir *= -1;
    }

    // 주기적 적 스폰
    if (Math.random() < 0.02) spawnEnemy();
}

// 그리기 (Canvas Rendering)
function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (gameOver) {
        ctx.fillStyle = "#ff3366";
        ctx.font = "bold 40px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("💥 GAME OVER", canvas.width / 2, canvas.height / 2);
        ctx.font = "20px sans-serif";
        ctx.fillStyle = "#ffffff";
        ctx.fillText("Score: " + score + " | 새로고침(R)하여 다시 도전하세요", canvas.width / 2, canvas.height / 2 + 50);
        return;
    }

    // 1. 플레이어 그리기
    ctx.save();
    ctx.translate(player.x, player.y);
    ctx.fillStyle = "#ff4500";
    ctx.beginPath(); ctx.moveTo(15, 45); ctx.lineTo(25, 65); ctx.lineTo(35, 45); ctx.fill();
    ctx.fillStyle = "#e2e8f0";
    ctx.strokeStyle = "#4a5568";
    ctx.lineWidth = 2;
    ctx.beginPath(); ctx.moveTo(25, 0); ctx.lineTo(5, 40); ctx.lineTo(45, 40); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#00ffff";
    ctx.beginPath(); ctx.ellipse(25, 25, 6, 12, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();

    // 2. 일반 적 우주선 그리기
    enemies.forEach(enemy => {
        ctx.save();
        ctx.translate(enemy.x - 20, enemy.y - 10);
        ctx.fillStyle = "#ff3366";
        ctx.beginPath();
        ctx.moveTo(0, 10);
        ctx.quadraticCurveTo(20, -10, 40, 10);
        ctx.quadraticCurveTo(30, 30, 20, 20);
        ctx.quadraticCurveTo(10, 30, 0, 10);
        ctx.fill();
        ctx.fillStyle = "#fff";
        ctx.beginPath(); ctx.arc(13, 10, 3, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(27, 10, 3, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
    });

    // 3. 보스 우주선 그리기
    if (boss) {
        ctx.save();
        ctx.translate(boss.x, boss.y);
        ctx.fillStyle = "#44337a";
        ctx.strokeStyle = "#7928ca";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(0, 20); ctx.lineTo(70, 0); ctx.lineTo(140, 20); ctx.lineTo(120, 60); ctx.lineTo(20, 60);
        ctx.closePath(); ctx.fill(); ctx.stroke();
        ctx.fillStyle = "#00ffff";
        ctx.beginPath(); ctx.arc(70, 55, 10, 0, Math.PI * 2); ctx.fill();
        
        // 보스 HP 바
        ctx.fillStyle = "#1a202c";
        ctx.fillRect(0, -15, 140, 6);
        ctx.fillStyle = "#00f0ff";
        ctx.fillRect(0, -15, (boss.hp / boss.maxHp) * 140, 6);
        ctx.restore();
    }
}

// 메인 루프 실행
function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

// 최초 적 스폰 및 루프 시작
spawnEnemy();
loop();
</script>
"""

# HTML 컴포넌트 실행 (정상적으로 닫힌 문자열을 전달)
st.components.v1.html(game_html, height=550)
