from openai import OpenAI
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LLM:
    def __init__(self, api_key, base_url, model_name):
       self.api_key = api_key
       self.base_url = base_url
       self.model_name = model_name

       # Start OpenAI client
       self.client = OpenAI(
           api_key=self.api_key,
           base_url=self.base_url
       )

    def create_chat_completion(self, message):
        chat_completion = self.client.chat.completions.create(
            messages = [
                        {"role":"system",
                                 "content":"You are a helpful assistant"}, #set behavioral context of model
                         {"role":"user",
                                 "content": message}
                        ],
            model = self.model_name,
        )

        return chat_completion