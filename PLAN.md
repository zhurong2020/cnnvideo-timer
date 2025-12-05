# CNN Video Timer 重构计划 v2

## 产品定位

**英语学习视频服务** - WordPress 网站的后端服务，为用户提供新闻/短视频下载 + AI字幕 + 学习增强处理

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     WordPress (PHP)                              │
│                    用户界面 + 会员管理                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────────┐
│                  Python 后端服务 (FastAPI)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ 视频下载器   │  │ 字幕处理器   │  │ 视频处理器 (FFmpeg)      │  │
│  │ - YouTube   │  │ - Whisper   │  │ - 重复播放              │  │
│  │ - 短视频    │  │ - 时间轴    │  │ - 字幕嵌入              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  任务队列 (SQLite + 简单队列)    │   存储管理                    │
│  - 下载任务                      │   - 临时文件 → 用户下载       │
│  - 处理任务                      │   - 短视频 → OneDrive         │
└─────────────────────────────────────────────────────────────────┘
```

## 核心功能

### 1. 视频来源 (按用户等级)

| 等级 | 来源 |
|------|------|
| 普通用户 | CNN10, BBC Learning English, VOA |
| 高级用户 | + 更多YouTube频道, TikTok/抖音短视频 |

### 2. 视频处理流水线

```
原始视频 → AI字幕生成 → 学习增强处理 → 输出
                              ↓
                    ┌─────────────────────┐
                    │ 学习模式选项:        │
                    │ 1. 原视频+字幕       │
                    │ 2. 2遍播放(第2遍带幕)│
                    │ 3. 慢速+字幕         │
                    └─────────────────────┘
```

### 3. API 接口设计

```
POST /api/v1/tasks              # 创建下载任务
GET  /api/v1/tasks/{id}         # 查询任务状态
GET  /api/v1/tasks/{id}/download # 下载处理后的视频
GET  /api/v1/sources            # 获取可用视频源列表
POST /api/v1/videos/preview     # 预览视频信息(不下载)
```

---

## 项目结构 (重构后)

```
cnnvideo-timer/
├── src/
│   ├── __init__.py
│   ├── api/                      # REST API (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py               # API 入口
│   │   ├── routes/
│   │   │   ├── tasks.py          # 任务相关接口
│   │   │   └── sources.py        # 视频源接口
│   │   └── models.py             # Pydantic 模型
│   │
│   ├── core/                     # 核心业务逻辑
│   │   ├── __init__.py
│   │   ├── downloader.py         # 下载器基类+实现
│   │   ├── task_manager.py       # 任务管理
│   │   └── config.py             # 配置管理
│   │
│   ├── sources/                  # 视频源适配器
│   │   ├── __init__.py
│   │   ├── base.py               # 基类
│   │   ├── youtube.py            # YouTube/CNN10/BBC
│   │   └── tiktok.py             # TikTok/抖音
│   │
│   ├── processors/               # 视频处理器
│   │   ├── __init__.py
│   │   ├── subtitle.py           # Whisper 字幕生成
│   │   ├── ffmpeg.py             # FFmpeg 视频处理
│   │   └── learning_modes.py     # 学习模式处理
│   │
│   ├── storage/                  # 存储管理
│   │   ├── __init__.py
│   │   ├── local.py              # 本地临时存储
│   │   └── onedrive.py           # OneDrive (via rclone)
│   │
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       └── helpers.py
│
├── config/
│   ├── config.env                # 环境配置
│   └── sources.json              # 视频源配置
│
├── data/                         # 数据目录
│   ├── tasks.db                  # SQLite 任务数据库
│   └── temp/                     # 临时文件目录
│
├── main.py                       # CLI 入口
├── server.py                     # API 服务入口
├── requirements.txt
└── pyproject.toml
```

---

## 实施阶段

### 阶段 1: 核心重构 ✅ (已完成)
- [x] 修复现有 Bug
- [x] 创建项目入口
- [x] 现代化项目配置

### 阶段 2: API 服务框架 (当前)
- [ ] 安装 FastAPI + uvicorn
- [ ] 创建基础 API 结构
- [ ] 实现任务管理 (SQLite)
- [ ] 重构下载器为可扩展架构

### 阶段 3: 字幕功能
- [ ] 集成 Whisper (可用 faster-whisper 节省资源)
- [ ] 字幕时间轴生成
- [ ] SRT/VTT 格式输出

### 阶段 4: 视频处理
- [ ] FFmpeg 封装
- [ ] 学习模式实现 (重复播放+字幕)
- [ ] 字幕嵌入 (硬字幕/软字幕)

### 阶段 5: 存储与输出
- [ ] 临时文件管理 + 自动清理
- [ ] OneDrive 集成 (rclone)
- [ ] 下载链接生成

### 阶段 6: WordPress 集成
- [ ] API 认证 (API Key / JWT)
- [ ] WordPress 插件或短代码
- [ ] 用户权限对接

---

## 技术栈

```
# requirements.txt

# API 框架
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6

# 核心依赖
yt-dlp>=2024.1.0
apscheduler>=3.10.0
python-dotenv>=1.0.0
requests>=2.31.0
pydantic>=2.5.0

# 数据库
aiosqlite>=0.19.0       # 异步 SQLite

# 字幕生成
faster-whisper>=0.10.0  # 比原版 whisper 更快更省内存

# 视频处理
ffmpeg-python>=0.2.0    # FFmpeg Python 封装

# 工具
tqdm>=4.66.0
rich>=13.0.0
```

---

## 资源考虑 (VPS 优化)

1. **Whisper 模型选择**
   - `tiny` / `base` 模型适合小型 VPS
   - faster-whisper 比原版节省 4x 内存

2. **任务队列**
   - 小规模用户: SQLite + 简单后台线程
   - 无需 Redis/Celery

3. **临时文件清理**
   - 处理完成后保留 24 小时
   - 定时清理任务

4. **并发控制**
   - 同时处理任务数限制 (如最多 2 个)
   - 防止 VPS 资源耗尽
