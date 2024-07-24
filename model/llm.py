import sys
import ollama

from abc import ABC
from model.system_prompt import System_Prompt


def get_models_ollama():
    models_name = list()
    for model in ollama.list()['models']:
        models_name.append(model['name'])

    return models_name


class LLM(ABC):
    def __init__(self, model_name):
        if model_name in get_models_ollama():
            self.model_name = model_name
        else:
            sys.exit('Error: Model not exist: {}\n'.format(model_name))


    def talk(self, ststem_role, conversation):
        return ollama.chat(model=self.model_name, messages=[System_Prompt[ststem_role]]+conversation)


    def embeddings(self, data):
        ollama.embeddings(model=self.model_name, prompt=data)
