from asyncore import read
import os, random
import configparser
import json
from tkinter import E
import pyimgur
from setuptools import Command
import pic

from pic import add_enemy, add_player, profession, generate, background, scene_name, env, player, enemy
from PIL import Image
from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()

machine = TocMachine(
    states=["user", "create_team", "battle", "dead"],
    transitions=[
        {
            "trigger": "input",
            "source": "user",
            "dest": "create_team",
            "conditions": "創建腳色 編號",
        },
        {
            "trigger": "input",
            "source": "create_team",
            "dest": "battle",
            "conditions": "start",
        },
        {
            "trigger": "dead in battle",
            "source": "battle",
            "dest": "dead",
            "conditions": "All teammember HP is zero",
        },
        {"trigger": "go_back", "source": ["battle"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")

#================================================================================================================
var             = pic.var
enemy_var       = pic.enemy_var
secret          = var['var']['Secret']
token           = var['var']['Token']
imgur_id        = var['imgur']['id']

line_bot_api    = LineBotApi(token)
parser          = WebhookParser(secret)

state           = 0
Round           = 0
team            = []
raid            = []
command         = [[],[],[],[]]
skillArr        = pic.skillArr
crypt_raid      = pic.crypt_raid
cove_raid       = pic.cove_raid
warrens_raid    = pic.warrens_raid
weald_raid      = pic.weald_raid
#================================================================================================================
def upload():
    im      = pyimgur.Imgur(imgur_id)
    upload  = im.upload_image('./img/bg.png', title = "img") 
    url     = upload.link

    line_bot_api.reply_message(
        replyToken,
        ImageSendMessage(original_content_url = url, preview_image_url = url)
    )
def createRaid():
    global raid
    if(env == 'cove'):      raid = cove_raid[random.randint(0, 12)]
    elif(env == 'crypts'):  raid = crypt_raid[random.randint(0, 12)]
    elif(env == 'warrens'): raid = warrens_raid[random.randint(0, 12)]
    else:                   raid = weald_raid[random.randint(0, 12)]

    for it in raid:
        f = False
        dmg = int(enemy_var['damage'][it])
        hp  = int(enemy_var['health'][it])
        if(enemy_var['assist'][it] == '1'): f = True

        add_enemy(it, f, hp, dmg, 0)

def battlePlayerTurn():
    global player, enemy, background, command
    ind = 0
    for it in enemy:
        it.move = 'idle'
    for it in player:
        mult = False
        try: command[ind][1] = int(command[ind][1])
        except: mult = True

        for i in range(len(it.skills)):
            if(command[ind][0] == it.skills[i].name): skill = it.skills[i]
        
        if(skill.attribute > 0): it.move = 'atk'
        else: it.move = 'assist'
                        
        if(mult != True and skill.Range[command[ind][1]] == '1' and command[ind][1] > 3):                            
            try:
                aim = enemy[command[ind][1] - 4]
            except:
                break
            hit = False
            critical = False

            if(random.randint(0, 100) < skill.accurancy): hit = True
            if(random.randint(0, 100) < skill.critical): critical = True
                        
            if(critical):
                aim.Hp -= int (float(it.damage) * float(skill.power) * random.uniform(0.8, 1.2) * 2)
                print('Critical atk on ' + aim.name + ' hp: ' + str(aim.Hp))
            elif(hit):    #atk hitted
                aim.Hp -= int (float(it.damage) * float(skill.power) * random.uniform(0.8, 1.2))
                print('atk on ' + aim.name + ' hp: ' + str(aim.Hp))
            else:       #atk miss
                aim.move = 'miss'
                print('miss!')
        elif(mult and skill.num > 1):
            timer = 0
            for i in range(len(enemy)):
                if(skill.Range[i + 4] != '1'): continue
                if(timer == skill.num): break
                    
                timer += 1
                aim = enemy[i]
                hit = False
                critical = False

                if(random.randint(0, 100) < skill.accurancy): hit = True
                if(random.randint(0, 100) < skill.critical): critical = True

                if(critical):
                    aim.Hp -= int (float(it.damage) * float(skill.power) * random.uniform(0.8, 1.2) * 2)
                    print('Critical atk on ' + aim.name + ' hp: ' + str(aim.Hp))
                elif(hit):    #atk hitted
                    aim.Hp -= int (float(it.damage) * float(skill.power) * random.uniform(0.8, 1.2))
                    print('atk on ' + aim.name + ' hp: ' + str(aim.Hp))
                else:       #atk miss
                    aim.move = 'miss'
                    print('miss!')
    ind += 1
    background  = Image.open(var['scene'][env] + '/' + scene_name)
    generate(background)
    upload()
def battleEnemyTurn():
    global player, enemy, background
    for it in player:
        it.move = 'idle'
    for i in range(len(enemy)):
        for itt in player:
            if(itt.Hp <= 0): player.remove(it)
        hit = False
        critical = False
        assist   = False

        try: aim = player[0]
        except: break

        if(random.randint(0, 100) < 90): hit = True
        if(random.randint(0, 100) < 5): critical = True
        if(random.randint(0, 100) < 40): assist = True
        if(enemy[i].exmove == False):                
            aim = player[random.randint(0,min(len(player) - 1, 1))]
            enemy[i].move = 'atk'
        elif(enemy[i].exmove == True and assist):    
            aim = player[random.randint(0,len(player) -1)]
            enemy[i].move = 'assist'
            
        if(critical):
            aim.Hp -= int (float(enemy[i].damage) * random.uniform(0.8, 1.2) * 2)
            print('Critical atk! '+ aim.ID + ' remain: ' + str(aim.Hp))
        elif(hit):
            aim.Hp -= int (float(enemy[i].damage) * random.uniform(0.8, 1.2))
            print(aim.ID + ' remain: ' + str(aim.Hp))
        else:
            aim.move = 'miss'
            print('miss!')
    background  = Image.open(var['scene'][env] + '/' + scene_name)
    generate(background)
    upload()

#recieve and transfer
@app.route("/callback", methods=["POST"])
def callback():
    global team, player, enemy, background, scene_name, replyToken, state, env, Round
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
        replyToken = event.reply_token
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        id = (json.loads(str(event.source)))['userId']
        signed = False
        for it in team:
            if(it == id): signed = True
        words = event.message.text.split(" ")

        if state == 0: #create charcter
            if (words[0] == '清除' or words[0] == 'clear'):
                team    = []
                player  = []
                background  = Image.open(var['scene'][env] + '/' + scene_name)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '隊伍清除')
                )
            elif (words[0] == '創建職業' and words[1] and signed == False):
                add_player(id, int(words[1]))
                team.append(id)

                Career_msg  = '腳色職業 : ' + profession[int(words[1])] + '\n'
                Career_msg += '體力上限 : ' + str(player[len(player) - 1].MaxHp) + '\n'
                Career_msg += '攻擊傷害 : ' + str(player[len(player) - 1].damage) + '\n'
                Career_msg += '防禦值 : '   + str(player[len(player) - 1].defence) + '\n'
                Career_msg += '技能:\n'
                for it in player[len(player) - 1].skills:
                    Career_msg += it.name + ' 威力' + str(it.power) + ' 命中' + str(it.accurancy) + ' 要害率' + str(it.critical) + '\n'

                line_bot_api.push_message(id, TextSendMessage(text = str(Career_msg)))
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '創建職業 : ' + profession[int(words[1])])
                )
            elif(words[0] == 'check'):
                generate(background)
                background.save('./img/bg.png')

                im      = pyimgur.Imgur(imgur_id)
                upload  = im.upload_image('./img/bg.png', title = "img") 
                url     = upload.link
                
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url = url, preview_image_url = url)
                )
            elif(words[0] == '環境' and words[1]):
                enemy = []
                env   = words[1]
                scene_name  = random.choice(os.listdir(var['scene'][env]))
                background  = Image.open(var['scene'][env] + '/' + scene_name)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text = '環境已選擇 '+ env)
                )
            elif(words[0] == 'start'):
                state = 1
                background  = Image.open(var['scene'][env] + '/' + scene_name)
                createRaid()
                generate(background)
                background.save('./img/bg.png')

                im      = pyimgur.Imgur(imgur_id)
                upload  = im.upload_image('./img/bg.png', title = "img") 
                url     = upload.link
                
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url = url, preview_image_url = url)
                )
        else:
            ready = 0
            ind = 0
            for i in range(len(player)):
                if(player[i].ID == id): ind = i
            for i in range(0, 4):
                if(player[ind].skills[i].name == words[0]):
                    command[ind] = words
                    ready += 1
                    break
            if(ready == len(team)):
                Round = 1
                battlePlayerTurn()
            elif(Round == 1):
                Round = 0
                battleEnemyTurn()
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
