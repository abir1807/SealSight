# SealSight — AI Image Watermarking


Semantic-aware, crop-resistant watermarking for AI-generated images.

---

## What it does
- **Embeds** an invisible 32-bit signature into the core subject of any image using DCT frequency-domain encoding
- **Verifies** whether any image (even cropped/compressed) contains the SealSight watermark
- **Subject-first**: watermark is concentrated in the semantically important region, not scattered across the whole image

---

## Project Structure
```
watermark-project/
├── backend/
│   ├── main.py          ← FastAPI server (embed + verify endpoints)
│   └── requirements.txt
├── frontend/
│   └── index.html       ← Full UI (drop image, embed, verify)
├── start_backend.sh     ← Run backend
├── start_frontend.sh    ← Run frontend
└── README.md
```

---

## Quick Start

### Step 1 — Install Python deps
```bash
pip install -r backend/requirements.txt
```

### Step 2 — Start backend
```bash
bash start_backend.sh
# API runs at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Step 3 — Start frontend (new terminal)
```bash
bash start_frontend.sh
# Open http://localhost:3000 in your browser
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/embed` | Upload image → returns watermarked PNG |
| POST | `/verify` | Upload image → returns confidence score + verified/not |
| GET | `/health` | Health check |

### Example (curl)
```bash
# Embed watermark
curl -X POST http://localhost:8000/embed \
  -F "file=@your_image.jpg" \
  --output watermarked.png

# Verify image
curl -X POST http://localhost:8000/verify \
  -F "file=@watermarked.png"
```

---

## How it works

1. **Semantic mask** — center-weighted Gaussian identifies the subject region
2. **DCT embedding** — signature bits encoded into mid-frequency (3,2) coefficients of 8×8 blocks within the subject
3. **Redundant encoding** — signature repeated across all subject blocks for robustness
4. **Majority-vote decoding** — reads all blocks, votes on each bit, computes confidence score
5. **Threshold** — confidence ≥ 70% = verified

---

## Deploy to cloud (Render / Railway)

### Backend (Render)
1. Push project to GitHub
2. New Web Service → connect repo
3. Build command: `pip install -r backend/requirements.txt`
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Netlify / Vercel)
1. Drag and drop `frontend/` folder to netlify.com/drop
2. Update `API` variable in `index.html` to your Render backend URL

---

## Tech Stack
- **Backend**: Python, FastAPI, OpenCV, NumPy, Pillow
- **Watermarking**: DCT (Discrete Cosine Transform) frequency domain
- **Frontend**: Vanilla HTML/CSS/JS — zero dependencies, instant load

---

## Why SealSight beats existing solutions

| | SynthID / Traditional | SealSight |
|---|---|---|
| Survives cropping | ✗ | ✓ |
| Subject-aware | ✗ | ✓ |
| Open source | ✗ | ✓ |
| Post-process any image | ✗ | ✓ |
| Survives JPEG compression | Partial | ✓ |

---

