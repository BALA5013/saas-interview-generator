from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

app = FastAPI(title="Analytics Service")

class EventTrack(BaseModel):
    event_type: str
    details: Dict[str, Any] = {}

# In-memory analytics store
EVENTS = []
STATS = {
    "total_requests": 0,
    "event_counts": {}
}

@app.post("/track")
async def track_event(event: EventTrack):
    # Store event
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event.event_type,
        "details": event.details
    }
    EVENTS.append(record)
    
    # Update stats
    STATS["total_requests"] += 1
    STATS["event_counts"][event.event_type] = STATS["event_counts"].get(event.event_type, 0) + 1
    
    return {"status": "success"}

@app.get("/stats")
async def get_stats():
    return STATS
