import ollama
import json
from pathlib import Path
from services.database_service import DatabaseService

db_service = DatabaseService()

class AIService:

    def __init__(self):
        with open(Path(__file__).parent.parent/"prompts"/"db_reasoning_prompt.txt", "r", encoding="utf-8") as file:
            self.reasoning_prompt = file.read()

        with open(Path(__file__).parent.parent/"prompts"/"final_response_prompt.txt", "r", encoding="utf-8") as file:
            self.final_response_prompt = file.read()

        self.db_reasoning_model_setup = [{
            "role": "system",
            "content": self.reasoning_prompt
        }]

        self.final_response_model_setup = [{
            "role": "system",
            "content":  self.final_response_prompt
        }]

    def reason_if_need_data_from_db(self, user_message: str) -> list[dict]:
        chat_history = self.db_reasoning_model_setup
        chat_history.append({"role": "user",
                             "content": user_message})

        response = ollama.chat( # Don't load this on startup. It can freeze the application.
            model="mistral",
            messages=chat_history
        )

        reply = response['message']['content']

        print("Message = " + user_message)
        print("Reply = " + reply)

        reply_as_json = json.loads(reply)

        if(reply_as_json["isOldConversation"] == True): # A missmatch bug occured. For the future, add the first coouple of messages in chathistoy
            print("isOld ========= True")
            start_time = reply_as_json["startTime"]
            end_time = reply_as_json["endTime"]
            keywords = reply_as_json["keywords"]

            return db_service.get_messages(start_time, end_time, keywords)

        print("isOld ========= False")

        return None