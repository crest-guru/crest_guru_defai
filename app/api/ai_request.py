import requests
import json
import time
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

from config.settings import Settings
from .wallet import execute_transaction
from app.assistants.assistant import Assistant

settings = Settings()

assistant = Assistant()

ai_request_bp = Blueprint('ai_request', __name__)



@ai_request_bp.route('/', methods=['POST'])
@ai_request_bp.route('', methods=['POST'])
def ai_request():
    data = request.json
    print(data)

    
    
    assistant.delete_assistant()
    assistant.create_assistant()

    thread_id = assistant.create_thread(data["wallet"])
    assistant.create_message(thread_id, f'help my with request: {data["request"]}, for user: {data["wallet"]}')
    assistant.create_run(thread_id)
    assistant.wait_on_run(assistant.run, thread_id)
    openai_response = assistant.get_response(thread_id)
    return jsonify({"message": openai_response}), 200




 
            

           

        


    # class AssistantManager:
    #     def __init__(self, user_address: str):
    #         self.assistant = Assistant()
    #         self.threads = {}
    #         self.assistant.delete_assistant()
    #         self.assistant_id = self.assistant.create_assistant()

    #     def create_thread(self, user_address: str):
    #         self.threads[user_address] = self.assistant.create_thread(user_address)

    #     def get_thread(self, user_address: str):
    #         return self.threads[user_address]

    #     def create_message(self, thread_id: str, user_address: str, message: str):
    #         self.assistant.create_message(thread_id, message)

    #     def create_run(self, thread_id: str):
    #         self.assistant.create_run(thread_id)

    #     def get_response(self, thread_id: str):
    #         return self.assistant.get_response(thread_id)
            