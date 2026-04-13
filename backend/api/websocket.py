import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import base64
import cv2
import numpy as np
import time
from core.detector import detector_instance
from core.processor import IPCameraStream, analyzer_instance

ws_router = APIRouter()

@ws_router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ip_stream_task = None
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue
            
            msg_type = message.get("type")

            if msg_type == "local_frame":
                try:
                    encoded_data = message['image'].split(',')[1]
                    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if img is not None:
                        start_time = time.time()
                        results = detector_instance.detect(img)
                        detect_time = (time.time() - start_time) * 1000
                        
                        # 获取 VLM 场景描述
                        vlm_result = analyzer_instance.analyze(img, results.get('detections', []))
                        
                        await websocket.send_json({
                            "type": "detection_result", 
                            "data": results,
                            "detect_time_ms": round(detect_time, 1),
                            "vlm_analysis": vlm_result
                        })
                    else:
                        await websocket.send_json({"type": "error", "message": "Failed to decode image"})
                except Exception as e:
                    print(f"Local frame processing error: {e}")
                    await websocket.send_json({"type": "error", "message": str(e)})

            elif msg_type == "start_ip_stream":
                url = message.get("url")
                
                if not url:
                    await websocket.send_json({"type": "error", "message": "No URL provided"})
                    continue
                
                if ip_stream_task:
                    ip_stream_task.cancel()
                    try:
                        await ip_stream_task
                    except asyncio.CancelledError:
                        pass
                
                ip_stream_task = asyncio.create_task(
                    handle_ip_streaming(websocket, url)
                )
                
                await websocket.send_json({
                    "type": "ip_stream_started",
                    "message": f"IP stream started for {url}"
                })

            elif msg_type == "stop_ip_stream":
                if ip_stream_task:
                    ip_stream_task.cancel()
                    try:
                        await ip_stream_task
                    except asyncio.CancelledError:
                        pass
                    ip_stream_task = None
                
                await websocket.send_json({
                    "type": "ip_stream_stopped",
                    "message": "IP stream stopped"
                })

            else:
                await websocket.send_json({"type": "error", "message": f"Unknown message type: {msg_type}"})

    except WebSocketDisconnect:
        if ip_stream_task:
            ip_stream_task.cancel()
        print("WebSocket Disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        if ip_stream_task:
            ip_stream_task.cancel()

async def handle_ip_streaming(websocket, url):
    stream = None
    print(f"\n{'='*60}")
    print(f"🎥 Starting IP Stream: {url}")
    print(f"⚡ GPU 加速: {'✅ CUDA' if detector_instance.device == 'cuda' else '❌ CPU'}")
    print(f"🧠 场景分析: ✅ Advanced Analyzer v2.0 (零依赖)")
    print(f"   响应时间: <1ms | 描述质量: 智能")
    print(f"   特点: 无需下载模型，开箱即用")
    print(f"📊 跳帧策略: 每 {detector_instance.detect_interval} 帧检测一次")
    print(f"🔍 分析间隔: {analyzer_instance.analysis_interval} 秒")
    print(f"{'='*60}\n")
    
    frame_count = 0
    fps_start_time = time.time()
    
    try:
        stream = IPCameraStream(url)
        
        # 测试是否能成功读取帧
        test_frame = stream.get_frame()
        if not test_frame:
            await websocket.send_json({
                "type": "ip_stream_error",
                "message": "Cannot read frames from IP camera"
            })
            return
        
        # 发送连接成功消息，包含系统信息
        system_info = {
            "type": "ip_stream_connected",
            "message": f"✅ Connected | GPU: {detector_instance.device.upper()} | Analyzer: ✅ Ready",
            "system_status": {
                "gpu": detector_instance.device,
                "analyzer_ready": True,
                "analyzer_model": "Advanced Scene Analyzer v2.0 (Zero Dependencies)",
                "analyzer_type": "advanced"
            }
        }
        
        await websocket.send_json(system_info)
        
        while True:
            loop_start = time.time()
            
            # 在单独的线程运行 OpenCV 读图，防止阻塞异步循环
            frame_base64 = await asyncio.to_thread(stream.get_frame)
            
            if frame_base64:
                frame_count += 1
                
                # 解码进行检测
                nparr = np.frombuffer(base64.b64decode(frame_base64), np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    # 执行 YOLO 检测（带时间统计）
                    detect_start = time.time()
                    detection_results = detector_instance.detect(img)
                    detect_time = (time.time() - detect_start) * 1000
                    
                    # 执行智能场景分析（轻量级，<1ms）
                    analysis_start = time.time()
                    analysis_result = analyzer_instance.analyze(
                        img, 
                        detection_results.get('detections', [])
                    )
                    analysis_time = (time.time() - analysis_start) * 1000
                    
                    # 计算总耗时
                    total_time = (time.time() - loop_start) * 1000
                    
                    # 发送完整结果给前端
                    await websocket.send_json({
                        "type": "ip_frame_result",
                        "image": f"data:image/jpeg;base64,{frame_base64}",
                        "data": detection_results,
                        "vlm_analysis": analysis_result,
                        "performance": {
                            "frame_num": frame_count,
                            "detect_time_ms": round(detect_time, 1),
                            "analysis_time_ms": round(analysis_time, 1),
                            "total_time_ms": round(total_time, 1),
                            "fps": round(1.0 / (time.time() - loop_start), 1) if frame_count > 1 else 0
                        }
                    })
                
                # 每 5 秒输出一次 FPS 统计
                if frame_count % 150 == 0:  # 约 5 秒（假设 30fps）
                    elapsed = time.time() - fps_start_time
                    current_fps = frame_count / elapsed
                    print(f"📊 实时 FPS: {current_fps:.1f} | 总帧数: {frame_count} | "
                          f"检测耗时: {detect_time:.1f}ms | 分析耗时: {analysis_time:.1f}ms")
            
            # 动态调整帧率：目标 30FPS（33ms间隔）
            loop_elapsed = time.time() - loop_start
            target_interval = 0.033  # 30 FPS
            sleep_time = target_interval - loop_elapsed
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            else:
                # 如果处理超时，不休眠直接进入下一帧
                await asyncio.sleep(0.001)  # 最小休眠 1ms
    
    except asyncio.CancelledError:
        elapsed = time.time() - fps_start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"\n{'='*60}")
        print(f"⏹️ IP streaming task cancelled")
        print(f"📈 平均 FPS: {avg_fps:.1f} | 总帧数: {frame_count}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ IP Stream Error: {e}\n")
        try:
            await websocket.send_json({
                "type": "ip_stream_error",
                "message": str(e)
            })
        except Exception as send_error:
            print(f"Failed to send error message: {send_error}")
    finally:
        if stream and hasattr(stream, 'cap') and stream.cap is not None:
            stream.cap.release()