#!/bin/bash

# Kill any existing processes on port 8004
fuser -k 8004/tcp 2>/dev/null

# Wait for port to be free
sleep 2

# Start the server
cd /c/Users/cjarn/VIBE/simg_dashboard
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8004 --log-level info > uvicorn.log 2>&1 &

echo "Server started on port 8004"
echo "Logs available at: /c/Users/cjarn/VIBE/simg_dashboard/uvicorn.log"
