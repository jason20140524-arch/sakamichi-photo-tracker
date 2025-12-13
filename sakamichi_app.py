import streamlit as st
from enum import Enum
import json
from typing import List, Dict, Optional, Any
import os
import base64 

# --- 0. 設定檔案路徑 ---
DATA_FILE = "sakamichi_collection_data.json"

# V8.9.3 CSS: 確保行動裝置的點擊目標大且佈局合理
st.markdown("""
<style>
/* 隱藏 Chrome/Safari/Opera (針對 number input 欄位) */
input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* 隱藏 Firefox (針對 number input 欄位) */
input[type=number] {
  -moz-appearance: textfield;
}

/* 移除 Streamlit 預設的 Number Input 增加/減少按鈕，因為我們自己提供按鈕 */
div[data-testid="stNumberInput"] button {
    display: none !important;
}

/* ---------------------------------------------------- */
/* V8.9.3 核心優化: 針對行動裝置增加點擊目標尺寸和排版 */

/* 1. 統一所有按鈕/輸入框/FileUploader高度，使其容易點擊 */
div[data-testid="stColumn"] button,
div[data-testid="stNumberInput"] > div > input,
div[data-testid="stFileUploader"] {
    height: 48px !important; /* 增加到 48px，更適合手機觸摸 */
    line-height: 48px !important;
}
div[data-testid="stColumn"] button {
    padding: 0px 10px !important; /* 增加按鈕的點擊填充區域 */
    font-weight: bold; /* 讓 +/- 符號更清晰 */
}

/* 2. 移除手機上不必要的間距 */
div[data-testid="stNumberInput"] {
    margin-bottom: 0px !important;
}

/* 3. 圖片容器：設定最大高度，避免過度佔用垂直空間 */
.stImage > img {
    max-height: 180px; /* 限制圖片最大高度 */
    width: auto; 
    object-fit: contain; /* 確保圖片在容器內完整顯示 */
}

/* ---------------------------------------------------- */
</style>
""", unsafe_allow_html=True)


# --- 1. 核心資料模型 ---

# 生寫真類型 (Pose)
class Pose(Enum):
    # (排序值, 顯示的日文名稱, 圖片檔案後綴名)
    Y = (1, "ヨリ", "yori.jpg") 
    C = (2, "チュウ", "chuu.jpg") 
    H = (3, "ヒキ", "hiki.jpg") 
    SPY = (10, "特殊ヨリ", "spyori.jpg") 
    SPH = (11, "特殊ヒキ", "sphiki.jpg") 
    
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

