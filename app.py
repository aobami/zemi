import streamlit as st
import random
import time

# --- ゲームの状態を管理する変数 ---
DEFAULT_PLAYER_NAME = "勇者"

if 'player_hp' not in st.session_state:
    st.session_state.player_hp = 0 # 初期値は職業選択後に設定
if 'enemy_hp' not in st.session_state:
    st.session_state.enemy_hp = 120
if 'game_log' not in st.session_state:
    st.session_state.game_log = []
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'player_defending' not in st.session_state:
    st.session_state.player_defending = False
if 'enemy_preparing_strong_attack' not in st.session_state:
    st.session_state.enemy_preparing_strong_attack = False
if 'win_lose_status' not in st.session_state:
    st.session_state.win_lose_status = None
if 'player_name' not in st.session_state:
    st.session_state.player_name = DEFAULT_PLAYER_NAME
if 'name_set' not in st.session_state:
    st.session_state.name_set = False

# 職業関連の新しい状態変数
if 'player_class' not in st.session_state: # プレイヤーの職業
    st.session_state.player_class = None
if 'class_selected' not in st.session_state: # 職業が選択されたか
    st.session_state.class_selected = False

if 'player_max_hp' not in st.session_state:
    st.session_state.player_max_hp = 0 # 初期値は職業選択後に設定
if 'player_mp' not in st.session_state:
    st.session_state.player_mp = 0 # 初期値は職業選択後に設定
if 'player_max_mp' not in st.session_state:
    st.session_state.player_max_mp = 0 # 初期値は職業選択後に設定


# --- 定数 ---
PLAYER_ATTACK_MIN = 15
PLAYER_ATTACK_MAX = 25
PLAYER_HEAL_AMOUNT = 30
HEAL_SKILL_MP_COST = 2

PLAYER_MERA_MP_COST = 4
PLAYER_MERA_DAMAGE_MIN = 20
PLAYER_MERA_DAMAGE_MAX = 40

ENEMY_NORMAL_ATTACK_MIN = 10
ENEMY_NORMAL_ATTACK_MAX = 20
ENEMY_STRONG_ATTACK_MIN = 25
ENEMY_STRONG_ATTACK_MAX = 35
STRONG_ATTACK_PREPARE_CHANCE = 0.4
DEFENSE_REDUCTION = 0.5

# ★追加: 職業ごとのステータスとスキル
CLASS_STATS = {
    "戦士": {"hp": 120, "max_hp": 120, "mp": 5, "max_mp": 5},
    "魔法使い": {"hp": 80, "max_hp": 80, "mp": 15, "max_mp": 15},
}

CLASS_SKILLS = {
    "戦士": ["攻撃", "防御"],
    "魔法使い": ["攻撃", "防御", "回復", "メラ"],
}

# --- UI要素とゲームロジック ---
st.title("シンプルなターン性コマンドバトル")

# プレイヤー名入力セクション
if not st.session_state.name_set:
    st.write("### プレイヤーの名前を入力してください")
    player_input_name = st.text_input("名前", value=DEFAULT_PLAYER_NAME, key="player_name_input")
    if st.button("次に進む", key="set_name_button"): # ボタン名を変更
        if player_input_name:
            st.session_state.player_name = player_input_name
        else:
            st.session_state.player_name = DEFAULT_PLAYER_NAME
        st.session_state.name_set = True
        st.rerun()
    st.stop()

# ★追加: 職業選択セクション
if not st.session_state.class_selected:
    st.write(f"### {st.session_state.player_name}、職業を選択してください")
    selected_class = st.radio(
        "職業",
        ("戦士", "魔法使い"),
        key="class_selection"
    )
    st.write(f"**{selected_class}**を選びました。")
    if selected_class == "戦士":
        st.markdown(f"- HP: {CLASS_STATS['戦士']['hp']}, MP: {CLASS_STATS['戦士']['mp']}")
        st.markdown(f"- 使えるコマンド: {', '.join(CLASS_SKILLS['戦士'])}")
    else: # 魔法使い
        st.markdown(f"- HP: {CLASS_STATS['魔法使い']['hp']}, MP: {CLASS_STATS['魔法使い']['mp']}")
        st.markdown(f"- 使えるコマンド: {', '.join(CLASS_SKILLS['魔法使い'])}")

    if st.button("この職業で始める", key="start_game_button"):
        st.session_state.player_class = selected_class
        # 選択した職業のステータスを反映
        st.session_state.player_hp = CLASS_STATS[selected_class]["hp"]
        st.session_state.player_max_hp = CLASS_STATS[selected_class]["max_hp"]
        st.session_state.player_mp = CLASS_STATS[selected_class]["mp"]
        st.session_state.player_max_mp = CLASS_STATS[selected_class]["max_mp"]
        st.session_state.class_selected = True
        st.rerun()
    st.stop() # 職業が選択されるまでゲーム画面は表示しない


