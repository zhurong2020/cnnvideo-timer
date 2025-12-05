# SmartNews Learn - VPS 部署检查清单

**版本**: v2.0.0
**最后更新**: 2025-12-05

本文档是部署到 Ubuntu VPS 的完整检查清单，确保按照软件工程最佳实践进行部署。

---

## 📋 部署前检查（本地）

### 1. 代码状态检查
- [ ] 所有测试通过：`pytest tests/ -v`
- [ ] 代码覆盖率 > 40%：`pytest tests/ --cov=src`
- [ ] 无未提交的更改：`git status`
- [ ] 代码已推送到远程：`git push origin main`

### 2. 安全检查
- [ ] 敏感配置不在代码库中（config.env 在 .gitignore）
- [ ] API Key 认证已实现
- [ ] CORS 配置已设置
- [ ] 异常处理不泄露敏感信息
- [ ] DEBUG 模式在生产环境关闭

### 3. 依赖检查
- [ ] requirements.txt 是最新的
- [ ] 无已知安全漏洞：`pip audit`（可选）

---

## 🚀 VPS 部署步骤

### 阶段 1：服务器准备

```bash
# 1. 连接到 VPS
ssh user@your-vps-ip

# 2. 更新系统
sudo apt update && sudo apt upgrade -y

# 3. 安装必要工具
sudo apt install -y python3 python3-pip python3-venv git ffmpeg

# 4. 验证安装
python3 --version  # >= 3.10
ffmpeg -version
git --version
```

**检查项**:
- [ ] Python >= 3.10 已安装
- [ ] FFmpeg 已安装
- [ ] Git 已安装
- [ ] 系统已更新

### 阶段 2：项目部署

```bash
# 1. 创建项目目录
sudo mkdir -p /opt/smartnews-learn
sudo chown $USER:$USER /opt/smartnews-learn

# 2. 克隆代码
cd /opt
git clone https://github.com/znhskzj/smartnews-learn.git
# 或者如果仓库名不同
# git clone https://github.com/znhskzj/cnnvideo-timer.git smartnews-learn

# 3. 创建虚拟环境
cd /opt/smartnews-learn
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 5. 安装可选的 Whisper（如果需要字幕生成）
# pip install faster-whisper  # 需要 ~2GB RAM
```

**检查项**:
- [ ] 代码已克隆
- [ ] 虚拟环境已创建
- [ ] 依赖已安装
- [ ] FFmpeg 可用

### 阶段 3：配置设置

```bash
# 1. 复制配置模板
cp config/config.env.example config/config.env

# 2. 编辑配置（重要！）
nano config/config.env
```

**必须修改的配置**:
```env
# 生产环境必须设置
DEBUG=false
API_KEY=your-very-strong-secret-key-minimum-32-characters
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 根据 VPS 资源调整
MAX_CONCURRENT_TASKS=1
WHISPER_MODEL=tiny  # 或 base（需要更多内存）

# API 设置
API_HOST=127.0.0.1  # 使用 Nginx 反向代理时
API_PORT=8000
```

**检查项**:
- [ ] config.env 已创建
- [ ] DEBUG=false
- [ ] API_KEY 已设置（非默认值）
- [ ] CORS_ORIGINS 已配置
- [ ] 资源限制已根据 VPS 配置调整

### 阶段 4：测试运行

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 运行测试
python test_api.py

# 3. 手动启动服务器测试
python server.py

# 4. 在另一个终端测试 API
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/sources

# 5. 测试认证（如果设置了 API_KEY）
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/tasks
```

**检查项**:
- [ ] test_api.py 通过
- [ ] 服务器启动无错误
- [ ] 配置验证警告已解决（无安全警告）
- [ ] /health 端点响应正常
- [ ] API 认证工作正常

### 阶段 5：Systemd 服务配置

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/smartnews-learn.service
```

**服务配置内容**:
```ini
[Unit]
Description=SmartNews Learn API Server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/smartnews-learn
Environment="PATH=/opt/smartnews-learn/venv/bin"
ExecStart=/opt/smartnews-learn/venv/bin/python server.py
Restart=always
RestartSec=10

# 安全加固
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/smartnews-learn/data /opt/smartnews-learn/log

[Install]
WantedBy=multi-user.target
```

```bash
# 2. 设置权限
sudo chown -R www-data:www-data /opt/smartnews-learn

# 3. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable smartnews-learn
sudo systemctl start smartnews-learn

# 4. 检查状态
sudo systemctl status smartnews-learn
sudo journalctl -u smartnews-learn -f  # 查看日志
```

**检查项**:
- [ ] 服务文件已创建
- [ ] 权限已设置
- [ ] 服务已启动
- [ ] 服务状态为 active (running)
- [ ] 日志无错误

### 阶段 6：Nginx 反向代理

