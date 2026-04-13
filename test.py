from ultralytics import YOLO
model = YOLO('yolo11n.pt')  # 2026年我们直接上最新的11系列，更轻快
results = model.predict('https://ultralytics.com/images/bus.jpg')
results[0].show()