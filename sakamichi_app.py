import streamlit as st
from enum import Enum
import json
from typing import List, Dict, Optional
import os
import base64 

# --- 0. 設定檔案路徑 ---
DATA_FILE = "sakamichi_collection_data.json"

# --- 1. 核心資料模型 ---

# 生寫真類型 (Pose)
class Pose(Enum):
    # value: 顯示的中文名稱, image_suffix: 圖片檔案後綴名 (用於圖片網址生成)
    Y = (1,"ヨリ (より)", "yori.jpg")
    C = (2,"チュウ (ちゅう)", "chuu.jpg")
    H = (3,"ヒキ (ひき)", "hiki.jpg")
    SPY = (10,"特殊ヨリ (スペシャルより)", "spyori.jpg")
    SPH = (11,"特殊ヒキ (スペシャルひき)", "sphiki.jpg")
    
    def __new__(cls, order, value, image_suffix):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.order = order
        obj.image_suffix = image_suffix
        return obj

# 坂道團體 (Group)
class Group(Enum):
    NOGIZAKA = "乃木坂46"
    SAKURAZAKA = "櫻坂46"
    HINATAZAKA = "日向坂46"

# 固定的成員名單 (與 V8.8.23 相同)
ALL_MEMBERS = [
    # 乃木坂46 (NOGIZAKA)
    # 3期生 (加入所有現役3期生)
    {"name": "伊藤理々杏", "group": Group.NOGIZAKA, "gen": 3}, {"name": "岩本蓮加", "group": Group.NOGIZAKA, "gen": 3},
    {"name": "梅澤美波", "group": Group.NOGIZAKA, "gen": 3}, {"name": "吉田綾乃クリスティー", "group": Group.NOGIZAKA, "gen": 3},

    # 4期生 (加入所有現役4期生)
    {"name": "遠藤さくら", "group": Group.NOGIZAKA, "gen": 4}, {"name": "賀喜遥香", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "弓木奈於", "group": Group.NOGIZAKA, "gen": 4}, {"name": "金川紗耶", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "黒見明香", "group": Group.NOGIZAKA, "gen": 4}, {"name": "佐藤璃果", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "柴田柚菜", "group": Group.NOGIZAKA, "gen": 4}, {"name": "林瑠奈", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "田村真佑", "group": Group.NOGIZAKA, "gen": 4}, {"name": "筒井あやめ", "group": Group.NOGIZAKA, "gen": 4},

    # 5期生 (加入所有現役5期生)
    {"name": "井上和", "group": Group.NOGIZAKA, "gen": 5}, {"name": "一ノ瀬美空", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "小川彩", "group": Group.NOGIZAKA, "gen": 5}, {"name": "奥田いろは", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "川﨑桜", "group": Group.NOGIZAKA, "gen": 5}, {"name": "菅原咲月", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "冨里奈央", "group": Group.NOGIZAKA, "gen": 5}, {"name": "中西アルノ", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "五百城茉央", "group": Group.NOGIZAKA, "gen": 5}, {"name": "池田瑛紗", "group": Group.NOGIZAKA, "gen": 5}, 
    {"name": "岡本姫奈", "group": Group.NOGIZAKA, "gen": 5}, 

    # 6期生 (最新加入的 6 期生，請根據官方公告調整)
    {"name": "矢田萌華", "group": Group.NOGIZAKA, "gen": 6}, {"name": "瀬戸口心月", "group": Group.NOGIZAKA, "gen": 6},
    {"name": "川端晃菜", "group": Group.NOGIZAKA, "gen": 6}, {"name": "海邉朱莉", "group": Group.NOGIZAKA, "gen": 6}, 
    {"name": "長嶋凛桜", "group": Group.NOGIZAKA, "gen": 6}, {"name": "森平麗心", "group": Group.NOGIZAKA, "gen": 6}, 
    {"name": "愛宕心響", "group": Group.NOGIZAKA, "gen": 6}, {"name": "大越ひなの", "group": Group.NOGIZAKA, "gen": 6},
    {"name": "鈴木佑捺", "group": Group.NOGIZAKA, "gen": 6}, {"name": "小津玲奈", "group": Group.NOGIZAKA, "gen": 6},
    {"name": "増田三莉音", "group": Group.NOGIZAKA, "gen": 6}, 

    # 櫻坂46 (SAKURAZAKA)
    # 2期生 (原櫸坂46 2期生)
    {"name": "山﨑天", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "遠藤光莉", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "大園玲", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "大沼晶保", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "幸阪茉里乃", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "武元唯衣", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "田村保乃", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "藤吉夏鈴", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "増本綺良", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "松田里奈", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "森田ひかる", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "守屋麗奈", "group": Group.SAKURAZAKA, "gen": 2},

    # 3期生
    {"name": "石森璃花", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "遠藤理子", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "小田倉麗奈", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "小島凪紗", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "中嶋優月", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "的野美青", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "向井純葉", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "村井優", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "山下瞳月", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "谷口愛季", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "村山美羽", "group": Group.SAKURAZAKA, "gen": 3},

    # 4期生
    {"name": "浅井恋乃未", "group": Group.SAKURAZAKA, "gen": 3},{"name": "稲熊ひな", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "勝又春", "group": Group.SAKURAZAKA, "gen": 3},{"name": "佐藤愛桜", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "中川智尋", "group": Group.SAKURAZAKA, "gen": 3},{"name": "松本和子", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "目黒陽色", "group": Group.SAKURAZAKA, "gen": 3},{"name": "山川宇衣", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "山田桃実", "group": Group.SAKURAZAKA, "gen": 3},

    # 日向坂46 (HINATAZAKA)
    # 2期生 (原平假名櫸坂46 2期生)
    {"name": "金村美玖", "group": Group.HINATAZAKA, "gen": 2},{"name": "小坂菜緒", "group": Group.HINATAZAKA, "gen": 2}, 
    {"name": "松田好花", "group": Group.HINATAZAKA, "gen": 2}, 

    # 3期生
    {"name": "上村ひなの", "group": Group.HINATAZAKA, "gen": 3}, {"name": "髙橋未來虹", "group": Group.HINATAZAKA, "gen": 3}, 
    {"name": "森本茉莉", "group": Group.HINATAZAKA, "gen": 3}, {"name": "山口陽世", "group": Group.HINATAZAKA, "gen": 3}, 

    # 4期生
    {"name": "清水理央", "group": Group.HINATAZAKA, "gen": 4}, {"name": "正源司陽子", "group": Group.HINATAZAKA, "gen": 4}, 
    {"name": "平尾帆夏", "group": Group.HINATAZAKA, "gen": 4}, {"name": "藤嶌果歩", "group": Group.HINATAZAKA, "gen": 4},
    {"name": "山下葉留花", "group": Group.HINATAZAKA, "gen": 4},{"name": "石塚瑶季", "group": Group.HINATAZAKA,"gen": 4}, 
    {"name": "小西夏菜実", "group": Group.HINATAZAKA, "gen": 4},{"name": "竹内希来里", "group": Group.HINATAZAKA, "gen": 4}, 
    {"name": "平岡海月", "group": Group.HINATAZAKA, "gen": 4},{"name": "宮地すみれ", "group": Group.HINATAZAKA, "gen": 4}, 
    {"name": "渡辺莉奈", "group": Group.HINATAZAKA, "gen": 4}, 

    # 5期生 (最新加入的 5 期生，請根據官方公告調整)
    {"name": "大田美月", "group": Group.HINATAZAKA, "gen": 5}, {"name": "大野愛実", "group": Group.HINATAZAKA, "gen": 5},
    {"name": "片山紗希", "group": Group.HINATAZAKA, "gen": 5}, {"name": "蔵盛妃那乃", "group": Group.HINATAZAKA, "gen": 5},
    {"name": "坂井新奈", "group": Group.HINATAZAKA, "gen": 5}, {"name": "佐藤優羽", "group": Group.HINATAZAKA, "gen": 5},
    {"name": "下田衣珠季", "group": Group.HINATAZAKA, "gen": 5}, {"name": "高井俐香", "group": Group.HINATAZAKA, "gen": 5},
    {"name": "鶴崎仁香", "group": Group.HINATAZAKA, "gen": 5}, {"name": "松尾桜", "group": Group.HINATAZAKA, "gen": 5},
]
# --- 動態系列管理：預設系列 (已清空所有預設系列) ---
DEFAULT_SETS_BY_GROUP = {
    Group.NOGIZAKA.value: {},
    Group.SAKURAZAKA.value: {},
    Group.HINATAZAKA.value: {}
}

