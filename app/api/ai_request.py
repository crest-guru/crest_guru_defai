import requests
import json
import time
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

from config.settings import Settings
from .wallet import execute_transaction
from app.assistants.assistant import Assistant

logger = logging.getLogger('app')
settings = Settings()

assistant = Assistant()

ai_request_bp = Blueprint('ai_request', __name__)



@ai_request_bp.route('/', methods=['POST'])
@ai_request_bp.route('', methods=['POST'])
def ai_request():
    data = request.json
    logger.info(f"Received ai request: {data['request']}, from user: {data['wallet']}")

    
    
    assistant.delete_assistant()
    assistant.create_assistant()

    thread_id = assistant.create_thread(data["wallet"])
    try:
        assistant.create_message(thread_id, f'help my with request: {data["request"]}, for user: {data["wallet"]}')
        run = assistant.create_run(thread_id)
        assistant.wait_on_run(assistant.run, thread_id)
        openai_response = assistant.get_response(thread_id)
        return jsonify({"message": openai_response}), 200
    except Exception as e:
        assistant.cancel_run(thread_id, run.id)
        logger.error(f"Error: {e}")
        return jsonify({"message": "Error"}), 500




 
            

           
            