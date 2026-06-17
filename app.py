import streamlit as st

# 페이지 설정
st.set_page_config(page_title="3D Shooting Game", layout="centered")

st.title("🛸 초고퀄리티 3D 슈팅 게임")
st.write("화면을 **클릭**한 후, **방향키/WASD**로 이동하고 **스페이스바**로 레이저를 난사하세요!")

# 코드 분할 및 이스케이프 안정성 확보를 위한 구조화
game_code = """
<div id="game-container" tabindex="0" style="outline:none; text-align:center; cursor:pointer;">
    <div id="canvas3d" style="width: 700px; height: 500px; border:3px solid #00ffff; border-radius: 12px; overflow:hidden; box-shadow: 0 0 20px #00ffff;"></div>
    <div style="color: #00ffff; margin-top: 8px; font-family: monospace; font-size: 14px; text-shadow: 0 0 5px #00ffff;">
        [ SYSTEM ] MOVE: ARROWS/WASD | FIRE: SPACEBAR
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>

<script>
(function() {
    const container = document.getElementById('game-container');
    const canvasDiv = document.getElementById('canvas3d');
    container.focus();

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2('#050515', 0.03);

    const camera = new THREE.PerspectiveCamera(50, 700 / 500, 0.1, 1000);
    camera.position.set(0, 22, 12); 
    camera.lookAt(0, -1, -4);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(700, 500);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    canvasDiv.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight('#ffffff', 0.4);
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight('#00ffff', 1.5);
    sunLight.position.set(10, 20, 10);
    scene.add(sunLight);

    const neonLight = new THREE.PointLight('#ff00ff', 2, 50);
    neonLight.position.set(-10, 5, -5);
    scene.add(neonLight);

    const starGeo = new THREE.BufferGeometry();
    const starCount = 500;
    const starPos = new Float32Array(starCount * 3);
    for(let i=0; i<starCount*3; i+=3) {
        starPos[i] = (Math.random() - 0.5) * 40;
        starPos[i+1] = (Math.random() - 2) * 5;
        starPos[i+2] = (Math.random() - 0.5) * 60;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.15, transparent: true });
    const starField = new THREE.Points(starGeo, starMat);
    scene.add(starField);

    let player = { x: 0, z: 3, mesh: null };
    let enemies = [];
    let missiles = [];
    let particles = [];
    let score = 0;
    let gameOver = false;

    const loader = new THREE.GLTFLoader();
    loader.load('https://threejs.org/examples/models/gltf/DamagedHelmet/glTF/DamagedHelmet.gltf', (gltf) => {
        player.mesh = gltf.scene;
        player.mesh.scale.set(1.6, 1.6, 1.6);
        player.mesh.rotation.y = Math.PI;
        player.mesh.position.set(player.x, 0, player.z);
        scene.add(player.mesh);
    }, undefined, (error) => {
        const geometry = new THREE.ConeGeometry(0.8, 2, 4);
        const material = new THREE.MeshStandardMaterial({ color: 0x00ffff, roughness: 0.1, metalness: 0.8 });
        player.mesh = new THREE.Mesh(geometry, material);
        player.mesh.rotation.x = Math.PI / 2;
        scene.add(player.mesh);
    });

    const keys = {};
    window.addEventListener('keydown', e => {
        keys[e.key.toLowerCase()] = true;
        if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key)) e.preventDefault();
    });
    window.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

    let lastShotTime = 0;
    function fireLaser() {
        const now = Date.now();
        if (now - lastShotTime < 130) return;
        lastShotTime = now;

        const geometry = new THREE.CylinderGeometry(0.05, 0.05, 1.2, 4);
        const material = new THREE.MeshBasicMaterial({ color: 0x00ffff });
        const laser = new THREE.Mesh(geometry, material);
        
        laser.rotation.x = Math.PI / 2;
        laser.position.set(player.mesh.position.x, 0.2, player.mesh.position.z - 1.5);
        
        scene.add(laser);
        missiles.push(laser);
    }

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
            const geometry = new THREE.OctahedronGeometry(0.8, 0);
            const material = new THREE.MeshStandardMaterial({ 
                color: 0xff3366, metalness: 0.7, roughness: 0.2, emissive: 0x550011 
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

    function update() {
        if (gameOver) return;
        starField.position.z += 0.05;
        if (starField.position.z > 20) starField.position.z = 0;

        if (player.mesh) {
            if (keys['arrowleft'] || keys['a']) {
                player.mesh.position.x = Math.max(-8.5, player.mesh.position.x - 0.16);
                player.mesh.rotation.z = 0.4;
            } else if (keys['arrowright'] || keys['d']) {
                player.mesh.position.x = Math.min(8.5, player.mesh.position.x + 0.16);
                player.mesh.rotation.z = -0.4;
            } else {
                player.mesh.rotation.z = 0;
            }
            if (keys['arrowup'] || keys['w']) player.mesh.position.z = Math.max(-4, player.mesh.position.z - 0.14);
            if (keys['arrowdown'] || keys['s']) player.mesh.position.z = Math.min(6, player.mesh.position.z - 0.14);
            if (keys[' ']) fireLaser();
        }

        for (let i = missiles.length - 1; i >= 0; i--) {
            missiles[i].position.z -= 0.4;
            if (missiles[i].position.z < -22) {
                scene.remove(missiles[i]);
                missiles.splice(i, 1);
            }
        }

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.mesh.position.x += p.vx; p.mesh.position.y += p.vy; p.mesh.position.z += p.vz;
            p.life -= 0.04; p.mesh.material.opacity = p.life;
            if (p.life <= 0) { scene.remove(p.mesh); particles.splice(i, 1); }
        }

        for (let i = enemies.length - 1; i >= 0; i--) {
            let e = enemies[i];
            e.mesh.position.z += e.speedZ; e.mesh.position.x += e.speedX;
            e.mesh.rotation.x += 0.02; e.mesh.rotation.y += 0.02;
            if (e.mesh.position.x < -9 || e.mesh.position.x > 9) e.speedX *= -1;

            for (let j = missiles.length - 1; j >= 0; j--) {
                let m = missiles[j];
                let dist = e.mesh.position.distanceTo(m.position);
                if (dist < 1.1) {
                    createVFXExplosion(e.mesh.position, 0xff0055);
                    scene.remove(e.mesh); enemies.splice(i, 1);
                    scene.remove(m); missiles.splice(j, 1);
                    score += 100; break;
                }
            }

            if (player.mesh && e.mesh.position.distanceTo(player.mesh.position) < 1.4) {
                createVFXExplosion(player.mesh.position, 0x00ffff);
                gameOver = true;
                alert("💥 MISSION FAILED! Score: " + score);
            }
            if (e.mesh && e.mesh.position.z > 9) { scene.remove(e.mesh); enemies.splice(i, 1); }
        }
        if (Math.random() < 0.025) spawnEnemy();
    }

    function animate() {
        requestAnimationFrame(animate);
        update();
        renderer.render(scene, camera);
    }
    animate();
})();
</script>
"""

# 가독성과 마감 에러 차단을 위해 변수를 클린하게 렌더링
st.components.v1.html(game_code, height=560)
