import streamlit as st
import random
import math

# 페이지 설정
st.set_page_config(page_title="2D Boss Shooting Game", layout="centered")

st.title("🚀 2D 보스 슈팅 게임 (키보드 지원)")
st.write("화면을 한 번 클릭한 후, **키보드 방향키 / WASD** 및 **스페이스바(공격)**로 조작할 수 있습니다!")

# --- 게임 상태 초기화 ---
if "player_x" not in st.session_state:
    st.session_state.player_x = 350
    st.session_state.player_y = 420
    st.session_state.weapon_level = 1
    st.session_state.round_num = 1
    st.session_state.enemies_killed = 0
    st.session_state.enemies_required = 5
    st.session_state.enemies = []
    st.session_state.boss = None
    st.session_state.game_over = False
    st.session_state.score = 0

# --- 게임 로직 함수 ---
def reset_game():
    st.session_state.player_x = 350
    st.session_state.player_y = 420
    st.session_state.weapon_level = 1
    st.session_state.round_num = 1
    st.session_state.enemies_killed = 0
    st.session_state.enemies_required = 5
    st.session_state.enemies = []
    st.session_state.boss = None
    st.session_state.game_over = False
    st.session_state.score = 0

def spawn_enemy():
    if not st.session_state.boss and len(st.session_state.enemies) < 4 and st.session_state.enemies_killed < st.session_state.enemies_required:
        st.session_state.enemies.append({
            "x": random.randint(50, 650),
            "y": random.randint(30, 100),
            "speed_x": random.choice([-15, 0, 15]), # 자연스러운 대각선 이동을 위한 x축 속도
            "hp": st.session_state.round_num
        })

# 보스 스폰
if not st.session_state.boss and st.session_state.enemies_killed >= st.session_state.enemies_required and len(st.session_state.enemies) == 0:
    st.session_state.boss = {"x": 300, "y": 50, "hp": st.session_state.round_num * 5, "max_hp": st.session_state.round_num * 5, "dir": 1}

# 적 스폰 호출
if not st.session_state.game_over:
    spawn_enemy()

# --- 액션 함수 정의 (중복 제거용) ---
def move_left(): st.session_state.player_x = max(50, st.session_state.player_x - 40)
def move_right(): st.session_state.player_x = min(630, st.session_state.player_x + 40)
def move_up(): st.session_state.player_y = max(250, st.session_state.player_y - 40)
def move_down(): st.session_state.player_y = min(430, st.session_state.player_y + 40)

def update_enemies():
    # 적들이 플레이어를 향해 부드럽게 지그재그 혹은 하강하도록 유도
    for enemy in st.session_state.enemies:
        enemy["y"] += random.randint(10, 20) # 기존보다 낙하 폭을 줄여 자연스럽게 만듦
        enemy["x"] += enemy["speed_x"]
        
        # 벽에 부딪히면 튕김
        if enemy["x"] < 50 or enemy["x"] > 650:
            enemy["speed_x"] *= -1
            
        # 플레이어와 충돌 판정
        if enemy["y"] >= st.session_state.player_y - 20 and abs(enemy["x"] - st.session_state.player_x) < 40:
            st.session_state.game_over = True

    # 보스 좌우 부드러운 패트롤
    if st.session_state.boss:
        st.session_state.boss["x"] += 20 * st.session_state.boss["dir"]
        if st.session_state.boss["x"] <= 100 or st.session_state.boss["x"] >= 500:
            st.session_state.boss["dir"] *= -1

def fire_bullet():
    if st.session_state.boss:
        damage = st.session_state.weapon_level * 2
        st.session_state.boss["hp"] -= damage
        st.toast(f"💥 보스 직격! 데미지 {damage}!")
        if st.session_state.boss["hp"] <= 0:
            st.session_state.boss = None
            st.session_state.round_num += 1
            st.session_state.enemies_killed = 0
            st.session_state.enemies_required += 3
            if st.session_state.weapon_level < 3:
                st.session_state.weapon_level += 1
            st.success("🎉 보스를 처치했습니다! 무기 강화 장착!")
            st.session_state.score += 500
    elif st.session_state.enemies:
        # 가장 가까운 적 처치 (연사 속도 상향 연출을 위해 무기레벨만큼 다수 타격)
        targets = min(len(st.session_state.enemies), st.session_state.weapon_level)
        for _ in range(targets):
            st.session_state.enemies.pop(0)
            st.session_state.enemies_killed += 1
            st.session_state.score += 100
        st.toast(f"🚀 미사일 쾌속 발사! {targets}기 격추!")
    else:
        st.toast("허공에 미사일을 날렸습니다!")

# --- 조작 콘솔 (웹 UI 버튼) ---
if st.session_state.game_over:
    st.error(f"💥 GAME OVER! 최종 점수: {st.session_state.score}")
    if st.button("🔄 다시 시작하기 (R)", use_container_width=True):
        reset_game()
        st.rerun()
