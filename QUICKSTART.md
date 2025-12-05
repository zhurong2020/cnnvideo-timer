# Quick Start Guide

Get SmartNews Learn up and running in 5 minutes!

## Installation

### 1. Install Python & FFmpeg

**Windows:**
```bash
# Download Python from python.org
# Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/
# Add ffmpeg to PATH
```

**Linux:**
```bash
sudo apt install python3 python3-venv ffmpeg
```

**Mac:**
```bash
brew install python ffmpeg
```

### 2. Clone & Setup

```bash
# Clone repository
git clone https://github.com/znhskzj/smartnews-learn.git
cd smartnews-learn

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install Whisper for AI subtitles
pip install faster-whisper
```

### 3. Configure

```bash
# Copy config template
cp config/config.env.example config/config.env

# Edit config (optional for testing)
# nano config/config.env
```

## Usage

### Option 1: CLI (Command Line)

```bash
# Download latest CNN10 video
python main.py

# Download with options
python main.py --max-videos 3

# Start scheduler (runs every 12 hours)
python main.py --schedule
```

### Option 2: API Server

```bash
# Start server
python server.py

# In another terminal, test the API:
curl http://localhost:8000/health

# View API docs
# Open browser: http://localhost:8000/docs
```

## Test the API

### 1. Get Available Sources

```bash
curl http://localhost:8000/api/v1/sources
```

Response:
```json
{
  "sources": [
    {
      "id": "cnn10",
      "name": "CNN 10",
      "description": "10-minute daily news...",
      "url": "https://www.youtube.com/@CNN10/videos",
      "min_tier": "free"
    }
  ]
}
```

### 2. Get Latest Videos

```bash
curl "http://localhost:8000/api/v1/sources/cnn10/videos?limit=3"
```

### 3. Create a Download Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-User-Id: testuser" \
  -d '{
    "source_id": "cnn10",
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "processing_mode": "with_subtitle"
  }'
```

Response:
```json
{
  "id": "abc-123-def",
  "status": "pending",
  "progress": 0,
  "video_title": "CNN 10 - December 4, 2024",
  "processing_mode": "with_subtitle"
}
```

### 4. Check Task Status

```bash
# Get task ID from previous response
curl http://localhost:8000/api/v1/tasks/abc-123-def
```

### 5. Download Processed Video

```bash
# When status is "completed"
curl http://localhost:8000/api/v1/tasks/abc-123-def/download -o video.mp4
```

## Processing Modes

| Mode | Description | Best For |
|------|-------------|----------|
| `original` | Keep as-is | Just downloading |
| `with_subtitle` | Add AI subtitles | Reading while listening |
| `repeat_twice` | Play 2x (2nd with subs) | Testing comprehension |
| `slow` | 0.75x speed + subs | Beginners |

## Troubleshooting

### "FFmpeg not found"
```bash
# Windows: Add ffmpeg to PATH
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

### "faster-whisper not installed"
```bash
pip install faster-whisper
```

### Port 8000 already in use
```bash
# Edit config/config.env
API_PORT=8001

# Or specify when running
python server.py --port 8001
```

## Next Steps

- Read full [README.md](README.md) for details
- Check [API Documentation](http://localhost:8000/docs) after starting server
- Integrate with WordPress (see README.md)

## Need Help?

- GitHub Issues: https://github.com/znhskzj/smartnews-learn/issues
- Email: admin@zhurong.link
