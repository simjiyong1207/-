
import streamlit as st
import random

st.set_page_config(
    page_title="Midnight Vault",
    page_icon="🌃",
    layout="wide"
)

# ---------- 게임 설정 ----------
W, H = 11, 8
START = (1, 6)
VAULT = (8, 1)
MONEY = (8, 2)
CAR = (9, 6)

WALLS = {
    (3, 0), (3, 1), (3, 2), (3, 4), (3, 5),
    (5, 2), (5, 3), (5, 4), (7, 4), (7, 5),
    (1, 3), (2, 3), (8, 4)
}

def reset_game():
    st.session_state.player = START
    st.session_state.guards = [(5, 1), (7, 6), (9, 2)]
    st.session_state.money = False
    st.session_state.vault_open = False
    st.session_state.alert = 0
    st.session_state.steps = 0
    st.session_state.message = "잠입을 시작해. 경비원의 시야를 피해 금고로 가!"
    st.session_state.status = "playing"

if "player" not in st.session_state:
    reset_game()

def valid(pos):
    x, y = pos
    return 0 <= x < W and 0 <= y < H and pos not in WALLS

def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def move_player(dx, dy):
    if st.session_state.status != "playing":
        return

    x, y = st.session_state.player
    new_pos = (x + dx, y + dy)

    if valid(new_pos):
        st.session_state.player = new_pos
        st.session_state.steps += 1
        st.session_state.message = "조심스럽게 이동 중..."

        # 경비원 시야 및 근접 감지
        for gx, gy in st.session_state.guards:
            if distance(new_pos, (gx, gy)) <= 2:
                st.session_state.alert = min(5, st.session_state.alert + 1)
                st.session_state.message = "🚨 경비원이 수상한 움직임을 감지했어!"

        # 경비원이 플레이어를 추격
        new_guards = []
        for gx, gy in st.session_state.guards:
            if distance((gx, gy), new_pos) <= 5:
                choices = [(gx + 1, gy), (gx - 1, gy),
                           (gx, gy + 1), (gx, gy - 1)]
                choices = [p for p in choices if valid(p)]
                if choices:
                    choices.sort(key=lambda p: distance(p, new_pos))
                    best_dist = distance(choices[0], new_pos)
                    best = [p for p in choices
                            if distance(p, new_pos) == best_dist]
                    new_guards.append(random.choice(best))
                else:
                    new_guards.append((gx, gy))
            else:
                new_guards.append((gx, gy))
        st.session_state.guards = new_guards

        # 잡혔는지 확인
        if new_pos in new_guards:
            st.session_state.status = "caught"
            st.session_state.message = "🚓 경비원에게 붙잡혔어! 다시 도전해 봐."
        elif st.session_state.alert >= 4:
            st.session_state.message = "🚨 수배 레벨이 높아졌어. 빠르게 금고를 털고 탈출해!"

def interact():
    if st.session_state.status != "playing":
        return

    p = st.session_state.player

    if distance(p, VAULT) <= 1 and not st.session_state.vault_open:
        st.session_state.vault_open = True
        st.session_state.message = "🔓 금고가 열렸어! 돈가방을 챙겨!"
    elif distance(p, MONEY) <= 1 and st.session_state.vault_open:
        st.session_state.money = True
        st.session_state.alert = min(5, st.session_state.alert + 1)
        st.session_state.message = "💰 돈가방 획득! 이제 차량으로 탈출해!"
    elif p == CAR:
        if st.session_state.money:
            st.session_state.status = "won"
            st.session_state.message = "🏆 탈출 성공! 완벽한 야간 작전이야!"
        else:
            st.session_state.message = "먼저 금고에서 돈가방을 챙겨야 해."
    else:
        st.session_state.message = "주변에 상호작용할 대상이 없어. 금고나 차량 근처에서 행동해 봐."

