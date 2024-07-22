import _thread
import ollama
import logging
import datetime
from dotenv import load_dotenv
from attachment import download, parse_audio

import json
import schedule
import time
from slack_sdk.errors import SlackApiError

from flask import Flask, request, jsonify

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slacktoken import SLACK_BOT_TOKEN, SLACK_APP_TOKEN

session = dict()

# instantiate the app
flask_app = Flask(__name__)
flask_app.config.from_object(__name__)
flask_app.secret_key = 'onlyxool'

def conversation2txt(sesssion):
    text = ''
    for user in session.keys():
        text += user
        for sess in session[user]:
            text += sess['content']
        text += '\n'
    return text

@flask_app.route('/data_update', methods=['POST'])
def update_data():
    request.get_json()
    return jsonify('OK')


@flask_app.route('/vectorization', methods=['POST'])
def vectorization():
    request.get_json()
    return jsonify('pong!')


@flask_app.route('/embedding', methods=['POST'])
def embedding():
    req = request.get_json()
    try:
        ollama.embeddings(model='llama3', prompt=req['prrompt'])
    except:
        return jsonify('ERROR')
    return jsonify('OK')

@flask_app.route('/summary', methods=['POST'])
def summary():
    request.get_json()
    text = conversation2txt(session)
    text += 'summary the conversation and build a todo list for every member: '
    message = [{'role': 'user', 'content': text}]
    ollama.chat(model='llama3', messages=message)


@flask_app.route('/jira_update', methods=['POST'])
def jira_update():
    request.get_json()
    return jsonify('pong!')

def run_flask():
    flask_app.run()

load_dotenv()

app = App(token=SLACK_BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG)


def check_llm():
    for model in ollama.list()['models']:
        if model.get('name') == 'llama3:latest':
            return True
    return False


System_Prompt = \
'''
You are an AI Scrum Master, dedicated to helping teams effectively implement the Scrum framework and facilitate agile development processes. Your primary responsibilities include:

1. Generating Jira Interaction Code: Generate plain code snippets for interacting with Jira using Python requests library, including creating, updating, and managing issues, as well as generating reports and extracting data for analysis, without including explanations or formatting information.

In your role, you need to have a deep understanding of agile development, the ability to constructively drive the team forward, and ensure that Scrum practices deliver maximum business value.
'''



def get_event_userid(event):
    return event.get('event', {}).get('user')

def get_event_botid(event):
    return event.get('event', {}).get('text').split()[0]

def get_event_text(event):
    return event.get('event', {}).get('text')




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
def app_mention(event, say):
    sender_id = get_event_userid(event)

    bot_id = get_event_botid(event)
    recv_msg = get_event_text(event).replace(bot_id, '').strip()

    if sender_id in session.keys():
        session[sender_id] += [{'role': 'user', 'content': recv_msg}]
    else:
        session[sender_id] = [{'role': 'user', 'content': recv_msg}]

    resp_msg = ollama.chat(model='llama3', messages=session[sender_id])

    session[sender_id] += [resp_msg['message']]

    say(sender_id + ' ' + resp_msg['message']['content'])


@app.event('message')
def app_message(event, say):
    recv_msg = ''


#    print('--------')
#    print(app.client.conversations_list())
#    for result in app.client.conversations_list():

    sender_id = event.get('user')

#user_id = event.get('user')

    if 'files' in event:
        files = event.get('files')
        for file in files:
            filepath, headers = download(file['url_private_download'], SLACK_BOT_TOKEN)
            if file['filetype'].lower() in ('webm', 'mov'):
                recv_msg += parse_audio(filepath)["text"]

    for text in event.get('text').split():
        recv_msg += text


    if sender_id in session.keys():
        session[sender_id] += [{'role': 'user', 'content': recv_msg}]
    else:
        session[sender_id] = [{'role': 'system', 'content': System_Prompt}, {'role': 'user', 'content': recv_msg}] 

    resp_msg = ollama.chat(model='llama3', messages=session[sender_id])

    session[sender_id] += [resp_msg['message']]

    #if user_id not in conversation_history:
    #    conversation_history[user_id] = []



    # resp_msg = ollama.chat(model='llama3', messages=[
    #     {
    #         'role': 'user',
    #         'content': recv_msg,
    #     },
    # ])
    
    resp_msg = ollama.chat(model='llama3', messages= session[sender_id])



    say(resp_msg['message']['content'])

@app.message('summarize')
def summarize(event, say):
    print(event)


@app.command("/alarms")
def handle_alarms_command(ack, body, logger):
    result = app.client.chat_scheduledMessages_list()
    ack()
    logger.info(body)

#print(result)
#say()


def register_scheduleMessage():
#scheduled_time = datetime.datetime.now() + datetime.timedelta(seconds=120)

    today = datetime.date.today()# + datetime.timedelta(days=0)
    scheduled_time = datetime.time(hour=23, minute=59)
    schedule_timestamp = datetime.datetime.combine(today, scheduled_time).strftime('%s')

    app.client.chat_scheduleMessage(
        channel = '#project',
        post_at = schedule_timestamp,
        text = 'Time for Standup Meeting.')


#@app.action("button_click")
#def handle_some_action(ack, body, logger):
#    ack()
#    logger.info(body)

if __name__ == '__main__':
    if check_llm():
        register_scheduleMessage()
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        _thread.start_new_thread(run_flask, ())
        handler.start()
    else:
        sys.exit('No Model')
