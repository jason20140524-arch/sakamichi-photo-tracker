import streamlit as st
from enum import Enum
import json
from typing import List, Dict, Optional
import os

# --- 0. 設定檔案路徑 ---
DATA_FILE = "sakamichi_collection_data.json"

# --- 1. 核心資料模型 ---

# 生寫真類型 (Pose) - 新增特殊姿勢
class Pose(Enum):
    Y = "Yori (寄)"
    C = "Chuu (中)"
    H = "Hiki (引)"
    T = "Suwari (座)"
    SPY = "Special Yori (特殊寄)" # 新增特殊姿勢
    SPH = "Special Hiki (特殊引)" # 新增特殊姿勢

# 坂道團體 (Group)
class Group(Enum):
    NOGIZAKA = "乃木坂46"
    SAKURAZAKA = "櫻坂46"
    HINATAZAKA = "日向坂46"

# 固定的成員名單 (與您提供的最新名單一致)
ALL_MEMBERS = [
    # --- 乃木坂46 (NOGIZAKA46) ---
    # 3期生
    {"name": "梅澤美波", "group": Group.NOGIZAKA, "gen": 3}, {"name": "岩本蓮加", "group": Group.NOGIZAKA, "gen": 3}, {"name": "与田祐希", "group": Group.NOGIZAKA, "gen": 3}, {"name": "久保史緒里", "group": Group.NOGIZAKA, "gen": 3},
    # 4期生
    {"name": "遠藤さくら", "group": Group.NOGIZAKA, "gen": 4}, {"name": "賀喜遥香", "group": Group.NOGIZAKA, "gen": 4}, {"name": "筒井あやめ", "group": Group.NOGIZAKA, "gen": 4}, {"name": "田村真佑", "group": Group.NOGIZAKA, "gen": 4}, {"name": "金川紗耶", "group": Group.NOGIZAKA, "gen": 4}, {"name": "清宮レイ", "group": Group.NOGIZAKA, "gen": 4},
    # 5期生 (已修正)
    {"name": "井上和", "group": Group.NOGIZAKA, "gen": 5}, {"name": "一ノ瀬美空", "group": Group.NOGIZAKA, "gen": 5}, {"name": "川﨑桜", "group": Group.NOGIZAKA, "gen": 5}, {"name": "菅原咲月", "group": Group.NOGIZAKA, "gen": 5}, {"name": "五百城茉央", "group": Group.NOGIZAKA, "gen": 5}, {"name": "冨里奈央", "group": Group.NOGIZAKA, "gen": 5}, {"name": "奥田いろは", "group": Group.NOGIZAKA, "gen": 5}, {"name": "中西アルノ", "group": Group.NOGIZAKA, "gen": 5},
    # 6期生 (2025年加入 - 已修正)
    {"name": "矢田萌華", "group": Group.NOGIZAKA, "gen": 6}, {"name": "瀬戸口心月", "group": Group.NOGIZAKA, "gen": 6}, {"name": "川端晃菜", "group": Group.NOGIZAKA, "gen": 6}, {"name": "海邉朱莉", "group": Group.NOGIZAKA, "gen": 6}, {"name": "長嶋凛桜", "group": Group.NOGIZAKA, "gen": 6}, {"name": "森平麗心", "group": Group.NOGIZAKA, "gen": 6}, {"name": "愛宕心響", "group": Group.NOGIZAKA, "gen": 6}, {"name": "大越ひなの", "group": Group.NOGIZAKA, "gen": 6}, {"name": "鈴木佑捺", "group": Group.NOGIZAKA, "gen": 6}, {"name": "小津玲奈", "group": Group.NOGIZAKA, "gen": 6}, {"name": "増田三莉音", "group": Group.NOGIZAKA, "gen": 6},
    
    # --- 櫻坂46 (SAKURAZAKA46) ---
    # 2期生
    {"name": "田村保乃", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "森田ひかる", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "松田里奈", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "守屋麗奈", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "大園玲", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "武元唯衣", "group": Group.SAKURAZAKA, "gen": 2},
    # 3期生
    {"name": "谷口愛理", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "中嶋優月", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "山下瞳月", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "村井優", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "的野美青", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "石森璃花", "group": Group.SAKURAZAKA, "gen": 3},
    # 4期生 (2025年加入)
    {"name": "浅井恋乃未", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "稲熊ひな", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "勝又春", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "佐藤愛桜", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "中川智尋", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "松本和子", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "目黒陽色", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "山川宇衣", "group": Group.SAKURAZAKA, "gen": 4}, {"name": "山田桃実", "group": Group.SAKURAZAKA, "gen": 4},
    
    # --- 日向坂46 (HINATAZAKA46) ---
    # 1期生
    {"name": "佐々木久美", "group": Group.HINATAZAKA, "gen": 1}, {"name": "高瀬愛奈", "group": Group.HINATAZAKA, "gen": 1}, {"name": "佐々木美玲", "group": Group.HINATAZAKA, "gen": 1},
    # 2期生
    {"name": "金村美玖", "group": Group.HINATAZAKA, "gen": 2}, {"name": "河田陽菜", "group": Group.HINATAZAKA, "gen": 2}, {"name": "小坂菜緒", "group": Group.HINATAZAKA, "gen": 2}, {"name": "丹生明里", "group": Group.HINATAZAKA, "gen": 2}, {"name": "松田好花", "group": Group.HINATAZAKA, "gen": 2},
    # 3期生
    {"name": "上村ひなの", "group": Group.HINATAZAKA, "gen": 3}, {"name": "髙橋未來虹", "group": Group.HINATAZAKA, "gen": 3}, {"name": "森本茉莉", "group": Group.HINATAZAKA, "gen": 3},
    # 4期生
    {"name": "清水理央", "group": Group.HINATAZAKA, "gen": 4}, {"name": "正源司陽子", "group": Group.HINATAZAKA, "gen": 4}, {"name": "山下葉留花", "group": Group.HINATAZAKA, "gen": 4}, {"name": "藤嶌果歩", "group": Group.HINATAZAKA, "gen": 4}, {"name": "平尾帆夏", "group": Group.HINATAZAKA, "gen": 4},
    # 5期生 (2025年加入 - 已修正)
    {"name": "大田美月", "group": Group.HINATAZAKA, "gen": 5}, {"name": "大野愛実", "group": Group.HINATAZAKA, "gen": 5}, {"name": "片山紗希", "group": Group.HINATAZAKA, "gen": 5}, {"name": "蔵盛妃那乃", "group": Group.HINATAZAKA, "gen": 5}, {"name": "坂井新奈", "group": Group.HINATAZAKA, "gen": 5}, {"name": "佐藤優羽", "group": Group.HINATAZAKA, "gen": 5}, {"name": "下田衣珠季", "group": Group.HINATAZAKA, "gen": 5}, {"name": "高井俐香", "group": Group.HINATAZAKA, "gen": 5}, {"name": "鶴崎仁香", "group": Group.HINATAZAKA, "gen": 5}, {"name": "松尾桜", "group": Group.HINATAZAKA, "gen": 5},
]

