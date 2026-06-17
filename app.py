import streamlit as st

# 페이지 설정
st.set_page_config(page_title="2.5D 3D-Model Shooting Game", layout="centered")

st.title("🚀 3D 모델 기반 2.5D 보스 슈팅 게임")
st.write("화면을 **한 번 클릭한 후**, **방향키/WASD**로 이동하고 **스페이스바**로 미사일을 발사하세요!")

# --- Three.js 기반 2.5D 게임 엔진 주입 ---
game_html = """
<div id="game-container" tabindex="0" style="outline:none; text-align:center; cursor:pointer;">
    <div id="canvas3d" style="width: 700px; height: 500px; border:3px solid #4a5568; border-radius: 12px; overflow:hidden;"></div>
    <div style="color: #cbd5e1; margin-top: 8px; font-family: sans-serif; font-size: 14px;">
        🎮 이동: 방향키 또는 WASD | 공격: 스페이스바 (3D 모델 실시간 렌더링)
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

<script>
const container = document.getElementById('game-container');
const canvasDiv = document.getElementById('canvas3d');

container.focus();

// --- 1. Three.js 기본 씬 설정 ---
const scene = new THREE.Scene();
scene.background = new THREE.Color('#050510');

// 탑다운 2.5D 카메라 설정 (위에서 아래를 비춤)
const camera = new THREE.PerspectiveCamera(60, 700 / 500, 0.1, 1000);
camera.position.set(0, 25, 10); // 위쪽 배치
camera.lookAt(0, 0, -5);       // 앞쪽 바닥을 바라봄

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(700, 500);
canvasDiv.appendChild(renderer.domElement);

// 조명 설정 (3D 모델이 보이기 위해 필수)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(0, 20, 10);
scene.add(directionalLight);

// --- 2. 게임 상태 관리 ---
let player = { x: 0, z: 2, mesh: null };
let enemies = [];
let missiles = [];
let gameOver = false;
let score = 0;

// --- 3. 3D 모델 로드 (GLTFLoader) ---
const loader = new THREE.GLTFLoader();

// 플레이어 우주선 3D 모델 불러오기 (샘플 오픈소스 GLTF)
loader.load('https://threejs.org/examples/models/gltf/DamagedHelmet/glTF/DamagedHelmet.gltf', (gltf) => {
    player.mesh = gltf.scene;
    player.mesh.scale.set(1.5, 1.5, 1.5);
    player.mesh.position.set(player.x, 0, player.z);
    scene.add(player.mesh);
}, undefined, (error) => {
    // 모델 로드 실패시 대체할 임시 3D 박스 생성
    const geometry = new THREE.BoxGeometry(1.5, 0.5, 1.5);
    const material = new THREE.MeshStandardMaterial({ color: 0x00ffff });
    player.mesh = new THREE.Mesh(geometry, material);
    player.mesh.position.set(player.x, 0, player.z);
    scene.add(player.mesh);
});

// --- 4. 키보드 입력 핸들러 ---
const keys = {};
window.addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key)) {
        e.preventDefault();
    }
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

// --- 5. 미사일 & 적 생성 메커니즘 ---
let lastShotTime = 0;
function fireBullet() {
    const now = Date.now();
    if (now - lastShotTime < 200) return;
    lastShotTime = now;

    // 3D 미사일 (원기둥 모양)
    const geometry = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 8);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ffff });
    const missileMesh = new THREE.Mesh(geometry, material);
    
    missileMesh.rotation.x = Math.PI / 2; // 진행 방향으로 눕히기
    missileMesh.position.set(player.mesh.position.x, 0, player.mesh.position.z - 1);
    
    scene.add(missileMesh);
    missiles.push(missileMesh);
}

function spawnEnemy() {
    if (enemies.length < 5 && !gameOver) {
        // 3D 적 기체 (구체 또는 원뿔 모양으로 임시 생성)
        const geometry = new THREE.ConeGeometry(0.8, 1.5, 4);
        const material = new THREE.MeshStandardMaterial({ color: 0xff3366 });
        const enemyMesh = new THREE.Mesh(geometry, material);
        
        enemyMesh.rotation.x = Math.PI; // 플레이어를 보게 회전
        enemyMesh.position.set((Math.random() - 0.5) * 16, 0, -15);
        
        scene.add(enemyMesh);
        enemies.push({
            mesh: enemyMesh,
            speedX: (Math.random() - 0.5) * 0.05,
            speedZ: Math.random() * 0.05 + 0.03
        });
    }
}

// --- 6. 실시간 프레임 동역학 업데이트 ---
function update() {
    if (gameOver) return;

    // 플레이어 3D 이동
    if (player.mesh) {
        if (keys['arrowleft'] || keys['a']) player.mesh.position.x = Math.max(-9, player.mesh.position.x - 0.15);
        if (keys['arrowright'] || keys['d']) player.mesh.position.x = Math.min(9, player.mesh.position.x + 0.15);
        if (keys['arrowup'] || keys['w']) player.mesh.position.z = Math.max(-5, player.mesh.position.z - 0.15);
        if (keys['arrowdown'] || keys['s']) player.mesh.position.z = Math.min(5, player.mesh.position.z + 0.15);
        if (keys[' ']) fireBullet();
        
        // 3D 특유의 무빙 연출: 좌우 이동 시 기체 살짝 회전하기
        if (keys['arrowleft'] || keys['a']) player.mesh.rotation.y = 0.3;
        else if (keys['arrowright'] || keys['d']) player.mesh.rotation.y = -0.3;
        else player.mesh.rotation.y = 0;
    }

    // 미사일 이동 및 제거
    for (let i = missiles.length - 1; i >= 0; i--) {
        missiles[i].position.z -= 0.3;
        if (missiles[i].position.z < -20) {
            scene.remove(missiles[i]);
            missiles.splice(i, 1);
        }
    }

    // 적 이동 및 충돌 판정
    for (let i = enemies.length - 1; i >= 0; i--) {
        let e = enemies[i];
        e.mesh.position.z += e.speedZ;
        e.mesh.position.x += e.speedX;
        e.mesh.rotation.z += 0.02; // 적 기체 회전 이펙트

        // 벽 튕기기
        if (e.mesh.position.x < -9 || e.mesh.position.x > 9) e.speedX *= -1;

        // 미사일 vs 적 충돌 체크 (3D 거리 계산)
        for (let j = missiles.length - 1; j >= 0; j--) {
            let m = missiles[j];
            let dist = e.mesh.position.distanceTo(m.position);
            if (dist < 1.2) {
                // 적 제거
                scene.remove(e.mesh);
                enemies.splice(i, 1);
                // 미사일 제거
                scene.remove(m);
                missiles.splice(j, 1);
                score += 100;
                break;
            }
        }

        // 플레이어 vs 적 충돌 체크 (Game Over)
        if (player.mesh && e.mesh.position.distanceTo(player.mesh.position) < 1.5) {
            gameOver = true;
            alert("💥 GAME OVER! 최종 점수: " + score);
        }

        // 화면 아래로 지나간 적 제거
        if (e.mesh && e.mesh.position.z > 8) {
            scene.remove(e.mesh);
            enemies.splice(i, 1);
        }
    }

    if (Math.random() < 0.02) spawnEnemy();
}

// --- 7. 렌더 루프 가동 ---
function animate() {
    requestAnimationFrame(animate);
    update();
    renderer.render(scene, camera);
}

animate();
</script>
"""

st.components.v1.html(game_html, height=560)
