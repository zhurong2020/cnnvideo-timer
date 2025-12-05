# Windows 到 Ubuntu VPS 迁移指南

本指南帮助您将在 Windows 开发环境中测试好的 SmartNews Learn 项目迁移到 Ubuntu VPS 生产环境。

## 📋 迁移前检查清单

在 Windows 环境中确认以下内容：

- [ ] 所有测试通过（运行 `python test_api.py`）
- [ ] 配置文件已正确设置（`config/config.env`）
- [ ] FFmpeg 和 faster-whisper 工作正常
- [ ] Git 仓库已提交所有更改

## 🚀 快速迁移步骤

### 1. 在 Windows 上准备代码

```bash
# 确保所有更改已提交
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### 2. 在 Ubuntu VPS 上部署

```bash
# SSH 登录 VPS
ssh user@your-vps-ip

# 克隆项目
cd /opt
sudo git clone https://github.com/znhskzj/smartnews-learn.git
cd smartnews-learn

# 设置权限
sudo chown -R $USER:$USER /opt/smartnews-learn

# 运行安装脚本
chmod +x install.sh
./install.sh
```

### 3. 配置环境变量

```bash
# 编辑配置文件
nano config/config.env
```

**关键配置更改（Windows → Ubuntu）：**

```env
# Windows 路径 → Ubuntu 路径
FFMPEG_PATH=                          # 留空，使用系统 PATH
DATA_DIR=/opt/smartnews-learn/data     # 绝对路径
TEMP_DIR=/opt/smartnews-learn/data/temp
LOG_DIR=/opt/smartnews-learn/log

# API 设置
API_HOST=0.0.0.0                      # 允许外部访问
API_PORT=8000
DEBUG=false                           # 生产环境关闭调试
```

### 4. 测试部署

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python test_api.py
```

### 5. 启动服务

```bash
# 使用 systemd（推荐）
sudo systemctl start smartnews-learn
sudo systemctl enable smartnews-learn

# 或使用 nohup（临时）
nohup python server.py > log/server.log 2>&1 &
```

## 📊 配置对比表

| 配置项 | Windows 开发环境 | Ubuntu 生产环境 |
|--------|------------------|-----------------|
| FFmpeg 路径 | `C:/tools/ffmpeg.exe` | 留空（系统 PATH） |
| 数据目录 | `./data` | `/opt/smartnews-learn/data` |
| API Host | `127.0.0.1` | `0.0.0.0` |
| Debug 模式 | `true` | `false` |
| Whisper 模型 | `base` | `tiny` 或 `base` (取决于资源) |
| 并发任务 | `2` | `1-2` (取决于资源) |

## 🔧 平台差异处理

### 路径分隔符

代码已使用 `pathlib.Path`，自动处理平台差异：

```python
# ✓ 跨平台兼容
from pathlib import Path
config_path = Path("config") / "config.env"

# ✗ 不推荐
config_path = "config\\config.env"  # 仅 Windows
```

### 文件权限

Ubuntu 需要设置正确的文件权限：

```bash
# 确保目录可写
chmod 755 /opt/smartnews-learn
chmod -R 755 /opt/smartnews-learn/data
chmod -R 755 /opt/smartnews-learn/log
```

### 系统服务

Windows 使用后台进程，Ubuntu 使用 systemd：

```bash
# Ubuntu - 创建 systemd 服务
sudo nano /etc/systemd/system/smartnews-learn.service
```

参见 [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md) 的完整配置。

## 🔒 安全注意事项

### Windows 开发环境
- API 通常绑定到 `127.0.0.1`（仅本地访问）
- 调试模式开启，显示详细错误
- 防火墙可能允许所有端口

### Ubuntu 生产环境
- API 绑定到 `0.0.0.0`（允许外部访问）
- 调试模式关闭
- 配置防火墙仅允许必要端口
- 使用 Nginx 反向代理
- 配置 HTTPS（推荐）

```bash
# Ubuntu 防火墙配置
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
```

## 📦 依赖安装对比

### Windows

```bash
# Windows 使用 pip 直接安装
pip install -r requirements.txt
pip install faster-whisper
```

### Ubuntu

```bash
# Ubuntu 先安装系统依赖
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg -y

# 然后在虚拟环境中安装 Python 包
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install faster-whisper
```

