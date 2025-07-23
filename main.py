import ollama
from pymongo import MongoClient
from datetime import datetime
from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from services.ai_service import AIService
from services.database_service import DatabaseService

# Classes
class Message(BaseModel):
    date_time:str
    message:str
    reply:str

# Properties
db_service = DatabaseService()
ai_service = AIService()

chat_history = ai_service.final_response_model_setup # In the future the chat history should prob not save all the time from the database.

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

@app.get("/messages") # Don't want it to do this one.
def get_messages():
    return db_service.get_all_chats()    


@app.post("/message", response_model=Message)
def create_message(chat_message:str = Query(...)) -> Message:
    old_chat_messeges = ai_service.reason_if_need_data_from_db(chat_message)
    
    if(old_chat_messeges != None): # Adds the fetched messages to the chat history
        for message in old_chat_messeges:
            chat_history.append({"role":"user", "content": f"{datetime.now()} {message.get("message")}"})
            chat_history.append({"role":"assistant", "content": f"{message.get("reply")}"})

    chat_history.append({"role":"user", "content": f"{datetime.now()} {chat_message}"}) # Might not want to save a chathistory on the api in the future

    response = ollama.chat(
        model="mistral",
        messages=chat_history
    )
    chat_reply = response['message']['content']
    chat_history.append({"role":"assistant", "content": chat_reply})

    db_service.save_message_to_db(chat_message, chat_reply)

    full_message = Message(
        date_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        message=chat_message,
        reply=chat_reply
    )

    return full_message