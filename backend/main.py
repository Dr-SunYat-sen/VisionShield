import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.websocket import ws_router
from api.routes import api_router

app = FastAPI(title="VisionShield API", version="1.0.0")

# 注册路由
app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

# 挂载前端静态文件 (支持从项目根目录或 backend 目录运行)
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)