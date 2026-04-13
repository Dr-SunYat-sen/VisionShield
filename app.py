import streamlit as st
import cv2
from ultralytics import YOLO
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForCausalLM

# --- 1. 初始化与模型加载 ---
st.set_page_config(layout="wide", page_title="SCU 智能视觉监控系统")

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# --- 替换成 Moondream2 的加载逻辑 ---
@st.cache_resource
def load_all_models():
    yolo = YOLO('yolo11n.pt').to(device)
    
    # Moondream2 模型更小、兼容性更好
    vlm_model_id = "vikhyatk/moondream2"
    revision = "2024-08-26" # 指定版本更稳
    vlm_model = AutoModelForCausalLM.from_pretrained(
        vlm_model_id, trust_remote_code=True, revision=revision
    ).to(device).eval()
    vlm_processor = AutoProcessor.from_pretrained(vlm_model_id, revision=revision)
    
    return yolo, vlm_model, vlm_processor

with st.spinner("正在加载深度学习模型，请稍候..."):
    yolo_model, vlm_model, vlm_processor = load_all_models()

# --- 2. 侧边栏与布局 ---
st.sidebar.title("⚙️ 监控配置")
st.sidebar.info(f"当前算力设备: {device.upper()}")
stream_url = st.sidebar.text_input("推流地址 (手机IP摄像头)", "http://192.168.1.x:8080/video")
threshold = st.sidebar.slider("检测灵敏度", 0.1, 1.0, 0.4)
run_monitor = st.sidebar.toggle("🚀 开启实时实时监控", value=False)
vlm_trigger = st.sidebar.button("🤖 执行 VLM 智能分析")

st.title("🛡️ 异常检测与 AI 场景分析平台")
st.markdown("---")

col_video, col_analysis = st.columns([2, 1])

# --- 3. VLM 推理函数 ---
# --- 替换成 Moondream2 的推理函数 ---
def run_vlm_analysis(image):
    # Moondream 的推理非常直观
    enc_image = vlm_model.encode_image(image)
    result = vlm_model.answer_question(enc_image, "Describe this image in detail.", vlm_processor) # 这里的processor传tokenizer即可
    return result

# --- 4. 实时监控核心循环 ---
if run_monitor:
    cap = cv2.VideoCapture(stream_url)
    video_placeholder = col_video.empty()
    status_box = col_analysis.empty()
    vlm_box = col_analysis.empty()
    
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("视频流断开，请检查推流端")
            break
        
        frame_count += 1
        
        # 性能策略：降低分辨率 + 跳帧检测
        if frame_count % 3 == 0:
            frame_resized = cv2.resize(frame, (640, 480))
            
            # YOLO 推理
            results = yolo_model.predict(frame_resized, conf=threshold, verbose=False, device=device)
            annotated_frame = results[0].plot()
            
            # 转换颜色空间显示
            display_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(display_frame, channels="RGB", use_container_width=True)
            
            # 更新右侧状态
            objs = results[0].boxes.cls.tolist()
            status_box.subheader(f"📊 实时状态")
            status_box.write(f"检测到物体数量: {len(objs)}")
            
            # 自动/手动触发 VLM 分析
            # 逻辑：点击按钮 OR 检测到人且每隔100帧触发一次
            if vlm_trigger or (0 in objs and frame_count % 120 == 0):
                vlm_box.warning("🤖 VLM 正在深度分析画面...")
                pil_img = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
                description = run_vlm_analysis(pil_img)
                vlm_box.success(f"🔍 **场景描述**: \n\n {description}")
                vlm_trigger = False # 重置按钮状态

    cap.release()