# 固定的成員名單 (無變動) 
ALL_MEMBERS = [
    # 乃木坂46 (NOGIZAKA)
    {"name": "伊藤理々杏", "group": Group.NOGIZAKA, "gen": 3}, {"name": "岩本蓮加", "group": Group.NOGIZAKA, "gen": 3},
    {"name": "梅澤美波", "group": Group.NOGIZAKA, "gen": 3}, {"name": "吉田綾乃クリスティー", "group": Group.NOGIZAKA, "gen": 3},
    {"name": "遠藤さくら", "group": Group.NOGIZAKA, "gen": 4}, {"name": "賀喜遥香", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "弓木奈於", "group": Group.NOGIZAKA, "gen": 4}, {"name": "金川紗耶", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "黒見明香", "group": Group.NOGIZAKA, "gen": 4}, {"name": "佐藤璃果", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "柴田柚菜", "group": Group.NOGIZAKA, "gen": 4}, {"name": "林瑠奈", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "田村真佑", "group": Group.NOGIZAKA, "gen": 4}, {"name": "筒井あやめ", "group": Group.NOGIZAKA, "gen": 4},
    {"name": "井上和", "group": Group.NOGIZAKA, "gen": 5}, {"name": "一ノ瀬美空", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "小川彩", "group": Group.NOGIZAKA, "gen": 5}, {"name": "奥田いろは", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "川﨑桜", "group": Group.NOGIZAKA, "gen": 5}, {"name": "菅原咲月", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "冨里奈央", "group": Group.NOGIZAKA, "gen": 5}, {"name": "中西アルノ", "group": Group.NOGIZAKA, "gen": 5},
    {"name": "五百城茉央", "group": Group.NOGIZAKA, "gen": 5}, {"name": "池田瑛紗", "group": Group.NOGIZAKA, "gen": 5}, 
    {"name": "岡本姫奈", "group": Group.NOGIZAKA, "gen": 5}, 
    {"name": "矢田萌華", "group": Group.NOGIZAKA, "gen": 6}, {"name": "瀬戸口心月", "group": Group.NOGIZAKA, "gen": 6},
    {"name": "川端晃菜", "group": Group.NOGIZAKA, "gen": 6}, {"name": "海邉朱莉", "group": Group.NOGIZAKA, "gen": 6}, 
    {"name": "長嶋凛桜", "group": Group.NOGIZAKA, "gen": 6}, {"name": "森平麗心", "group": Group.NOGIZAKA, "gen": 6}, 
    {"name": "愛宕心響", "group": Group.NOGIZAKA, "gen": 6}, {"name": "大越ひなの", "group": Group.NOGIZAKA, "gen": 6},
    {"name": "鈴木佑捺", "group": Group.NOGIZAKA, "gen": 6}, {"name": "小津玲奈", "group": Group.NOGIZAKA, "gen": 6},
    {"name": "増田三莉音", "group": Group.NOGIZAKA, "gen": 6}, 
    # 櫻坂46 (SAKURAZAKA)
    {"name": "山﨑天", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "遠藤光莉", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "大園玲", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "大沼晶保", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "幸阪茉里乃", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "武元唯衣", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "田村保乃", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "藤吉夏鈴", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "増本綺良", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "松田里奈", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "森田ひかる", "group": Group.SAKURAZAKA, "gen": 2}, {"name": "守屋麗奈", "group": Group.SAKURAZAKA, "gen": 2},
    {"name": "石森璃花", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "遠藤理子", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "小田倉麗奈", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "小島凪紗", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "中嶋優月", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "的野美青", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "向井純葉", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "村井優", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "山下瞳月", "group": Group.SAKURAZAKA, "gen": 3}, {"name": "谷口愛季", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "村山美羽", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "淺井戀乃未", "group": Group.SAKURAZAKA, "gen": 3},{"name": "稲熊ひな", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "勝又春", "group": Group.SAKURAZAKA, "gen": 3},{"name": "佐藤愛桜", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "中川智尋", "group": Group.SAKURAZAKA, "gen": 3},{"name": "松本和子", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "目黒陽色", "group": Group.SAKURAZAKA, "gen": 3},{"name": "山川宇衣", "group": Group.SAKURAZAKA, "gen": 3},
    {"name": "山田桃実", "group": Group.SAKURAZAKA, "gen": 3},
    # 日向坂46 (HINATAZAKA)
    {"name": "金村美玖", "group": Group.HINATAZAKA, "gen": 2},{"name": "小坂菜緒", "group": Group.HINATAZAKA, "gen": 2}, 
    {"name": "松田好花", "group": Group.HINATAZAKA, "gen": 2}, 
    {"name": "上村ひなの", "group": Group.HINATAZAKA, "gen": 3}, {"name": "髙橋未來虹", "group": Group.HINATAZAKA, "gen": 3}, 
    {"name": "森本茉莉", "group": Group.HINATAZAKA, "gen": 3}, {"name": "山口陽世", "group": Group.HINATAZAKA, "gen": 3}, 
    {"name": "清水理央", "group": Group.HINATAZAKA, "gen": 4}, {"name": "正源司陽子", "group": Group.HINATAZAKA, "gen": 4}, 
    {"name": "平尾帆夏", "group": Group.HINATAZAKA, "gen": 4}, {"name": "藤嶌果歩", "group": Group.HINATAZAKA, "gen": 4},
    {"name": "山下葉留花", "group": Group.HINATAZAKA, "gen": 4},{"name": "石塚瑶季", "group": Group.HINATAZAKA,"gen": 4}, 
    {"name": "小西夏菜実", "group": Group.HINATAZAKA, "gen": 4},{"name": "竹内希来里", "group": Group.HINATAZAKA, "gen": 4}, 
    {"name": "平岡海月", "group": Group.HINATAZAKA, "gen": 4},{"name": "宮地すみれ", "group": Group.HINATAZAKA, "gen": 4}, 
    {"name": "渡辺莉奈", "group": Group.HINATAZAKA, "gen": 4}, 
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
    # 範例：如果您的圖片是 mydomain.com/images/sakamichi/member_setname_yori.jpg
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
        set_name_for_url = self.set_name.replace(" ", "_").replace(".", "") # 清理特殊字符
        # 假設 URL 格式為: BASE_URL + 成員名_系列名_姿勢後綴.jpg
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

def load_data(initial_load=False):
    """從 JSON 文件加載系列定義和收藏數據，並初始化 Photo 列表"""
    
    all_photos: List[Photo] = []
    member_objects: Dict[str, Member] = {}
    for member_info in ALL_MEMBERS:
        name = member_info['name']
        group_enum = member_info['group']    
        gen = member_info['gen']
        member = Member(name, group_enum, gen)
        member_objects[name] = member
            
    global ALL_SETS_BY_GROUP
    current_sets = {g: sets for g, sets in DEFAULT_SETS_BY_GROUP.items()}    
    
    saved_collection_data = []

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            
            if 'sets' in full_data and full_data['sets']:
                current_sets = full_data['sets']
                
            if 'collection' in full_data:
                saved_collection_data = full_data['collection']    
                
            
        except json.JSONDecodeError:
            print("Warning: JSON Decode Error, resetting sets to default.")
        except Exception as e:
            print(f"Warning: Unexpected error loading JSON: {e}")
            
    # 將讀取到的系列數據同步到 global 變數和 session state (初始化時)
    ALL_SETS_BY_GROUP = current_sets
    if initial_load:
        st.session_state.all_sets_by_group = current_sets
        st.session_state.all_sets_by_group_str = current_sets
        
    VALID_POSE_KEYS = set(p.name for p in Pose)

    for group_value, sets in ALL_SETS_BY_GROUP.items():
        try:
            group_enum = Group(group_value)
        except ValueError:
            continue

        for set_name, set_info in sets.items():
            
            members_with_poses = set_info.get("members_with_poses", {})
            
            # --- 處理舊結構 (如果 JSON 中只有 member_list 和 poses) ---
            if not members_with_poses:
                member_names_for_set = set_info.get("member_list", [])
                pose_names_for_set = set_info.get("poses", [])
                
                if member_names_for_set and pose_names_for_set:
                    # 如果是舊結構，轉換為新結構
                    members_with_poses = {
                        m_name: [p for p in pose_names_for_set if p in VALID_POSE_KEYS]
                        for m_name in member_names_for_set
                    }
                    # 順便清理舊鍵，將新結構寫入 set_info (避免舊數據汙染)
                    if "member_list" in set_info: del set_info["member_list"]
                    if "poses" in set_info: del set_info["poses"]
                    set_info["members_with_poses"] = members_with_poses

            # --- 遍歷新結構並生成 Photo 物件 ---
            for member_name, pose_names_for_member in members_with_poses.items():
                
                if member_name in member_objects and member_objects[member_name].group == group_enum:
                    member = member_objects[member_name]
                    
                    for pose_name in pose_names_for_member:
                        try:
                            if pose_name in VALID_POSE_KEYS:
                                pose = Pose[pose_name]    
                                photo = Photo(set_name, member, pose)
                                all_photos.append(photo)
                            
                        except KeyError:
                            continue
    
    # Map saved status by photo ID
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
            
            if status.get('custom_image_url'):
                photo.custom_image_url = status['custom_image_url']
                photo.image_url = status['custom_image_url']
                
            elif not status.get('custom_image_url') and photo.custom_image_url:
                 photo.custom_image_url = None
                 photo.image_url = photo._generate_image_url()
        
        elif photo.custom_image_url:
             photo.custom_image_url = None
             photo.image_url = photo._generate_image_url()

    # 確保第一次載入後，如果有資料，則儲存一次，確保格式正確
    if initial_load or not os.path.exists(DATA_FILE) or not any(ALL_SETS_BY_GROUP.values()):
        save_data(all_photos, ALL_SETS_BY_GROUP)
        
    return all_photos
# -------------------- load_data 函數結束 --------------------


# --- 3. 函數區：單張/批量操作 ---

def update_photo_and_save():
    """處理圖片張數/檔案上傳的變更並儲存 (主要用於 on_change 觸發，尤其是檔案上傳)"""
    photo_id = st.session_state.get('last_updated_photo_id')
    if not photo_id:
        return 

    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == photo_id), None)
    
    if updated_photo:
        
        # 1. 處理張數 (如果 number_input 被修改)
        new_count = max(0, st.session_state.get(f"count_{photo_id}_num_input", updated_photo.owned_count))
        
        # 2. 處理檔案上傳
        uploaded_file = st.session_state.get(f"file_uploader_{photo_id}")
        
        new_custom_image_source = None
        
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            file_type = uploaded_file.type
            base64_encoded_data = base64.b64encode(bytes_data).decode('utf-8')
            new_custom_image_source = f"data:{file_type};base64,{base64_encoded_data}"
            
        is_changed = (
            new_count != updated_photo.owned_count or 
            new_custom_image_source != updated_photo.custom_image_url
        )
        
        if is_changed:
            
            if uploaded_file is not None:
                st.session_state[f"file_uploader_{photo_id}"] = None 
                
            updated_photo.owned_count = new_count
            
            updated_photo.custom_image_url = new_custom_image_source
            updated_photo.image_url = new_custom_image_source if new_custom_image_source else updated_photo._generate_image_url()
            
            save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
            
            st.session_state[f"count_{photo_id}_num_input"] = updated_photo.owned_count 
            
            if uploaded_file is not None:
                st.rerun()


