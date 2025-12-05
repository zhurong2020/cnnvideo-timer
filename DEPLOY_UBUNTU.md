# Ubuntu VPS 部署指南

本指南帮助您将 SmartNews Learn 部署到 Ubuntu VPS 服务器。

## 目录

1. [系统要求](#系统要求)
2. [快速部署](#快速部署)
3. [详细步骤](#详细步骤)
4. [配置说明](#配置说明)
5. [使用 Systemd 守护进程](#使用-systemd-守护进程)
6. [使用 Nginx 反向代理](#使用-nginx-反向代理)
7. [OneDrive 集成](#onedrive-集成)
8. [故障排除](#故障排除)

---

## 系统要求

### 最低配置
- **OS**: Ubuntu 20.04+ (推荐 22.04 LTS)
- **CPU**: 2核
- **RAM**: 2GB (建议 4GB 用于 Whisper AI)
- **存储**: 20GB
- **Python**: 3.8+

### 推荐配置
- **CPU**: 4核 (用于 faster-whisper)
- **RAM**: 4GB+
- **存储**: 50GB+ (用于临时视频处理)

---

## 快速部署

```bash
# 1. 下载项目
cd /opt
git clone https://github.com/znhskzj/smartnews-learn.git
cd smartnews-learn

# 2. 运行安装脚本
chmod +x install.sh
./install.sh

# 3. 配置环境变量
nano config/config.env

# 4. 启动服务
python server.py
```

---

## 详细步骤

### 1. 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. 安装 Python 3.8+

```bash
# 检查 Python 版本
python3 --version

# 如果版本低于 3.8，安装新版本
sudo apt install python3.10 python3.10-venv python3-pip -y
```

### 3. 安装 FFmpeg

```bash
sudo apt install ffmpeg -y

# 验证安装
ffmpeg -version
```

### 4. 克隆项目

```bash
cd /opt
sudo git clone https://github.com/znhskzj/smartnews-learn.git
cd smartnews-learn

# 设置权限
sudo chown -R $USER:$USER /opt/smartnews-learn
```

### 5. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 6. 安装依赖

```bash
# 升级 pip
pip install --upgrade pip

# 安装核心依赖
pip install -r requirements.txt

# 可选：安装 faster-whisper (用于 AI 字幕)
pip install faster-whisper
```

### 7. 配置环境变量

```bash
# 复制配置模板
cp config/config.env.example config/config.env

# 编辑配置
nano config/config.env
```

**关键配置项：**

```env
# API 设置
API_HOST=0.0.0.0          # 允许外部访问
API_PORT=8000
DEBUG=false

# 路径设置
DATA_DIR=/opt/smartnews-learn/data
TEMP_DIR=/opt/smartnews-learn/data/temp
LOG_DIR=/opt/smartnews-learn/log

# FFmpeg (留空使用系统 PATH)
FFMPEG_PATH=

# Whisper 模型 (tiny|base|small|medium|large)
WHISPER_MODEL=base        # base 推荐用于低资源服务器

# 任务设置
MAX_CONCURRENT_TASKS=2    # 根据 VPS 资源调整
TASK_RETENTION_HOURS=24   # 保留已完成任务 24 小时

# OneDrive (通过 rclone)
ENABLE_ONEDRIVE=false
RCLONE_REMOTE=onedrive:videos
```

### 8. 创建数据目录

```bash
mkdir -p data/temp log
```

### 9. 测试安装

```bash
python test_api.py
```

应该看到所有测试通过，包括：
- ✓ 配置加载
- ✓ 视频源
- ✓ 任务管理器
- ✓ FFmpeg 可用
- ✓ Whisper 已安装

### 10. 启动服务器

```bash
# 前台运行（测试用）
python server.py

# 后台运行（使用 nohup）
nohup python server.py > log/server.log 2>&1 &

# 查看日志
tail -f log/server.log
```

---

## 配置说明

### 资源优化配置

针对低资源 VPS 的推荐配置：

```env
# 使用较小的 Whisper 模型
WHISPER_MODEL=tiny        # 或 base

# 限制并发任务
MAX_CONCURRENT_TASKS=1    # 低资源服务器设为 1

# 较低的分辨率
MAX_RESOLUTION=480        # 或 720

# 更频繁的清理
TASK_RETENTION_HOURS=12   # 12 小时后清理
```

### 高性能配置

针对高配置 VPS：

```env
WHISPER_MODEL=medium      # 或 large
MAX_CONCURRENT_TASKS=4
MAX_RESOLUTION=1080
TASK_RETENTION_HOURS=48
```

---

## 使用 Systemd 守护进程

创建一个 systemd 服务，让服务器开机自启动。

### 1. 创建服务文件

```bash
sudo nano /etc/systemd/system/smartnews-learn.service
```

### 2. 添加以下内容

```ini
[Unit]
Description=SmartNews Learn API Service
After=network.target

[Service]
Type=simple
User=your-username
Group=your-group
WorkingDirectory=/opt/smartnews-learn
Environment="PATH=/opt/smartnews-learn/venv/bin"
ExecStart=/opt/smartnews-learn/venv/bin/python server.py

# 重启策略
Restart=always
RestartSec=10

# 日志
StandardOutput=append:/opt/smartnews-learn/log/server.log
StandardError=append:/opt/smartnews-learn/log/error.log

[Install]
WantedBy=multi-user.target
```

**注意**：将 `your-username` 和 `your-group` 替换为您的用户名和组。

### 3. 启动服务

```bash
# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start smartnews-learn

# 设置开机自启
sudo systemctl enable smartnews-learn

# 查看状态
sudo systemctl status smartnews-learn

# 查看日志
sudo journalctl -u smartnews-learn -f
```

### 4. 常用命令

```bash
# 停止服务
sudo systemctl stop smartnews-learn

# 重启服务
sudo systemctl restart smartnews-learn

# 查看日志
sudo journalctl -u smartnews-learn --since today
```

---

## 使用 Nginx 反向代理

将 API 通过 Nginx 暴露，支持 HTTPS 和域名访问。

### 1. 安装 Nginx

```bash
sudo apt install nginx -y
```

### 2. 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/smartnews-learn
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名或 IP

    # 日志
    access_log /var/log/nginx/smartnews-learn-access.log;
    error_log /var/log/nginx/smartnews-learn-error.log;

    # API 代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置（用于长时间视频处理）
        proxy_read_timeout 600s;
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
    }

    # 文件上传大小限制
    client_max_body_size 500M;
}
```

### 3. 启用站点

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/smartnews-learn /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4. 配置 HTTPS（可选但推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## OneDrive 集成

使用 rclone 将处理后的视频上传到 OneDrive。

### 1. 安装 rclone

```bash
curl https://rclone.org/install.sh | sudo bash
```

### 2. 配置 OneDrive

```bash
rclone config
```

按照提示配置：
1. 选择 `n` (新建远程)
2. 名称：`onedrive`
3. 类型：选择 `onedrive`
4. 按照提示完成 OAuth 授权

### 3. 测试连接

```bash
# 列出 OneDrive 文件
rclone ls onedrive:

# 创建测试目录
rclone mkdir onedrive:videos
```

### 4. 在配置中启用

编辑 `config/config.env`：

```env
ENABLE_ONEDRIVE=true
RCLONE_REMOTE=onedrive:videos
```

### 5. 使用示例

处理完成的视频会自动上传到 OneDrive（如果在任务中启用）。

---

## 防火墙配置

### UFW (推荐)

```bash
# 启用 UFW
sudo ufw enable

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 如果直接暴露 API（不推荐）
sudo ufw allow 8000/tcp

# 查看状态
sudo ufw status
```

---

## 故障排除

### 1. FFmpeg 未找到

```bash
# 检查 FFmpeg 是否安装
which ffmpeg

# 重新安装
sudo apt install --reinstall ffmpeg
```

### 2. 内存不足

Whisper AI 需要较多内存。如果遇到内存问题：

```env
# 使用更小的模型
WHISPER_MODEL=tiny

# 减少并发任务
MAX_CONCURRENT_TASKS=1
```

或者添加 swap：

```bash
# 创建 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. 端口占用

```bash
# 检查端口占用
sudo lsof -i :8000

# 或使用其他端口
# 在 config/config.env 中修改：
API_PORT=8001
```

### 4. 权限问题

```bash
# 确保目录权限正确
sudo chown -R $USER:$USER /opt/smartnews-learn
chmod -R 755 /opt/smartnews-learn
```

### 5. 查看日志

```bash
# 应用日志
tail -f log/server.log

# Systemd 日志
sudo journalctl -u smartnews-learn -f

# Nginx 日志
sudo tail -f /var/log/nginx/smartnews-learn-error.log
```

### 6. Python 依赖问题

```bash
# 激活虚拟环境
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

---

## 性能监控

### 1. 安装监控工具

```bash
# htop - CPU/内存监控
sudo apt install htop -y

# iotop - 磁盘 I/O 监控
sudo apt install iotop -y

# nethogs - 网络监控
sudo apt install nethogs -y
```

### 2. 监控命令

```bash
# 实时查看资源使用
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看 Python 进程
ps aux | grep python
```

---

## 备份与恢复

### 备份

```bash
# 备份数据库
cp data/tasks.db data/tasks.db.backup

# 备份配置
cp config/config.env config/config.env.backup

# 完整备份（不包括虚拟环境）
tar -czf smartnews-learn-backup-$(date +%Y%m%d).tar.gz \
    --exclude='venv' \
    --exclude='data/temp' \
    --exclude='*.log' \
    /opt/smartnews-learn
```

### 恢复

```bash
# 解压备份
tar -xzf smartnews-learn-backup-YYYYMMDD.tar.gz -C /opt/

# 恢复数据库
cp data/tasks.db.backup data/tasks.db

# 重启服务
sudo systemctl restart smartnews-learn
```

---

## 更新部署

```bash
# 停止服务
sudo systemctl stop smartnews-learn

# 备份
cp data/tasks.db data/tasks.db.backup

# 拉取更新
git pull

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt --upgrade

# 重启服务
sudo systemctl start smartnews-learn

# 查看状态
sudo systemctl status smartnews-learn
```

---

## 安全建议

1. **使用防火墙**：只开放必要端口
2. **使用 HTTPS**：通过 Let's Encrypt 配置 SSL
3. **限制 API 访问**：配置 `API_KEY` 进行认证
4. **定期更新**：保持系统和依赖最新
5. **备份数据**：定期备份数据库和配置
6. **监控日志**：定期检查异常访问

---

## 性能优化建议

### 针对低资源 VPS

1. 使用 `tiny` 或 `base` Whisper 模型
2. 限制 `MAX_CONCURRENT_TASKS=1`
3. 降低视频分辨率 `MAX_RESOLUTION=480`
4. 启用 swap 内存
5. 定期清理临时文件

### 针对高性能 VPS

1. 使用 `medium` 或 `large` Whisper 模型
2. 增加并发任务数
3. 使用更高分辨率
4. 配置 Redis 缓存（未来版本）

---

## WordPress 集成示例

### 在 WordPress 中调用 API

```php
<?php
// WordPress 插件中调用 SmartNews Learn API

function cnn_video_timer_create_task($video_url, $mode = 'with_subtitle') {
    $api_url = 'http://your-vps-ip:8000/api/v1/tasks';

    $data = array(
        'user_id' => get_current_user_id(),
        'video_url' => $video_url,
        'processing_mode' => $mode,
    );

    $response = wp_remote_post($api_url, array(
        'body' => json_encode($data),
        'headers' => array(
            'Content-Type' => 'application/json',
        ),
    ));

    if (is_wp_error($response)) {
        return false;
    }

    $body = json_decode(wp_remote_retrieve_body($response), true);
    return $body['task_id'];
}
?>
```

---

## 相关链接

- **项目主页**: https://github.com/znhskzj/smartnews-learn
- **问题反馈**: https://github.com/znhskzj/smartnews-learn/issues
- **文档**: README.md, QUICKSTART.md, EXAMPLES.md

---

## 下一步

部署完成后，您可以：

1. 访问 API 文档：`http://your-domain.com/docs`
2. 测试 API 接口
3. 集成到 WordPress 网站
4. 配置定时任务（使用 cron）

祝您使用愉快！