# ゲーム本体のUI
# HP/MP表示
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"職業: {st.session_state.player_class}") # 職業名を表示
    st.subheader(f"{st.session_state.player_name} HP: {st.session_state.player_hp} / {st.session_state.player_max_hp}")
    st.subheader(f"{st.session_state.player_name} MP: {st.session_state.player_mp} / {st.session_state.player_max_mp}")
with col2:
    st.subheader(f"敵HP: {st.session_state.enemy_hp}")

st.markdown("---")

# ゲームログ表示
st.subheader("ゲームログ")
game_log_area = st.empty()
with game_log_area.container():
    for log_entry in st.session_state.game_log:
        st.text(log_entry)

# ゲームオーバー判定
if st.session_state.player_hp <= 0 and not st.session_state.game_over:
    st.session_state.game_log.append(f"{st.session_state.player_name}は戦闘不能になった...")
    st.session_state.game_log.append("ゲームオーバー！")
    st.session_state.game_over = True
    st.session_state.win_lose_status = 'lose'
elif st.session_state.enemy_hp <= 0 and not st.session_state.game_over:
    st.session_state.game_log.append("敵を倒した！")
    st.session_state.game_log.append(f"{st.session_state.player_name}の勝利！")
    st.session_state.game_over = True
    st.session_state.win_lose_status = 'win'

if st.session_state.game_over:
    st.error("ゲーム終了！")
    if st.session_state.win_lose_status == 'win':
        st.markdown(f"<h2 style='text-align: center; color: green;'>🎉 {st.session_state.player_name}の勝利！ 🎉</h2>", unsafe_allow_html=True)
    elif st.session_state.win_lose_status == 'lose':
        st.markdown(f"<h2 style='text-align: center; color: red;'>💀 {st.session_state.player_name}は倒れた... ゲームオーバー！ 💀</h2>", unsafe_allow_html=True)

    if st.button("もう一度プレイ"):
        # ゲーム状態をリセット
        st.session_state.player_hp = 0 # 職業選択で再設定されるため一旦0
        st.session_state.player_mp = 0 # 職業選択で再設定されるため一旦0
        st.session_state.player_max_hp = 0
        st.session_state.player_max_mp = 0
        st.session_state.enemy_hp = 120
        st.session_state.game_log = []
        st.session_state.game_over = False
        st.session_state.player_defending = False
        st.session_state.enemy_preparing_strong_attack = False
        st.session_state.win_lose_status = None
        st.session_state.name_set = False
        st.session_state.player_name = DEFAULT_PLAYER_NAME
        st.session_state.player_class = None # 職業もリセット
        st.session_state.class_selected = False # 職業選択画面に戻る
        st.rerun()
    st.stop()

# コマンドボタン
st.subheader("コマンドを選択")
col_commands = st.columns(4) # コマンドは最大4つ

def player_attack():
    st.session_state.player_defending = False
    damage = random.randint(PLAYER_ATTACK_MIN, PLAYER_ATTACK_MAX)
    st.session_state.enemy_hp -= damage
    st.session_state.game_log.append(f"{st.session_state.player_name}の攻撃！敵に {damage} ダメージ与えた！")
    enemy_turn()

def player_defend():
    st.session_state.player_defending = True
    st.session_state.game_log.append(f"{st.session_state.player_name}は身を守った！")
    enemy_turn()

