const video = document.getElementById('webcam');
const ipCameraImg = document.getElementById('ip-camera-feed');
const btn = document.getElementById('toggleStream');
const cameraType = document.getElementById('cameraType');
const ipCameraConfig = document.getElementById('ipCameraConfig');
const ipCameraUrl = document.getElementById('ipCameraUrl');

let isStreaming = false;
let streamInterval;
let lastClickTime = 0; // 防抖：记录上次点击时间
let currentCameraMode = 'local'; // 记录当前使用的摄像头模式

// 切换摄像头类型时显示/隐藏 IP 摄像头配置
cameraType.addEventListener('change', () => {
    if (cameraType.value === 'ip') {
        ipCameraConfig.style.display = 'block';
    } else {
        ipCameraConfig.style.display = 'none';
    }
});

btn.addEventListener('click', async () => {
    // 防抖：500ms 内不允许重复点击
    const now = Date.now();
    if (now - lastClickTime < 500) {
        console.log("点击过于频繁，请稍候");
        return;
    }
    lastClickTime = now;
    
    if (!isStreaming) {
        try {
            if (cameraType.value === 'local') {
                // 本地摄像头需要检查浏览器兼容性
                if (!navigator.mediaDevices) {
                    alert("您的浏览器不支持媒体设备 API，请使用现代浏览器。");
                    console.error("navigator.mediaDevices 未定义");
                    return;
                }
                
                if (!navigator.mediaDevices.getUserMedia) {
                    alert("您的浏览器不支持摄像头访问功能，请使用现代浏览器。");
                    console.error("navigator.mediaDevices.getUserMedia 未定义");
                    return;
                }
                
                // 检查连接协议
                if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost') {
                    alert("摄像头访问需要在安全上下文（HTTPS 或 localhost）中运行。");
                    console.error("非安全上下文");
                    return;
                }
                
                // 检查 WebSocket 连接状态（使用 WSState 对象）
                if (!window.WSState || !window.WSState.isConnected) {
                    alert("WebSocket 连接未建立，正在尝试连接...\n\n请稍候几秒后重试，或刷新页面。");
                    
                    // 尝试手动触发连接
                    if (typeof connectWebSocket === 'function') {
                        connectWebSocket();
                    }
                    console.log("WebSocket state:", window.WSState ? window.WSState.readyState : "WSState not found");
                    return;
                }
                
                // 本地摄像头
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
                    
                    // 显示 video 元素，隐藏 img 元素
                    video.style.display = 'block';
                    ipCameraImg.style.display = 'none';
                    video.srcObject = stream;
                    
                    // 只有本地摄像头模式才启动帧发送定时器
                    streamInterval = setInterval(sendLocalFrame, 100);
                    
                    // 记录当前模式
                    currentCameraMode = 'local';
                    
                } catch (err) {
                    console.error("获取摄像头权限失败:", err);
                    if (err.name === 'NotAllowedError') {
                        alert("摄像头权限被拒绝，请在浏览器设置中允许摄像头访问。");
                    } else if (err.name === 'NotFoundError') {
                        alert("未找到摄像头设备，请确保摄像头已连接。");
                    } else {
                        alert("无法访问摄像头: " + err.message);
                    }
                    return;
                }
            } else {
                // IP 摄像头 - 使用服务端主动推送模式
                const url = ipCameraUrl.value.trim();
                if (!url) {
                    alert("请输入 IP 摄像头地址");
                    return;
                }
                
                // 检查 WebSocket 连接状态（使用 WSState 对象）
                if (!window.WSState || !window.WSState.isConnected) {
                    alert("WebSocket 连接未建立，正在尝试连接...\n\n请稍候几秒后重试，或刷新页面。");
                    
                    // 尝试手动触发连接
                    if (typeof connectWebSocket === 'function') {
                        connectWebSocket();
                    }
                    console.log("WebSocket state:", window.WSState ? window.WSState.readyState : "WSState not found");
                    return;
                }
                
                console.log("发送 IP 摄像头流请求:", url);
                
                // 显示 img 元素，隐藏 video 元素
                video.style.display = 'none';
                ipCameraImg.style.display = 'block';
                
                // 清除之前的视频源
                video.srcObject = null;
                video.src = '';
                ipCameraImg.src = '';
                
                // 发送启动 IP 流指令给后端
                window.WSState.ws.send(JSON.stringify({
                    type: "start_ip_stream",
                    url: url
                }));
                
                logInfo(`开始 IP 摄像头流: ${url}`);
                
                // 记录当前模式
                currentCameraMode = 'ip';
            }
            
            isStreaming = true;
            btn.innerText = "HALT STREAM";
            btn.style.color = "red";
            btn.style.borderColor = "red";
            
        } catch (err) {
            console.error("摄像头访问失败:", err);
            alert("无法访问摄像头，请检查设置。");
        }
    } else {
        // 停止流
        if (currentCameraMode === 'local') {
            const stream = video.srcObject;
            if (stream) {
                const tracks = stream.getTracks();
                tracks.forEach(track => track.stop());
            }
            
            // 清除本地摄像头的帧发送定时器
            if (streamInterval) {
                clearInterval(streamInterval);
                streamInterval = null;
            }
            
            // 隐藏 video 元素
            video.style.display = 'none';
        } else {
            // 发送停止 IP 流指令给后端
            if (window.WSState && window.WSState.isConnected && window.WSState.ws) {
                window.WSState.ws.send(JSON.stringify({
                    type: "stop_ip_stream"
                }));
                logInfo("停止 IP 摄像头流");
            } else {
                console.warn("WebSocket not connected when trying to stop IP stream");
            }
            
            // 隐藏 img 元素
            ipCameraImg.style.display = 'none';
        }
        
        video.srcObject = null;
        video.src = '';
        isStreaming = false;
        btn.innerText = "INITIALIZE STREAM";
        btn.style.color = "var(--neon-green)";
        btn.style.borderColor = "var(--neon-green)";
        
        // 重置模式
        currentCameraMode = cameraType.value;
    }
});

// 仅用于本地摄像头的帧发送函数
function sendLocalFrame() {
    if (!window.WSState || !window.WSState.isConnected || !window.WSState.ws) {
        console.warn("WebSocket not ready for sending frame, state:", window.WSState ? window.WSState.readyState : "undefined");
        return;
    }
    
    if (!video || video.readyState < video.HAVE_CURRENT_DATA) {
        return;
    }
    
    const captureCanvas = document.createElement('canvas');
    const captureCtx = captureCanvas.getContext('2d');
    captureCanvas.width = video.videoWidth;
    captureCanvas.height = video.videoHeight;
    captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
    
    // 压缩质量以减少网络延迟
    const base64Image = captureCanvas.toDataURL('image/jpeg', 0.6);
    
    window.WSState.ws.send(JSON.stringify({
        type: "local_frame",
        timestamp: Date.now(),
        image: base64Image
    }));
}

// 导出当前摄像头模式供其他模块使用
window.currentCameraMode = () => currentCameraMode;