```bash
# 1. 安装 Nginx
sudo apt install -y nginx

# 2. 创建配置
sudo nano /etc/nginx/sites-available/smartnews-learn
```

**Nginx 配置**:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # 超时设置（视频处理可能需要较长时间）
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

```bash
# 3. 启用站点
sudo ln -s /etc/nginx/sites-available/smartnews-learn /etc/nginx/sites-enabled/

# 4. 测试配置
sudo nginx -t

# 5. 重启 Nginx
sudo systemctl restart nginx
```

**检查项**:
- [ ] Nginx 已安装
- [ ] 配置文件语法正确
- [ ] 站点已启用
- [ ] Nginx 已重启

### 阶段 7：HTTPS 配置（Let's Encrypt）

```bash
# 1. 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 2. 获取证书
sudo certbot --nginx -d api.yourdomain.com

# 3. 验证自动续期
sudo certbot renew --dry-run
```

**检查项**:
- [ ] SSL 证书已获取
- [ ] HTTPS 工作正常
- [ ] 自动续期已配置

### 阶段 8：防火墙配置

```bash
# 1. 配置 UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 2. 验证规则
sudo ufw status
```

**检查项**:
- [ ] UFW 已启用
- [ ] 只开放必要端口（22, 80, 443）
- [ ] 8000 端口未对外开放（仅通过 Nginx）

---

## ✅ 部署后验证

### 功能测试
```bash
# 1. 健康检查
curl https://api.yourdomain.com/health

# 2. API 文档
# 在浏览器打开: https://api.yourdomain.com/docs

# 3. 视频源列表
curl https://api.yourdomain.com/api/v1/sources

# 4. 认证测试
curl -H "X-API-Key: your-api-key" https://api.yourdomain.com/api/v1/tasks
```

**检查项**:
- [ ] HTTPS 正常工作
- [ ] API 端点响应正常
- [ ] 认证工作正常
- [ ] 无 CORS 错误

### 安全验证
- [ ] DEBUG=false 在生产环境
- [ ] 错误消息不泄露敏感信息
- [ ] API Key 是强密码
- [ ] CORS 只允许你的域名
- [ ] 服务以非 root 用户运行

### 监控设置
```bash
# 查看服务日志
sudo journalctl -u smartnews-learn -f

# 查看应用日志
tail -f /opt/smartnews-learn/log/*.log

# 检查资源使用
htop
df -h
```

---

## 🔧 常见问题排查

### 服务无法启动
```bash
# 检查日志
sudo journalctl -u smartnews-learn -n 50

# 检查权限
ls -la /opt/smartnews-learn/

# 手动运行测试
cd /opt/smartnews-learn
source venv/bin/activate
python server.py
```

### 502 Bad Gateway
```bash
# 检查服务是否运行
sudo systemctl status smartnews-learn

# 检查端口
ss -tlnp | grep 8000

# 检查 Nginx 日志
sudo tail -f /var/log/nginx/error.log
```

### 内存不足
```bash
# 检查内存
free -h

# 考虑添加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 减少 Whisper 模型大小
# 在 config.env 中设置 WHISPER_MODEL=tiny
```

---

## 📊 部署后监控

### 日志轮转
```bash
# 创建 logrotate 配置
sudo nano /etc/logrotate.d/smartnews-learn
```

```
/opt/smartnews-learn/log/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

### 定期维护
- [ ] 每周检查日志
- [ ] 每月更新系统：`sudo apt update && sudo apt upgrade`
- [ ] 每月更新 Python 依赖：`pip install --upgrade -r requirements.txt`
- [ ] 定期备份 data/ 目录

---

## 📞 WordPress 集成

部署完成后，在 WordPress 中配置：

```php
// wp-config.php 或插件配置
define('SMARTNEWS_API_URL', 'https://api.yourdomain.com');
define('SMARTNEWS_API_KEY', 'your-api-key');
```

API 调用示例：
```php
$response = wp_remote_get('https://api.yourdomain.com/api/v1/sources', [
    'headers' => [
        'X-API-Key' => SMARTNEWS_API_KEY,
    ],
]);
```

---

## ✅ 最终检查清单

### 部署完成确认
- [ ] 服务正常运行
- [ ] HTTPS 正常工作
- [ ] API 认证正常
- [ ] 日志无错误
- [ ] 资源使用正常
- [ ] 备份策略已设置
- [ ] 监控已配置
- [ ] WordPress 集成已测试

### 文档更新
- [ ] 更新 PROJECT_STATUS.md
- [ ] 记录部署的 VPS IP/域名
- [ ] 记录重要配置

---

**部署完成！** 🎉

如有问题，参考：
- [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md) - 详细部署指南
- [SECURITY_IMPROVEMENTS.md](SECURITY_IMPROVEMENTS.md) - 安全配置说明
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - 项目状态
