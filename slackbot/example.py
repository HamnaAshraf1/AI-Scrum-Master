import ollama
import logging
from dotenv import load_dotenv
from attachment import download, parse_audio

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slacktoken import SLACK_BOT_TOKEN, SLACK_APP_TOKEN


load_dotenv()

app = App(token=SLACK_BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG)

conversation_history = {}

@app.event('app_mention')
def app_mention(body, say):
    #sender_id = f"<@{body.get('event', {}).get('user')}>"
    sender_id = body.get('event', {}).get('user')

    bot_id = body.get('event', {}).get('text').split()[0]
    recv_msg = body.get('event', {}).get('text').replace(bot_id, '').strip()

    resp_msg = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': recv_msg,
        },
    ])

    say(sender_id + ' ' + resp_msg['message']['content'])


@app.event('message')
def app_message(event, say):
    #sender_id = f"<@{event.get('user')}>"
    recv_msg = ''

    user_id = event.get('user')

    if 'files' in event:
        files = event.get('files')
        for file in files:
            filepath, headers = download(file['url_private_download'], SLACK_BOT_TOKEN)
            if file['filetype'].lower() == 'webm':
                recv_msg += parse_audio(filepath)["text"]

    for text in event.get('text').split():
        recv_msg += text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({'role': 'user', 'content': recv_msg})

    # resp_msg = ollama.chat(model='llama3', messages=[
    #     {
    #         'role': 'user',
    #         'content': recv_msg,
    #     },
    # ])
    
    resp_msg = ollama.chat(model='llama3', messages= conversation_history[user_id])

    # Append the model's response to the user's history
    conversation_history[user_id].append({'role': 'assistant', 'content': resp_msg['message']['content']})

    say(resp_msg['message']['content'])


#@app.action("button_click")
#def handle_some_action(ack, body, logger):
#    ack()
#    logger.info(body)


if __name__ == '__main__':
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
