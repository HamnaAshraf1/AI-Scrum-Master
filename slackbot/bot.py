import re
import json
import datetime

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_sdk.errors import SlackApiError
import re
from model.llm import LLM
from slackbot.slackuser import slackuser 
from slackbot.event_parse import parse_message

import time

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



meeting_active = False
num_members = 0
member_times = []
current_member = 0

def countdown(say, seconds):
    for i in range(seconds, 0, -1):
        say(f"{i}...")
        time.sleep(1)

def handle_member_timer(say):
    global current_member
    if current_member < len(member_times):
        say(f"Member {current_member + 1}, your time starts now!")
        time.sleep(member_times[current_member])
        current_member += 1
        if current_member < len(member_times):
            say(f"Next member get ready!")
            countdown(say, 3)
            handle_member_timer(say)
        else:
            say("Meeting time is over. Thank you everyone!")
    else:
        say("Meeting time is over. Thank you everyone!")

@app.message("start the meeting")
def start_meeting(message, say):
    global meeting_active
    if not meeting_active:
        ("$$$$$$$$$$$$$$$$$$$$$$$$$$$MEETING ACTIVE$$$$$$$$$$$$$$$$$$$$$$$$")
        meeting_active = True
        say("How many members are present today for the meeting?")
    else:
        say("A meeting is already in progress.")

@app.message(re.compile(r'^\d+$'))
def set_num_members(message, say):
    global num_members, member_times, current_member
    if meeting_active:
        print("***************MEETING STARTED*********************")
        num_members = int(message['text'])
        if num_members > 0:
            total_meeting_time = 15 * 60  # 15 minutes in seconds
            member_time = total_meeting_time / num_members
            member_times = [member_time] * num_members
            current_member = 0
            say(f"Each member will have {member_time / 60:.2f} minutes to speak.")
            say("Get ready for the meeting.")
            countdown(say, 5)
            handle_member_timer(say)
        else:
            say("Please enter a valid number of members.")



@app.message(re.compile('jira', re.IGNORECASE))
def jira(event, say):
    user_id, channel, recv_msg = parse_message(event)

    if user_id not in users.keys():
        users[user_id] = slackuser(user_id)
    users[user_id].conversation_grow(channel, 'user', recv_msg)

    response = llm.run_jira('AI_Scrum_Assistant', users[user_id].get_conversation(channel))

    resp_msg = response['message']['content']

    users[user_id].conversation_grow(channel, 'assistant', resp_msg)

    say(resp_msg)


@app.event('message')
def bot_message(event, say):
    user_id, channel, recv_msg = parse_message(event)

    if user_id not in users.keys():
        users[user_id] = slackuser(user_id)

    users[user_id].conversation_grow(channel, 'user', recv_msg)

    response = llm.talk('AI_Scrum_Assistant', users[user_id].get_conversation(channel))
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