class Member:
    def __init__(self, name: str, group: Group, generation: int):
        self.name = name
        self.group = group
        self.generation = generation
        self.is_pinned = False
    def __repr__(self):
        return f"[{self.group.value}] {self.name}"

class Photo:
    # 圖片基底網址 (!!!請自行替換為您圖片的公開網址!!!)
    BASE_IMAGE_URL = "https://example.com/images/sakamichi/" 

    def __init__(self, set_name: str, member: Member, pose: Pose, owned_count: int = 0, custom_image_url: Optional[str] = None):
        self.id = f"{member.name}_{set_name}_{pose.name}"
        self.set_name = set_name
        self.member = member
        self.pose = pose
        self.owned_count = owned_count
        self.custom_image_url = custom_image_url
        self.image_url = custom_image_url if custom_image_url else self._generate_image_url()

    def _generate_image_url(self):
        """生成圖片網址 (您需要確保您的圖片命名和上傳位置與此邏輯匹配)"""
        member_name_for_url = self.member.name 
        set_name_for_url = self.set_name.replace(" ", "_")
        return f"{Photo.BASE_IMAGE_URL}{member_name_for_url}_{set_name_for_url}_{self.pose.image_suffix}"

    def to_dict(self):
        """轉換為字典，方便存儲為 JSON"""
        return {
            "id": self.id,
            "set_name": self.set_name,
            "member_name": self.member.name,
            "group": self.member.group.value, 
            "pose": self.pose.name,
            "owned_count": self.owned_count,
            "custom_image_url": self.custom_image_url 
        }

# --- 2. 資料儲存與載入函數 ---
ALL_SETS_BY_GROUP: Dict[str, Dict] = {}