def set_update_tracker(p_id):
    """設置追蹤器，確保 on_change 能找到正確的 ID。主要用於 number_input 和 file_uploader。"""
    st.session_state['last_updated_photo_id'] = p_id
    update_photo_and_save()


def decrement_count(p_id):
    """將數量減 1，直接儲存並強制刷新。"""
    current_count = st.session_state.get(f"count_{p_id}_num_input", 0) 
    new_count = max(0, current_count - 1)
    
    if current_count != new_count:
        st.session_state[f"count_{p_id}_num_input"] = new_count
        
        updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == p_id), None)
        if updated_photo:
            updated_photo.owned_count = new_count
            save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
            st.rerun() 


def increment_count(p_id):
    """將數量加 1，直接儲存並強制刷新。"""
    current_count = st.session_state.get(f"count_{p_id}_num_input", 0)
    new_count = current_count + 1
    
    if current_count != new_count:
        st.session_state[f"count_{p_id}_num_input"] = new_count
        
        updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == p_id), None)
        if updated_photo:
            updated_photo.owned_count = new_count
            save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
            st.rerun()

def clear_custom_image(photo_id: str):
    """清除自訂圖片的 Base64 數據，並將圖片 URL 重設為預設，直接儲存並強制刷新。"""
    
    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == photo_id), None)
    
    if updated_photo and updated_photo.custom_image_url: 
        updated_photo.custom_image_url = None
        updated_photo.image_url = updated_photo._generate_image_url()
        
        st.session_state[f"file_uploader_{photo_id}"] = None 
        
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        st.rerun() 
    else:
        st.info(f"ID: {photo_id} 的生寫真沒有設定自訂圖片。")

def set_count_to_zero(photo_id: str):
    """將指定的 Photo 張數設定為 0 並儲存，直接儲存並強制刷新。"""
    
    updated_photo = next((ph for ph in st.session_state.photo_set if ph.id == photo_id), None)
    
    if updated_photo and updated_photo.owned_count != 0: 
        updated_photo.owned_count = 0
        
        st.session_state[f"count_{photo_id}_num_input"] = 0 
        
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        st.rerun() 
    else:
        st.info(f"ID: {photo_id} 的生寫真張數已是 0。")