else:
    # 게임 정보 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("STAGE", f"STAGE {st.session_state.round_num}")
    col2.metric("WEAPON", f"LV {st.session_state.weapon_level}")
    col3.metric("SCORE", f"{st.session_state.score}점")

    if st.session_state.boss:
        st.warning(f"⚠️ 보스 출현! (보스 HP: {st.session_state.boss['hp']} / {st.session_state.boss['max_hp']})")
    else:
        st.info(f"👾 보스 등장까지 남은 적: {max(0, st.session_state.enemies_required - st.session_state.enemies_killed)}마리")

    # 이동 및 공격 컨트롤러 (숨겨진 키보드 연결용 버튼 매핑)
    st.write("### 🎮 조작 패널")
    move_col1, move_col2, move_col3, action_col = st.columns([1, 1, 1, 2])
    
    with move_col1:
        if st.button("◀ LEFT (A)", use_container_width=True, key="btn_left"):
            move_left()
            update_enemies()
    with move_col2:
        if st.button("▲ UP (W)", use_container_width=True, key="btn_up"):
            move_up()
            update_enemies()
        if st.button("▼ DOWN (S)", use_container_width=True, key="btn_down"):
            move_down()
            update_enemies()
    with move_col3:
        if st.button("RIGHT ▶ (D)", use_container_width=True, key="btn_right"):
            move_right()
            update_enemies()
            
    with action_col:
        if st.button("🔥 미사일 발사! (Space)", use_container_width=True, type="primary", key="btn_fire"):
            fire_bullet()
            update_enemies()

    # --- 실시간 게임 화면 그리기 + 키보드 이벤트 JS 주입 ---
    svg_content = f"""
    <div id="game-container" tabindex="0" style="outline:none;">
        <svg width="700" height="500" style="background-color:#050510; border:3px solid #4a5568; border-radius: 12px;">
            <g transform="translate({st.session_state.player_x}, {st.session_state.player_y})">
                <polygon points="15,45 25,65 35,45" fill="#ff4500" />
                <polygon points="25,0 5,40 45,40" fill="#e2e8f0" stroke="#4a5568" stroke-width="2"/>
                <ellipse cx="25" cy="25" rx="6" ry="12" fill="#00ffff"/>
                <rect x="0" y="25" width="4" height="15" fill="#cbd5e1" />
                <rect x="46" y="25" width="4" height="15" fill="#cbd5e1" />
            </g>
    """
    
    # 자연스러워진 일반 적 우주선 그리기
    for enemy in st.session_state.enemies:
        svg_content += f"""
        <g transform="translate({enemy['x']-20}, {enemy['y']-10})">
            <path d="M 0,10 Q 20,-10 40,10 Q 30,30 20,20 Q 10,30 0,10 Z" fill="#ff3366" />
            <circle cx="13" cy="10" r="3" fill="#fff" />
            <circle cx="27" cy="10" r="3" fill="#fff" />
        </g>
        """
        
    # 보스 우주선 그리기
    if st.session_state.boss:
        bx = st.session_state.boss["x"]
        by = st.session_state.boss["y"]
        svg_content += f"""
        <g transform="translate({bx}, {by})">
            <polygon points="0,20 70,0 140,20 120,60 20,60" fill="#44337a" stroke="#7928ca" stroke-width="3"/>
            <circle cx="70" cy="55" r="10" fill="#00ffff" />
        </g>
        """

    # JavaScript를 이용해 실제 키보드 패널 버튼과 매핑
    svg_content += """
        </svg>
    </div>
    <script>
        const container = document.getElementById('game-container');
        // 사용자가 화면을 누르면 포커스를 잡아 키보드 이벤트를 수집합니다.
        container.focus();
        
        container.addEventListener('keydown', function(e) {
            let btnId = "";
            if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") btnId = "bttn-btn_left";
            if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") btnId = "bttn-btn_right";
            if (e.key === "ArrowUp" || e.key === "w" || e.key === "W") btnId = "bttn-btn_up";
            if (e.key === "ArrowDown" || e.key === "s" || e.key === "S") btnId = "bttn-btn_down";
            if (e.key === " " || e.key === "Spacebar") {
                btnId = "bttn-btn_fire";
                e.preventDefault(); // 스페이스바 화면 스크롤 방지
            }
            
            if (btnId) {
                // Streamlit 버튼 컴포넌트의 실제 DOM을 찾아 클릭 이벤트를 발생시킵니다.
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.getAttribute('data-testid') === 'stBaseButton-Primary' || btn.getAttribute('data-testid') === 'stBaseButton-Secondary') {
                        // 대략적인 매핑 또는 내부 텍스트 매칭
                        if(btnId === "bttn-btn_left" && btn.innerText.includes("LEFT")) btn.click();
                        if(btnId === "bttn-btn_right" && btn.innerText.includes("RIGHT")) btn.click();
                        if(btnId === "bttn-btn_up" && btn.innerText.includes("UP")) btn.click();
                        if(btnId === "bttn-btn_down" && btn.innerText.includes("DOWN")) btn.click();
                        if(btnId === "bttn-btn_fire" && btn.innerText.includes("미사일")) btn.click();
                    }
                }
            }
        });
    </script>
    """
    st.components.v1.html(svg_content, height=520)
