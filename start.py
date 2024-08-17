import sys
import logging

from slackbot.bot import start_slack_bot
from flaskapp.app import start_flask_app


logging.basicConfig(level=logging.DEBUG, filename='log.txt', filemode='a', format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def main():
    logging.debug('Start...')
    start_flask_app()
    start_slack_bot()


if __name__ == '__main__':
    sys.exit(main())
