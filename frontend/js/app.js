const WSState = {
    ws: null,
    reconnectInterval: null,
    isConnecting: false,
    
    get isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    },
    
    get readyState() {
        return this.ws ? this.ws.readyState : undefined;
    }
};

const logOutput = document.getElementById('log-output');
const vlmStatusEl = document.getElementById('vlm-status');
const vlmOutputEl = document.getElementById('vlm-output');
const performanceMetricsEl = document.getElementById('performance-metrics');

function logInfo(msg) {
    const p = document.createElement('div');
    p.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
    if (logOutput) {
        logOutput.prepend(p);
    }
}

function updateVLMStatus(status, isReady = false) {
    if (vlmStatusEl) {
        const icon = isReady ? '✅' : '🔄';
        const color = isReady ? '#00ff41' : '#ffa500';
        vlmStatusEl.innerHTML = `${icon} ${status}`;
        vlmStatusEl.style.color = color;
    }
}

function updateVLMOutput(analysis) {
    if (!vlmOutputEl || !analysis) return;
    
    const description = analysis.vlm_description || '';
    const analysisType = analysis.analysis_type || 'unknown';
    const isAnomaly = analysis.is_anomaly || false;
    const threats = analysis.detected_threats || [];
    
    // 根据分析类型设置样式
    let typeLabel = '';
    let bgColor = '#1a1a2e';
    let borderColor = '#00ff41';
    
    switch (analysisType) {
        case 'threat_detected':
            typeLabel = '⚠️ 威胁检测';
            bgColor = '#2d1a1a';
            borderColor = '#ff4444';
            break;
        case 'routine':
            typeLabel = '🔍 定时分析';
            bgColor = '#1a2d1a';
            borderColor = '#00ff41';
            break;
        case 'loading':
            typeLabel = '🔄 加载中';
            bgColor = '#2d2d1a';
            borderColor = '#ffa500';
            break;
        case 'analyzing':
            typeLabel = '⏳ 分析中...';
            bgColor = '#1a1a2e';
            borderColor = '#00f3ff';
            break;
        case 'error':
            typeLabel = '❌ 错误';
            bgColor = '#2d1a1a';
            borderColor = '#ff0000';
            break;
        case 'cached':
            typeLabel = '💾 缓存结果';
            bgColor = '#1a1a2e';
            borderColor = '#888888';
            break;
        case 'smart_analysis':
            typeLabel = '🧠 智能分析';
            bgColor = '#1a2d2d';
            borderColor = '#00d4ff';
            break;
        default:
            typeLabel = '📊 分析结果';
    }
    
    // 构建 HTML 内容
    let html = `
        <div class="vlm-analysis-card" style="background: ${bgColor}; border-left: 4px solid ${borderColor};">
            <div class="vlm-header">
                <span class="vlm-type">${typeLabel}</span>
                ${isAnomaly ? '<span class="vlm-anomaly-badge">异常</span>' : '<span class="vlm-normal-badge">正常</span>'}
                ${threats.length > 0 ? `<span class="vlm-threats-badge">威胁: ${threats.join(', ')}</span>` : ''}
            </div>
            <div class="vlm-description">${description || '暂无描述'}</div>
            <div class="vlm-timestamp">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    
    vlmOutputEl.innerHTML = html;
}

function updatePerformanceMetrics(performance) {
    if (!performanceMetricsEl || !performance) return;
    
    const fps = performance.fps || 0;
    const detectTime = performance.detect_time_ms || 0;
    const analysisTime = performance.analysis_time_ms || 0;
    const totalTime = performance.total_time_ms || 0;
    const frameNum = performance.frame_num || 0;
    
    let html = `
        <div class="perf-card">
            <h4>📊 实时性能指标</h4>
            <div class="perf-grid">
                <div class="perf-item">
                    <span class="perf-label">帧率</span>
                    <span class="perf-value" style="color: ${fps >= 20 ? '#00ff41' : '#ffa500'};">${fps} FPS</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">帧数</span>
                    <span class="perf-value">#${frameNum}</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">YOLO 检测</span>
                    <span class="perf-value">${detectTime} ms</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">场景分析</span>
                    <span class="perf-value" style="color: ${analysisTime > 100 ? '#ffa500' : '#00ff41'};">${analysisTime} ms</span>
                </div>
                <div class="perf-item">
                    <span class="perf-label">总耗时</span>
                    <span class="perf-value">${totalTime} ms</span>
                </div>
            </div>
        </div>
    `;
    
    performanceMetricsEl.innerHTML = html;
}

function connectWebSocket() {
    if (WSState.isConnecting || (WSState.ws && WSState.ws.readyState === WebSocket.CONNECTING)) {
        console.log("WebSocket already connecting...");
        return;
    }
    
    WSState.isConnecting = true;
    
    try {
        WSState.ws = new WebSocket(`ws://localhost:8000/ws/stream`);
        
        WSState.ws.onopen = () => {
            logInfo("SYSTEM ONLINE. Connection established.");
            WSState.isConnecting = false;
            clearInterval(WSState.reconnectInterval);
            WSState.reconnectInterval = null;
            
            updateVLMStatus("等待系统信息...", false);
            
            // 触发自定义事件通知其他模块连接成功
            document.dispatchEvent(new CustomEvent('ws-connected'));
        };
        
        WSState.ws.onclose = (event) => {
            logInfo("SYSTEM OFFLINE. Connection lost.");
            WSState.isConnecting = false;
            
            updateVLMStatus("连接断开", false);
            
            // 触发自定义事件通知其他模块连接断开
            document.dispatchEvent(new CustomEvent('ws-disconnected'));
            
            // 自动重连（除非是正常关闭）
            if (!WSState.reconnectInterval && event.code !== 1000) {
                logInfo("Attempting to reconnect in 3 seconds...");
                WSState.reconnectInterval = setInterval(connectWebSocket, 3000);
            }
        };
        
        WSState.ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            logInfo("WebSocket connection error");
            WSState.isConnecting = false;
            updateVLMStatus("连接错误", false);
        };
        
        WSState.ws.onmessage = (event) => {
            try {
                const response = JSON.parse(event.data);
                
                switch (response.type) {
                    case 'detection_result':
                        handleDetectionResult(response.data);
                        // 处理 VLM 分析结果
                        if (response.vlm_analysis) {
                            handleVLMAnalysis(response.vlm_analysis);
                        }
                        break;
                    
                    case 'ip_frame_result':
                        handleIPFrameResult(response);
                        // 处理 VLM 分析结果
                        if (response.vlm_analysis) {
                            handleVLMAnalysis(response.vlm_analysis);
                        }
                        // 更新性能指标
                        if (response.performance) {
                            updatePerformanceMetrics(response.performance);
                        }
                        break;
                    
                    case 'ip_stream_started':
                        logInfo(response.message || "IP stream started");
                        document.dispatchEvent(new CustomEvent('ip-stream-started', { detail: response }));
                        break;
                    
                    case 'ip_stream_connected':
                        logInfo("✓ " + (response.message || "Connected to IP camera"));
                        
                        // 更新 VLM 状态
                        if (response.system_status) {
                            const status = response.system_status;
                            const vlmReady = status.vlm_ready;
                            const gpu = status.gpu;
                            const model = status.vlm_model;
                            
                            updateVLMStatus(
                                `GPU: ${gpu.toUpperCase()} | VLM: ${model} (${vlmReady ? '就绪' : '加载中'})`,
                                vlmReady
                            );
                            
                            logInfo(`System Status - GPU: ${gpu}, VLM: ${model}, Ready: ${vlmReady}`);
                        } else {
                            updateVLMStatus("已连接到摄像头", true);
                        }
                        
                        document.dispatchEvent(new CustomEvent('ip-stream-connected', { detail: response }));
                        break;
                    
                    case 'ip_stream_stopped':
                        logInfo(response.message || "IP stream stopped");
                        updateVLMStatus("流已停止", false);
                        document.dispatchEvent(new CustomEvent('ip-stream-stopped', { detail: response }));
                        break;
                    
                    case 'ip_stream_error':
                        logInfo("✗ IP Stream Error: " + (response.message || "Unknown error"));
                        alert("IP 摄像头错误: " + (response.message || "未知错误"));
                        updateVLMStatus("流错误", false);
                        document.dispatchEvent(new CustomEvent('ip-stream-error', { detail: response }));
                        break;
                    
                    case 'error':
                        logInfo("✗ Server Error: " + (response.message || "Unknown error"));
                        console.error("Server error:", response.message);
                        break;
                        
                    default:
                        console.log("Unknown message type:", response.type);
                }
                
            } catch (e) {
                console.error("Failed to parse message:", e, event.data);
            }
        };
        
    } catch (error) {
        console.error("Failed to create WebSocket:", error);
        WSState.isConnecting = false;
        updateVLMStatus("创建连接失败", false);
        
        // 尝试重连
        if (!WSState.reconnectInterval) {
            WSState.reconnectInterval = setInterval(connectWebSocket, 3000);
        }
    }
}

