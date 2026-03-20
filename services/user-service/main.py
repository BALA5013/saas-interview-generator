from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import secrets

app = FastAPI(title="User Service")

# In-memory database for users
# In a real app, use PostgreSQL/MongoDB
USERS_DB = {}
SESSIONS = {}

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/register")
async def register(user: UserCreate):
    if user.username in USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Simple clear-text password for demo purposes. MUST hash in production!
    USERS_DB[user.username] = {"password": user.password}
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: UserLogin):
    if user.username not in USERS_DB or USERS_DB[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate a dummy token
    token = secrets.token_hex(16)
    SESSIONS[token] = user.username
    
    return {"message": "Login successful", "token": token, "username": user.username}

@app.get("/validate-token")
async def validate_token(token: str):
    if token not in SESSIONS:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": SESSIONS[token]}
