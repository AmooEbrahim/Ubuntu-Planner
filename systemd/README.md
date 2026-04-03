# Ubuntu Planner Systemd User Services

This directory contains systemd user service files for running Ubuntu Planner as a system service.

## Files

- `ubuntu-planner-backend.service` - Backend API (FastAPI/Uvicorn)
- `ubuntu-planner-frontend.service` - Frontend development server (Vite)
- `ubuntu-planner-tray.service` - System tray icon (GTK)
- `ubuntu-planner.target` - Target to manage all services together
- `install.sh` - Installation script

## Installation

Run the installation script:

```bash
cd systemd
./install.sh
```

This will:
1. Create `~/.config/systemd/user/` directory if it doesn't exist
2. Copy all service files to the user systemd directory
3. Reload the systemd user daemon

## Usage

### Start all services together

```bash
systemctl --user start ubuntu-planner.target
```

### Start individual services

```bash
systemctl --user start ubuntu-planner-backend.service
systemctl --user start ubuntu-planner-frontend.service
systemctl --user start ubuntu-planner-tray.service
```

### Check status

```bash
# Check all services
systemctl --user status ubuntu-planner.target

# Check individual service
systemctl --user status ubuntu-planner-backend.service
systemctl --user status ubuntu-planner-frontend.service
systemctl --user status ubuntu-planner-tray.service
```

### Stop services

```bash
# Stop all
systemctl --user stop ubuntu-planner.target

# Stop individual
systemctl --user stop ubuntu-planner-backend.service
```

### View logs

```bash
# View backend logs
journalctl --user -u ubuntu-planner-backend.service -f

# View frontend logs
journalctl --user -u ubuntu-planner-frontend.service -f

# View tray logs
journalctl --user -u ubuntu-planner-tray.service -f

# View all logs together
journalctl --user -u ubuntu-planner-backend.service -u ubuntu-planner-frontend.service -u ubuntu-planner-tray.service -f
```

### Enable auto-start on login (Optional)

If you want the services to start automatically when you log in:

```bash
systemctl --user enable ubuntu-planner.target
```

To disable auto-start:

```bash
systemctl --user disable ubuntu-planner.target
```

### Restart services

```bash
# Restart all
systemctl --user restart ubuntu-planner.target

# Restart individual
systemctl --user restart ubuntu-planner-backend.service
```

## Service Dependencies

- Backend starts first (depends on MySQL)
- Frontend starts after backend
- Tray icon starts after backend and graphical session

## Important Notes

1. **MySQL Dependency**: The backend service expects MySQL to be running. Make sure MySQL is started before starting the backend.

2. **Environment Variables**: All services read from `/home/ebrhaim/bin/bash/Ubuntu-Planner/.env`

3. **GTK/Tray Icon**: The tray service requires a graphical session and uses `DISPLAY=:0`. If you use a different display, you may need to modify the service file.

4. **Development Mode**: These services run in development mode:
   - Backend: Uvicorn without `--reload` (for production stability)
   - Frontend: Vite dev server with hot reload

5. **User Services**: These are user services (`systemctl --user`), not system services. They run under your user account and don't require sudo.

## Troubleshooting

### Services fail to start

Check the logs:
```bash
journalctl --user -u ubuntu-planner-backend.service -n 50
```

### Tray icon doesn't appear

Make sure:
1. You're in a graphical session
2. DISPLAY environment variable is set correctly in the service file
3. The tray icon venv is properly set up

### Backend can't connect to database

Ensure MySQL is running:
```bash
sudo systemctl status mysql
```

### After making changes to service files

Reload the daemon and restart services:
```bash
systemctl --user daemon-reload
systemctl --user restart ubuntu-planner.target
```

## Manual Installation

If you prefer to install manually:

```bash
# Copy service files
cp *.service *.target ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload
```

## Uninstallation

```bash
# Stop all services
systemctl --user stop ubuntu-planner.target

# Disable auto-start if enabled
systemctl --user disable ubuntu-planner.target

# Remove service files
rm ~/.config/systemd/user/ubuntu-planner-*.service
rm ~/.config/systemd/user/ubuntu-planner.target

# Reload daemon
systemctl --user daemon-reload
```