def save_data(photos: List['Photo'], sets_by_group: Dict[str, Dict]):
    """將收藏數據和系列定義保存到 JSON 文件"""
    
    collection_data = [photo.to_dict() for photo in photos]
    sets_data = sets_by_group 
    
    data_to_save = {
        "sets": sets_data,
        "collection": collection_data
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    # st.sidebar.info("數據已自動保存。") 


def load_data():
    """從 JSON 文件加載系列定義和收藏數據，並初始化 Photo 列表"""
    
    # 步驟 A: 初始化成員物件和照片列表
    all_photos: List[Photo] = []
    member_objects: Dict[str, Member] = {}
    for member_info in ALL_MEMBERS:
        name = member_info['name']
        group_enum = member_info['group'] 
        gen = member_info['gen']
        member = Member(name, group_enum, gen)
        member_objects[name] = member
        
    # 步驟 B: 決定要使用的系列定義 (從 JSON 載入或使用預設)
    global ALL_SETS_BY_GROUP
    ALL_SETS_BY_GROUP = {g: sets for g, sets in DEFAULT_SETS_BY_GROUP.items()} 
    
    saved_collection_data = []

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            if 'sets' in full_data and full_data['sets']:
                ALL_SETS_BY_GROUP = full_data['sets']
                
            if 'collection' in full_data:
                saved_collection_data = full_data['collection'] 
                
        
        except json.JSONDecodeError:
            st.error("⚠️ 數據文件損壞 (JSONDecodeError)，將使用空白初始化數據！")
            
        except Exception as e:
            st.error(f"⚠️ 載入數據時發生未知錯誤: {e}")
            
    # 🌟 V8.8.24 修正：定義有效的 Pose 鍵集合
    VALID_POSE_KEYS = set(p.name for p in Pose)

    # 步驟 C: 根據系列定義初始化 Photo 物件
    for group_value, sets in ALL_SETS_BY_GROUP.items():
        try:
            group_enum = Group(group_value)
        except ValueError:
            continue

        for set_name, set_info in sets.items():
            
            member_names_for_set = set_info.get("member_list", [])
            pose_names_for_set = set_info.get("poses", [])
            
            # 🌟 V8.8.24 修正：動態清理無效的 Pose
            cleaned_pose_names_for_set = []
            for pose_name in pose_names_for_set:
                if pose_name in VALID_POSE_KEYS:
                    cleaned_pose_names_for_set.append(pose_name)
                # 提示：如果這裡偵測到 T，它會被忽略。
            
            # 將清理後的列表存回 ALL_SETS_BY_GROUP，這樣在編輯頁面載入時就是乾淨的
            set_info["poses"] = cleaned_pose_names_for_set 
            
            for member_name in member_names_for_set:
                if member_name in member_objects and member_objects[member_name].group == group_enum:
                    member = member_objects[member_name]
                    
                    for pose_name in cleaned_pose_names_for_set: # 使用清理後的列表
                        try:
                            pose = Pose[pose_name]
                            photo = Photo(set_name, member, pose)
                            all_photos.append(photo)
                            
                        except KeyError:
                            # 由於我們已經在上面清理過，理論上這裡不應該再發生 KeyError
                            continue
    
    # 步驟 D: 載入張數狀態 
    saved_status = {
        d['id']: {
            'owned_count': d['owned_count'],
            'custom_image_url': d.get('custom_image_url')
        } 
        for d in saved_collection_data if 'owned_count' in d
    }
            
    for photo in all_photos:
        if photo.id in saved_status:
            status = saved_status[photo.id]
            photo.owned_count = status['owned_count']
            
            if status['custom_image_url']:
                photo.custom_image_url = status['custom_image_url']
                photo.image_url = status['custom_image_url']
                
    if not os.path.exists(DATA_FILE) or not any(ALL_SETS_BY_GROUP.values()):
        save_data(all_photos, ALL_SETS_BY_GROUP)
        
    # 在 load_data 結束時，將清理過的系列定義寫回 JSON，確保下次啟動是乾淨的
    save_data(all_photos, ALL_SETS_BY_GROUP)
        
    return all_photos
# -------------------- load_data 函數結束 --------------------


# --- 函數區：單張/批量操作 (略，與 V8.8.23 相同) ---

def update_photo_and_save():
    """處理圖片張數/URL/檔案上傳的變更並儲存"""
    photo_id = st.session_state.get('last_updated_photo_id')
    if not photo_id:
        return 

    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == photo_id), None)
    
    if updated_photo:
        new_count = max(0, st.session_state.get(f"count_{photo_id}_num_input", updated_photo.owned_count))
        new_url = st.session_state.get(f"url_input_{photo_id}", "").strip()
        uploaded_file = st.session_state.get(f"file_uploader_{photo_id}")
        
        new_custom_image_source = None
        
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            file_type = uploaded_file.type
            base64_encoded_data = base64.b64encode(bytes_data).decode('utf-8')
            new_custom_image_source = f"data:{file_type};base64,{base64_encoded_data}"
            
        elif new_url:
            new_custom_image_source = new_url
            
        updated_photo.owned_count = new_count
        
        if new_custom_image_source != updated_photo.custom_image_url:
            updated_photo.custom_image_url = new_custom_image_source
            updated_photo.image_url = new_custom_image_source if new_custom_image_source else updated_photo._generate_image_url()
            
        if not new_custom_image_source:
            updated_photo.custom_image_url = None
            updated_photo.image_url = updated_photo._generate_image_url()
            
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        st.session_state[f"count_{photo_id}_num_input"] = updated_photo.owned_count 

def set_update_tracker(p_id):
    """設置追蹤器，確保 on_change 能找到正確的 ID"""
    st.session_state['last_updated_photo_id'] = p_id
    st.rerun() 

def decrement_count(p_id):
    current_count = st.session_state.get(f"count_{p_id}_num_input", 0) 
    new_count = max(0, current_count - 1)
    
    st.session_state[f"count_{p_id}_num_input"] = new_count
    
    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == p_id), None)
    if updated_photo:
        updated_photo.owned_count = new_count
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
    st.rerun()  