# --- 新增：定義要追蹤的生寫真系列 ---
# 每個系列會定義它包含哪些姿勢。
ALL_SETS = {
    "2025年1月月別": [Pose.Y, Pose.C, Pose.H, Pose.T], # 標準4種
    "2025年 サンタ衣装": [Pose.Y, Pose.C, Pose.H, Pose.T, Pose.SPY, Pose.SPH], # 包含特殊姿勢
    "木枯らしは泣かないMV衣装": [Pose.Y, Pose.C, Pose.H, Pose.T],
    "12th Single BACKS LIVE!! 黒衣装": [Pose.Y, Pose.C, Pose.H], # 假設只有3種姿勢
}

class Member:
    def __init__(self, name: str, group: Group, generation: int):
        self.name = name
        self.group = group
        self.generation = generation
        self.is_pinned = False # <-- 新增：釘選狀態
    def __repr__(self):
        return f"[{self.group.value}] {self.name}"

class Photo:
    # 這裡將 'owned' (布林值) 改為 'owned_count' (整數)
    def __init__(self, set_name: str, member: Member, pose: Pose, owned_count: int = 0):
        self.id = f"{member.name}_{set_name}_{pose.name}"
        self.set_name = set_name
        self.member = member
        self.pose = pose
        self.owned_count = owned_count # <-- 追蹤擁有的張數

    def to_dict(self):
        """轉換為字典，方便存儲為 JSON"""
        return {
            "id": self.id,
            "set_name": self.set_name,
            "member_name": self.member.name,
            "group": self.member.group.value, # 方便篩選和載入
            "pose": self.pose.name,
            "owned_count": self.owned_count 
        }

# --- 2. 資料儲存與載入函數 (需更新以處理多系列) ---

def load_data():
    """從 JSON 文件加載收藏數據，並根據 ALL_SETS 初始化最新的目標"""
    
    # 步驟 A: 建立所有可能的生寫真目標
    all_photos: List[Photo] = []
    member_objects = {}
    
    # 初始化 Member 物件
    for m in ALL_MEMBERS:
        member = Member(m["name"], m["group"], m["gen"])
        member_objects[m["name"]] = member
        
    # 根據 ALL_SETS 建立所有 Photo 目標
    for set_name, poses in ALL_SETS.items():
        for m in member_objects.values():
            for pose in poses:
                all_photos.append(Photo(set_name, m, pose))
            
    # 如果數據文件存在，則加載並更新 'owned_count' 狀態
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            # 建立一個以 ID 為鍵的字典，方便快速查找和更新
            saved_status = {d['id']: d['owned_count'] for d in saved_data if 'owned_count' in d}
            
            for photo in all_photos:
                if photo.id in saved_status:
                    photo.owned_count = saved_status[photo.id]
            
            st.sidebar.success(f"成功加載 {len(saved_data)} 筆收藏紀錄！")
        except json.JSONDecodeError:
            st.sidebar.error("警告：收藏數據文件已損壞或格式錯誤，已重新初始化。")
            save_data(all_photos) 
    else:
        st.sidebar.info("首次運行，已初始化多系列追蹤清單。")
        save_data(all_photos) 
        
    return all_photos

