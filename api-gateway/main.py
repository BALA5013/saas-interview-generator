from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs mapped to Docker Compose service names
SERVICES = {
    "user": "http://user-service:8002",
    "ai": "http://ai-service:8001",
    "analytics": "http://analytics-service:8003"
}

@app.get("/")
def read_root():
    return {"message": "API Gateway is running"}

async def forward_request(method: str, url: str, request: Request, json_data=None):
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if method == "GET":
                response = await client.get(url, params=request.query_params)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")

# --- User Routes ---
@app.post("/auth/register")
async def register(request: Request):
    data = await request.json()
    return await forward_request("POST", f"{SERVICES['user']}/register", request, data)

@app.post("/auth/login")
async def login(request: Request):
    data = await request.json()
    return await forward_request("POST", f"{SERVICES['user']}/login", request, data)

# --- AI Service Routes ---
@app.post("/generate-questions")
async def generate_questions(request: Request):
    data = await request.json()
    # Log analytics event asynchronously (basic approach)
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            await client.post(f"{SERVICES['analytics']}/track", json={
                "event_type": "question_generation",
                "details": data
            })
        except Exception:
            pass # Ignore analytics tracking failure for now
            
    return await forward_request("POST", f"{SERVICES['ai']}/generate", request, data)

# --- Analytics Routes ---
@app.get("/analytics/stats")
async def get_stats(request: Request):
    return await forward_request("GET", f"{SERVICES['analytics']}/stats", request)
