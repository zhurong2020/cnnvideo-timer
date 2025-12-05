# SmartNews Learn v2.0

**AI-Powered News Video Platform for Language Learning**

Transform news videos into personalized learning experiences with intelligent subtitles and adaptive playback modes.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Whisper](https://img.shields.io/badge/Whisper-AI-orange.svg)](https://github.com/openai/whisper)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Overview

**SmartNews Learn** is an intelligent video processing platform that helps language learners master English through authentic news content. Leveraging AI-powered subtitle generation and smart learning modes, it transforms standard news videos into optimized learning materials.

### Key Highlights

- 📺 **Multi-Source Integration** - CNN10, BBC Learning English, VOA, and custom YouTube channels
- 🤖 **AI Subtitle Generation** - Powered by faster-whisper for accurate, real-time transcription
- 🎓 **Smart Learning Modes** - Adaptive playback with repeat, slow-motion, and subtitle options
- 🔌 **RESTful API** - Seamless WordPress integration and third-party connectivity
- ⚡ **Task Queue System** - Efficient background processing with progress tracking
- 💾 **Cloud Storage Ready** - OneDrive integration via rclone (optional)

---

## ✨ Features

### 📡 Multi-Source Video Library

| Source | Description | Content Type | Tier |
|--------|-------------|--------------|------|
| **CNN10** | 10-minute daily news designed for students | Current events | Free |
| **BBC Learning English** | Educational content with clear pronunciation | Language learning | Free |
| **VOA Learning English** | Simplified news at reduced speed | Beginner-friendly | Free |
| **Custom Channels** | Any YouTube channel or playlist | Flexible | Premium |

### 🎯 Intelligent Learning Modes

Transform standard videos into optimized learning experiences:

#### 1. **Original Mode**
- Downloads video without modifications
- Preserves original quality and pacing
- Best for: Advanced learners or casual viewing

#### 2. **Subtitle Mode**
- AI-generated subtitles embedded directly into video
- Customizable font, size, and position
- Best for: Visual learners who need text support

#### 3. **Repeat Twice Mode**
- **First playback**: No subtitles (test comprehension)
- **Second playback**: With subtitles (verify understanding)
- Best for: Active learning and self-assessment

#### 4. **Slow Mode**
- 0.75x playback speed with embedded subtitles
- Clearer pronunciation and more time to read
- Best for: Beginners or challenging content

### 🔄 Processing Pipeline

```
User Request → Video Download (yt-dlp) → Audio Extraction (FFmpeg)
    → AI Transcription (Whisper) → Learning Mode Processing
    → Video Output → Optional Cloud Upload
```

### 🛠️ Technical Stack

- **Backend**: Python 3.8+, FastAPI, uvicorn
- **AI Engine**: faster-whisper (optimized Whisper implementation)
- **Video Processing**: FFmpeg, ffmpeg-python
- **Task Management**: SQLite, async task queue
- **Downloader**: yt-dlp (YouTube/web video download)
- **Optional**: rclone (OneDrive integration)

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **FFmpeg** (for video processing)
- **Git** (for cloning repository)

### Installation

#### Windows

```bash
# Clone repository
git clone https://github.com/yourusername/smartnews-learn.git
cd smartnews-learn

# Run installation script
install.bat

# Follow prompts to install dependencies
```

#### Linux/Mac

```bash
# Clone repository
git clone https://github.com/yourusername/smartnews-learn.git
cd smartnews-learn

# Run installation script
chmod +x install.sh
./install.sh

# Follow prompts to install dependencies
```

#### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install AI subtitle generation
pip install faster-whisper

# Configure
cp config/config.env.example config/config.env
nano config/config.env  # Edit with your settings
```

### First Run

```bash
# Test installation
python test_api.py

# Start API server
python server.py

# Access API documentation
# Open browser: http://localhost:8000/docs
```

---

## 📖 Usage

### Command Line Interface (CLI)

```bash
# Download latest CNN10 video with subtitles
python main.py --source cnn10 --mode with_subtitle

# Download BBC video in slow mode
python main.py --source bbc_learning --mode slow

# Schedule daily downloads
python main.py --schedule
```

### REST API

Start the API server:

```bash
python server.py
```

Access interactive documentation at `http://localhost:8000/docs`

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/sources` | List available video sources |
| `GET` | `/api/v1/sources/{id}/videos` | Preview latest videos from a source |
| `POST` | `/api/v1/tasks` | Create a new processing task |
| `GET` | `/api/v1/tasks` | List user's tasks |
| `GET` | `/api/v1/tasks/{id}` | Get task status and details |
| `GET` | `/api/v1/tasks/{id}/download` | Download processed video |
| `DELETE` | `/api/v1/tasks/{id}` | Delete a task |

#### Example: Create Processing Task

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "processing_mode": "repeat_twice"
  }'
```

### Python SDK

```python
import requests

# Get available sources
response = requests.get("http://localhost:8000/api/v1/sources")
sources = response.json()

# Create task
task_data = {
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "processing_mode": "with_subtitle"
}
response = requests.post(
    "http://localhost:8000/api/v1/tasks",
    json=task_data,
    headers={"X-User-Id": "user123"}
)
task = response.json()

# Check task status
task_id = task['task_id']
response = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}")
status = response.json()
```

---

## 🔧 Configuration

Edit `config/config.env`:

### Basic Settings

```env
# API Configuration
API_HOST=0.0.0.0          # Bind address
API_PORT=8000             # Port number
DEBUG=false               # Debug mode (true for development)

# FFmpeg (leave empty to use system PATH)
FFMPEG_PATH=

# Whisper AI Model (tiny|base|small|medium|large)
WHISPER_MODEL=base        # Smaller = faster, larger = more accurate

# Task Management
MAX_CONCURRENT_TASKS=2    # Parallel processing limit
TASK_RETENTION_HOURS=24   # Keep completed tasks for X hours
```

### Performance Tuning

**Low-Resource VPS (1-2GB RAM):**
```env
WHISPER_MODEL=tiny
MAX_CONCURRENT_TASKS=1
MAX_RESOLUTION=480
```

**High-Performance Server (4GB+ RAM):**
```env
WHISPER_MODEL=base  # or small
MAX_CONCURRENT_TASKS=4
MAX_RESOLUTION=1080
```

---

## 🌐 WordPress Integration

SmartNews Learn provides a RESTful API that seamlessly integrates with WordPress.

### Installation

1. Deploy SmartNews Learn on your VPS (see [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md))
2. Install our WordPress plugin (coming soon) or use custom code
3. Configure API endpoint in WordPress settings

### Example WordPress Plugin Code

```php
<?php
/**
 * Plugin Name: SmartNews Learn Integration
 * Description: Integrate SmartNews Learn video processing
 */

function smartnews_create_task($video_url, $mode = 'with_subtitle') {
    $api_url = get_option('smartnews_api_url') . '/api/v1/tasks';
    $user_id = get_current_user_id();

    $response = wp_remote_post($api_url, array(
        'body' => json_encode(array(
            'video_url' => $video_url,
            'processing_mode' => $mode,
        )),
        'headers' => array(
            'Content-Type' => 'application/json',
            'X-User-Id' => $user_id,
        ),
    ));

    if (is_wp_error($response)) {
        return false;
    }

    return json_decode(wp_remote_retrieve_body($response), true);
}

// Shortcode: [smartnews_video url="..."]
add_shortcode('smartnews_video', 'smartnews_video_shortcode');
?>
```

---

## 📦 Deployment

### Ubuntu VPS

Comprehensive deployment guide: [DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md)

Quick deployment:

```bash
# SSH to VPS
ssh user@your-vps-ip

# Install
cd /opt
sudo git clone https://github.com/yourusername/smartnews-learn.git
cd smartnews-learn
chmod +x install.sh
./install.sh

# Configure
nano config/config.env

# Start with systemd
sudo systemctl start smartnews-learn
sudo systemctl enable smartnews-learn
```

### Docker (Coming Soon)

```bash
docker pull smartnews/learn:latest
docker run -p 8000:8000 -v ./config:/app/config smartnews/learn
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and code snippets
- **[DEPLOY_UBUNTU.md](DEPLOY_UBUNTU.md)** - Ubuntu VPS deployment guide
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrate from development to production
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Technical architecture
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## 🎯 Use Cases

### For Language Learners

- Download daily news with accurate AI subtitles
- Practice listening with repeat-twice mode
- Build vocabulary from authentic content
- Slow down difficult segments for better comprehension

### For Educators

- Create customized learning materials
- Provide students with accessible news content
- Track student progress via API
- Integrate with LMS platforms

### For Content Creators

- Generate subtitles for YouTube videos
- Process video libraries in batch
- Offer multilingual content (future feature)
- Automate video enhancement workflows

---

## 🛠️ Development

### Project Structure

```
smartnews-learn/
├── src/
│   ├── api/              # FastAPI routes and models
│   ├── core/             # Core business logic
│   ├── sources/          # Video source adapters
│   ├── processors/       # Video and subtitle processors
│   └── storage/          # Storage management
├── config/               # Configuration files
├── data/                 # Data storage (gitignored)
├── log/                  # Application logs (gitignored)
├── tests/                # Test suite
└── docs/                 # Additional documentation
```

### Running Tests

```bash
# Run all tests
python test_api.py

# Run with pytest (if installed)
pytest tests/

# Test specific component
python -m pytest tests/test_sources.py
```

### Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🔒 Security

- API authentication via `X-User-Id` header (basic) or API keys
- HTTPS recommended for production (use Nginx + Let's Encrypt)
- Rate limiting enabled by default
- Input validation with Pydantic models
- SQL injection protection (parameterized queries)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - For groundbreaking speech recognition technology
- **faster-whisper** - For optimized Whisper implementation
- **FFmpeg** - For powerful video processing capabilities
- **FastAPI** - For modern Python web framework
- **yt-dlp** - For reliable video downloading

---

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/yourusername/smartnews-learn/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/smartnews-learn/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/smartnews-learn/discussions)

---

## 🗺️ Roadmap

### v2.1 (Q1 2025)
- [ ] WordPress plugin release
- [ ] User authentication and authorization
- [ ] OneDrive automatic upload
- [ ] Webhook support for task completion

### v2.2 (Q2 2025)
- [ ] Dual-language subtitles (EN + CN)
- [ ] Short video platform support (TikTok, Instagram)
- [ ] Subtitle translation
- [ ] Batch processing improvements

### v3.0 (Q3 2025)
- [ ] Web UI dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics
- [ ] Premium tier features
- [ ] Multi-user support with roles

---

## 💡 Why SmartNews Learn?

### Traditional Approach Problems

- ❌ Manual subtitle creation is time-consuming
- ❌ Fixed playback speed doesn't suit all learners
- ❌ No way to practice listening without subtitles first
- ❌ Limited access to quality English learning content

### SmartNews Learn Solutions

- ✅ **Automated AI Subtitles** - Generate accurate subtitles in seconds
- ✅ **Adaptive Learning Modes** - Choose what works for your level
- ✅ **Progressive Disclosure** - Test yourself before seeing answers
- ✅ **Unlimited Content** - Access news from multiple trusted sources

---

<div align="center">

**Built with ❤️ by the SmartNews Learn Team**

⭐ Star us on GitHub if this project helps you!

[Report Bug](https://github.com/yourusername/smartnews-learn/issues) ·
[Request Feature](https://github.com/yourusername/smartnews-learn/issues) ·
[Documentation](https://github.com/yourusername/smartnews-learn/wiki)

</div>