## 🎯 性能优化建议

### 根据 VPS 资源调整配置

**1GB RAM VPS：**
```env
WHISPER_MODEL=tiny
MAX_CONCURRENT_TASKS=1
MAX_RESOLUTION=480
TASK_RETENTION_HOURS=12
```

**2GB RAM VPS：**
```env
WHISPER_MODEL=base
MAX_CONCURRENT_TASKS=1
MAX_RESOLUTION=720
TASK_RETENTION_HOURS=24
```

**4GB+ RAM VPS：**
```env
WHISPER_MODEL=base  # 或 small
MAX_CONCURRENT_TASKS=2
MAX_RESOLUTION=720  # 或 1080
TASK_RETENTION_HOURS=48
```

## 🔍 故障排除

### 问题 1: 导入错误

**Windows 环境：**
```python
# Windows 对大小写不敏感
from src.Core.Config import get_settings  # 可以工作
```

**Ubuntu 环境：**
```python
# Ubuntu 对大小写敏感
from src.core.config import get_settings  # 正确
```

**解决方案：** 确保所有导入使用正确的大小写。

### 问题 2: 行尾符差异

Git 在 Windows 和 Linux 之间可能转换行尾符。

```bash
# 在 Ubuntu 上，如果脚本无法执行：
dos2unix install.sh
chmod +x install.sh
```

或在 `.gitattributes` 中配置：
```
*.sh text eol=lf
*.py text eol=lf
```

### 问题 3: FFmpeg 未找到

**Windows：** 手动下载并配置路径
**Ubuntu：** 使用包管理器安装

```bash
# Ubuntu
sudo apt install ffmpeg -y

# 验证
which ffmpeg
ffmpeg -version
```

## 📈 监控和维护

### Windows 开发环境
- 使用任务管理器查看进程
- 手动启动/停止服务

### Ubuntu 生产环境
- 使用 `systemd` 管理服务
- 使用 `htop` 监控资源
- 配置日志轮转

```bash
# 查看服务状态
sudo systemctl status smartnews-learn

# 查看日志
sudo journalctl -u smartnews-learn -f

# 监控资源
htop
```

## 🔄 持续部署流程

### 1. 在 Windows 上开发和测试

```bash
# 开发新功能
git checkout -b feature/new-feature

# 测试
python test_api.py

# 提交
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

### 2. 合并到主分支

```bash
git checkout main
git merge feature/new-feature
git push origin main
```

### 3. 在 Ubuntu 上更新

```bash
# SSH 到 VPS
ssh user@your-vps-ip

# 停止服务
sudo systemctl stop smartnews-learn

# 拉取更新
cd /opt/smartnews-learn
git pull origin main

# 更新依赖（如果需要）
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl start smartnews-learn
```

## 📝 迁移检查清单

完成以下检查后，迁移即成功：

- [ ] 代码已推送到 Git 仓库
- [ ] Ubuntu VPS 已安装必要系统依赖（Python, FFmpeg）
- [ ] 项目已克隆到 `/opt/smartnews-learn`
- [ ] 虚拟环境已创建并激活
- [ ] Python 依赖已安装（包括 faster-whisper）
- [ ] 配置文件已调整为生产环境设置
- [ ] 测试通过（`python test_api.py`）
- [ ] Systemd 服务已创建并启动
- [ ] 防火墙已配置
- [ ] Nginx 反向代理已配置（可选）
- [ ] HTTPS 已配置（可选但推荐）
- [ ] OneDrive (rclone) 已配置（如果需要）
- [ ] 监控和日志已设置
- [ ] 备份策略已建立

## 🎉 迁移完成

恭喜！您的 SmartNews Learn 已成功从 Windows 开发环境迁移到 Ubuntu VPS 生产环境。

### 验证部署

访问以下 URL 验证服务：

```
http://your-vps-ip:8000/docs
```

应该看到 Swagger API 文档界面。

### 下一步

1. 配置 WordPress 集成
2. 设置定时任务（cron）
3. 配置监控和告警
4. 优化性能参数

## 📚 相关文档

- [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md) - 详细的 Ubuntu 部署指南
- [README.md](README.md) - 项目主文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [EXAMPLES.md](EXAMPLES.md) - 使用示例

---

如有问题，请访问：https://github.com/znhskzj/smartnews-learn/issues
