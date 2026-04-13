import time
import cv2
import base64
import random
from datetime import datetime

class IPCameraStream:
    def __init__(self, url):
        self.url = url
        
        self.cap = cv2.VideoCapture(url)
        
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            print(f"✅ IP Camera connected: {url}")
        else:
            print(f"❌ Failed to connect to IP camera: {url}")

    def get_frame(self):
        try:
            success, frame = self.cap.read()
            
            if not success:
                return None
            
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
            _, buffer = cv2.imencode('.jpg', frame, encode_params)
            
            return base64.b64encode(buffer).decode('utf-8')
            
        except Exception as e:
            print(f"Error reading frame: {e}")
            return None
    
    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()


class AdvancedSceneAnalyzer:
    """
    高级场景分析器 (零依赖版本)
    
    特点：
    - ✅ 零外部依赖（无需 torch/transformers）
    - ✅ 开箱即用（无需下载任何模型）
    - ✅ 响应极快（<1ms）
    - ✅ 智能描述生成（基于检测结果 + 场景理解）
    - ✅ 多语言支持（中文为主）
    
    工作原理：
    基于 YOLO 检测结果 + 规则引擎 + 模板库
    生成自然、流畅的场景描述
    """
    
    def __init__(self):
        self.last_analysis_time = 0
        self.analysis_interval = 20
        self.last_description = ""
        
        # 目标类别映射（中文 + 英文）
        self.class_labels = {
            'person': {'zh': '人员', 'en': 'person', 'emoji': '👤'},
            'car': {'zh': '汽车', 'en': 'car', 'emoji': '🚗'},
            'truck': {'zh': '卡车', 'en': 'truck', 'emoji': '🚚'},
            'bus': {'zh': '公交车', 'en': 'bus', 'emoji': '🚌'},
            'bicycle': {'zh': '自行车', 'en': 'bicycle', 'emoji': '🚲'},
            'motorcycle': {'zh': '摩托车', 'en': 'motorcycle', 'emoji': '🏍️'},
            'dog': {'zh': '狗', 'en': 'dog', 'emoji': '🐕'},
            'cat': {'zh': '猫', 'en': 'cat', 'emoji': '🐈'},
            'chair': {'zh': '椅子', 'en': 'chair', 'emoji': '💺'},
            'table': {'zh': '桌子', 'en': 'table', 'emoji': '🪑'},
            'laptop': {'zh': '笔记本电脑', 'en': 'laptop', 'emoji': '💻'},
            'cell phone': {'zh': '手机', 'en': 'phone', 'emoji': '📱'},
            'tv': {'zh': '电视', 'en': 'TV', 'emoji': '📺'},
            'book': {'zh': '书籍', 'en': 'book', 'emoji': '📚'},
            'bottle': {'zh': '瓶子', 'en': 'bottle', 'emoji': '🍾'},
            'cup': {'zh': '杯子', 'en': 'cup', 'emoji': '☕'},
            'knife': {'zh': '刀具', 'en': 'knife', 'emoji': '🔪', 'danger': True},
            'gun': {'zh': '枪支', 'en': 'gun', 'emoji': '🔫', 'danger': True},
            'fire': {'zh': '火源', 'en': 'fire', 'emoji': '🔥', 'danger': True},
            'weapon': {'zh': '武器', 'en': 'weapon', 'emoji': '⚔️', 'danger': True},
        }
        
        # 场景描述模板库（多样化、自然化）
        self.scene_templates = {
            'empty': [
                "当前监控区域空旷，未检测到任何目标",
                "场景正常，区域内无异常目标",
                "监控画面清晰，环境安静无异常",
                "当前画面显示空旷区域，状态良好",
            ],
            'person_only': [
                "检测到 {count} 名人员在{location}活动",
                "监控区域发现 {count} 个{action}的人员",
                "画面中有 {count} 人{status}",
                "观察到 {count} 名人员在现场{behavior}",
            ],
            'vehicles': [
                "检测到 {details}，可能为交通或停车场景",
                "画面中包含 {details}，属于交通工具类",
                "发现 {details} 在监控范围内",
                "当前场景有 {details} 存在",
            ],
            'indoor_objects': [
                "室内场景检测：{details}",
                "监控到室内物品：{details}",
                "画面显示 {details} 等物体",
                "检测到 {details} 等室内设施",
            ],
            'mixed_scene': [
                "复合场景：{details}",
                "当前画面包含多种目标：{details}",
                "监控区域呈现 {details} 等多个目标",
                "综合检测结果：{details}",
            ],
            'threat_detected': [
                "⚠️ 警告：检测到威胁物品 {threats}！请立即处理",
                "⚠️ 安全警报：发现危险物品 {threats}，需关注",
                "⚠️ 异常检测：识别到 {threats} 等潜在威胁",
                "⚠️ 危险警告：画面中出现 {threats}",
            ],
        }
        
        # 地点词汇
        self.locations = ['现场', '区域内', '监控范围', '视野内']
        
        # 动作词汇
        self.actions = ['活动', '移动', '停留', '走动']
        
        # 状态词汇
        self.statuses = ['在场', '活动', '存在', '可见']
        
        # 行为词汇
        self.behaviors = ['活动', '移动', '作业', '徘徊']
        
        print(f"\n{'='*60}")
        print(f"🧠 高级场景分析器初始化完成")
        print(f"{'='*60}")
        print(f"   类型: Advanced Scene Analyzer v2.0")
        print(f"   特点:")
        print(f"   ✅ 零依赖（无需下载任何模型）")
        print(f"   ✅ 即时响应（< 1ms）")
        print(f"   ✅ 智能描述（自然语言生成）")
        print(f"   ✅ 多类别支持（20+ 种目标）")
        print(f"   ⚠️  自动威胁检测（刀具/枪支/火源）")
        print(f"   📊 分析间隔: {self.analysis_interval} 秒")
        print(f"{'='*60}\n")

    def analyze(self, frame_np, detections):
        """分析帧并返回结果"""
        current_time = time.time()
        
        # 缓存检查
        if current_time - self.last_analysis_time < self.analysis_interval:
            return {
                "is_anomaly": False,
                "vlm_description": self.last_description,
                "analysis_type": "cached",
                "detected_threats": [],
                "vlm_processing_time": 0.5,
                "timestamp": current_time
            }
        
        # 执行分析
        start_time = time.time()
        
        # 分类统计
        categories = self._categorize_detections(detections)
        
        # 生成描述
        description = self._generate_description(categories, detections)
        
        # 检测威胁
        threats = [d['class'] for d in detections 
                   if self.class_labels.get(d.get('class', ''), {}).get('danger', False) 
                   and d.get('confidence', 0) > 0.5]
        
        is_anomaly = len(threats) > 0
        
        # 更新缓存
        self.last_description = description
        self.last_analysis_time = current_time
        
        processing_time = (time.time() - start_time) * 1000
        
        print(f"\n🧠 [Advanced] 场景分析完成 ({processing_time:.1f}ms)")
        print(f"   {description}")
        
        return {
            "is_anomaly": is_anomaly,
            "vlm_description": description,
            "analysis_type": "advanced_analysis",
            "detected_threats": threats,
            "vlm_processing_time": round(processing_time, 1),
            "timestamp": current_time
        }

    def _categorize_detections(self, detections):
        """将检测结果分类"""
        categories = {
            'persons': [],      # 人员
            'vehicles': [],     # 车辆
            'animals': [],      # 动物
            'objects': [],      # 物品
            'electronics': [],  # 电子设备
            'furniture': [],    # 家具
            'threats': [],      # 威胁物品
        }
        
        for det in detections:
            cls = det.get('class', '').lower()
            conf = det.get('confidence', 0)
            
            label_info = self.class_labels.get(cls, {})
            
            item = {
                'class': cls,
                'confidence': conf,
                'label': label_info.get('zh', cls),
                'emoji': label_info.get('emoji', ''),
                'is_danger': label_info.get('danger', False),
            }
            
            if cls == 'person':
                categories['persons'].append(item)
            elif cls in ['car', 'truck', 'bus', 'bicycle', 'motorcycle']:
                categories['vehicles'].append(item)
            elif cls in ['dog', 'cat']:
                categories['animals'].append(item)
            elif label_info.get('danger'):
                categories['threats'].append(item)
            elif cls in ['laptop', 'cell phone', 'tv']:
                categories['electronics'].append(item)
            elif cls in ['chair', 'table']:
                categories['furniture'].append(item)
            else:
                categories['objects'].append(item)
        
        return categories

    def _generate_description(self, categories, detections):
        """智能生成场景描述"""
        
        # 如果没有检测结果
        if not detections or len(detections) == 0:
            return random.choice(self.scene_templates['empty'])
        
        # 如果有威胁物品（最高优先级）
        if len(categories['threats']) > 0:
            threat_names = [t['emoji'] + t['label'] for t in categories['threats']]
            template = random.choice(self.scene_templates['threat_detected'])
            return template.format(threats=', '.join(threat_names))
        
        # 统计各类别数量
        person_count = len(categories['persons'])
        vehicle_count = len(categories['vehicles'])
        animal_count = len(categories['animals'])
        object_count = len(categories['objects']) + len(categories['electronics']) + len(categories['furniture'])
        
        # 构建详细列表
        details_list = []
        
        if person_count > 0:
            details_list.append(f"{categories['persons'][0]['emoji']}人员×{person_count}")
        
        for vehicle in categories['vehicles']:
            details_list.append(f"{vehicle['emoji']}{vehicle['label']}")
        
        for animal in categories['animals']:
            details_list.append(f"{animal['emoji']}{animal['label']}×{len([a for a in categories['animals'] if a['class'] == animal['class']])}")
        
        for obj in (categories['electronics'] + categories['furniture']):
            details_list.append(f"{obj['emoji']}{obj['label']}")
        
        details = ', '.join(details_list)
        
        # 根据场景类型选择模板
        if person_count > 0 and vehicle_count == 0 and object_count == 0 and animal_count == 0:
            # 只有人员
            template = random.choice(self.scene_templates['person_only'])
            location = random.choice(self.locations)
            action = random.choice(self.actions)
            status = random.choice(self.statuses)
            behavior = random.choice(self.behaviors)
            desc = template.format(
                count=person_count,
                location=location,
                action=action,
                status=status,
                behavior=behavior
            )
            
        elif vehicle_count > 0 and person_count == 0 and object_count < 2:
            # 主要为车辆
            template = random.choice(self.scene_templates['vehicles'])
            desc = template.format(details=details)
            
        elif object_count > 0 and vehicle_count == 0 and person_count == 0:
            # 只有物品（可能是室内场景）
            template = random.choice(self.scene_templates['indoor_objects'])
            desc = template.format(details=details)
            
        else:
            # 混合场景
            template = random.choice(self.scene_templates['mixed_scene'])
            desc = template.format(details=details)
        
        return desc


# 创建全局实例
analyzer_instance = AdvancedSceneAnalyzer()