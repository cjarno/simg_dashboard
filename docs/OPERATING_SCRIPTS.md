# Operating Scripts Documentation

This document describes the operational scripts for the SIMG Dashboard application.

## Overview

The SIMG Dashboard uses helper scripts to manage server lifecycle operations. These scripts are designed to:

- Avoid port conflicts
- Provide consistent startup procedures
- Simplify development workflows

## Scripts Location

```
simg_dashboard/
├── start.sh      # Start the server
├── stop.sh       # Stop the server
└── docs/
    └── OPERATING_SCRIPTS.md  # This file
```

## start.sh

### Purpose
Starts the SIMG Dashboard server in background mode with proper error handling.

### How It Works
1. Kills any existing process on port 8004
2. Waits 2 seconds for the port to be released
3. Starts uvicorn in background mode
4. Redirects output to `uvicorn.log`

### Usage

```bash
cd /c/Users/cjarn/VIBE/simg_dashboard
./start.sh
```

### Output
After running, you'll see:
```
Server started on port 8004
Logs available at: /c/Users/cjarn/VIBE/simg_dashboard/uvicorn.log
```

### Accessing the Application

- **Frontend**: http://localhost:8004/frontend/
- **API Docs**: http://localhost:8004/docs
- **Health Check**: http://localhost:8004/api/v1/health
- **Logs**: `/c/Users/cjarn/VIBE/simg_dashboard/uvicorn.log`

## stop.sh

### Purpose
Stops the SIMG Dashboard server by killing processes on port 8004.

### Usage

```bash
cd /c/Users/cjarn/VIBE/simg_dashboard
./stop.sh
```

### Output
```
Server stopped
```

## Manual Server Control

### Starting Without Scripts

```bash
cd /c/Users/cjarn/VIBE/simg_dashboard
python -m uvicorn main:app --host 0.0.0.0 --port 8004 --log-level info --reload
```

### Stopping Server Manually

```bash
# Kill process on port 8004
fuser -k 8004/tcp

# Or kill by PID (check with: netstat -ano | findstr :8001)
taskkill /F /PID <PID>
```

## Troubleshooting

### Port Already in Use

If you get an error about the port being in use:

```bash
# Check what's using the port
netstat -ano | findstr :8004

# Kill the process
taskkill /F /PID <PID>

# Or use the stop script
./stop.sh
```

### Server Not Starting

1. Check if Python is installed:
   ```bash
   python --version
   ```

2. Check if uvicorn is installed:
   ```bash
   pip list | findstr uvicorn
   ```

3. Install dependencies if needed:
   ```bash
   pip install -r requirements.txt
   ```

### View Logs

```bash
# Live tail of logs
tail -f /c/Users/cjarn/VIBE/simg_dashboard/uvicorn.log

# Last 50 lines
tail -50 /c/Users/cjarn/VIBE/simg_dashboard/uvicorn.log
```

## Development vs Production

### Development Mode

The scripts are configured for development use:
- Logs to file (`uvicorn.log`)
- Runs on port 8004
- No production database

### Production Mode

For production deployment, use:
- `docker-compose up -d`
- Environment variables from `.env`
- Production database connection
- Access logging and monitoring

## Additional Notes

- Scripts are located in the project root directory
- Scripts require execute permissions (already set)
- Server runs in background mode
- All logs are written to `uvicorn.log` in the project root
- Default port is 8004 to avoid conflicts with other services
