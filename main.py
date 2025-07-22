import ollama
from pymongo import MongoClient
from datetime import datetime
from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict

class Message(BaseModel):
    date_time:str
    message:str
    reply:str

# Properties
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_assistant_memory"]
chats_collection = db["chats"]
chat_history = [{
    "role": "system",
    "content":
        "You're my personal ai assistant\n"
        "Messages you recieve from the user will start with a datetime in ISO format (YYYY-MM-DD HH:MM:SS)"
        "This is metadata and not part of the user's actual message."
        "Use it to understand the context in time."}]

# Functions
def get_all_chats() -> list[dict]:
    result = chats_collection.find({}, {"_id":0})

    return list(result)

def save_message_to_db(chat_message: str, chat_reply: str):
    
    doc = {
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": chat_message,
        "reply": chat_reply
    }

    chats_collection.insert_one(doc)

    return doc

# Endpoints
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/messages")
def get_messages():
    return get_all_chats()

@app.post("/message", response_model=Message)
def create_message(chat_message:str = Query(...)) -> Message:
    chat_history.append({"role":"user", "content": f"{datetime.now()} {chat_message}"})

    response = ollama.chat(
        model="mistral",
        messages=chat_history
    )
    chat_reply = response['message']['content']
    chat_history.append({"role":"assistant", "content": chat_reply})

    save_message_to_db(chat_message, chat_reply)

    full_message = Message(
        date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        message=chat_message,
        reply=chat_reply
    )

    return full_message