def increment_count(p_id):
    current_count = st.session_state.get(f"count_{p_id}_num_input", 0)
    new_count = current_count + 1
    
    st.session_state[f"count_{p_id}_num_input"] = new_count
    
    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == p_id), None)
    if updated_photo:
        updated_photo.owned_count = new_count
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
    st.rerun()  


# 將單張生寫真張數設定為 0
def set_count_to_zero(photo_id: str):
    """將指定的 Photo 張數設定為 0 並儲存"""
    
    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == photo_id), None)
    
    if updated_photo:
        updated_photo.owned_count = 0
        
        st.session_state[f"count_{photo_id}_num_input"] = 0
        
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        st.rerun() 
    else:
        st.error(f"找不到 ID 為 {photo_id} 的生寫真。")

# 核心批量修正函數：set_n_sets_collected
def set_n_sets_collected(member_name: str, current_set_name: str, target_n: int):
    """將指定成員在指定系列中的所有生寫真張數設為目標套數 N"""
    
    if current_set_name == "所有系列總計":
        st.error("無法在 '所有系列總計' 模式下進行一鍵設定。請先選擇一個特定系列。")
        return
    
    target_count = max(1, target_n) 
    photos_updated = 0
    
    for photo in st.session_state.photo_set:
        if photo.member.name == member_name and photo.set_name == current_set_name:
            
            if photo.owned_count < target_count: 
                photo.owned_count = target_count
                photos_updated += 1
            
            st.session_state[f"count_{photo.id}_num_input"] = photo.owned_count
            
    if photos_updated > 0:
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        st.success(f"已將 **{member_name}** 在 **{current_set_name}** 中的 {photos_updated} 張生寫真張數設為 {target_count} (收齊 {target_n} 套)。")
        
        st.rerun() 
        
    else:
        st.info(f"**{member_name}** 在 **{current_set_name}** 中的生寫真已經滿足 {target_n} 套目標，無需變更。")

# 釘選成員函數
def toggle_pin_and_save(member_name: str):
    """切換成員的釘選狀態並儲存 (實際只是觸發 st.rerun)"""
    
    current_pin_state = st.session_state.get(f"pin_{member_name}", False)
    st.session_state[f"pin_{member_name}"] = not current_pin_state
    st.rerun()


# --- 函數區：管理系列 ---

def set_manage_tab():
    """設定當前選中的管理 Tab"""
    new_tab_value = st.session_state.get("manage_radio_tabs")
    if new_tab_value:
        st.session_state.manage_tab_state = new_tab_value

def load_edit_set_data():
    """根據選中的系列 ID，將其成員和姿勢載入到 session_state 暫存變數中"""
    selected_edit_id = st.session_state.get("edit_set_id") 

    if selected_edit_id:
        group_value, set_name = selected_edit_id.split("|", 1)
        
        # 這裡讀取的是 load_data 清理後的 ALL_SETS_BY_GROUP
        current_info = st.session_state.all_sets_by_group.get(group_value, {}).get(set_name, {})
        
        st.session_state.edit_current_group_value = group_value 
        st.session_state.edit_current_members = current_info.get("member_list", [])
        # 由於 load_data 已經清理過，這裡的 poses 就不會包含 T
        st.session_state.edit_current_poses = current_info.get("poses", []) 
        
    else:
        st.session_state.edit_current_group_value = None
        st.session_state.edit_current_members = []
        st.session_state.edit_current_poses = []
        
def get_available_member_names(group_identifier: str, current_members: Optional[List[str]] = None) -> List[str]:
    """獲取指定團體的現役成員名稱列表 (輸入為團體中文名稱字串)"""
    
    try:
        group_enum = Group(group_identifier)
    except ValueError:
        return []

    available_members = sorted(list(m['name'] for m in ALL_MEMBERS if m['group'] == group_enum))
    
    if not available_members and current_members:
        return current_members
    
    return available_members


def add_new_set():
    """新增系列邏輯"""
    final_selected_poses = st.session_state.get("add_set_poses", []) 
    new_set_name = st.session_state.get("new_set_name", "").strip() 
    new_group_value = st.session_state.get("new_set_group")
    selected_members = st.session_state.get("selected_members", [])

    if not new_set_name or not final_selected_poses or not selected_members:
        st.error("系列名稱、姿勢和適用成員不能為空。")
        return
        
    current_sets = st.session_state.all_sets_by_group 

    group_key = new_group_value
    if group_key not in current_sets:
        current_sets[group_key] = {}
    
    if new_set_name in current_sets[group_key]:
        st.warning(f"系列 '{new_set_name}' 已存在於 {new_group_value} 中。請改用編輯功能。")
        return

    new_set_info = {
        "poses": final_selected_poses,
        "member_list": selected_members
    }
    current_sets[group_key][new_set_name] = new_set_info
    
    # 重新載入數據以生成新的 Photo 物件並儲存
    st.session_state.photo_set = load_data() 
    save_data(st.session_state.photo_set, current_sets)
    
    # 確保 session state 立即更新
    st.session_state.all_sets_by_group = current_sets
    st.session_state.all_sets_by_group_str = current_sets
    
    st.success(f"成功新增系列: {new_set_name}！")
    
    # 關鍵修正：清除 Selectbox 的狀態鍵，強制它使用新的 options 列表重新繪製。
    if 'tracking_set_id' in st.session_state:
        del st.session_state['tracking_set_id']
        
    st.rerun() 
    