function handleVLMAnalysis(analysis) {
    if (!analysis) return;
    
    // 如果后端标记为跳过更新（VLM 不可用），不刷新界面
    if (analysis.skip_update) {
        return;  // 静默跳过，不更新显示
    }
    
    // 更新 VLM 输出显示
    updateVLMOutput(analysis);
    
    // 如果有新的分析结果（非缓存和非跳过），记录到日志
    if (analysis.analysis_type && 
        !['cached', 'unavailable'].includes(analysis.analysis_type)) {
        const desc = analysis.vlm_description || '';
        if (desc && !desc.includes('Loading') && !desc.includes('Error')) {
            logInfo(`🧠 分析: ${desc.substring(0, 80)}...`);
        }
    }
    
    // 如果检测到异常，触发警报动画
    if (analysis.is_anomaly && window.triggerThreatAnimation) {
        window.triggerThreatAnimation(5); // 高优先级警报
    }
}

function handleDetectionResult(data) {
    const detections = data.detections;
    
    // 获取当前摄像头模式
    let mode = 'local';
    if (typeof window.currentCameraMode === 'function') {
        mode = window.currentCameraMode();
    }
    
    if (detections && detections.length > 0) {
        logInfo(`Threats/Objects detected: ${detections.length}`);
        drawOverlay(detections, mode); // 在视频上画框
        
        // 触发 3D 动画反馈
        if (window.triggerThreatAnimation) {
            window.triggerThreatAnimation(detections.length);
        }
    } else {
        clearOverlay();
    }
}

