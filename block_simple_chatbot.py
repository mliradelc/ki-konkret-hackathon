import gradio as gr
from functions.LLMConnection import LLM
import yaml
import time
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def load_metadata():
    try:
        with open("settings.yml", "r") as file:
            meta_data = yaml.safe_load(file)
    except Exception as e:
        logger.info(f"Failed to read config file settings.yml \nException was:")
        logger.error(e)
        raise e
    return [meta_data["models"], meta_data['api_key'], meta_data['base_url']]

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    model, api_key, base_url = load_metadata()
    llmConnection = LLM(api_key[0],base_url[0], model[0])


    def user(user_message, history: list):
        return "", history + [{"role": "user", "content": user_message}]

    def bot(history: list):
        logger.info(f"User history: {history}")
        user_query = history[len(history)-1]['content']
        logger.info(f"User query: {user_query}")

        bot_message =  llmConnection.create_chat_completion(user_query)

        history.append({"role": "assistant", "content": bot_message.choices[0].message.content})

        for character in bot_message.choices[0].message.content:
            history[-1]['content'] += character
            time.sleep(0.05)
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

demo.launch(server_port=7871, share=True)
