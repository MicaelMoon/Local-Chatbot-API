from pymongo import MongoClient
from datetime import datetime

class DatabaseService:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["ai_assistant_memory"]
        self.chats_collection = self.db["chats"]

        self.chats_collection.create_index({"message": "text", "response": "text"})


    def get_all_chats(self) -> list[dict]:
        result = self.chats_collection.find({}, {"_id":0})

        return list(result)
    
    def get_messages(self, start_time: datetime, end_time: datetime, keywords: list[str]) -> list[dict]:
        search_string = " ".join(keywords)
        query = {"$text": {"$search": search_string}}
        result = self.chats_collection.find(query, {"_id":0})

        return list(result)

    
    def save_message_to_db(self, chat_message: str, chat_reply: str):
    
        doc = {
            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": chat_message,
            "reply": chat_reply
        }

        self.chats_collection.insert_one(doc)

        return doc