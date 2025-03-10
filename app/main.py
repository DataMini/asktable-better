from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.routes import home
from app.utils.db_manager import init_db


# 初始化数据库
init_db()

# 创建 FastAPI 应用实例
app = FastAPI(title="AskTable Better")

# Middleware 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 Header
)

# 路由配置
app.include_router(home.router, prefix="/api/home", tags=["Home"])

# 静态文件服务
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def index_page():
    """加载首页模板"""
    with open("app/templates/index.html", "r", encoding='utf-8') as f:
        return f.read()
    
