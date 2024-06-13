import urllib.request

opener = urllib.request.build_opener()

def download(url:str, SLACK_BOT_TOKEN:str):
    opener.addheaders = [('Authorization', 'Bearer '+SLACK_BOT_TOKEN)]
    urllib.request.install_opener(opener)
    return urllib.request.urlretrieve(url)


import whisper
stt_model = whisper.load_model("base.en")

def parse_audio(file_path):
    return stt_model.transcribe(file_path)
