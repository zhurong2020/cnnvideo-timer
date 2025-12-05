# SmartNews Learn v2.0 - Project Overview

**完整项目概览与技术文档**

---

## 📋 项目信息

| 项目 | 信息 |
|------|------|
| **名称** | SmartNews Learn |
| **版本** | 2.0.0 |
| **类型** | 英语学习视频服务 |
| **语言** | Python 3.8+ |
| **许可** | MIT License |
| **仓库** | https://github.com/znhskzj/smartnews-learn |

---

## 🎯 项目定位

为英语学习者提供视频下载与处理服务，支持：
- 多新闻源视频下载（CNN10, BBC, VOA）
- AI 自动生成字幕（Whisper）
- 学习模式视频处理（重复播放、慢速等）
- REST API 接口（可集成 WordPress）

---

## 📁 项目结构

```
smartnews-learn/
│
├── 📄 文档
│   ├── README.md              # 完整项目文档
│   ├── QUICKSTART.md         # 5分钟快速入门
│   ├── EXAMPLES.md           # 使用示例
│   ├── CHANGELOG.md          # 版本更新日志
│   ├── PLAN.md               # 重构计划
│   └── PROJECT_OVERVIEW.md   # 本文档
│
├── 🚀 入口文件
│   ├── main.py               # CLI 命令行入口
│   ├── server.py             # API 服务入口
│   └── test_api.py           # 测试脚本
│
├── 📦 源代码 (src/)
│   ├── api/                  # REST API 模块
│   │   ├── main.py           # FastAPI 应用
│   │   ├── models.py         # Pydantic 数据模型
│   │   └── routes/           # API 路由
│   │       ├── tasks.py      # 任务管理接口
│   │       └── sources.py    # 视频源接口
│   │
│   ├── core/                 # 核心业务逻辑
│   │   ├── config.py         # 配置管理 (Pydantic)
│   │   ├── downloader.py     # 视频下载器
│   │   └── task_manager.py   # 任务队列 (SQLite)
│   │
│   ├── sources/              # 视频源适配器
│   │   ├── base.py           # 抽象基类
│   │   └── youtube.py        # YouTube 实现
│   │
│   ├── processors/           # 视频处理器 ⭐
│   │   ├── subtitle.py       # Whisper 字幕生成
│   │   ├── ffmpeg.py         # FFmpeg 视频处理
│   │   └── learning_modes.py # 学习模式处理
│   │
│   └── storage/              # 存储管理
│       └── (future)
│
├── ⚙️ 配置
│   └── config/
│       ├── config.env.example # 配置模板
│       └── config.env        # 实际配置（不入库）
│
├── 💾 数据目录
│   ├── data/                 # 数据文件
│   │   ├── tasks.db          # SQLite 数据库
│   │   └── temp/             # 临时文件
│   └── log/                  # 日志文件
│
├── 🛠️ 安装脚本
│   ├── install.sh            # Linux/Mac 安装
│   └── install.bat           # Windows 安装
│
└── 📦 配置文件
    ├── requirements.txt      # Python 依赖
    ├── pyproject.toml        # 项目配置
    └── .gitignore            # Git 忽略规则
```

---

