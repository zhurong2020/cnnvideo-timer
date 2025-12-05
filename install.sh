#!/bin/bash
# SmartNews Learn - Installation Script for Linux/Mac

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     SmartNews Learn v2.0 - Installation Script           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is not installed!"
    echo "  Please install Python 3.8+ first"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Found Python $PYTHON_VERSION"

# Check FFmpeg
echo ""
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠ FFmpeg is not installed"
    echo "  Installing FFmpeg..."

    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            echo "✗ Could not install FFmpeg automatically"
            echo "  Please install manually: https://ffmpeg.org/download.html"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Mac
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "✗ Homebrew not found"
            echo "  Install Homebrew: https://brew.sh"
            echo "  Then run: brew install ffmpeg"
            exit 1
        fi
    fi
else
    echo "✓ FFmpeg is installed"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Optional: Install Whisper
echo ""
read -p "Install faster-whisper for AI subtitle generation? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing faster-whisper..."
    pip install faster-whisper
    echo "✓ faster-whisper installed"
else
    echo "⊘ Skipped faster-whisper installation"
    echo "  (You can install later with: pip install faster-whisper)"
fi

# Setup config
echo ""
if [ ! -f "config/config.env" ]; then
    echo "Setting up configuration..."
    cp config/config.env.example config/config.env
    echo "✓ Configuration file created: config/config.env"
    echo "  Please edit this file with your settings"
else
    echo "✓ Configuration file already exists"
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/temp log

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✓ Installation completed successfully!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit configuration (optional):"
echo "   nano config/config.env"
echo ""
echo "2. Test installation:"
echo "   source venv/bin/activate"
echo "   python test_api.py"
echo ""
echo "3. Start API server:"
echo "   python server.py"
echo ""
echo "4. Or use CLI:"
echo "   python main.py"
echo ""
echo "For documentation, see:"
echo "  - README.md      - Full documentation"
echo "  - QUICKSTART.md  - Quick start guide"
echo "  - EXAMPLES.md    - Usage examples"
echo ""
echo "API Documentation:"
echo "  http://localhost:8000/docs (after starting server)"
echo ""
