import os, random
from sre_parse import State
import sys
import configparser
import json
import pathlib
import pyimgur

from cgitb import handler
from distutils.command.config import config
from dataclasses import dataclass
from PIL import ImageTk, Image
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()

machine = TocMachine(
    states=["user", "state1", "state2"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state1",
            "conditions": "is_going_to_state1",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {"trigger": "go_back", "source": ["state1", "state2"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

@dataclass
class Career:
    ID      : str
    idle    : Image.Image
    atk     : Image.Image
    assist  : Image.Image
    miss    : Image.Image
    MaxHp   : int
    Hp      : int
    damage  : int
    defence : int
    Maxmind : int
    mind    : int
    insane  : bool

app = Flask(__name__, static_url_path="")

#================================================================================================================
var = configparser.ConfigParser()
var.read('config.ini')

secret = var['var']['Secret']
token = var['var']['Token']

imgur_id        = var['imgur']['id']

line_bot_api = LineBotApi(token)
parser = WebhookParser(secret)

state  = 0
team   = []
player = []
profession  = ['alchemist', 'archer', 'bounty', 'hunter', 'jester', 'knight', 'tank', 'vestal']

background  = Image.open(var['scene']['crypts'] + '/' + random.choice(os.listdir(var['scene']['crypts'])))
#================================================================================================================

def add_player(id, carrer_num):
    global player, team, profession, state, background, var
    
    idle    = Image.open(var['character'][profession[carrer_num]] + 'A' + '.png')
    atk     = Image.open(var['character'][profession[carrer_num]] + 'A_atk' + '.png')
    assist  = Image.open(var['character'][profession[carrer_num]] + 'A_assist' + '.png')
    miss    = Image.open(var['character'][profession[carrer_num]] + 'A_miss' + '.png')

    img     = idle.resize((idle.width // 2, idle.height // 2))
    img1    = atk.resize((atk.width // 2, atk.height // 2))
    img2    = assist.resize((assist.width // 2, assist.height // 2))
    img3    = miss.resize((miss.width // 2, miss.height // 2))
    idle    = img
    atk     = img1
    assist  = img2
    miss    = img3
    
    MaxHp   = var['health'][profession[carrer_num]]
    Hp      = MaxHp
    damage  = var['damage'][profession[carrer_num]]
    defence = var['defence'][profession[carrer_num]]
    Maxmind = var['mind'][profession[carrer_num]]
    mind    = 0

    player.append(Career(id, idle, atk, assist, miss, MaxHp, Hp, damage, defence, Maxmind, mind, False))

def gen_player():
    global player, team, profession, state, background, var
    
    for i in range(len(player)):
        bar         = Image.open(var['ui']['bar'])
        health_pip  = Image.open(var['ui']['health_pip'])
        img         = player[len(player) - i - 1].idle
        bar        = bar.resize((bar.width, int(bar.height * 2)))
        img1        = health_pip.resize((int(health_pip.width * 16.875), int(health_pip.height * 2)))
        
        offset      = [img.width // 2, img.height]

        img1.paste(bar, (0, 0), bar)
        
        background.paste(img, ( 700 - 150 * (len(player) - i - 1) - offset[0], 675 - offset[1]), img)
        background.paste(img1, ( 650 - 160 * (len(player) - i - 1) , 670), img1)

#recieve and transfer
@app.route("/callback", methods=["POST"])
def callback():
    global player, team, profession, state, background, var
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        id = (json.loads(str(event.source)))['userId']
        signed = False
        for it in team:
            if(it == id): signed = True
        words = event.message.text.split(" ")

        #sendmessage to user inperson
        #line_bot_api.push_message(id, TextSendMessage(text = id))

        if state == 0: #create charcter
            if (words[0] == '清除' or words[0] == 'clear'):
                team    = []
                player  = []
                background  = Image.open(var['scene']['crypts'] + '/' + random.choice(os.listdir(var['scene']['crypts'])))
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '隊伍清除')
                )
            if (words[0] == '創建職業' and words[1] and signed == False):
                add_player(id, int(words[1]))
                team.append(id)

                Career_msg  = '腳色職業 : ' + profession[int(words[1])] + '\n'
                Career_msg += '體力上限 : ' + str(player[len(player) - 1].MaxHp) + '\n'
                Career_msg += '攻擊傷害 : ' + str(player[len(player) - 1].damage) + '\n'
                Career_msg += '防禦值 : '   + str(player[len(player) - 1].defence) + '\n'
                Career_msg += '理智值 : '   + str(player[len(player) - 1].Maxmind)

                line_bot_api.push_message(id, TextSendMessage(text = str(Career_msg)))
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '創建職業 : ' + profession[int(words[1])])
                )
            if(words[0] == 'check'):
                gen_player()
                background.save('bg.png')

                im      = pyimgur.Imgur(imgur_id)
                upload  = im.upload_image('bg.png', title = "img") 
                url     = upload.link

                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url = url, preview_image_url = url)
                )
    return "OK"

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"

@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
