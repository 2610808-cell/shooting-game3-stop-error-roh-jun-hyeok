import streamlit as st

# 페이지 설정
st.set_page_config(page_title="쌈뽕한 3D 2.5D 슈팅 게임", layout="centered")

st.title("🛸 초고퀄리티 3D 모델 2.5D 슈팅 게임")
st.write("화면을 **클릭**한 후, **방향키/WASD**로 이동하고 **스페이스바**로 레이저를 난사하세요!")

# --- Three.js 기반 하이엔드 2.5D 게임 엔진 주입 ---
game_html = """
<div id="game-container" tabindex="0" style="outline:none; text-align:center; cursor:pointer;">
    <div id="canvas3d" style="width: 700px; height: 500px; border:3px solid #00ffff; border-radius: 12px; overflow:hidden; box-shadow: 0 0 20px #00ffff;"></div>
    <div style="color: #00ffff; margin-top: 8px; font-family: monospace; font-size: 14px; text-shadow: 0 0 5px #00ffff;">
        [ SYSTEM ] MOVE: ARROWS/WASD | FIRE: SPACEBAR
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

<script>
const container = document.getElementById('game-container');
const canvasDiv = document.getElementById('canvas3d');

container.focus();

// --- 1. 3D 그래픽스 & 씬 세팅 ---
const scene = new THREE.Scene();
// 깊은 우주 느낌을 위한 안개(Fog) 효과 추가
scene.fog = new THREE.FogExp2('#050515', 0.03);

// 탑다운 쿼터뷰 카메라 설정
const camera = new THREE.PerspectiveCamera(50, 700 / 500, 0.1, 1000);
camera.position.set(0, 22, 12); 
camera.lookAt(0, -1, -4);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(700, 500);
renderer.toneMapping = THREE.ACESFilmicToneMapping; // 고급 질감 표현을 위한 톤맵핑
renderer.toneMappingExposure = 1.2;
canvasDiv.appendChild(renderer.domElement);

// --- 2. 입체적 조명 (Lighting) ---
const ambientLight = new THREE.AmbientLight('#ffffff', 0.4);
scene.add(ambientLight);

// 메인 태양광 (기체의 금속 질감을 살려줌)
const sunLight = new THREE.DirectionalLight('#00ffff', 1.5);
sunLight.position.set(10, 20, 10);
scene.add(sunLight);

// 보조 네온광 (신비로운 우주 분위기 연출)
const neonLight = new THREE.PointLight('#ff00ff', 2, 50);
neonLight.position.set(-10, 5, -5);
scene.add(neonLight);

// --- 3. 우주 배경 파티클 (Starfield) ---
const starGeo = new THREE.BufferGeometry();
const starCount = 500;
const starPos = new Float32Array(starCount * 3);
for(let i=0; i<starCount*3; i+=3) {
    starPos[i] = (Math.random() - 0.5) * 40;     // X
    starPos[i+1] = (Math.random() - 2) * 5;      // Y (바닥 쪽에 깔림)
    starPos[i+2] = (Math.random() - 0.5) * 60;   // Z
}
starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.15, transparent: true });
const starField = new THREE.Points(starGeo, starMat);
scene.add(starField);

// --- 4. 게임 데이터 상태 관리 ---
let player = { x: 0, z: 3, mesh: null };
let enemies = [];
let missiles = [];
let particles = []; // 피격 폭발 이펙트용 파티클
let score = 0;
let gameOver = false;

// --- 5. 쌈뽕한 3D 모델 로딩 (GLTF) ---
const loader = new THREE.GLTFLoader();

// 플레이어: 세련된 미래형 SF 전투기 모델 (Three.js 공식 샘플 헬멧/기체 융합 형태 바디 대체 구조)
// 안정적인 고퀄리티 오픈소스 모델 연동
loader.load('https://threejs.org/examples/models/gltf/DamagedHelmet/glTF/DamagedHelmet.gltf', (gltf) => {
    player.mesh = gltf.scene;
    player.mesh.scale.set(1.6, 1.6, 1.6);
    player.mesh.rotation.y = Math.PI; // 앞을 바라보게 회전
    player.mesh.position.set(player.x, 0, player.z);
    scene.add(player.mesh);
}, undefined, (error) => {
    // 대체용 하이엔드 크리스탈 메쉬 기체
    const geometry = new THREE.ConeGeometry(0.8, 2, 4);
    const material = new THREE.MeshStandardMaterial({ color: 0x00ffff, roughness: 0.1, metalness: 0.8 });
    player.mesh = new THREE.Mesh(geometry, material);
    player.mesh.rotation.x = Math.PI / 2;
    scene.add(player.mesh);
});

// --- 6. 키보드 인터랙션 제어 ---
const keys = {};
window.addEventListener('keydown', e => {
    keys[e.key.toLowerCase()] = true;
    if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key)) e.preventDefault();
});
window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

// --- 7. 무기 발사 및 폭발 이펙트 (VFX) ---
let lastShotTime = 0;
function fireLaser() {
    const now = Date.now();
    if (now - lastShotTime < 130) return; // 연사 속도 상향
    lastShotTime = now;

    // 형광색 레이저 빔 (3D Capsule/Cylinder)
    const geometry = new THREE.CylinderGeometry(0.05, 0.05, 1.2, 4);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ffff });
    const laser = new THREE.Mesh(geometry, material);
    
    laser.rotation.x = Math.PI / 2;
    laser.position.set(player.mesh.position.x, 0.2, player.mesh.position.z - 1.5);
    
    scene.add(laser);
    missiles.push(laser);
}

// 3D 파티클 폭발 효과 생성 함수
function createVFXExplosion(pos, colorHex) {
    for (let i = 0; i < 15; i++) {
        const pGeo = new THREE.BoxGeometry(0.15, 0.15, 0.15);
        const pMat = new THREE.MeshBasicMaterial({ color: colorHex, transparent: true, opacity: 1 });
        const pMesh = new THREE.Mesh(pGeo, pMat);
        
        pMesh.position.copy(pos);
        scene.add(pMesh);
        
        particles.push({
            mesh: pMesh,
            vx: (Math.random() - 0.5) * 0.2,
            vy: (Math.random() - 0.5) * 0.1,
            vz: (Math.random() - 0.5) * 0.2,
            life: 1.0
        });
    }
}

function spawnEnemy() {
    if (enemies.length < 6 && !gameOver) {
        // 적 기체: 날카로운 다이아몬드형 3D 스파이크 기체
        const geometry = new THREE.OctahedronGeometry(0.8, 0);
        const material = new THREE.MeshStandardMaterial({ 
            color: 0xff3366, 
            metalness: 0.7, 
            roughness: 0.2,
            emissive: 0x550011 
        });
        const enemyMesh = new THREE.Mesh(geometry, material);
        
        enemyMesh.position.set((Math.random() - 0.5) * 16, 0.3, -18);
        scene.add(enemyMesh);
        
        enemies.push({
            mesh: enemyMesh,
            speedX: (Math.random() - 0.5) * 0.06,
            speedZ: Math.random() * 0.06 + 0.05
        });
    }
}

// --- 8.
