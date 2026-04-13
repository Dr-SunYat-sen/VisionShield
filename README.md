# 🛡️ VisionShield - 智能视觉监控系统

> 基于 YOLO + VLM 的实时异常检测与 AI 场景分析平台

## ✨ 项目简介

VisionShield 是一个集成 **目标检测** 和 **视觉语言模型 (VLM)** 的智能监控系统，能够：

- **实时目标检测**：使用 YOLO11n 模型识别视频流中的物体
- **AI 场景理解**：通过 Moondream2 VLM 模型深度分析画面内容
- **多源接入**：支持本地摄像头和 IP 摄像头（手机推流）
- **GPU 加速**：支持 CUDA GPU 加速，推理速度提升 2-3 倍
- **双模式运行**：
  - Streamlit 版本（快速原型开发）
  - FastAPI + Web 前端版本（生产部署）

## 🎯 核心功能

### 1， 实时监控与检测

- 支持 RTSP/HTTP 视频流输入
- YOLO 实时物体检测与标注
- 智能跳帧策略（每 3 帧检测一次）优化性能
- 可调节检测灵敏度阈值

### 2， VLM 智能分析

- 自动/手动触发场景描述
- 检测到人物时自动进行深度分析
- 输出详细的画面内容描述

### 3，双运行模式

| 模式        | 入口文件              | 特点                      |
| --------- | ----------------- | ----------------------- |
| Streamlit | `app.py`          | 快速启动，适合开发和演示            |
| FastAPI   | `backend/main.py` | 生产级部署，支持 WebSocket 实时通信 |

## 🔧 技术栈

```
前端: HTML5 + CSS3 + JavaScript + Three.js (3D可视化)
后端: Python 3.10+
Web框架: Streamlit / FastAPI + Uvicorn
AI模型:
  - 目标检测: YOLO11n (Ultralytics)
  - 视觉语言: Moondream2 (HuggingFace Transformers)
图像处理: OpenCV + Pillow + NumPy
加速: PyTorch (CUDA GPU)
```

## 📋 环境要求

- **Python**: >= 3.8 (推荐 3.10+)
- **操作系统**: Windows / Linux / macOS
- **硬件**:
  - CPU: 4核以上推荐
  - 内存: 8GB+ (16GB+ 推荐)
  - GPU: NVIDIA GPU 可选 (CUDA 11.8+, 用于加速)

## 🚀 快速开始

### 第一步：克隆项目

```bash
git clone <你的仓库地址>
cd VisionShield
```

### 第二步：创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 第三步：安装依赖

**CPU 版本**（无独立显卡或不需要加速）:

```bash
pip install -r requirements.txt
```

**GPU 加速版**（推荐，需要 NVIDIA 显卡）:

```bash
# 1. 安装 CUDA 版本的 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# 2. 安装其他依赖
pip install -r requirements.txt

# 3. 验证 CUDA 是否可用
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'GPU名称: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

### 第四步：下载预训练模型

项目已包含 YOLO11n 模型 (`yolo11n.pt`)，首次运行时会自动下载 Moondream2 VLM 模型。

## ▶️ 运行方式

### 方式一：Streamlit 版本（推荐新手）（使用独立脚本app.py）

```bash
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`

**功能说明**:

- 在侧边栏配置摄像头地址
- 调整检测灵敏度（0.1-1.0）
- 点击"开启实时监控"按钮
- 可手动点击"执行 VLM 智能分析"或等待自动触发

### 方式二：FastAPI 版本（生产部署）

```bash
cd backend
python main.py
```

访问 `http://localhost:8000` 查看 Web 界面

**API 端点**:

- `/api` - RESTful API 接口
- `/ws` - WebSocket 实时数据推送

## 📁 项目结构

```
VisionShield/
├── app.py                 # Streamlit 主程序入口
├── test.py                # 测试脚本
├── yolo11n.pt             # YOLO 预训练模型
│
├── backend/               # FastAPI 后端
│   ├── main.py            # FastAPI 应用入口
│   ├── api/
│   │   ├── routes.py      # API 路由
│   │   └── websocket.py   # WebSocket 处理
│   └── core/
│       ├── detector.py    # YOLO 检测器封装
│       └── processor.py   # 视频流处理
│
├── frontend/              # Web 前端
│   ├── index.html         # 主页面
│   ├── css/style.css      # 样式文件
│   └── js/
│       ├── app.js         # 应用逻辑
│       ├── dashboard_3d.js # 3D可视化
│       └── stream.js      # 视频流处理
│
├── requirements.txt       # Python 依赖
├── LICENSE                # 许可证
└── README.md              # 项目说明
```

## 使用指南

### 配置 IP 摄像头（手机作为监控设备）

1. **Android 手机**: 使用 "IP Webcam" 应用
   - 启动应用 → 点击"Start Server"
   - 记录显示的 URL
2. **iPhone**: 使用 "TinyCam Monitor" 或类似应用
   - 配置 HTTP 服务器模式
   - 获取推流地址
3. **在 VisionShield 中使用**:
   - 将手机和电脑连接到同一 WiFi
   - 在侧边栏输入推流地址
   - 开启监控即可

### 性能优化建议

- **启用 GPU 加速**: 安装 CUDA 版 PyTorch，速度提升 2-3 倍
- **调整检测间隔**: 默认每 3 帧检测一次，可适当增大
- **降低分辨率**: 已内置 640x480 缩放
- **提高置信度阈值**: 减少误检，降低计算量

## 常见问题

### Q: 提示 "CUDA out of memory"

**A**: 降低 batch size 或使用 CPU 模式运行

### Q: 视频流无法连接

**A**:

1. 确认手机和电脑在同一网络
2. 检查防火墙设置
3. 尝试更换推流端口

### Q: 模型下载失败

**A**:

1. 检查网络连接（可能需要科学上网）
2. 手动从 HuggingFace 下载模型到本地
3. 设置镜像源: `HF_ENDPOINT=https://hf-mirror.com`

### Q: 检测速度太慢

**A**:

1. 确认是否使用了 GPU 加速
2. 增大跳帧间隔（修改 `detect_interval` 参数）
3. 降低输入分辨率（修改 `imgsz` 参数）

## 贡献指南

欢迎提交 Issue 和 Pull Request！

