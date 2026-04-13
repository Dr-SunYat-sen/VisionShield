from ultralytics import YOLO
import numpy as np
import cv2
import torch

class YOLODetector:
    def __init__(self, model_path="../../yolo11n.pt"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🚀 使用设备: {self.device}")
        
        if self.device == 'cuda':
            print(f"💾 GPU: {torch.cuda.get_device_name(0)}")
        
        try:
            # 启用 GPU 加速和性能优化
            self.model = YOLO(model_path)
            
            # 将模型移动到 GPU
            self.model.to(self.device)
            
            # 性能优化设置
            if self.device == 'cuda':
                # 使用 FP16 半精度加速（速度提升 2-3 倍）
                self.model.fuse()
                print("✅ 已启用 GPU 加速 (FP16)")
            
            self.ready = True
            
        except Exception as e:
            print(f"模型加载失败 (请确保模型文件存在): {e}")
            self.ready = False
        
        # 帧计数器（用于跳帧检测）
        self.frame_count = 0
        self.detect_interval = 3  # 每 3 帧检测一次（提升性能）

    def detect(self, image_np: np.ndarray):
        if not self.ready:
            return {"status": "error", "message": "Model not loaded"}
        
        self.frame_count += 1
        
        # 跳帧策略：每 N 帧才进行一次检测
        if self.frame_count % self.detect_interval != 0:
            return {"status": "skipped", "detections": []}
        
        try:
            # 运行推理（启用 GPU 加速）
            results = self.model(
                image_np, 
                verbose=False,
                half=(self.device == 'cuda'),  # GPU 使用半精度
                imgsz=320,  # 降低输入尺寸以提升速度
                conf=0.25   # 置信度阈值
            )
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    name = self.model.names[cls]
                    
                    # 只返回高置信度的检测结果
                    if conf >= 0.3:  # 提高置信度过滤
                        detections.append({
                            "class": name,
                            "confidence": round(conf, 2),
                            "bbox": [int(x1), int(y1), int(x2), int(y2)]
                        })
            
            return {"status": "success", "detections": detections}
            
        except Exception as e:
            print(f"检测错误: {e}")
            return {"status": "error", "message": str(e)}

# 单例模式
detector_instance = YOLODetector()
print(f"✅ YOLO 检测器初始化完成")
print(f"⚡ 跳帧策略: 每 {detector_instance.detect_interval} 帧检测一次")