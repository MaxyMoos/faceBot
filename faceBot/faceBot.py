from slackclient import SlackClient

from faceDetection import *

import time
import requests
import StringIO


with open("./token.txt") as tok:
    TOKEN = tok.read().strip()

BOT_NAME = ''
BOT_ID = ''
sc = SlackClient(TOKEN)

FACE_PATH = "./data/face.png"


def list_channels():
    channels_call = sc.api_call("channels.list")
    if channels_call.get('ok'):
        return channels_call['channels']
    return None


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output.get('upload') and output.get('file')\
                and output['file'].get('initial_comment')\
                and output['file']['initial_comment'].get('comment'):
                if "<@{}>".format(BOT_ID) in output['file']['initial_comment']['comment']:
                    with open("./last_message_received.txt", 'w') as dump:
                        dump.write(str(output))
                    print("Processing request from user {} in channel {}".format(
                        output['username'],
                        output['channel']))
                    return output['file']['url_private_download'], output['channel']
    return None, None


def swap_face(img_url, channel):
    if img_url:
        req = requests.get(img_url, headers={'Authorization': 'Bearer {}'.format(TOKEN)})
        im = Image.open(StringIO.StringIO(req.content))
        tmp_path = "./tmp.jpg"
        im.save(tmp_path)

        faces = detectFaces(tmp_path)
        if len(faces) == 0:
            print("No faces detected !")
            return None
        for face in faces:
            tmp_path = insertFace(FACE_PATH, tmp_path, face)
        tmp_path.save("out.png")
        return "./out.png"


if __name__ == '__main__':
    if sc.rtm_connect():
        print("faceBot connected and running")
        while True:
            img_url, channel = parse_slack_output(sc.rtm_read())
            if img_url and channel:
                img_path = swap_face(img_url, channel)
                if img_path is not None:
                    sc.api_call('files.upload',
                                channels=channel,
                                filename="aminized.png",
                                file=open(img_path, 'rb'))
                    print("JUST AMINIZED A PICTURE !")
                else:
                    sc.api_call('chat.postMessage',
                                channel=channel,
                                text="Sorry mais je n'ai pas vu de visage dans cette image :cry:")
            time.sleep(1)
    else:
        print("Connection failed. Invalid Slack token or bot ID ?")