# ---------- 화면 ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(160deg, #07111f, #111b30 60%, #241b35);
    color: #eef5ff;
}
h1, h2, h3, p, label {
    color: #eef5ff !important;
}
.tile {
    min-height: 54px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 9px;
    font-size: 25px;
    border: 1px solid #31435b;
    box-shadow: inset 0 0 12px #0005, 0 3px 0 #0005;
}
.floor { background: #1b2b3b; }
.wall { background: linear-gradient(135deg,#5a6675,#293445); }
.player { background: linear-gradient(135deg,#00d4ff,#1764b5); }
.guard { background: linear-gradient(135deg,#ff6262,#8f1d32); }
.vault { background: linear-gradient(135deg,#f5c451,#775018); }
.money { background: linear-gradient(135deg,#54df8d,#116c4a); }
.car { background: linear-gradient(135deg,#b39aff,#5033a4); }
</style>
""", unsafe_allow_html=True)

st.title("🌃 MIDNIGHT VAULT")
st.caption("STEALTH ARCADE  •  NIGHT SHIFT  •  GET IN, GET OUT")

a, b, c, d = st.columns(4)
a.metric("🚨 수배 레벨", f"{st.session_state.alert}/5")
b.metric("💰 돈가방", "획득" if st.session_state.money else "없음")
c.metric("🔐 금고", "열림" if st.session_state.vault_open else "잠김")
d.metric("👣 이동 횟수", st.session_state.steps)

st.markdown("### 🏙️ 은행 내부")
st.caption("파란색은 너 · 빨간색은 경비원 · 금색은 금고 · 초록색은 돈가방 · 보라색은 탈출 차량")

player = st.session_state.player
guards = st.session_state.guards

for y in range(H):
    cols = st.columns(W, gap="small")
    for x in range(W):
        pos = (x, y)
        emoji = ""
        cls = "floor"

        if pos in WALLS:
            emoji, cls = "🧱", "wall"
        if pos == VAULT:
            emoji, cls = ("🔓" if st.session_state.vault_open else "🔐"), "vault"
        if pos == MONEY and not st.session_state.money:
            emoji, cls = "💰", "money"
        if pos == CAR:
            emoji, cls = "🚗", "car"
        if pos in guards:
            emoji, cls = "👮", "guard"
        if pos == player:
            emoji, cls = "🕵️", "player"

        cols[x].markdown(
            f'<div class="tile {cls}">{emoji}</div>',
            unsafe_allow_html=True
        )

st.info(st.session_state.message)

if st.session_state.status == "won":
    st.success("임무 성공! 돈가방을 가지고 안전하게 탈출했어.")
elif st.session_state.status == "caught":
    st.error("작전 실패! 경비원에게 잡혔어.")

st.markdown("### 🎮 이동 및 행동")
left, middle, right = st.columns([1, 1.3, 1])

with middle:
    if st.button("⬆️ 위로", use_container_width=True):
        move_player(0, -1)
        st.rerun()

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ 왼쪽", use_container_width=True):
            move_player(-1, 0)
            st.rerun()
    with c2:
        if st.button("⬇️ 아래", use_container_width=True):
            move_player(0, 1)
            st.rerun()
    with c3:
        if st.button("➡️ 오른쪽", use_container_width=True):
            move_player(1, 0)
            st.rerun()

    if st.button("🔑 상호작용 / 열기", use_container_width=True):
        interact()
        st.rerun()

st.markdown("### 📋 임무")
st.write("1. 🕵️ 경비원을 피하면서 금고(🔐) 근처로 이동해.")
st.write("2. 🔑 금고 옆에서 상호작용해 금고를 열어.")
st.write("3. 💰 돈가방 근처에서 다시 상호작용해 돈가방을 챙겨.")
st.write("4. 🚗 오른쪽 아래 탈출 차량에 도착해 상호작용하면 성공!")
st.caption("이 게임은 가상의 아케이드 잠입 게임입니다.")

if st.button("🔄 처음부터 다시 시작", use_container_width=True):
    reset_game()
    st.rerun()
