from pymongo import MongoClient

class AIService:
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

    def reason_if_need_data_from_db():
        return True