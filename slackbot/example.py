import ollama
import logging
from dotenv import load_dotenv
from attachment import download, parse_audio
import json
import schedule
import time
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slacktoken import SLACK_BOT_TOKEN, SLACK_APP_TOKEN


load_dotenv()

app = App(token=SLACK_BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG)

conversation_history = {}

with open('config.json') as config_file:
    config = json.load(config_file)

CHANNEL_IDS = config["CHANNEL_IDS"]

def send_reminder(message):
    for channel_id in CHANNEL_IDS:
        try:
            response = app.client.chat_postMessage(
                channel=channel_id,
                text=message
            )
            assert response["message"]["text"] == message
        
        except SlackApiError as e:
            print(f"Error sending message to {channel_id}: {e.response['error']}")

def schedule_reminders():
    for reminder in config["reminders"]:
        day = reminder["day"]
        time_str = reminder["time"]
        message = reminder["message"]

        if day == "Monday":
            schedule.every().monday.at(time_str).do(send_reminder, message)
        elif day == "Tuesday":
            schedule.every().tuesday.at(time_str).do(send_reminder, message)
        elif day == "Wednesday":
            schedule.every().wednesday.at(time_str).do(send_reminder, message)
        elif day == "Thursday":
            schedule.every().thursday.at(time_str).do(send_reminder, message)
        elif day == "Friday":
            schedule.every().friday.at(time_str).do(send_reminder, message)



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

    schedule_reminders()