function handleIPFrameResult(response) {
    const ipCameraImg = document.getElementById('ip-camera-feed');
    
    if (ipCameraImg && response.image) {
        ipCameraImg.src = response.image;
        
        // 处理检测结果
        if (response.data) {
            const detections = response.data.detections;
            if (detections && detections.length > 0) {
                logInfo(`Threats/Objects detected: ${detections.length}`);
                drawOverlay(detections, 'ip'); // 在 IP 摄像头画面上画框
                
                // 触发 3D 动画反馈
                if (window.triggerThreatAnimation) {
                    window.triggerThreatAnimation(detections.length);
                }
            } else {
                clearOverlay();
            }
        }
    }
}

// 绘制 Bounding Box
function drawOverlay(detections, cameraType = 'local') {
    let sourceElement;
    
    if (cameraType === 'ip') {
        sourceElement = document.getElementById('ip-camera-feed');
    } else {
        sourceElement = document.getElementById('webcam');
    }
    
    const canvas = document.getElementById('overlay');
    
    if (!sourceElement || !canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 根据元素类型获取尺寸
    let width, height;
    if (cameraType === 'ip') {
        width = sourceElement.naturalWidth || 640;
        height = sourceElement.naturalHeight || 480;
    } else {
        width = sourceElement.videoWidth || 640;
        height = sourceElement.videoHeight || 480;
    }
    
    // 设置 canvas 尺寸
    canvas.width = width;
    canvas.height = height;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    detections.forEach(det => {
        const [x1, y1, x2, y2] = det.bbox;
        ctx.strokeStyle = '#00ff41';
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
        
        ctx.fillStyle = 'rgba(0, 255, 65, 0.5)';
        ctx.fillRect(x1, y1 - 25, 120, 25);
        ctx.fillStyle = '#fff';
        ctx.font = '16px Courier New';
        ctx.fillText(`${det.class} ${det.confidence}`, x1 + 5, y1 - 8);
    });
}

function clearOverlay() {
    const canvas = document.getElementById('overlay');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
}

// 导出给其他模块使用（使用对象引用，确保始终获取最新状态）
window.WSState = WSState;
window.connectWebSocket = connectWebSocket;

// 页面加载后自动连接
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(connectWebSocket, 500);
    });
} else {
    setTimeout(connectWebSocket, 500);
}