# 核心批量修正函數：set_n_sets_collected
def set_n_sets_collected(member_name: str, current_set_name: str, target_n: int):
    """將指定成員在指定系列中的所有生寫真張數設為目標套數 N"""
    
    if current_set_name == "所有系列總計":
        st.error("「所有系列總計」模式下無法進行一鍵設定，請選擇特定系列。")
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
        st.success(f"已將 **{member_name}** 在 **{current_set_name}** 中的 {photos_updated} 張生寫真數量設為 {target_count} (共 {target_n} 套)。")
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        st.rerun() 
        
    else:
        st.info(f"**{member_name}** 在 **{current_set_name}** 中的生寫真數量已達到或超過目標的 {target_n} 套，無需修改。")

def toggle_pin_and_save(member_name: str):
    """切換成員的釘選狀態並儲存 (實際只是觸發 st.rerun)"""
    
    current_pin_state = st.session_state.get(f"pin_{member_name}", False)
    st.session_state[f"pin_{member_name}"] = not current_pin_state
    st.rerun()


# --- 4. 函數區：管理系列 ---

def set_manage_tab():
    """設定當前選中的管理 Tab"""
    new_tab_value = st.session_state.get("manage_radio_tabs")
    if new_tab_value:
        st.session_state.manage_tab_state = new_tab_value
        
        if 'edit_set_id' in st.session_state and st.session_state.edit_set_id:
            load_edit_set_data() 


def load_edit_set_data():
    """根據選中的系列 ID，將其成員和姿勢載入到 session_state 暫存變數中"""
    selected_edit_id = st.session_state.get("edit_set_id") 

    if selected_edit_id:
        if selected_edit_id == "所有系列總計":
            st.session_state.edit_current_group_value = None
            st.session_state.edit_current_members_with_poses = {} 
            st.session_state.edit_selected_members = []
            return 

        group_value, set_name = selected_edit_id.split("|", 1)
        
        current_info = st.session_state.all_sets_by_group.get(group_value, {}).get(set_name, {})
        
        members_with_poses = current_info.get("members_with_poses", {})
        
        if not members_with_poses and current_info.get("member_list") and current_info.get("poses"):
            members_with_poses = {
                m_name: current_info["poses"]
                for m_name in current_info["member_list"]
            }
        
        st.session_state.edit_current_group_value = group_value 
        st.session_state.edit_current_members_with_poses = members_with_poses 
        
        # V8.9.2 核心: 初始化成員選擇器的預選值
        pre_selected_members = list(members_with_poses.keys())
        st.session_state.edit_selected_members = pre_selected_members

        for member_name in pre_selected_members:
            key = f"edit_pose_for_member_{set_name}_{member_name}"
            default_poses = members_with_poses.get(member_name, []) 
            st.session_state[key] = default_poses
        
    else:
        st.session_state.edit_current_group_value = None
        st.session_state.edit_current_members_with_poses = {}
        st.session_state.edit_selected_members = []
        
def get_available_member_names(group_identifier: str) -> List[str]:
    """獲取指定團體的現役成員名稱列表 (輸入為團體中文名稱字串)"""
    
    try:
        group_enum = Group(group_identifier)
    except ValueError:
        return []

    available_members = sorted(list(m['name'] for m in ALL_MEMBERS if m['group'] == group_enum))
    
    return available_members

def add_new_set():
    """新增系列邏輯 (確保數據同步與強制刷新)"""
    new_set_name = st.session_state.get("new_set_name_simple", "").strip() 
    new_group_value = st.session_state.get("new_set_group_simple")

    if not new_set_name:
        st.error("系列名稱不能為空。")
        return
        
    current_sets = st.session_state.all_sets_by_group 

    group_key = new_group_value
    if group_key not in current_sets:
        current_sets[group_key] = {}
    
    if new_set_name in current_sets[group_key]:
        st.warning(f"系列 '{new_set_name}' 已在 {new_group_value} 中存在。請使用編輯功能。")
        return

    new_set_info = {
        "members_with_poses": {}
    }
    current_sets[group_key][new_set_name] = new_set_info
    
    new_set_id = f"{group_key}|{new_set_name}"
    
    st.session_state.all_sets_by_group = current_sets
    save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
    
    st.session_state.photo_set = load_data() 
    st.session_state.all_sets_by_group_str = st.session_state.all_sets_by_group 
    
    st.success(f"成功新增系列: {new_set_name}！請接著設定成員和姿勢。")
    
    st.session_state['tracking_set_id'] = new_set_id 
    st.session_state.manage_tab_state = "編輯/刪除現有系列" 
    st.session_state.manage_radio_tabs = "編輯/刪除現有系列" 
    st.session_state.edit_set_id = new_set_id 
    
    if 'new_set_name_simple' in st.session_state:
        del st.session_state['new_set_name_simple']
        
    st.rerun() 