def edit_existing_set():
    """編輯系列邏輯"""
    edit_set_id = st.session_state.get("edit_set_id") 
    final_edit_poses = st.session_state.get("edit_set_poses", []) 
    final_edit_members = st.session_state.get("edit_selected_members", [])

    if not edit_set_id:
        st.warning("請先選擇要編輯的系列。")
        return
        
    if not final_edit_poses or not final_edit_members:
        st.error("姿勢和適用成員不能為空。")
        return

    group_value, set_name = edit_set_id.split("|", 1)
    
    if group_value in st.session_state.all_sets_by_group and set_name in st.session_state.all_sets_by_group[group_value]:
        st.session_state.all_sets_by_group[group_value][set_name] = {
            "poses": final_edit_poses,
            "member_list": final_edit_members
        }
        
        # 重新載入數據以應用變更並儲存 (舊的 Photo 物件會被替換/更新)
        st.session_state.photo_set = load_data()
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        # 確保 session state 立即更新
        st.session_state.all_sets_by_group_str = st.session_state.all_sets_by_group
        
        st.success(f"成功更新系列: {set_name}！")
        
        # 編輯後也清除 Selectbox 的狀態鍵，避免選項索引錯位
        if 'tracking_set_id' in st.session_state:
            del st.session_state['tracking_set_id']
            
        st.rerun()
        

def hard_reload_after_delete():
    """清除所有 Streamlit UI 狀態鍵，模擬頁面首次載入，並強制 st.rerun()"""
    
    keys_to_delete = ["tracking_set_id", "edit_set_id", "manage_radio_tabs", 
                      "edit_current_group_value", "edit_current_members", 
                      "edit_current_poses"]
    
    for key in keys_to_delete:
        if key in st.session_state:
             del st.session_state[key]
             
    st.rerun()


def delete_existing_set_on_edit():
    """刪除系列邏輯 (作為 on_click 函數執行)"""
    delete_set_id = st.session_state.get("edit_set_id")

    if not delete_set_id:
        st.session_state['delete_success_flag'] = "請先選擇要刪除的系列。" 
        return

    group_value, set_name = delete_set_id.split("|", 1)
    
    if group_value in st.session_state.all_sets_by_group and set_name in st.session_state.all_sets_by_group[group_value]:
        # 1. 從系列定義中刪除
        del st.session_state.all_sets_by_group[group_value][set_name]
        
        # 2. 清理收藏紀錄並儲存
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        # 3. 清理與編輯相關的 session state key
        if 'edit_set_id' in st.session_state:
            del st.session_state['edit_set_id']
        
        # 在刪除操作中，也需要清除 'tracking_set_id' 鍵
        if 'tracking_set_id' in st.session_state:
            del st.session_state['tracking_set_id']
            
        # 4. 設定刪除標誌
        st.session_state['delete_success_flag'] = f"成功刪除系列: {set_name}！請點擊下方的按鈕刷新介面。"
        
    else:
        st.error(f"找不到要刪除的系列: {set_name}，可能團體鍵 {group_value} 匹配失敗。")


# --- 側邊欄繪製函數 ---

def draw_sidebar_controls():
    """
    繪製側邊欄控制項，使用 st.container() 確保內容連貫。
    """
    with st.container():
        st.header("🎛️ 追蹤控制")
        
        all_set_options = ["所有系列總計"]
        
        # 根據最新的 session state 重新生成選項列表
        for group_sets in st.session_state.all_sets_by_group_str.values():
            all_set_options.extend(list(group_sets.keys()))
            
        # 系列選擇器 (Series Selector)
        
        # 嘗試從 session_state 讀取選中值，如果被清除 (例如新增後)，則為 None
        selected_tracking_set = st.session_state.get("tracking_set_id")
        
        if selected_tracking_set not in all_set_options:
            # 如果 session_state 值不在新的選項列表中
            if all_set_options:
                selected_tracking_set = all_set_options[0] # 選第一個有效選項
            else:
                selected_tracking_set = "所有系列總計" # 預設值

        
        # 計算 index，如果 selected_tracking_set 為 None 或不在列表中，index 將是 0
        current_index = all_set_options.index(selected_tracking_set) if selected_tracking_set in all_set_options else 0

        # 繪製 Selectbox
        selected_set_output = st.selectbox(
            "選擇要追蹤的系列:", 
            options=all_set_options,
            index=current_index,
            key="tracking_set_id"
        )
        
        if len(all_set_options) == 1:
            st.warning("目前沒有任何系列，請在下方 '管理系列' 區塊新增。")

        # 顯示成員名單
        st.markdown("---")
        st.header("現役成員名單")
        for group in Group:
            st.subheader(group.value)
            group_members = [m['name'] for m in ALL_MEMBERS if m['group'] == group] 
            if group_members:
                st.markdown(", ".join(group_members))
                
    return selected_set_output
# --- 側邊欄繪製函數結束 ---


# --- 4. 初始化數據 ---
# 確保 load_data 在 Streamlit session_state 初始化
if 'photo_set' not in st.session_state:
    
    # A. 載入數據，這會返回 photo_set，並將 ALL_SETS_BY_GROUP 變數設定好
    st.session_state.photo_set = load_data()
    
    # B. 核心 Session State 變數初始化
    # 這裡必須使用 load_data 結束後被更新的 ALL_SETS_BY_GROUP
    st.session_state.all_sets_by_group = ALL_SETS_BY_GROUP 
    
    # 🎯 修正點：確保 all_sets_by_group_str 在 photo_set 首次載入時就設定
    st.session_state.all_sets_by_group_str = ALL_SETS_BY_GROUP 

