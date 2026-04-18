#!/bin/bash
echo "================================"
echo "  SealSight Backend — Starting  "
echo "================================"
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q
echo ""
echo "API running at: http://localhost:8000"
echo "Docs at:        http://localhost:8000/docs"
echo ""
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
