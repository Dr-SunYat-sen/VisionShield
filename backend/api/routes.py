from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
async def health_check():
    return {"status": "online", "system": "VisionShield", "version": "1.0.0"}

@api_router.get("/config")
async def get_config():
    # 这里以后可以返回模型的配置信息
    return {"model": "YOLOv11n", "threshold": 0.5}