def edit_existing_set():
    """編輯系列邏輯 (確保強制刷新)"""
    edit_set_id = st.session_state.get("edit_set_id") 
    group_value, set_name = edit_set_id.split("|", 1)
    
    selected_member_names = st.session_state.get('edit_selected_members', [])
    
    new_members_with_poses = {}
    total_poses_count = 0
    
    for member_name in selected_member_names:
        key = f"edit_pose_for_member_{set_name}_{member_name}"
        selected_poses = st.session_state.get(key, []) 
        
        if selected_poses:
            cleaned_poses = [p_name for p_name in selected_poses if p_name in set(p.name for p in Pose)]
            if cleaned_poses:
                new_members_with_poses[member_name] = cleaned_poses
                total_poses_count += len(cleaned_poses)

    if not edit_set_id:
        st.warning("請選擇要編輯的系列。")
        return
        
    if not new_members_with_poses:
        st.error("您必須為至少一位成員選擇姿勢。")
        return

    current_sets_for_group = st.session_state.all_sets_by_group.get(group_value, {})
    current_info = current_sets_for_group.get(set_name, {})
    
    old_members_with_poses = current_info.get("members_with_poses", {})
    is_changed = (old_members_with_poses != new_members_with_poses)
    
    if group_value in st.session_state.all_sets_by_group and set_name in current_sets_for_group:
        
        st.session_state.all_sets_by_group[group_value][set_name] = {
            "members_with_poses": new_members_with_poses 
        }
        
        if "member_list" in st.session_state.all_sets_by_group[group_value][set_name]:
            del st.session_state.all_sets_by_group[group_value][set_name]["member_list"]
        if "poses" in st.session_state.all_sets_by_group[group_value][set_name]:
            del st.session_state.all_sets_by_group[group_value][set_name]["poses"]
        
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        st.session_state.photo_set = load_data()
        st.session_state.all_sets_by_group_str = st.session_state.all_sets_by_group
        
        st.success(f"成功更新系列: {set_name}！總共設定了 {len(new_members_with_poses)} 位成員的 {total_poses_count} 張生寫真項目。" + ("數據已變更並重新計算。" if is_changed else "數據未變更，介面已更新。"))
        
        st.session_state['tracking_set_id'] = f"{group_value}|{set_name}"
            
        st.rerun()

def hard_reload_after_delete():
    """清除所有 Streamlit UI 狀態鍵，模擬頁面首次載入，並強制 st.rerun()"""
    
    keys_to_delete = ["tracking_set_id", "edit_set_id", "manage_radio_tabs", 
                      "edit_current_group_value", "edit_current_members_with_poses", 
                      "edit_selected_members", 
                      "new_set_name_simple", "new_set_group_simple",
                      "delete_success_flag", "confirm_delete"]
    
    for key in set(keys_to_delete): 
        if key in st.session_state:
             del st.session_state[key]
             
    st.session_state.photo_set = load_data(initial_load=True)
    
    st.rerun()

def delete_existing_set_on_edit():
    """刪除系列邏輯 (作為 on_click 函數執行)"""
    delete_set_id = st.session_state.get("edit_set_id")

    if not delete_set_id:
        st.session_state['delete_success_flag'] = "請選擇要刪除的系列。"
        return

    group_value, set_name = delete_set_id.split("|", 1)
    
    if group_value in st.session_state.all_sets_by_group and set_name in st.session_state.all_sets_by_group[group_value]:
        
        del st.session_state.all_sets_by_group[group_value][set_name]
        
        save_data(st.session_state.photo_set, st.session_state.all_sets_by_group)
        
        if 'edit_set_id' in st.session_state:
            del st.session_state['edit_set_id']
        
        if 'tracking_set_id' in st.session_state:
            del st.session_state['tracking_set_id']
            
        st.session_state.photo_set = load_data() 
        
        st.session_state['delete_success_flag'] = f"成功刪除系列: {set_name}！請點擊下方按鈕更新介面。"
        
    else:
        st.error(f"找不到要刪除的系列: {set_name}。團體鍵 {group_value} 驗證失敗。")

# 獨立格式化函數
def format_set_display(option_id: str) -> str:
    """格式化系列選項的顯示名稱：團體 - 系列名稱"""
    if option_id == "所有系列總計":
        return option_id
    
    parts = option_id.split("|", 1)
    if len(parts) == 2:
        return f"{parts[0]} - {parts[1]}"
    return option_id

# 核心功能：計算收藏進度 (無變動)
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

# --- 5. 初始化數據 ---

if 'photo_set' not in st.session_state:
    st.session_state.photo_set = []
    st.session_state.all_sets_by_group = {}
    st.session_state.all_sets_by_group_str = {}
    
    st.session_state.photo_set = load_data(initial_load=True) 
    st.session_state.all_sets_by_group = ALL_SETS_BY_GROUP 
    st.session_state.all_sets_by_group_str = ALL_SETS_BY_GROUP 
    
    if not st.session_state.photo_set and not st.session_state.all_sets_by_group:
         st.session_state.photo_set = []
         st.session_state.all_sets_by_group = DEFAULT_SETS_BY_GROUP 
         st.session_state.all_sets_by_group_str = DEFAULT_SETS_BY_GROUP 

VALID_TABS = ["新增系列", "編輯/刪除現有系列"]
if 'manage_tab_state' not in st.session_state or st.session_state.manage_tab_state not in VALID_TABS:
    st.session_state.manage_tab_state = "新增系列"
    
if 'edit_current_group_value' not in st.session_state:
    st.session_state.edit_current_group_value = None
    
if 'edit_current_members_with_poses' not in st.session_state:
    st.session_state.edit_current_members_with_poses = {}

if 'edit_selected_members' not in st.session_state:
    st.session_state.edit_selected_members = []
    
if 'edit_set_id' not in st.session_state:
    st.session_state['edit_set_id'] = None
# --- 5. 初始化數據 結束 ---