def save_data(photos: List[Photo]):
    """將當前收藏數據保存到 JSON 文件"""
    # 這裡只儲存 Photo 資料
    data_to_save = [p.to_dict() for p in photos]
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

# --- 3. 核心功能：計算收藏進度 (現在可以分系列計算) ---

def calculate_progress(photos: List[Photo], selected_set: Optional[str] = None) -> Dict[str, Dict]:
    """計算所有成員在指定系列中的收藏進度"""
    progress: Dict[str, Dict] = {}
    
    # 篩選出選定的系列
    filtered_photos = photos
    if selected_set and selected_set != "所有系列總計":
        filtered_photos = [p for p in photos if p.set_name == selected_set]
        
    for photo in filtered_photos:
        name = photo.member.name
        if name not in progress:
            progress[name] = {'group': photo.member.group.value, 'total_needed': 0, 'total_collected': 0}
        
        progress[name]['total_needed'] += 1 
        progress[name]['total_collected'] += photo.owned_count 
    return progress

# --- 4. 初始化數據 ---
st.session_state.photo_set = load_data()


# --- 5. Streamlit APP 頁面佈局 ---

st.set_page_config(layout="wide", page_title="坂道生寫真收藏追蹤器")
st.title("🌸 坂道生寫真收藏追蹤器 (V3.0 多系列追蹤)")
st.markdown("---")


# A. 側邊欄控制項

with st.sidebar:
    st.header("🎛️ 追蹤控制")
    
    # 需求 4: 系列選擇器 (Series Selector)
    set_options = list(ALL_SETS.keys())
    set_options.insert(0, "所有系列總計")
    selected_set = st.selectbox("選擇要追蹤的系列:", options=set_options)

    # 顯示成員名單
    st.markdown("---")
    st.header("現役成員名單")
    for group in Group:
        st.subheader(group.value)
        group_members = [m['name'] for m in ALL_MEMBERS if m['group'] == group]
        if group_members:
            st.markdown(", ".join(group_members))


# B. 收藏進度總覽

st.header(f"🎯 進度總覽: {selected_set}")
progress_data = calculate_progress(st.session_state.photo_set, selected_set)

progress_table_data = []
for name, data in progress_data.items():
    collected = data['total_collected']
    needed = data['total_needed']
    
    # 完成度 (以至少完成一個 Set 計算)
    completion_percentage = (min(collected, needed) / needed) * 100 if needed > 0 else 0
    
    progress_table_data.append({
        "團體": data['group'],
        "成員": name,
        "目標/擁有": f"{needed} 張目標 / {collected} 張",
        "完成度 (至少 1 Set)": completion_percentage,
        "擁有總張數": collected, 
    })

# 排序: 優先顯示完成度最高的
progress_table_data = sorted(progress_table_data, key=lambda x: x['完成度 (至少 1 Set)'], reverse=True)


st.dataframe(
    progress_table_data,
    column_config={
        "完成度 (至少 1 Set)": st.column_config.ProgressColumn(
            "完成度 (至少 1 Set)",
            help="完成該成員在這個系列中的一整套的進度",
            format="%f%%",
            min_value=0,
            max_value=100,
        ),
        "擁有總張數": st.column_config.NumberColumn(
            "擁有總張數",
            format="%d 張",
        )
    },
    hide_index=True,
)

st.markdown("---")

# C. 追蹤頁面

st.header(f"🗂️ 追蹤系列: {selected_set}")

# 按成員分組展示 (只顯示在選定系列中有生寫真的成員)
member_groups = {}
current_set_photos = [p for p in st.session_state.photo_set if p.set_name == selected_set or selected_set == "所有系列總計"]

# 整理分組數據
for photo in current_set_photos:
    name = photo.member.name
    if name not in member_groups:
        member_groups[name] = []
    member_groups[name].append(photo)

# 建立分頁標籤
member_names = sorted(list(member_groups.keys()))
tabs = st.tabs(member_names)

# 在每個分頁中顯示該成員的所有生寫真
for i, name in enumerate(member_names):
    with tabs[i]:
        # 顯示該成員在當前選定系列中的擁有總數
        current_collected = progress_data.get(name, {}).get('total_collected', 0)
        st.subheader(f"追蹤 {name} 的生寫真 - 已擁有總數: {current_collected}")
        
        st.write("---")
        
        # 顯示該成員在選定系列中的每個姿勢
        photos_to_display = sorted(member_groups[name], key=lambda p: p.set_name)
        
        for photo in photos_to_display:
            
            # 定義一個回調函數，在狀態改變時執行
            def update_photo_and_save(p=photo):
                new_count = max(0, st.session_state[f"count_{p.id}"])
                p.owned_count = new_count
                save_data(st.session_state.photo_set)
            
            # 如果選中「所有系列總計」，則顯示系列名稱
            label = photo.pose.value
            if selected_set == "所有系列總計":
                 label = f"[{photo.set_name}] {photo.pose.value}"

            st.number_input(
                f"**{label}**", 
                min_value=0, 
                value=photo.owned_count, 
                key=f"count_{photo.id}",
                on_change=update_photo_and_save, 
                step=1 
            )