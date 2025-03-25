import openai
from config.settings import Settings
import json
import time
import logging
from datetime import datetime
from app.db.database import get_thread_record, create_thread_record
from app.tools.assistant_tools import tool_registry
settings = Settings()
logger = logging.getLogger('app')

TOOL_CONFIGS = tool_registry.configs
TOOL_FUNCTIONS = tool_registry.functions

openai.api_key = settings.OPENAI_API_KEY


class Assistant:
    def __init__(self, assistant_id=None, thread_id=None, run_id=None):
        self.assistant = None
        self.thread = None
        self.run = None
        self.assistant_id = assistant_id

    def get_assistants(self):
        return openai.beta.assistants.list()

    def delete_assistant(self):
        assistants = self.get_assistants()
        for assistant in assistants:
            if assistant.name == "Guru AI#2":
                return openai.beta.assistants.delete(
                    assistant_id=assistant.id
                )
            else:
                return "Assistant not found"

    def create_assistant(self):
        guru_exists = False
        for assistant in self.get_assistants():
            if assistant.name == "Guru AI#2":
                guru_exists = True
                self.assistant = assistant
                return self.assistant

        if not guru_exists:
            assistant = openai.beta.assistants.create(
                name="Guru AI#2",
                instructions="You are highly specialized crypto and DEFI assistant that can answer questions and help with tasks. You have access to money, so do everything clearly and within the limits of your functions, that is, if a user asks on distracted topics, answer on distracted topics, if he asks you to do something that you have in your functions, you just have to do it strictly correctly application is send to you user wallet address, but not every time tou need resposne it If a user asks you to execute a function (or you realize that you need to execute a function) use the user address (wallet) in functions if possible, try to write separately about your skills or in the answer, as the text merges into one setif user ask you about your skills, you need to answer about your skills and tools that you have",
                tools=TOOL_CONFIGS,
                model="gpt-4o"
            )
            self.assistant = assistant
            return self.assistant

    def create_thread(self, user_wallet_address):
        threads_records = get_thread_record(user_wallet_address)
        if threads_records:
            
            self.thread = threads_records["thread_id"]
            logger.info(f"Thread found: {self.thread}")
            return self.thread
        else:
            self.thread = openai.beta.threads.create(
                metadata={
                    "user_wallet_address": user_wallet_address
                }
            )
            create_thread_record(user_wallet_address, self.thread.id, datetime.now(), None)
            return self.thread.id

    def get_thread(self, thread_id):
        return openai.beta.threads.retrieve(
            thread_id=thread_id
        )
        
    def create_run(self, thread_id):
        self.run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        return self.run
    def get_run_status(self):
        return openai.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
    def create_message(self, thread_id, message):
        return openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

    def wait_on_run(self, run, thread_id):
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                run = self.process_tool_call(thread_id, run)
            else:
                run = openai.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id,
                )
            time.sleep(0.5)
        self.run = run
        return run


    def get_response(self, thread_id):
        response = openai.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        return response.data[0].content[0].text.value

    def process_tool_call(self, thread_id, run):
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run.status == "requires_action":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = []
            
            for tool_call in tool_calls:
                function = tool_call.function
                function_name = function.name
                function_args = json.loads(function.arguments)

                if function_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[function_name](**function_args)
    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": str(result)
                    })
            
            return openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        return run
    
    def cancel_run(self, thread_id, run_id):
        if self.run.status in ["in_progress", "requires_action"]:
            return openai.beta.threads.runs.cancel(
                thread_id=thread_id,
                run_id=run_id
            )
        else:
            return "Run is not in progress"
    


