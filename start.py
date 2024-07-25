import sys
import logging

from slackbot.bot import start_slack_bot
from flaskapp.app import start_flask_app


logging.basicConfig(level=logging.DEBUG)


def main():
    start_flask_app()
    start_slack_bot()


if __name__ == '__main__':
    sys.exit(main())
