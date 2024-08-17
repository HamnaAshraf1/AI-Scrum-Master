import os
import sys
import ollama
import time

from abc import ABC
from projmgr.jira import *
from model.system_prompt import System_Prompt


def get_models_ollama():
    models_name = list()
    for model in ollama.list()['models']:
        models_name.append(model['name'])

    return models_name


def log_runtime(file_path):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            runtime = end_time - start_time

            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write('Function Execution Time Log\n')

            with open(file_path, 'a') as file:
                file.write(f'{func.__name__} executed in {runtime:.4f} seconds\n')

            return result
        return wrapper
    return decorator


class LLM(ABC):
    def __init__(self, model_name):
        if model_name in get_models_ollama():
            self.model_name = model_name
        else:
            sys.exit('Error: Model not exist: {}\n'.format(model_name))


    @log_runtime('function_runtime.log')
    def talk(self, system_role, conversation):
        return ollama.chat(model=self.model_name, messages=[System_Prompt[system_role]]+conversation)


    @log_runtime('function_runtime.log')
    def run_jira(self, system_role, conversation):
        response = ollama.chat(model=self.model_name, messages=[System_Prompt[system_role]]+conversation, tools=jira_tools)

        # Process function calls made by the model
        if response['message'].get('tool_calls'):
            available_functions = {
                'get_all_projects': get_all_projects,
                'get_all_issues': get_all_issues,
            }

            for tool in response['message']['tool_calls']:
                function_to_call = available_functions[tool['function']['name']]
                function_response = function_to_call()
            # Add function response to the conversation
            conversation.append({'role': 'tool', 'content': function_response})
        else:
            return response

        # Second API call: Get final response from the model
        final_response = ollama.chat(model=self.model_name, messages=[System_Prompt[system_role]]+conversation)
        return final_response


    def embeddings(self, data):
        ollama.embeddings(model=self.model_name, prompt=data)
