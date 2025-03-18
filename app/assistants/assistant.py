import openai
from config.settings import Settings
import json
import time
from app.tools.assistant_tools import tool_registry
settings = Settings()

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
            if assistant.name == "Guru AI":
                return openai.beta.assistants.delete(
                    assistant_id=assistant.id
                )
            else:
                return "Assistant not found"

    def create_assistant(self):
        guru_exists = False
        for assistant in self.get_assistants():
            if assistant.name == "Guru AI":
                guru_exists = True
                self.assistant = assistant
                return self.assistant

        if not guru_exists:
            assistant = openai.beta.assistants.create(
                name="Guru AI",
                instructions="You are a helpful assistant that can answer questions and help with tasks.",
                tools=TOOL_CONFIGS,
                model="gpt-4o-mini"
            )
            self.assistant = assistant
            return self.assistant

    def create_thread(self):
        self.thread = openai.beta.threads.create()
        
    def create_run(self):
        self.run = openai.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
    def get_run_status(self):
        return openai.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
    def create_message(self, message):
        return openai.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

    def wait_on_run(self, run, thread):
        while run.status in ["queued", "in_progress", "requires_action"]:
            if run.status == "requires_action":
                run = self.process_tool_call(thread, run)
            else:
                run = openai.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id,
                )
            time.sleep(0.5)
        self.run = run
        return run


    def get_response(self):
        response = openai.beta.threads.messages.list(
            thread_id=self.thread.id,
            order="desc",
            limit=1
        )
        return response.data[0].content[0].text.value

    def process_tool_call(self, thread, run):
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
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
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        return run
    


