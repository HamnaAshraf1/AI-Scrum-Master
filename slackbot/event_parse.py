
from tokens import SLACK_BOT_TOKEN
from slackbot.attachment import download, parse_audio


def get_botid(event):
    return event.get('event', {}).get('text').split()[0]


def get_audio(event):
    parse_msg = str()
    if 'files' in event:
        files = event.get('files')
        for file in files:
            filepath, headers = download(file['url_private_download'], SLACK_BOT_TOKEN)
            if file['filetype'].lower() in ('webm', 'mov'):
                parse_msg += parse_audio(filepath)["text"]
        
    return parse_msg


def parse_message(event):
    user_id = event.get('user')
    channel = event.get('channel')

    message = get_audio(event)
    message += event.get('text')

    return user_id, channel, message 