## 🏗️ 技术架构

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      WordPress (前端)                        │
│                   用户界面 + 会员管理                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────▼──────────────────────────────────┐
│                  Python 后端 (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐ │
│  │ 视频下载器   │  │ 字幕处理器   │  │ 视频处理器 (FFmpeg)  │ │
│  │ - YouTube   │  │ - Whisper   │  │ - 重复播放           │ │
│  │ - yt-dlp    │  │ - SRT/VTT   │  │ - 字幕嵌入           │ │
│  └─────────────┘  └─────────────┘  └──────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  任务队列 (SQLite)       │   临时文件存储                     │
│  - 任务创建              │   - 下载的视频                     │
│  - 状态追踪              │   - 处理后的视频                   │
│  - 进度更新              │   - 自动清理                       │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **API 框架** | FastAPI | 现代、高性能 Python Web 框架 |
| **服务器** | Uvicorn | ASGI 服务器 |
| **数据验证** | Pydantic | 类型安全的数据模型 |
| **视频下载** | yt-dlp | YouTube 视频下载 |
| **视频处理** | FFmpeg | 专业视频编辑工具 |
| **AI 字幕** | faster-whisper | 高效的语音识别 |
| **任务队列** | SQLite | 轻量级数据库 |
| **调度器** | APScheduler | Python 定时任务 |

---

## 🔧 核心模块详解

### 1. API 模块 (`src/api/`)

**功能**: 提供 REST API 接口

**端点**:
- `GET /api/v1/sources` - 获取视频源列表
- `GET /api/v1/sources/{id}/videos` - 获取视频列表
- `POST /api/v1/tasks` - 创建下载任务
- `GET /api/v1/tasks` - 查询任务列表
- `GET /api/v1/tasks/{id}` - 查询任务详情
- `GET /api/v1/tasks/{id}/download` - 下载处理后的视频

**特性**:
- 自动生成 API 文档 (Swagger UI)
- 请求验证 (Pydantic)
- 异常处理
- CORS 支持

### 2. 核心模块 (`src/core/`)

#### 2.1 配置管理 (`config.py`)
- 使用 Pydantic Settings
- 类型安全
- 环境变量支持
- 默认值配置

#### 2.2 下载器 (`downloader.py`)
```python
# 主要功能
- 视频信息获取
- 视频下载
- 格式选择
- 字幕下载
```

#### 2.3 任务管理器 (`task_manager.py`)
```python
# 任务状态
- pending    # 等待处理
- downloading # 下载中
- processing  # 处理中
- completed   # 已完成
- failed      # 失败
- cancelled   # 已取消
```

### 3. 视频源模块 (`src/sources/`)

**设计模式**: 策略模式 + 适配器模式

```python
# 抽象基类
class VideoSource(ABC):
    @abstractmethod
    async def get_latest_videos(limit): ...

    @abstractmethod
    async def get_video_url(video_id): ...
```

**已实现源**:
- CNN10
- BBC Learning English
- VOA Learning English

**扩展方式**: 继承 `VideoSource` 实现新源

### 4. 处理器模块 (`src/processors/`)

#### 4.1 字幕处理器 (`subtitle.py`)

```python
# 主要功能
1. 从视频提取音频
2. Whisper AI 语音识别
3. 生成 SRT/VTT 字幕
4. 下载已有字幕（YouTube）
```

**Whisper 模型选择**:
| 模型 | 速度 | 内存 | 质量 |
|------|------|------|------|
| tiny | 最快 | ~1GB | 基础 |
| base | 快 | ~1GB | 良好 |
| small | 中等 | ~2GB | 很好 |
| medium | 慢 | ~5GB | 优秀 |
| large | 最慢 | ~10GB | 最佳 |

#### 4.2 FFmpeg 处理器 (`ffmpeg.py`)

```python
# 功能清单
- 硬字幕嵌入（烧录到视频）
- 软字幕嵌入（独立字幕流）
- 视频拼接
- 速度调整
- 格式转换
- 片段提取
```

#### 4.3 学习模式处理器 (`learning_modes.py`)

**4种学习模式**:

| 模式 | 处理 | 适用人群 |
|------|------|----------|
| **original** | 无处理 | 仅需下载 |
| **with_subtitle** | +AI字幕 | 中级学习者 |
| **repeat_twice** | 播放2遍（第2遍带字幕） | 测试理解力 |
| **slow** | 0.75x速度+字幕 | 初学者 |

---

## 🔄 工作流程

### 完整处理流程

```
1. 用户发起请求
   ↓
2. API 接收请求 → 创建任务 → 返回任务ID
   ↓
3. 后台处理开始
   ├─ 下载视频 (yt-dlp)
   │   ↓
   ├─ 提取音频 (FFmpeg)
   │   ↓
   ├─ 生成字幕 (Whisper) [可选]
   │   ↓
   ├─ 应用学习模式
   │   ├─ 原始: 无处理
   │   ├─ 带字幕: 嵌入字幕
   │   ├─ 重复: 拼接2次
   │   └─ 慢速: 调速+字幕
   │   ↓
   └─ 保存处理后的视频
       ↓
4. 更新任务状态为 completed
   ↓
5. 用户下载处理后的视频
   ↓
6. 24小时后自动清理临时文件
```

### 状态转换图

```
pending → downloading → processing → completed
   ↓           ↓            ↓
failed ← ─ ─ ─ ┴ ─ ─ ─ ─ ─ ┘
```

---

## 📊 数据模型

### Task (任务)

```python
@dataclass
class Task:
    id: str                      # UUID
    user_id: str                 # 用户ID
    source_id: str               # 视频源ID (cnn10, bbc_learning, etc.)
    video_id: str                # 视频ID
    video_url: str               # 视频URL
    video_title: str             # 视频标题
    status: TaskStatus           # 任务状态
    processing_mode: ProcessingMode  # 处理模式
    progress: int                # 进度 (0-100)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    output_file: Optional[str]   # 输出文件路径
    subtitle_file: Optional[str] # 字幕文件路径
    error_message: Optional[str]
```

### VideoInfo (视频信息)

```python
@dataclass
class VideoInfo:
    id: str
    title: str
    url: str
    description: str
    duration: int                # 秒
    thumbnail: Optional[str]
    uploader: Optional[str]
    upload_date: Optional[str]
    view_count: int
```

---

## ⚙️ 配置说明

### config.env 关键配置

```bash
# API 设置
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your-secret-key

# 下载设置
MAX_VIDEOS_TO_DOWNLOAD=1
MAX_RESOLUTION=720
MAX_CONCURRENT_TASKS=2

# Whisper 设置
WHISPER_MODEL=base              # tiny, base, small, medium, large
WHISPER_LANGUAGE=en

# 任务管理
TASK_RETENTION_HOURS=24         # 保留已完成任务的时间

# 路径设置
DATA_DIR=./data
TEMP_DIR=./data/temp
LOG_DIR=./log
```

---

## 🚀 部署指南

### 开发环境

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install faster-whisper  # 可选

# 2. 配置
cp config/config.env.example config/config.env

# 3. 测试
python test_api.py

# 4. 启动
python server.py
```

### 生产环境

```bash
# 使用 systemd (Linux)
# /etc/systemd/system/cnnvideo.service
[Unit]
Description=SmartNews Learn API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/smartnews-learn
ExecStart=/path/to/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# 启动服务
sudo systemctl start cnnvideo
sudo systemctl enable cnnvideo
```

### Docker 部署 (未来)

```dockerfile
# Dockerfile (示例)
FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0"]
```

---

## 📈 性能优化

### VPS 资源优化

| 配置 | 小型VPS (2GB) | 中型VPS (4GB) | 大型VPS (8GB+) |
|------|---------------|---------------|----------------|
| **Whisper模型** | tiny | base/small | medium/large |
| **并发任务** | 1 | 2 | 4+ |
| **视频分辨率** | 480p | 720p | 1080p |

### 优化建议

1. **使用 faster-whisper** (比原版快4倍，内存省4倍)
2. **限制并发** (`MAX_CONCURRENT_TASKS=1`)
3. **选择小模型** (`WHISPER_MODEL=tiny`)
4. **定期清理** (自动清理24小时前的任务)
5. **使用 CDN** (如果面向多用户)

---

## 🔐 安全考虑

### 当前实现

- ✅ 输入验证 (Pydantic)
- ✅ SQL 注入防护 (参数化查询)
- ✅ 路径遍历防护
- ⚠️ 简单的用户ID (Header: X-User-Id)

### 生产环境建议

```python
# 添加认证
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/tasks")
async def create_task(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # 验证 token
    verify_token(credentials.credentials)
    ...
```

---

## 🧪 测试

### 运行测试

```bash
# 快速测试
python test_api.py

# 单元测试 (需安装 pytest)
pytest tests/

# 带覆盖率
pytest --cov=src tests/
```

### API 测试

使用 Swagger UI:
1. 启动服务: `python server.py`
2. 打开浏览器: http://localhost:8000/docs
3. 测试各个接口

---

## 📚 扩展开发

### 添加新视频源

```python
# src/sources/my_source.py
from .base import VideoSource, SourceInfo, VideoPreview

class MyVideoSource(VideoSource):
    @property
    def info(self) -> SourceInfo:
        return SourceInfo(
            id="my_source",
            name="My Video Source",
            description="Description here",
            url="https://example.com",
            min_tier=UserTier.FREE,
        )

    async def get_latest_videos(self, limit: int) -> List[VideoPreview]:
        # 实现获取视频逻辑
        ...

# 注册到 youtube.py 的 YOUTUBE_SOURCES
YOUTUBE_SOURCES["my_source"] = MyVideoSource
```

### 添加新学习模式

```python
# src/processors/learning_modes.py
class LearningMode(str, Enum):
    # ... existing modes ...
    MY_MODE = "my_mode"

def _process_my_mode(self, video_path, output_path, ...):
    # 实现自定义处理逻辑
    ...
```

---

## 🐛 故障排查

### 常见问题

**1. FFmpeg not found**
```bash
# 安装 FFmpeg
# Windows: https://www.gyan.dev/ffmpeg/builds/
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

**2. faster-whisper 安装失败**
```bash
pip install --upgrade pip
pip install faster-whisper --no-cache-dir
```

**3. 端口被占用**
```bash
# 修改端口
# config/config.env
API_PORT=8001
```

**4. 内存不足**
```bash
# 使用更小的 Whisper 模型
WHISPER_MODEL=tiny
MAX_CONCURRENT_TASKS=1
```

---

## 📞 支持

- **GitHub Issues**: https://github.com/znhskzj/smartnews-learn/issues
- **Email**: admin@zhurong.link
- **文档**: README.md, QUICKSTART.md, EXAMPLES.md

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**最后更新**: 2024-12-05
**版本**: 2.0.0
**维护者**: SmartNews Learn Team
