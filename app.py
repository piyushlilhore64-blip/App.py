from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import SessionLocal, engine
import models

# Create tables if not exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "✅ FastAPI server is running on Render!"}


# Register user with expiry time
@app.post("/register")
def register(username: str, password: str, minutes: int, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    expiry = datetime.utcnow() + timedelta(minutes=minutes)
    user = models.User(username=username, password=password, expiry=expiry)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "expiry": expiry}


# Login with expiry check
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password != password:
        raise HTTPException(status_code=401, detail="Invalid password")

    if datetime.utcnow() > user.expiry:
        raise HTTPException(status_code=403, detail="Account expired")

    return {"message": "Login successful", "expiry": user.expiry}