# C. 其他 Session State 變數初始化
if 'expanded_state' not in st.session_state:
    st.session_state.expanded_state = False
    
VALID_TABS = ["新增系列", "編輯/刪除現有系列"]
if 'manage_tab_state' not in st.session_state or st.session_state.manage_tab_state not in VALID_TABS:
    st.session_state.manage_tab_state = "新增系列"
    
if 'edit_current_group_value' not in st.session_state:
    st.session_state.edit_current_group_value = None
if 'edit_current_members' not in st.session_state:
    st.session_state.edit_current_members = []
if 'edit_current_poses' not in st.session_state:
    st.session_state.edit_current_poses = []
    
if 'edit_set_id' not in st.session_state:
    st.session_state['edit_set_id'] = None

# 🌟 臨時強制執行 load_data 刷新數據和類別實例 (完成後可移除)
st.session_state.photo_set = load_data() 

# 檢查並修正 'photo_set' 的初始化
if 'photo_set' not in st.session_state:
    # st.session_state.photo_set = load_data() # 移除此處的重複呼叫
    st.session_state.all_sets_by_group = ALL_SETS_BY_GROUP 
    st.session_state.all_sets_by_group_str = ALL_SETS_BY_GROUP
# ... 其他初始化代碼

# 狀態初始化 
if 'expanded_state' not in st.session_state:
    st.session_state.expanded_state = False
    
VALID_TABS = ["新增系列", "編輯/刪除現有系列"]
if 'manage_tab_state' not in st.session_state or st.session_state.manage_tab_state not in VALID_TABS:
    st.session_state.manage_tab_state = "新增系列"
    
if 'edit_current_group_value' not in st.session_state:
    st.session_state.edit_current_group_value = None
if 'edit_current_members' not in st.session_state:
    st.session_state.edit_current_members = []
if 'edit_current_poses' not in st.session_state:
    st.session_state.edit_current_poses = []
    
if 'edit_set_id' not in st.session_state:
    st.session_state['edit_set_id'] = None


# --- 3. 核心功能：計算收藏進度 ---

def calculate_progress(photos: List[Photo], selected_set: Optional[str] = None) -> Dict[str, Dict]:
    """計算所有成員在指定系列中的收藏進度"""
    progress: Dict[str, Dict] = {}
    
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

# --- 5. Streamlit APP 頁面佈局 ---

st.set_page_config(layout="wide", page_title="坂道生寫真收藏追蹤器")
st.title("🌸 坂道生寫真收藏追蹤器 (V8.8.24 - 修正 Pose 錯誤)")
st.markdown("---")


# A. 側邊欄控制項 
with st.sidebar:
    selected_set = draw_sidebar_controls()


# B. 收藏進度總覽

st.header(f"🎯 進度總覽: {selected_set}")
progress_data = calculate_progress(st.session_state.photo_set, selected_set)

progress_table_data = []
for name, data in progress_data.items():
    collected = data['total_collected']
    needed = data['total_needed']
    
    completion_percentage = (min(collected, needed) / needed) * 100 if needed > 0 else 0
    
    progress_table_data.append({
        "團體": data['group'],
        "成員": name,
        "目標/擁有": f"{needed} 張目標 / {collected} 張",
        "完成度 (至少 1 Set)": completion_percentage,
        "擁有總張數": collected, 
        "可交換張數 (重覆)": max(0, collected - needed) 
    })

progress_table_data = sorted(progress_table_data, key=lambda x: x['完成度 (至少 1 Set)'], reverse=True)

if progress_table_data:
    st.dataframe(
        progress_table_data,
        column_config={
            "完成度 (至少 1 Set)": st.column_config.ProgressColumn(
                "完成度 (至少 1 Set)",
                format="%f%%",
                min_value=0,
                max_value=100,
            ),
            "擁有總張數": st.column_config.NumberColumn(
                "擁有總張數",
                format="%d 張",
                step=1
            ),
            "可交換張數 (重覆)": st.column_config.NumberColumn(
                "可交換張數 (重覆)",
                format="%d 張",
                step=1
            )
        },
        hide_index=True,
    )
else:
      st.info("請在下方 '管理系列' 區塊新增至少一個系列，以開始追蹤進度。")


st.markdown("---")


# C. 追蹤頁面 

member_objects_dict = {}
current_set_photos = [p for p in st.session_state.photo_set if p.set_name == selected_set or selected_set == "所有系列總計"]

for photo in st.session_state.photo_set:
    if photo.member.name not in member_objects_dict:
        member_objects_dict[photo.member.name] = photo.member
        
for photo in current_set_photos:
    name = photo.member.name
    photo.member.is_pinned = st.session_state.get(f"pin_{name}", False)
    
member_groups = {}
for photo in current_set_photos:
    name = photo.member.name
    if name not in member_groups:
        member_groups[name] = []
    member_groups[name].append(photo)

member_names = sorted(
    list(member_groups.keys()), 
    key=lambda name: (not member_objects_dict[name].is_pinned, name)
)

