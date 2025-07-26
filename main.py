from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session as DBSession
from sqlalchemy import create_engine
from models import Base, Product, Order, User, Session, Message
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os
import httpx

# Load .env
load_dotenv()
DB_URL = os.getenv("DB_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# DB setup
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
app = FastAPI()

# Request format
class ChatRequest(BaseModel):
    user_id: int
    message: str
    conversation_id: int = None

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Talk to Groq LLM
async def query_groq(message: str):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"role": "user", "content": message}],
        "model": "mixtral-8x7b-32768"
    }
    async with httpx.AsyncClient() as client:
        res = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        return res.json()["choices"][0]["message"]["content"]

# Main chat endpoint
@app.post("/api/chat")
async def chat(request: ChatRequest, db: DBSession = Depends(get_db)):
    # Start or resume conversation
    if request.conversation_id:
        session_obj = db.query(Session).filter(Session.id == request.conversation_id).first()
        if not session_obj:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session_obj = Session(user_id=request.user_id)
        db.add(session_obj)
        db.commit()
        db.refresh(session_obj)

    # Save user message
    db.add(Message(session_id=session_obj.id, sender="user", content=request.message))

    # response
    reply = await query_groq(request.message)

    # Save bot reply
    db.add(Message(session_id=session_obj.id, sender="bot", content=reply))

    db.commit()

    return {
        "conversation_id": session_obj.id,
        "user_message": request.message,
        "bot_response": reply
    }


@app.get("/top-products")
def top_products(db: DBSession = Depends(get_db)):
    return db.query(Product).order_by(Product.sold.desc()).limit(5).all()


@app.get("/order-status/{order_id}")
def order_status(order_id: int, db: DBSession = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status":order.status}