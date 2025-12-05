# Changelog

All notable changes to SmartNews Learn will be documented in this file.

## [2.0.0] - 2024-12-05

### 🎉 Major Refactor & New Features

This is a complete rewrite of the project with modern architecture and new capabilities.

### Added

#### Core Features
- ✨ **REST API Service** - FastAPI-based API for programmatic access
- 🤖 **AI Subtitle Generation** - Whisper-powered speech recognition
- 🎓 **Learning Modes** - 4 different video processing modes for language learning
  - Original (no changes)
  - With Subtitle (AI-generated subtitles)
  - Repeat Twice (play twice, second time with subtitle)
  - Slow Mode (0.75x speed with subtitle)
- 📺 **Multi-Source Support** - CNN10, BBC Learning English, VOA
- 🔄 **Task Queue System** - SQLite-based task management
- 📊 **Progress Tracking** - Real-time progress updates for tasks

#### Developer Features
- 🏗️ **Modern Architecture** - Modular, extensible design
- 🔌 **Plugin System** - Easy to add new video sources
- 📝 **Type Safety** - Pydantic models for validation
- 📚 **Auto-generated API Docs** - Swagger/OpenAPI documentation
- 🧪 **Test Suite** - Basic test coverage

#### Video Processing
- 🎬 **FFmpeg Integration** - Complete video editing capabilities
  - Subtitle embedding (hard/soft)
  - Video concatenation
  - Speed adjustment
  - Format conversion
  - Segment extraction
- 📝 **Subtitle Processing** - Multiple subtitle formats (SRT, VTT)
- 🎨 **Customizable Subtitle Styles** - Font, size, color, position

#### Storage & Management
- 💾 **SQLite Task Database** - Persistent task storage
- 🗑️ **Auto Cleanup** - Remove old tasks and temporary files
- 📁 **Organized Structure** - Clean directory layout

### Changed

- 🔄 **Complete project restructure** - From flat to modular
- ⚡ **Performance improvements** - Better resource management
- 🎯 **Simplified CLI** - More intuitive command-line interface
- 📖 **Enhanced documentation** - README, QUICKSTART, EXAMPLES
- 🔧 **Better configuration** - Pydantic-based settings management

### Removed

- ❌ **Baidu Cloud Upload** - Removed to focus on core features
- ❌ **Legacy code** - Cleaned up unused modules

### Technical Details

#### New Project Structure
```
src/
├── api/           # REST API (FastAPI)
├── core/          # Core business logic
├── sources/       # Video source adapters
├── processors/    # Video & subtitle processors
└── storage/       # Storage management
```

#### New Dependencies
- FastAPI (API framework)
- uvicorn (ASGI server)
- pydantic-settings (config management)
- faster-whisper (AI subtitles)
- ffmpeg-python (video processing)

#### API Endpoints
- `GET /api/v1/sources` - List video sources
- `GET /api/v1/sources/{id}/videos` - Get latest videos
- `POST /api/v1/tasks` - Create download task
- `GET /api/v1/tasks` - List user tasks
- `GET /api/v1/tasks/{id}` - Get task details
- `GET /api/v1/tasks/{id}/download` - Download processed video

### Migration from v1.x

**For Users:**
1. Install new dependencies: `pip install -r requirements.txt`
2. Update config file (see `config/config.env.example`)
3. Use new CLI: `python main.py` or start API: `python server.py`

**For Developers:**
- Old `video_downloader.py` → New `src/core/downloader.py`
- Old `scheduler.py` → New `src/core/scheduler.py` (legacy) or use API
- Configuration now uses Pydantic Settings

### Breaking Changes

- ⚠️ Configuration file format changed
- ⚠️ CLI arguments changed (see `python main.py --help`)
- ⚠️ Python module imports restructured
- ⚠️ Removed Baidu Cloud integration

---

## [1.x] - 2023-2024

### Previous Versions

For changelog of v1.x releases, see `docs/CHANGELOG.md` (legacy).

### Summary of v1.x Features
- Basic CNN10 video downloading
- Scheduled downloads with APScheduler
- Email notifications
- Metadata management
- Baidu Cloud upload
- Windows executable builds

---

## Future Plans

### v2.1 (Coming Soon)
- [ ] OneDrive integration (via rclone)
- [ ] User authentication & authorization
- [ ] Rate limiting
- [ ] Webhook support

### v2.2
- [ ] Short video platform support (TikTok, etc.)
- [ ] Dual-language subtitles (EN + CN)
- [ ] Subtitle translation
- [ ] Mobile app

### v3.0 (Long Term)
- [ ] Web UI dashboard
- [ ] WordPress plugin
- [ ] Distributed processing
- [ ] Cloud deployment guides
- [ ] Premium features

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Links

- **GitHub**: https://github.com/znhskzj/smartnews-learn
- **Issues**: https://github.com/znhskzj/smartnews-learn/issues
- **Documentation**: See README.md

---

[2.0.0]: https://github.com/znhskzj/smartnews-learn/releases/tag/v2.0.0
