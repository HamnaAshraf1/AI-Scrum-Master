import ollama
import logging
import datetime
from dotenv import load_dotenv
from attachment import download, parse_audio

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slacktoken import SLACK_BOT_TOKEN, SLACK_APP_TOKEN


load_dotenv()

app = App(token=SLACK_BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG)

System_Prompt = \
'''
You are an AI Scrum Master, dedicated to helping teams effectively implement the Scrum framework and facilitate agile development processes. Your primary responsibilities include:

1. Generating Jira Interaction Code: Generate plain code snippets for interacting with Jira using Python requests library, including creating, updating, and managing issues, as well as generating reports and extracting data for analysis, without including explanations or formatting information.

In your role, you need to have a deep understanding of agile development, the ability to constructively drive the team forward, and ensure that Scrum practices deliver maximum business value.
'''


session = dict()


def get_event_userid(event):
    return event.get('event', {}).get('user')

def get_event_botid(event):
    return event.get('event', {}).get('text').split()[0]

def get_event_text(event):
    return event.get('event', {}).get('text')


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
    register_scheduleMessage()
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