if member_names:
    tabs = st.tabs(member_names)

    for i, name in enumerate(member_names):
        member = member_objects_dict[name]
        with tabs[i]: 
            
            # -------------------- 成員標題與批量操作按鈕 (N 套修正版) --------------------
            col_title, col_target, col_set_n, col_pin = st.columns([0.4, 0.2, 0.2, 0.2])
            
            with col_title:
                current_collected = progress_data.get(name, {}).get('total_collected', 0)
                st.subheader(f"追蹤 {name} 的生寫真 - 已擁有總數: {current_collected}")
            
            with col_target:
                target_n = st.number_input(
                    "目標收齊套數 N",
                    min_value=1,
                    value=1,
                    key=f"target_n_{name}", 
                    step=1,
                    label_visibility="collapsed"
                )
                
            with col_set_n:
                st.markdown("<br>", unsafe_allow_html=True)
                st.button(
                    f"收齊 {target_n} 套", 
                    key=f"set_n_btn_{name}", 
                    on_click=set_n_sets_collected, 
                    args=(name, selected_set, target_n), 
                    type="primary",
                    use_container_width=True
                )
            
            with col_pin:
                st.markdown("<br>", unsafe_allow_html=True)
                is_pinned = st.session_state.get(f"pin_{name}", False)
                pin_label = "📌 已釘選" if is_pinned else "未釘選"
                st.button(
                    pin_label, 
                    key=f"pin_btn_{name}", 
                    on_click=toggle_pin_and_save, 
                    args=(name,),
                    type="secondary" if is_pinned else "secondary",
                    use_container_width=True
                )
            
            st.write("---")
            # -------------------- 標題與按鈕結束 --------------------
            
            photos_to_display = sorted(member_groups[name], key=lambda p: (p.set_name, p.pose.order))
            
            for photo in photos_to_display:
                col_img, col_input, col_zero, col_file, col_url = st.columns([1, 0.4, 0.2, 1.2, 1.2]) 
                
                if f"count_{photo.id}_num_input" not in st.session_state:
                    st.session_state[f"count_{photo.id}_num_input"] = photo.owned_count
                
                with col_img:
                    label = photo.pose.value
                    if selected_set == "所有系列總計":
                        label = f"**[{photo.set_name}]** {photo.pose.value}"
                        
                    st.markdown(f"**{label}**")
                    
                    st.image(
                        photo.image_url, 
                        caption=f"點擊下方 '更新' 按鈕以變更圖片", 
                        width=100
                    )

                with col_input:
                    st.markdown("##### 🔢 **調整張數**", unsafe_allow_html=True)
                    
                    col_minus, col_num, col_plus = st.columns([1, 2, 1])
                    
                    with col_minus:
                        st.button(
                            "-1", 
                            key=f"minus_{photo.id}", 
                            on_click=decrement_count, 
                            args=(photo.id,), 
                            type="secondary", 
                            use_container_width=True
                        )
                    
                    with col_num:
                        st.number_input(
                            "擁有張數", 
                            min_value=0, 
                            value=st.session_state[f"count_{photo.id}_num_input"], 
                            key=f"count_{photo.id}_num_input", 
                            on_change=update_photo_and_save, 
                            step=1,
                            label_visibility="collapsed"
                        )
                    with col_plus:
                        st.button(
                            "+1", 
                            key=f"plus_{photo.id}", 
                            on_click=increment_count, 
                            args=(photo.id,), 
                            type="primary", 
                            use_container_width=True
                        )
                    
                with col_zero:
                    st.markdown("<br>", unsafe_allow_html=True) 
                    st.markdown("##### ", unsafe_allow_html=True) 
                    st.markdown("<br>", unsafe_allow_html=True) 
                    st.button(
                        "🗑️ 歸零", 
                        key=f"zero_btn_{photo.id}", 
                        on_click=set_count_to_zero, 
                        args=(photo.id,), 
                        type="secondary",
                        use_container_width=True
                    )
                        
                with col_file:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("##### 📁 **上傳生寫真圖片**")
                    st.file_uploader(
                        "選擇圖片檔案 (PNG, JPG, JPEG)",
                        type=["png", "jpg", "jpeg"],
                        key=f"file_uploader_{photo.id}",
                        on_change=update_photo_and_save, 
                        label_visibility="collapsed"
                    )
                    
                    if st.button("清除上傳圖片", 
                              key=f"btn_clear_file_{photo.id}", 
                              on_click=set_update_tracker, 
                              args=(photo.id,), 
                              type="secondary",
                              use_container_width=True):
                        pass
                        
                with col_url:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("##### 🔗 **或輸入網路 URL**")
                    initial_url = photo.custom_image_url if photo.custom_image_url and not photo.custom_image_url.startswith("data:") else ""
                    st.text_input(
                        "自訂圖片 URL (可從網路上複製)",
                        value=initial_url,
                        key=f"url_input_{photo.id}",
                        on_change=update_photo_and_save,
                        label_visibility="collapsed" 
                    )
                    st.button("更新圖片URL", 
                              key=f"btn_url_{photo.id}", 
                              on_click=set_update_tracker, 
                              args=(photo.id,), 
                              type="secondary",
                              use_container_width=True)
# C. 追蹤頁面結束


# E. 系列管理頁面 (新增、編輯、刪除系列功能)

# V8.8.23 修正：POSE_OPTIONS 不再包含 T (座り)
POSE_OPTIONS = {p.name: p.value for p in Pose}

# 顯示刪除後的強制刷新按鈕
if 'delete_success_flag' in st.session_state and st.session_state['delete_success_flag']:
    st.success(st.session_state['delete_success_flag'])
    
    if st.button("點擊這裡：強制刷新介面 (必須步驟)", type="primary", use_container_width=True):
         del st.session_state['delete_success_flag']
         hard_reload_after_delete()

