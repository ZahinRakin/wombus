#!/bin/bash

# Wumpus World Game Runner Script
# This script provides multiple ways to run the Wumpus World game

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "Python is not installed or not in PATH"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
}

# Install dependencies if needed
install_dependencies() {
    print_info "Installing dependencies..."
    
    # Try system packages first (for Ubuntu/Debian)
    if command -v apt &> /dev/null && [ "$EUID" -eq 0 ]; then
        print_info "Installing via apt (system packages)..."
        apt update && apt install -y python3-pygame python3-numpy
        return $?
    fi
    
    # Try with --user flag first
    if [ -f "requirements.txt" ]; then
        print_info "Attempting user-level installation..."
        if $PYTHON_CMD -m pip install --user -r requirements.txt 2>/dev/null; then
            print_success "Dependencies installed in user directory"
            return 0
        fi
    fi
    
    # Try installing individual packages with --user
    print_info "Installing pygame and numpy with --user flag..."
    if $PYTHON_CMD -m pip install --user pygame numpy 2>/dev/null; then
        print_success "Dependencies installed in user directory"
        return 0
    fi
    
    # If all else fails, suggest manual installation
    print_error "Automatic installation failed. Please install manually:"
    echo "  Option 1 (Recommended): sudo apt install python3-pygame python3-numpy"
    echo "  Option 2: python3 -m pip install --user pygame numpy"
    echo "  Option 3: Create virtual environment:"
    echo "    python3 -m venv venv"
    echo "    source venv/bin/activate"
    echo "    pip install pygame numpy"
    echo ""
    echo "Then run the script again."
    return 1
}

# Check if required modules are available
check_dependencies() {
    print_info "Checking if required modules are installed..."
    
    # Check for pygame
    if ! $PYTHON_CMD -c "import pygame" 2>/dev/null; then
        print_warning "pygame not found, attempting to install..."
        install_dependencies
        return $?
    fi
    
    print_success "All required modules are available"
    return 0
}

# Display usage information
show_usage() {
    echo "🏛️  Wumpus World Game Runner 🏛️"
    echo "=================================="
    echo ""
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "MODES:"
    echo "  gui       - Run with graphical interface (default)"
    echo "  console   - Run in console mode"
    echo "  auto      - Run in autonomous mode"
    echo "  help      - Show this help message"
    echo ""
    echo "OPTIONS:"
    echo "  --world [file]    - Specify world file (default: worlds/default.txt)"
    echo "  --install         - Install dependencies before running"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                              # Run GUI mode with default world"
    echo "  $0 gui --world worlds/easy.world   # Run GUI with easy world"
    echo "  $0 console                     # Run in console mode"
    echo "  $0 auto --world worlds/hard.world  # Run autonomous mode with hard world"
    echo "  $0 --install gui               # Install deps and run GUI"
    echo ""
}

# Parse command line arguments
MODE="gui"
WORLD_FILE="worlds/default.txt"
INSTALL_DEPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        gui|console|auto)
            MODE="$1"
            shift
            ;;
        --world)
            WORLD_FILE="$2"
            shift 2
            ;;
        --install)
            INSTALL_DEPS=true
            shift
            ;;
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_info "Starting Wumpus World Game..."
    
    # Check Python availability
    check_python
    
    # Install dependencies if requested or if missing
    if [ "$INSTALL_DEPS" = true ]; then
        install_dependencies
    else
        # Auto-check and install if missing
        check_dependencies
        if [ $? -ne 0 ]; then
            print_error "Failed to install dependencies"
            exit 1
        fi
    fi
    
    # Check if world file exists
    if [ ! -f "$WORLD_FILE" ]; then
        print_warning "World file '$WORLD_FILE' not found, using default"
        WORLD_FILE="worlds/default.txt"
    fi
    
    print_info "Mode: $MODE"
    print_info "World: $WORLD_FILE"
    
    # Run the appropriate mode
    case $MODE in
        gui)
            print_info "Launching GUI mode..."
            $PYTHON_CMD -m src.game.wumpus
            ;;
        console)
            print_info "Launching console mode..."
            $PYTHON_CMD play_wumpus.py
            ;;
        auto)
            print_info "Launching autonomous mode..."
            $PYTHON_CMD -m src.game.wumpus --world "$WORLD_FILE"
            ;;
        *)
            print_error "Invalid mode: $MODE"
            show_usage
            exit 1
            ;;
    esac
    
    print_success "Game finished!"
}

# Run main function
main "$@"