# --- 6. 側邊欄繪製函數 (無變動) ---
def draw_sidebar_controls():
    """
    繪製側邊欄控制項，使用 st.container() 確保內容連貫。
    """
    with st.container():
        st.header("🎛️ 追蹤控制")
        
        all_set_options_ids = []
        current_sets_data = st.session_state.get('all_sets_by_group_str', {}) 
        
        for group_value, group_sets in current_sets_data.items():
            for set_name in group_sets.keys():
                all_set_options_ids.append(f"{group_value}|{set_name}")
            
        all_set_options_ids.insert(0, "所有系列總計")
        
        selected_tracking_set_id = st.session_state.get("tracking_set_id")
        
        if selected_tracking_set_id not in all_set_options_ids:
            if all_set_options_ids:
                selected_tracking_set_id = all_set_options_ids[0]
            else:
                selected_tracking_set_id = "所有系列總計"

        current_index = all_set_options_ids.index(selected_tracking_set_id) if selected_tracking_set_id in all_set_options_ids else 0

        selected_set_output_id = st.selectbox(
            "選擇要追蹤的系列:",
            options=all_set_options_ids,
            index=current_index,
            key="tracking_set_id",
            format_func=format_set_display 
        )
        
        if selected_set_output_id == "所有系列總計":
            selected_set_name_for_app = "所有系列總計"
        else:
            selected_set_name_for_app = selected_set_output_id.split("|", 1)[1] 

        if len(all_set_options_ids) <= 1:
            st.warning("目前沒有任何系列，請在「管理系列」區塊新增。")

        st.markdown("---")
        st.header("現役成員名單")
        for group in Group:
            st.subheader(group.value)
            group_members = [m['name'] for m in ALL_MEMBERS if m['group'] == group] 
            if group_members:
                st.markdown(", ".join(group_members))
                
    return selected_set_name_for_app
# --- 側邊欄繪製函數結束 ---


# --- 7. Streamlit APP 頁面佈局 ---

st.set_page_config(layout="wide", page_title="坂道生寫真收藏追蹤器")
st.title("🌸 坂道生寫真收藏追蹤器 (V8.9.3 - 手機介面優化)")
st.markdown("---")


# A. 側邊欄控制項 
with st.sidebar:
    selected_set = draw_sidebar_controls()


# B. 收藏進度總覽 
has_any_set = any(st.session_state.all_sets_by_group_str.values())

st.header(f"🎯 進度總覽: {selected_set}")
progress_data = calculate_progress(st.session_state.photo_set, selected_set)

progress_table_data = []
for name, data in progress_data.items():
    collected = data['total_collected']
    needed = data['total_needed']
    
    completion_percentage = (min(collected, needed) / needed) * 100 if needed > 0 else 0
    
    progress_table_data.append({
        "成員": name,
        "目標/擁有": f"{needed} 張目標 / {collected} 張",
        "完成度": completion_percentage,
    })

progress_table_data = sorted(progress_table_data, key=lambda x: x['完成度'], reverse=True)