def player_heal():
    st.session_state.player_defending = False

    if "回復" not in CLASS_SKILLS[st.session_state.player_class]:
        st.session_state.game_log.append("この職業では回復スキルを使えません！")
        st.rerun()
        return

    if st.session_state.player_mp >= HEAL_SKILL_MP_COST:
        st.session_state.player_mp -= HEAL_SKILL_MP_COST
        heal_amount = PLAYER_HEAL_AMOUNT
        st.session_state.player_hp = min(st.session_state.player_max_hp, st.session_state.player_hp + heal_amount)
        st.session_state.game_log.append(f"{st.session_state.player_name}はHPを {heal_amount} 回復し、MPを {HEAL_SKILL_MP_COST} 消費した！")
        enemy_turn()
    else:
        st.session_state.game_log.append(f"{st.session_state.player_name}はMPが足りない！(必要MP: {HEAL_SKILL_MP_COST})")
        st.rerun()

def player_mera():
    st.session_state.player_defending = False

    if "メラ" not in CLASS_SKILLS[st.session_state.player_class]:
        st.session_state.game_log.append("この職業ではメラを使えません！")
        st.rerun()
        return

    if st.session_state.player_mp >= PLAYER_MERA_MP_COST:
        st.session_state.player_mp -= PLAYER_MERA_MP_COST
        damage = random.randint(PLAYER_MERA_DAMAGE_MIN, PLAYER_MERA_DAMAGE_MAX)
        st.session_state.enemy_hp -= damage
        st.session_state.game_log.append(f"{st.session_state.player_name}はメラを唱えた！敵に {damage} ダメージ与え、MPを {PLAYER_MERA_MP_COST} 消費した！")
        enemy_turn()
    else:
        st.session_state.game_log.append(f"{st.session_state.player_name}はMPが足りない！(必要MP: {PLAYER_MERA_MP_COST})")
        st.rerun()


def enemy_turn():
    time.sleep(0.5)

    enemy_damage = 0
    attack_type = ""

    if st.session_state.enemy_preparing_strong_attack:
        attack_type = "強攻撃"
        enemy_damage = random.randint(ENEMY_STRONG_ATTACK_MIN, ENEMY_STRONG_ATTACK_MAX)
        st.session_state.enemy_preparing_strong_attack = False
    else:
        if random.random() < STRONG_ATTACK_PREPARE_CHANCE:
            st.session_state.game_log.append("敵は力を溜めている！")
            st.session_state.enemy_preparing_strong_attack = True
            st.rerun()
            return

        attack_type = "通常攻撃"
        enemy_damage = random.randint(ENEMY_NORMAL_ATTACK_MIN, ENEMY_NORMAL_ATTACK_MAX)

    if st.session_state.player_defending:
        actual_damage = int(enemy_damage * DEFENSE_REDUCTION)
        st.session_state.player_hp -= actual_damage
        st.session_state.game_log.append(f"敵の{attack_type}！{st.session_state.player_name}は身を守ったので {actual_damage} ダメージ受けた！")
    else:
        st.session_state.player_hp -= enemy_damage
        st.session_state.game_log.append(f"敵の{attack_type}！{st.session_state.player_name}に {enemy_damage} ダメージ！")

    st.session_state.player_hp = max(0, st.session_state.player_hp)
    st.session_state.enemy_hp = max(0, st.session_state.enemy_hp)

    st.session_state.player_defending = False

    st.rerun()


# コマンドボタンの表示と活性・非活性制御
with col_commands[0]:
    if st.button("攻撃", on_click=player_attack, disabled=("攻撃" not in CLASS_SKILLS[st.session_state.player_class])):
        pass

with col_commands[1]:
    can_heal = st.session_state.player_mp >= HEAL_SKILL_MP_COST and ("回復" in CLASS_SKILLS[st.session_state.player_class])
    if st.button(f"回復 (MP:{HEAL_SKILL_MP_COST})", on_click=player_heal, disabled=not can_heal):
        pass

with col_commands[2]:
    can_mera = st.session_state.player_mp >= PLAYER_MERA_MP_COST and ("メラ" in CLASS_SKILLS[st.session_state.player_class])
    if st.button(f"メラ (MP:{PLAYER_MERA_MP_COST})", on_click=player_mera, disabled=not can_mera):
        pass

with col_commands[3]:
    if st.button("防御", on_click=player_defend, disabled=("防御" not in CLASS_SKILLS[st.session_state.player_class])):
        pass
