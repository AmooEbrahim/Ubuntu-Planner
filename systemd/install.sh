#!/bin/bash
# Install Ubuntu Planner systemd user services

echo "Installing Ubuntu Planner systemd user services..."

# Create user systemd directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Copy service files
cp ubuntu-planner-backend.service ~/.config/systemd/user/
cp ubuntu-planner-frontend.service ~/.config/systemd/user/
cp ubuntu-planner-tray.service ~/.config/systemd/user/
cp ubuntu-planner.target ~/.config/systemd/user/

# Reload systemd user daemon
systemctl --user daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "Available services:"
echo "  - ubuntu-planner-backend.service   (Backend API)"
echo "  - ubuntu-planner-frontend.service  (Frontend Dev Server)"
echo "  - ubuntu-planner-tray.service      (System Tray Icon)"
echo "  - ubuntu-planner.target            (All services together)"
echo ""
echo "To start all services:"
echo "  systemctl --user start ubuntu-planner.target"
echo ""
echo "To start individual services:"
echo "  systemctl --user start ubuntu-planner-backend.service"
echo "  systemctl --user start ubuntu-planner-frontend.service"
echo "  systemctl --user start ubuntu-planner-tray.service"
echo ""
echo "To check status:"
echo "  systemctl --user status ubuntu-planner.target"
echo "  systemctl --user status ubuntu-planner-backend.service"
echo ""
echo "To stop all services:"
echo "  systemctl --user stop ubuntu-planner.target"
echo ""
echo "To enable auto-start on login (optional):"
echo "  systemctl --user enable ubuntu-planner.target"
echo ""
