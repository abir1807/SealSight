#!/bin/bash
echo "================================"
echo "  SealSight Frontend — Starting "
echo "================================"
cd "$(dirname "$0")/frontend"
echo ""
echo "Frontend running at: http://localhost:3000"
echo ""
python3 -m http.server 3000
