#!/bin/bash

# Kill any existing processes on port 8004
fuser -k 8004/tcp 2>/dev/null

echo "Server stopped"
