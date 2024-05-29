import ollama
import logging

from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slacktoken import SLACK_BOT_TOKEN, SLACK_APP_TOKEN


load_dotenv()

app = App(token=SLACK_BOT_TOKEN)
logging.basicConfig(level=logging.DEBUG)

@app.event('app_mention')
def app_mention(body, say):
    sender_id = f"<@{body.get('event', {}).get('user')}>"
    bot_id = body.get('event', {}).get('text').split()[0]
    recv_msg = body.get('event', {}).get('text').replace(bot_id, '').strip()

    resp_msg = ollama.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': recv_msg,
        },
    ])
    print(resp_msg)
    say(sender_id + ' ' +resp_msg['message']['content'])


@app.event('message')
def app_message(message, say):
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>!"},
                "accessory": {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click Me"},
                    "action_id": "button_click"
                }
            }
        ],
        text=f"Hey there <@{message['user']}>!"
    )


@app.action("button_click")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)


if __name__ == '__main__':
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
