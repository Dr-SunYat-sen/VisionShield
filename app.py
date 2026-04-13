import streamlit as st
import cv2
from ultralytics import YOLO
from PIL import Image
import torch  # 现在我们要正式用到它了

# 1. 强制检测环境并分配设备
device = 'cuda' if torch.cuda.is_available() else 'cpu'
st.sidebar.info(f"🚀 当前运行设备: {device.upper()}")

# 2. 缓存模型加载
@st.cache_resource
def load_models():
    # 明确指定模型加载到 GPU
    yolo = YOLO('yolo11n.pt').to(device) 
    return yolo
yolo_model = load_models()

# 3. 侧边栏：推流配置
st.sidebar.title("📡 推流设置")
stream_url = st.sidebar.text_input("输入手机/无人机流地址", "http://192.168.x.x:8080/video")
threshold = st.sidebar.slider("检测阈值", 0.1, 1.0, 0.4)
run_monitor = st.sidebar.toggle("开启实时监控")

# 4. 主界面布局
st.title("🛡️ 异常检测与分析平台")
col_video, col_analysis = st.columns([2, 1])

with col_video:
    st.subheader("🎥 实时视频流")
    video_placeholder = st.empty()

with col_analysis:
    st.subheader("📝 智能分析报告")
    status_text = st.empty()
    vlm_output = st.empty()
    alert_placeholder = st.empty()

# 5. 核心逻辑循环
if run_monitor:
    cap = cv2.VideoCapture(stream_url)
    
    # 计数器，防止VLM跑得太频繁导致画面卡死
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("无法读取视频流，请检查地址或网络")
            break
        
        frame_count += 1
        
        # 每隔2帧做一次检测，缓解计算压力
        if frame_count % 3 == 0:
 # 这里的 device=0 也是通过 torch 间接传递的
            results = yolo_model.predict(frame, conf=threshold, verbose=False, device=device)
            
            # 缩放画面显示，减少网络传输压力（Streamlit 瓶颈所在）
            annotated_frame = results[0].plot()
            display_frame = cv2.resize(annotated_frame, (640, 480)) 
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(display_frame, channels="RGB", use_container_width=True)
            
            # 更新右侧状态
            objs = results[0].boxes.cls.tolist()
            if len(objs) > 0:
                status_text.markdown(f"✅ **当前检测到目标数**: {len(objs)}")
                
                # 简单逻辑：如果检测到特定的“异常”（比如person且在特定场景）
                # 这里可以触发 VLM 分析逻辑
                if frame_count % 60 == 0:  # 每60帧触发一次VLM，避免卡顿
                    vlm_output.info("🤖 VLM 正在生成详细描述...")
                    # TODO: 调用 Florence-2 推理
            else:
                status_text.write("等待目标中...")

    cap.release()