if progress_table_data and has_any_set:
    st.dataframe(
        progress_table_data,
        column_config={
            "完成度": st.column_config.ProgressColumn(
                "完成度",
                format="%f%%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
    )
else:
     st.info("請在下方的「管理系列」區塊新增至少一個系列來開始追蹤。")


st.markdown("---")


# C. 追蹤頁面 (V8.9.3 核心優化區塊)

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
            
            # --- V8.9.3: 批量操作使用 Expander ---
            current_collected = progress_data.get(name, {}).get('total_collected', 0)
            st.markdown(f"## {name} - 總擁有張數: {current_collected} 張")
            
            with st.expander("🎯 設定目標套數並批量操作"):
                
                col_target, col_set_n = st.columns([0.5, 0.5])
                
                with col_target:
                    st.number_input(
                        "目標擁有套數 N",
                        min_value=1,
                        value=1,
                        key=f"target_n_{name}", 
                        step=1, 
                    )
                    target_n = st.session_state[f"target_n_{name}"]
                    
                with col_set_n:
                    st.markdown("<br>", unsafe_allow_html=True) 
                    st.button(
                        f"一鍵收齊 {target_n} 套",
                        key=f"set_n_btn_{name}", 
                        on_click=set_n_sets_collected, 
                        args=(name, selected_set, target_n), 
                        type="primary",
                        use_container_width=True
                    )
                    
            st.markdown("---") 
            # -------------------- 成員生寫真列表 --------------------
            
            photos_for_member = sorted(
                member_groups[name], 
                key=lambda p: (p.pose.order, p.set_name if selected_set == "所有系列總計" else "")
            )

            # 顯示
            if selected_set == "所有系列總計":
                # 在 "所有系列總計" 模式下，按系列分組顯示
                grouped_by_set = {}
                for p in photos_for_member:
                    if p.set_name not in grouped_by_set:
                        grouped_by_set[p.set_name] = []
                    grouped_by_set[p.set_name].append(p)
                    
                set_names_sorted = sorted(grouped_by_set.keys())

                for set_name in set_names_sorted:
                    st.subheader(f"系列: {set_name}")
                    
                    # V8.9.3: 在總計模式下，每張卡片仍使用行動友好的垂直佈局 (佔滿寬度)
                    for photo in grouped_by_set[set_name]:
                        
                        with st.container(border=True): 
                            
                            col_image, col_controls = st.columns([0.6, 0.4]) 
                            
                            with col_image:
                                st.image(photo.image_url, caption=f"姿勢: **{photo.pose.value}** (ID: {photo.id})") 
                            
                            with col_controls:
                                # 數量輸入和 +/- 按鈕分三欄顯示
                                col_dec, col_input, col_inc = st.columns([0.25, 0.5, 0.25])
                                
                                count_key = f"count_{photo.id}_num_input"
                                if count_key not in st.session_state:
                                    st.session_state[count_key] = photo.owned_count

                                with col_dec:
                                    st.button(
                                        "➖", 
                                        key=f"dec_{photo.id}", 
                                        on_click=decrement_count, 
                                        args=(photo.id,),
                                        use_container_width=True,
                                        type="secondary"
                                    )
                                
                                with col_input:
                                    st.number_input(
                                        "張數", 
                                        min_value=0,
                                        value=st.session_state[count_key],
                                        key=count_key,
                                        step=1,
                                        on_change=set_update_tracker,
                                        args=(photo.id,),
                                        label_visibility="collapsed",
                                        help=f"張數: {photo.pose.value}", 
                                    )
                                    
                                with col_inc:
                                    st.button(
                                        "➕", 
                                        key=f"inc_{photo.id}", 
                                        on_click=increment_count, 
                                        args=(photo.id,), 
                                        type="primary",
                                        use_container_width=True
                                    )
                                
                                # 額外功能 
                                with st.expander("🛠️ 自訂圖片 / 清除"):
                                    file_key = f"file_uploader_{photo.id}"
                                    st.file_uploader(
                                        "上傳自訂圖片 (JPG/PNG)",
                                        type=["jpg", "jpeg", "png"],
                                        key=file_key,
                                        on_change=set_update_tracker, 
                                        args=(photo.id,),
                                        accept_multiple_files=False,
                                        label_visibility="collapsed"
                                    )
                                    col_clear_img, col_clear_count = st.columns(2)
                                    if photo.custom_image_url:
                                        with col_clear_img:
                                            st.button("清除圖片", key=f"clear_img_{photo.id}", on_click=clear_custom_image, args=(photo.id,), use_container_width=True)
                                    with col_clear_count:
                                        st.button("清零張數", key=f"set_zero_{photo.id}", on_click=set_count_to_zero, args=(photo.id,), use_container_width=True)


            else:
                # V8.9.3: 單一系列模式下的行動友善佈局
                for photo in photos_for_member:
                    
                    with st.container(border=True): 
                        
                        col_image, col_controls = st.columns([0.6, 0.4]) 
                        
                        with col_image:
                            st.image(photo.image_url, caption=f"姿勢: **{photo.pose.value}**") 
                        
                        with col_controls:
                            col_dec, col_input, col_inc = st.columns([0.25, 0.5, 0.25])
                            
                            count_key = f"count_{photo.id}_num_input"
                            if count_key not in st.session_state:
                                st.session_state[count_key] = photo.owned_count

                            with col_dec:
                                st.button(
                                    "➖", 
                                    key=f"dec_{photo.id}", 
                                    on_click=decrement_count, 
                                    args=(photo.id,),
                                    use_container_width=True,
                                    type="secondary"
                                )
                            
                            with col_input:
                                st.number_input(
                                    "張數", 
                                    min_value=0,
                                    value=st.session_state[count_key],
                                    key=count_key,
                                    step=1,
                                    on_change=set_update_tracker,
                                    args=(photo.id,),
                                    label_visibility="collapsed",
                                    help=f"張數: {photo.pose.value}", 
                                )
                                
                            with col_inc:
                                st.button(
                                    "➕", 
                                    key=f"inc_{photo.id}", 
                                    on_click=increment_count, 
                                    args=(photo.id,), 
                                    type="primary",
                                    use_container_width=True
                                )

                            with st.expander("🛠️ 自訂圖片 / 清除"):
                                file_key = f"file_uploader_{photo.id}"
                                st.file_uploader(
                                    "上傳自訂圖片 (JPG/PNG)",
                                    type=["jpg", "jpeg", "png"],
                                    key=file_key,
                                    on_change=set_update_tracker, 
                                    args=(photo.id,),
                                    accept_multiple_files=False,
                                    label_visibility="collapsed"
                                )
                                col_clear_img, col_clear_count = st.columns(2)
                                if photo.custom_image_url:
                                    with col_clear_img:
                                        st.button("清除圖片", key=f"clear_img_{photo.id}", on_click=clear_custom_image, args=(photo.id,), use_container_width=True)
                                with col_clear_count:
                                    st.button("清零張數", key=f"set_zero_{photo.id}", on_click=set_count_to_zero, args=(photo.id,), use_container_width=True)


st.markdown("---")
# D. 管理系列介面 (V8.9.2 成員選擇器優化保留)

st.header("⚙️ 管理系列")
st.markdown("在這裡新增、編輯或刪除您要追蹤的生寫真系列。")

tab_radio = st.radio(
    "選擇操作",
    VALID_TABS,
    key="manage_radio_tabs",
    index=VALID_TABS.index(st.session_state.manage_tab_state),
    on_change=set_manage_tab,
    horizontal=True
)

if st.session_state.manage_tab_state == "新增系列":
    st.subheader("新增系列")
    
    col_group, col_name = st.columns([0.3, 0.7])
    
    with col_group:
        group_options = [g.value for g in Group]
        st.selectbox("選擇所屬團體", group_options, key="new_set_group_simple")
        
    with col_name:
        st.text_input("輸入系列名稱 (例: 2024.Apr)", key="new_set_name_simple")
        
    st.button(
        "✨ 新增此系列",
        on_click=add_new_set,
        type="primary",
        use_container_width=True
    )
    st.info("新增後，介面將自動切換到「編輯/刪除現有系列」區塊，您可以立即設定成員和姿勢。")


elif st.session_state.manage_tab_state == "編輯/刪除現有系列":
    
    st.subheader("編輯/刪除系列成員和姿勢")
    
    edit_options_ids = []
    current_sets_data = st.session_state.get('all_sets_by_group_str', {})
    
    for group_value, group_sets in current_sets_data.items():
        for set_name in group_sets.keys():
            edit_options_ids.append(f"{group_value}|{set_name}")
            
    current_edit_id = st.session_state.get("edit_set_id")
    if current_edit_id not in edit_options_ids:
        current_edit_id = edit_options_ids[0] if edit_options_ids else None
        
    current_index = edit_options_ids.index(current_edit_id) if current_edit_id in edit_options_ids else 0

    if edit_options_ids:
        selected_edit_id = st.selectbox(
            "選擇要編輯或刪除的系列:",
            options=edit_options_ids,
            index=current_index,
            key="edit_set_id",
            format_func=format_set_display, 
            on_change=load_edit_set_data 
        )
        
        if not st.session_state.edit_current_group_value or st.session_state.edit_current_group_value != selected_edit_id.split("|", 1)[0]:
             load_edit_set_data()

        if st.session_state.edit_set_id:
            
            group_value, set_name = st.session_state.edit_set_id.split("|", 1)
            
            st.markdown(f"### 編輯: {group_value} - {set_name}")
            
            # --- V8.9.2 成員選擇器 ---
            available_members = get_available_member_names(group_value)
            
            current_selected_members = st.session_state.get('edit_selected_members', [])
            
            selected_members_for_edit = st.multiselect(
                f"選擇要配置姿勢的 {group_value} 成員:",
                options=available_members,
                default=current_selected_members, 
                key="edit_selected_members", 
                help="只有在這裡選擇的成員，才會顯示在下方進行姿勢設定。"
            )
            
            if not selected_members_for_edit:
                st.info("請在上方選擇您要配置姿勢的成員。")
            
            # --- 為選中的成員動態生成姿勢 Expander ---
            all_pose_names = [p.name for p in Pose]
            all_pose_values_map = {p.name: p.value for p in Pose}
            
            def format_pose_display(pose_name):
                return all_pose_values_map.get(pose_name, pose_name)

            st.markdown("#### 點擊成員名稱設定追蹤姿勢")
            
            for member_name in selected_members_for_edit:
                
                key = f"edit_pose_for_member_{set_name}_{member_name}"
                
                if key in st.session_state:
                    current_selected_poses = st.session_state[key]
                else:
                    current_selected_poses = st.session_state.edit_current_members_with_poses.get(member_name, [])
                    st.session_state[key] = current_selected_poses 
                
                
                if current_selected_poses:
                    pose_values = [all_pose_values_map.get(p_name, p_name) for p_name in current_selected_poses]
                    summary = f" (已設定: {', '.join(pose_values)})"
                    expander_label = f"**{member_name}** {summary}"
                else:
                    expander_label = f"**{member_name}** (未設定姿勢)"
                    
                with st.expander(expander_label):
                    
                    st.multiselect(
                        "選擇姿勢:",
                        options=all_pose_names,
                        default=current_selected_poses, 
                        key=key, 
                        format_func=format_pose_display,
                        label_visibility="visible",
                        help=f"為 {member_name} 在 {set_name} 系列中設定要追蹤的姿勢。"
                    )
            
            
            # --- 預覽與儲存 ---
            
            preview_members_with_poses = {}
            for member_name in selected_members_for_edit:
                key = f"edit_pose_for_member_{set_name}_{member_name}"
                selected_poses = st.session_state.get(key, [])
                if selected_poses:
                    preview_members_with_poses[member_name] = [all_pose_values_map.get(p_name, p_name) for p_name in selected_poses]

            st.markdown("#### 變更預覽")
            
            preview_data = {
                "所屬團體": group_value,
                "系列名稱": set_name,
                "成員與追蹤姿勢": preview_members_with_poses,
                "總追蹤生寫真數量": sum(len(poses) for poses in preview_members_with_poses.values())
            }
            with st.expander("展開查看詳細預覽 (JSON)"):
                st.json(preview_data)

            col_update, col_delete = st.columns([0.7, 0.3])
            
            with col_update:
                st.button(
                    "✅ 更新此系列",
                    on_click=edit_existing_set,
                    type="primary",
                    use_container_width=True
                )
            
            with col_delete:
                if st.button("❌ 刪除此系列", use_container_width=True):
                    if st.session_state.get('confirm_delete', False):
                        delete_existing_set_on_edit()
                        st.session_state['confirm_delete'] = False
                    else:
                        st.warning("⚠️ 再次點擊以確認刪除，此操作無法復原！")
                        st.session_state['confirm_delete'] = True
                else:
                    st.session_state['confirm_delete'] = False

            if st.session_state.get('delete_success_flag'):
                st.success(st.session_state['delete_success_flag'])
                st.button("點擊這裡更新介面", on_click=hard_reload_after_delete)
                
            
    else:
        st.info("目前沒有可編輯的系列，請在「新增系列」區塊建立一個。")