# Expander 區塊開始
with st.expander(
    "🛠️ 管理系列與生寫真定義 - 簡化介面", 
    expanded=st.session_state.expanded_state, 
):
    
    st.header("新增與編輯/刪除系列")
    
    manage_tab = st.radio(
        "選擇操作", 
        VALID_TABS, 
        horizontal=True,
        key="manage_radio_tabs", 
        index=VALID_TABS.index(st.session_state.manage_tab_state),
        on_change=set_manage_tab, 
    )
    
    
    if manage_tab == "新增系列":
        st.subheader("📝 新增生寫真系列")
        
        # 1. 選擇團體
        new_group_value = st.selectbox(
            "選擇所屬團體", 
            options=[g.value for g in Group], 
            key="new_set_group"
        )
        # 傳入字串 group_value
        available_members = get_available_member_names(new_group_value)
        
        # 2. 選擇成員 (可多選)
        if available_members:
            st.multiselect(
                "選擇適用成員 (可多選，默認全選)",
                options=available_members,
                default=available_members,
                key="selected_members"
            )
        else:
            st.warning(f"團體 {new_group_value} 目前沒有現役成員可供選擇。")


        # 3. 輸入系列名稱
        st.text_input("輸入新的生寫真系列名稱", key="new_set_name")
        
        # 4. 選擇姿勢
        # V8.8.23 修正：預設選項中移除 T
        st.multiselect(
            "選擇該系列包含的姿勢 (多選)",
            options=list(POSE_OPTIONS.keys()),
            format_func=lambda x: POSE_OPTIONS[x], 
            default=["Y", "C", "H"], # 預設只包含 Y, C, H
            key="add_set_poses" 
        )
        
        st.button("確認新增此系列", on_click=add_new_set, type="primary")

    
    elif manage_tab == "編輯/刪除現有系列":
        st.subheader("✏️ 編輯或刪除現有系列")
        
        # 建立所有可編輯的系列 ID 列表 (格式: GroupValue|SetName)
        edit_options = []
        for group_value, sets in st.session_state.all_sets_by_group_str.items():
            for set_name in sets.keys():
                edit_options.append(f"{group_value}|{set_name}")
        
        selected_option = None
        current_edit_id = st.session_state.get("edit_set_id")
        
        if current_edit_id and current_edit_id in edit_options:
            selected_option = current_edit_id
        elif edit_options:
            selected_option = edit_options[0]
            
        if not edit_options:
            st.warning("目前沒有可編輯的系列。請先新增系列。")
        else:
            selected_edit_id = st.selectbox(
                "選擇要編輯的系列", 
                options=edit_options,
                index=edit_options.index(selected_option) if selected_option and selected_option in edit_options else 0,
                format_func=lambda x: x.split("|")[0] + " - " + x.split("|")[1],
                key="edit_set_id",
                on_change=load_edit_set_data 
            )
            
            # 如果是第一次進入編輯頁面，且選單有值，主動載入一次數據
            if st.session_state.edit_current_group_value is None and selected_edit_id:
                load_edit_set_data()

            if selected_edit_id and st.session_state.edit_current_group_value:
                
                # 刪除功能按鈕
                st.error("警告：刪除系列將同時清除該系列所有成員的所有收藏張數紀錄。")
                st.button(
                    "⚠️ 確認刪除此系列", 
                    on_click=delete_existing_set_on_edit, 
                    type="secondary",
                    help="點擊後，選中的系列和所有相關收藏數據將被永久刪除。",
                    use_container_width=True
                )
                st.markdown("---")

                group_value = st.session_state.edit_current_group_value
                group_value_display = group_value 
                
                group_value, set_name = selected_edit_id.split("|", 1) 
                
                # 這裡讀取的是 load_edit_set_data 清理過的值
                current_members = st.session_state.edit_current_members
                current_poses = st.session_state.edit_current_poses
                
                member_options_for_edit = get_available_member_names(group_value, current_members)

                st.markdown(f"#### 編輯 **[{group_value_display}] {set_name}**")
                
                # 2. 編輯成員名單
                if not member_options_for_edit and not current_members:
                    st.info(f"團體 {group_value_display} 目前沒有現役成員，且該系列沒有儲存任何成員。無法編輯成員名單。")
                elif not member_options_for_edit and current_members:
                    st.warning(f"**團體 {group_value_display} 目前沒有現役成員。** 下方選項為該系列當前儲存的成員名單。")

                if member_options_for_edit:
                    st.multiselect(
                        "編輯適用成員 (只顯示該團體現役成員或當前已儲存的成員)",
                        options=member_options_for_edit,
                        default=current_members, 
                        key="edit_selected_members"
                    )
                
                # 3. 編輯姿勢
                # 由於 current_poses 已經在 load_data 和 load_edit_set_data 中被清理，
                # 這裡的 default 值不會再包含 T，從而解決了 StreamlitAPIException。
                st.multiselect(
                    "編輯系列包含的姿勢 (點擊❌即可移除姿勢)",
                    options=list(POSE_OPTIONS.keys()),
                    format_func=lambda x: POSE_OPTIONS[x], 
                    default=current_poses,
                    key="edit_set_poses" 
                )
                
                st.markdown("> **💡 刪除提示:** 要刪除姿勢或成員，請在上方方框內，點擊您想移除的項目旁邊的 **紅色 '❌'** 標記，然後點擊下方的 **'確認更新此系列'** 按鈕。")

                st.button("確認更新此系列", on_click=edit_existing_set, type="primary")

            
    st.markdown("---")
    st.subheader("當前已定義的系列 (點擊展開可查看成員名單)")
    st.json(st.session_state.all_sets_by_group_str)