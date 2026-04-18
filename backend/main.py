from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import numpy as np
from PIL import Image
import cv2
import io
import hashlib

app = FastAPI(title="SealSight — AI Image Watermarking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "SEALSIGHT_IDEAJAM_2026"
WATERMARK_BITS = 16
DCT_STRENGTH = 50.0
BLOCK = 8


def get_signature_bits():
    h = hashlib.sha256(SECRET_KEY.encode()).digest()
    bits = []
    for byte in h[:WATERMARK_BITS // 8]:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits[:WATERMARK_BITS]


def embed_watermark(img_array):
    bits = get_signature_bits()
    n = len(bits)
    out = img_array.astype(np.float32).copy()
    h, w = img_array.shape[:2]
    for c in range(min(3, img_array.shape[2])):
        ch = out[:, :, c]
        idx = 0
        for y in range(0, h - BLOCK + 1, BLOCK):
            for x in range(0, w - BLOCK + 1, BLOCK):
                tile = ch[y:y+BLOCK, x:x+BLOCK].copy()
                D = cv2.dct(tile.astype(np.float32))
                bit = bits[idx % n]
                q = round(D[4, 1] / DCT_STRENGTH)
                if bit == 1:
                    if q % 2 == 0: q += 1
                else:
                    if q % 2 != 0: q -= 1
                D[4, 1] = q * DCT_STRENGTH
                ch[y:y+BLOCK, x:x+BLOCK] = cv2.idct(D)
                idx += 1
        out[:, :, c] = ch
    return np.clip(out, 0, 255).astype(np.uint8)


def decode_watermark(img_array):
    expected = get_signature_bits()
    n = len(expected)
    h, w = img_array.shape[:2]
    votes = np.zeros(n, dtype=int)
    counts = np.zeros(n, dtype=int)
    for c in range(min(3, img_array.shape[2])):
        ch = img_array[:, :, c].astype(np.float32)
        idx = 0
        for y in range(0, h - BLOCK + 1, BLOCK):
            for x in range(0, w - BLOCK + 1, BLOCK):
                tile = ch[y:y+BLOCK, x:x+BLOCK].copy()
                D = cv2.dct(tile)
                q = round(D[4, 1] / DCT_STRENGTH)
                bit = abs(q) % 2
                pos = idx % n
                votes[pos] += bit
                counts[pos] += 1
                idx += 1
    final = [1 if counts[i] > 0 and votes[i] > counts[i] / 2 else 0 for i in range(n)]
    matches = sum(1 for a, b in zip(final, expected) if a == b)
    return matches / n, matches, n


def read_image(data):
    img = Image.open(io.BytesIO(data)).convert("RGB")
    return np.array(img)


@app.post("/embed")
async def embed_endpoint(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    data = await file.read()
    try:
        img = read_image(data)
    except Exception:
        raise HTTPException(400, "Could not read image")
    wm = embed_watermark(img)
    out = Image.fromarray(wm)
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=watermarked.png"})


@app.post("/verify")
async def verify_endpoint(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    data = await file.read()
    try:
        img = read_image(data)
    except Exception:
        raise HTTPException(400, "Could not read image")
    conf, matched, total = decode_watermark(img)
    verified = conf >= 0.70
    return JSONResponse({
        "verified": verified,
        "confidence": round(conf * 100, 1),
        "bits_matched": matched,
        "total_bits": total,
        "label": "AI-Generated — SealSight Verified" if verified else "No watermark detected",
        "status": "VERIFIED" if verified else "NOT_VERIFIED"
    })


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SealSight Watermarking API v1.0"}


@app.get("/")
async def root():
    return {"name": "SealSight", "endpoints": ["/embed", "/verify", "/health", "/docs"]}


# Serve frontend static files (for single-port deployment)
import os
from fastapi.responses import HTMLResponse

@app.get("/app", response_class=HTMLResponse)
async def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
    if os.path.exists(frontend_path):
        with open(frontend_path) as f:
            html = f.read()
        # Replace localhost:8000 with relative path for cloud deploy
        html = html.replace("const API = 'http://localhost:8000'", "const API = ''")
        return HTMLResponse(html)
    return HTMLResponse("<h1>Frontend not found</h1>")
