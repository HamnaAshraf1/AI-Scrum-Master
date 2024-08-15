import _thread
import logging
from projmgr.jira import *
from tokens import FLASK_SECRET_KEY
from flask import Flask, request, jsonify


# instantiate the app
flask_app = Flask(__name__)
flask_app.config.from_object(__name__)
flask_app.secret_key = FLASK_SECRET_KEY
flask_app.config['JSON_AS_ASCII'] = False

logging.basicConfig(level=logging.DEBUG, filename='log.txt', filemode='a', format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def conversation2txt(sesssion):
    text = ''
    for user in session.keys():
        text += user
        for sess in session[user]:
            text += sess['content']
        text += '\n'
    return text

@flask_app.route('/data_update', methods=['POST', 'GET'])
def update_data():
    logging.debug('update_data Start...')
    request.get_json()
    logging.debug('update_data End...')
    return jsonify('update_data')


@flask_app.route('/vectorization', methods=['POST', 'GET'])
def vectorization():
    logging.debug('vectorization Start...')
    request.get_json()
    logging.debug('vectorization End...')
    return jsonify('vectorization')


@flask_app.route('/embedding', methods=['POST', 'GET'])
def embedding():
    logging.debug('embedding Start...')
    req = request.get_json()
    try:
        ollama.embeddings(model='llama3', prompt=req['prrompt'])
    except:
        return jsonify('ERROR')
    logging.debug('embedding End...')
    return jsonify('OK')


@flask_app.route('/summary', methods=['POST', 'GET'])
def summary():
    logging.debug('summary Start...')
    request.get_json()
    text = conversation2txt(session)
    text += 'summary the conversation and build a todo list for every member: '
    message = [{'role': 'user', 'content': text}]
    ollama.chat(model='llama3', messages=message)
    logging.debug('summary End...')


@flask_app.route('/jira_update', methods=['POST', 'GET'])
def jira_update():
    logging.debug('jira_update Start...')
    logging.debug('jira_update End...')
    return jsonify(get_all_issues())


def start_flask_app():
    _thread.start_new_thread(flask_app.run, ('0.0.0.0', 80))

