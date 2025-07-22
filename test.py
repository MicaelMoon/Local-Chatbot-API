import ollama
from pymongo import MongoClient
from datetime import datetime
from pydantic import BaseModel
from typing import Dict

client = MongoClient("mongodb://localhost:27017/")
db = client["ai_assistant_memory"]
chats_collection = db["chats"]
chat_history = []

def save_message_to_db(message: str, ai_response: str):
    
    doc = {
        "date_time": datetime.now(),
        "message": message,
        "response": ai_response
    }

    chats_collection.insert_one(doc)

    return doc

def get_all_chats() -> list[dict]:
    result = chats_collection.find({}, {"_id":0})

    return list(result)

# Post setup

database_chats = get_all_chats()

if len(database_chats) > 10:
    print("") # pop the list to remove the first thing

while True:
    local_chats = database_chats.copy()
    user_input = input("You: ")

    my_messages = [{
    "role": "system",
    "content":
        "You're my personal ai assistant\n"
        "Messages you recieve from the user will start with a datetime in ISO format (YYYY-MM-DD HH:MM:SS)"
        "This is metadata and not part of the user's actual message."
        "Use it to understand the context in time."}]

    for chat in local_chats:
        my_messages.append({"role": "user", "content": f"{chat["date_time"]} {chat["message"]}"})
        my_messages.append({"role":"assistant", "content": chat["response"]})
        
    my_messages.append({"role": "user", "content": f"{datetime.now()} {user_input}" })
        
    response = ollama.chat(
        model='mistral',
        messages = my_messages)

    reply = response['message']['content']
    print("Assistant:", reply)
    local_chats.append(save_message_to_db(user_input, reply))