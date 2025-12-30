#!/bin/bash
# Setup script for tray icon

echo "Setting up Ubuntu Planner tray icon..."
echo ""

# Check for system dependencies
echo "Checking system dependencies..."
if ! dpkg -l | grep -q python3-gi; then
    echo "Installing system packages..."
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
else
    echo "System packages already installed."
fi

# Create virtual environment with system site packages for GTK access
echo ""
echo "Creating virtual environment..."
python3 -m venv venv --system-site-packages

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "The tray icon will automatically start with start-dev.sh"
