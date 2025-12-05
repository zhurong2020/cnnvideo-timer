# Legacy Code

This directory contains the original CNN Video Timer implementation (v1.x) which has been superseded by the new SmartNews Learn API architecture (v2.0+).

## What's in here?

- `main.py` - Original CLI entry point with scheduler
- `config_loader.py` - Old configuration system (replaced by `src/core/config.py`)
- `video_downloader.py` - Original downloader (replaced by `src/core/downloader.py`)
- `downloader_checker.py` - Old download checker
- `metadata_manager.py` - Old metadata management
- `link_extractor.py` - Original link extraction
- `notifier.py` - Email notification system
- `scheduler.py` - APScheduler-based job scheduling
- `utils.py` - Various utility functions
- `youtube_metadata_checker.py` - Old YouTube metadata checking

## Why deprecated?

The v1.x architecture was a monolithic CLI tool. Version 2.0 refactored the codebase into a modern microservices-style API with:

- **RESTful API** (`src/api/`) - FastAPI-based web API
- **Core Services** (`src/core/`) - Business logic layer
- **Video Sources** (`src/sources/`) - Multi-source video adapters
- **Processors** (`src/processors/`) - Video/subtitle processing
- **Storage** (`src/storage/`) - Cloud storage integrations

## Should I use these files?

**No.** Use the new API server (`server.py` and the `src/api/`, `src/core/`, etc. modules).

These files are kept for reference and potential migration of any missing features.

## When will these be removed?

After confirming all functionality has been migrated to v2.0 architecture, these files will be deleted in a future release (v2.1 or v3.0).

---

**Last Updated**: 2024-12-05
**Deprecated Since**: v2.0.0
