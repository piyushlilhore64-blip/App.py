from fastapi import FastAPI, HTTPException
from models import add_user, delete_user, authenticate_user, set_login_time, check_time_remaining, update_time

app = FastAPI()
ADMIN_KEY = "supersecretadminkey"  # Change to a strong key

# User login
@app.post("/login")
def login(username: str, password: str):
    user = authenticate_user(username, password)
    if user:
        set_login_time(username)
        return {"status": "success", "time_limit": user["time_limit"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Check remaining time
@app.get("/check")
def check_access(username: str):
    remaining = check_time_remaining(username)
    if remaining <= 0:
        return {"status": "expired", "time_remaining": 0}
    return {"status": "active", "time_remaining": remaining}

# Admin: Add user
@app.post("/add_user")
def api_add_user(username: str, password: str, time_limit: int, admin_key: str):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    add_user(username, password, time_limit)
    return {"status": "user added"}

# Admin: Delete user
@app.post("/delete_user")
def api_delete_user(username: str, admin_key: str):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    delete_user(username)
    return {"status": "user deleted"}

# Admin: Update user time limit
@app.post("/update_time")
def api_update_time(username: str, new_time: int, admin_key: str):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")
    update_time(username, new_time)
    return {"status": "time updated"}
