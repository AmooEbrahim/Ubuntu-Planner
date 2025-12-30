# Port Configuration Guide

Both the backend API port and frontend port are now fully customizable via the `.env` file.

## Configuration

Edit the `.env` file in the project root:

```bash
# Application Ports
API_PORT=1717              # Backend API port
FRONTEND_PORT=1718         # Frontend dev server port

# Frontend Environment (must match API_PORT)
VITE_API_URL=http://localhost:1717
```

## Important Notes

1. **VITE_API_URL must match API_PORT**:
   - If you change `API_PORT` to `8080`, also change `VITE_API_URL` to `http://localhost:8080`

2. **Restart required**:
   - After changing ports in `.env`, restart both services
   - The development scripts will automatically use the new ports

3. **CORS Configuration**:
   - The backend automatically allows CORS from the frontend port specified in `.env`
   - No manual CORS configuration needed

## How It Works

### Backend (API_PORT)
- Read by `backend/run-dev.sh` from `.env`
- Used by uvicorn to bind the server
- Default: 1717

### Frontend (FRONTEND_PORT)
- Read by `vite.config.js` from `.env`
- Used by Vite dev server
- Default: 1718

### API Communication (VITE_API_URL)
- Read by `frontend/src/services/api.js`
- Used by Axios to connect to backend
- Must match the backend API_PORT

## Examples

### Example 1: Use Default Ports
```bash
API_PORT=1717
FRONTEND_PORT=1718
VITE_API_URL=http://localhost:1717
```

### Example 2: Custom Ports
```bash
API_PORT=8080
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:8080
```

### Example 3: Backend on Different Machine
```bash
API_PORT=1717
FRONTEND_PORT=1718
VITE_API_URL=http://192.168.1.100:1717
```

## Changing Ports

1. Edit `.env` file:
   ```bash
   nano .env
   ```

2. Update the three variables:
   ```
   API_PORT=<your-backend-port>
   FRONTEND_PORT=<your-frontend-port>
   VITE_API_URL=http://localhost:<your-backend-port>
   ```

3. Restart services:
   ```bash
   ./start-dev.sh
   ```

## Verification

After starting the services, verify they're running on the correct ports:

```bash
# Check backend
curl http://localhost:<API_PORT>/health

# Check frontend
# Open browser to http://localhost:<FRONTEND_PORT>
```

## Troubleshooting

### Port Already in Use
If you get "port already in use" error:
```bash
# Find what's using the port (example for port 1717)
lsof -i :1717

# Kill the process
kill -9 <PID>
```

### Frontend Can't Connect to Backend
- Check that `VITE_API_URL` matches `API_PORT`
- Restart frontend after changing `.env` (Vite needs restart for env changes)
- Check CORS is allowing your frontend port (should be automatic)

### systemd Service
If you're using the systemd service, update `ubuntu-planner.service` to use the port from `.env` or hardcode your preferred port in the service file.
