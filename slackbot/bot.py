import re
import json
import datetime

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_sdk.errors import SlackApiError

from model.llm import LLM
from slackbot.slackuser import slackuser 
from slackbot.event_parse import parse_message
from tokens import SLACK_BOT_TOKEN, SLACK_APP_TOKEN


llm = LLM('llama3.1:latest')
app = App(token=SLACK_BOT_TOKEN)
users = dict()


with open('slackbot/config.json') as config_file:
    config = json.load(config_file)

CHANNEL_IDS = config["CHANNEL_IDS"]


def send_reminders():
    for reminder in config["reminders"]:
        today = datetime.date.today()

        time_str = reminder["time"]
        message = reminder["message"]

        if today.weekday() < 5:
            t = datetime.datetime.strptime(time_str, "%H:%M").time()
            hour = t.hour
            minute = t.minute
            scheduled_time = datetime.time(hour=hour, minute=minute)

            schedule_timestamp = datetime.datetime.combine(today, scheduled_time).timestamp()
            for channel_id in CHANNEL_IDS:
                try:
                    app.client.chat_scheduleMessage(
                        channel = channel_id,
                        post_at = schedule_timestamp,
                        text = message
                        )

                except SlackApiError as e:
                    print(f"Error sending message to {channel_id}: {e.response['error']}")

                except Exception as e:
                    print(f"An unexpected error occurred: {e}")


@app.message(re.compile('jira', re.IGNORECASE))
def jira(event, say):
    user_id, channel, recv_msg = parse_message(event)

    if user_id not in users.keys():
        users[user_id] = slackuser(user_id)
    users[user_id].conversation_grow(channel, 'user', recv_msg)

    response = llm.run_jira('Jira_Assistant', users[user_id].get_conversation(channel))

    resp_msg = response['message']['content']

    users[user_id].conversation_grow(channel, 'assistant', resp_msg)

    say(resp_msg)


@app.event('message')
def bot_message(event, say):
    user_id, channel, recv_msg = parse_message(event)

    if user_id not in users.keys():
        users[user_id] = slackuser(user_id)
    
    users[user_id].conversation_grow(channel, 'user', recv_msg)

    response = llm.talk('AI_Scrum_Master', users[user_id].get_conversation(channel))
    resp_msg = response['message']['content']

    users[user_id].conversation_grow(channel, 'assistant', resp_msg)

    say(resp_msg)


@app.event('app_mention')
def app_mention(event, say):
    user_id, channel, recv_msg = parse_message(event)

    if user_id in slackuser.keys():
        users[user_id] = slackuser(user_id)
    
    users[user_id].conversation_grow(channel, 'user', recv_msg)

    response = llm.talk('AI_Scrum_Master', users[user_id].get_conversation(channel))
    resp_msg = response['message']['content']

    users[user_id].conversation_grow(channel, 'assistant', resp_msg)

    say(user_id + ' ' + resp_msg)


def start_slack_bot():
    send_reminders()
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
