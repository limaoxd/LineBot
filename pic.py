import configparser
import os, random

from ctypes.wintypes import HPALETTE
from dataclasses import dataclass
from PIL import Image
from cv2 import randShuffle

@dataclass
class Skill:
    name            : str
    attribute       : int  #0 輔助, 1 斬擊, 2 鈍器, 3 穿刺, 4 魔法
    power           : int
    accurancy       : int
    critical        : int
    num             : int
    Range           : list

@dataclass
class Career:
    ID      : str
    move    : str
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
    skills  : list
    atkPlus : float
    defPlus : float

@dataclass
class Enemy:
    name    : str
    move    : str
    idle    : Image.Image
    atk     : Image.Image
    assist  : Image.Image
    miss    : Image.Image
    MaxHp   : int
    Hp      : int
    damage  : int
    defence : int
    exmove  : bool
    skills  : list

#================================================================================================================
var = configparser.ConfigParser()
var.read('config.ini')
enemy_var = configparser.ConfigParser()
enemy_var.read('enemy.ini')

env         = 'crypts'
scene_name  = random.choice(os.listdir(var['scene'][env]))
background  = Image.open(var['scene'][env] + '/' + scene_name)

player      = []
enemy       = []
profession  = ['alchemist', 'archer', 'bounty', 'hunter', 'jester', 'knight', 'tank', 'vestal']
skillArr    = [
    ['noxiousBlast', 'plagueGrenade', 'incision', 'battlefieldMedicine'],
    ['sniperShot', 'volleyFire', 'ravage', 'flight'],
    ['collectBounty', 'comeHither', 'uppercut', 'mark'],
    ['sawcleaver', 'hecklingShot', 'visceralAttack', 'salutation'],
    ['dirk_stab', 'harvest', 'inspiringTune', 'battleBallad'],
    ['smite', 'stunning', 'inspiringCry', 'bulwarkOfFaith'],
    ['crush', 'rampart', 'bellow', 'defender'],
    ['maceBash', 'judgement', 'divineGrace', 'divineComfort']
]
crypt_raid  = [
    ['ghoul'],
    ['skeleton0','skeleton0'],
    ['skeleton0','skeleton2'],
    ['skeleton1','skeleton2'],
    ['skeleton1','skeleton3'],
    ['skeleton0','skeleton0','skeleton2'],
    ['skeleton1','skeleton0','skeleton2'],
    ['skeleton1','skeleton1','skeleton2'],
    ['skeleton1','skeleton0','skeleton3'],
    ['skeleton1','skeleton0','skeleton2','skeleton3'],
    ['skeleton1','skeleton1','skeleton2','skeleton2'],
    ['skeleton1','skeleton1','skeleton2','skeleton3'],
    ['skeleton1','skeleton1','skeleton3','skeleton3']
]
cove_raid  = [
    ['shambler'],
    ['murloc2','murloc2'],
    ['murloc0','murloc2'],
    ['murloc1','murloc2'],
    ['murloc2','murloc3'],
    ['murloc0','murloc2','murloc2'],
    ['murloc0','murloc0','murloc3'],
    ['murloc0','murloc2','murloc3'],
    ['murloc1','murloc0','murloc3'],
    ['murloc0','murloc2','murloc2','murloc3'],
    ['murloc0','murloc0','murloc2','murloc3'],
    ['murloc1','murloc0','murloc2','murloc3'],
    ['murloc1','murloc0','murloc0','murloc3']
]
warrens_raid  = [
    ['swinetaur'],
    ['swine0','swine1'],
    ['swine1','swine1'],
    ['swine2','swine0'],
    ['swine2','swine1'],
    ['swine1','swine1','swine0'],
    ['swine2','swine1','swine1'],
    ['swine2','swine0','swine3'],
    ['swine2','swine1','swine3'],
    ['swine2','swine1','swine0','swine3'],
    ['swine2','swine1','swine1','swine3'],
    ['swine1','swine1','swine3','swine3'],
    ['swine2','swine2','swine0','swine3']
]
weald_raid = [
    ['virago'],
    ['brigand1','brigand1'],
    ['brigand1','brigand2'],
    ['brigand1','dog'],
    ['dog','brigand2'],
    ['dog','brigand1','brigand2'],
    ['brigand1','brigand1','dog'],
    ['brigand0','brigand1','dog'],
    ['brigand0','brigand1','brigand2'],
    ['brigand0','brigand1','dog','brigand2'],
    ['brigand0','brigand1','brigand2','brigand2'],
    ['brigand0','brigand0','dog','brigand2'],
    ['dog','brigand1','brigand2','brigand2'],
]
#================================================================================================================
def add_player(id, carrer_num):
    global player
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
    
    MaxHp   = int(var['health'][profession[carrer_num]])
    Hp      = MaxHp
    damage  = int(var['damage'][profession[carrer_num]])
    defence = int(var['defence'][profession[carrer_num]])
    Maxmind = int(var['mind'][profession[carrer_num]])
    mind    = 0
    skills  = []
    for i in range(0, 4):
        name = skillArr[carrer_num][i]
        rangeList = var['range'][name].split(' ')
        attri = int(var['attribute'][name])
        power = float(var['power'][name])
        acc   = int(var['accurancy'][name])
        cri   = int(var['critical'][name])
        num   = int(var['num'][name])
        skills.append(Skill(name, attri, power, acc, cri, num, rangeList))

    player.append(Career(id, 'idle', idle, atk, assist, miss, MaxHp, Hp, damage, defence, Maxmind, mind, False, skills, 1, 1))

def add_enemy(name, f, MaxHp, damage, defence):
    global enemy
    idle    = Image.open('./sprite/monsters/' + name + '/' + name +'.png')
    atk     = Image.open('./sprite/monsters/' + name + '/' + name +'_atk.png')
    miss    = Image.open('./sprite/monsters/' + name + '/' + name +'_miss.png')
    img     = idle.resize((idle.width // 2, idle.height // 2))
    img1    = atk.resize((atk.width // 2, atk.height // 2))
    img3    = miss.resize((miss.width // 2, miss.height // 2))
    idle    = img
    atk     = img1
    miss    = img3
    Hp      = MaxHp
    skills  = []

    if(f == True):
        assist  = Image.open('./sprite/monsters/' + name + '/' + name +'_assist.png')
        img2    = assist.resize((assist.width // 2, assist.height // 2))
        assist  = img2
        enemy.append(Enemy(name, 'idle', idle, atk, assist, miss, MaxHp, Hp, damage, defence, True, skills))
    else:
        enemy.append(Enemy(name, 'idle', idle, atk, atk, miss, MaxHp, Hp, damage, defence, False, skills))

def generate(background):
    for it in player:
        if(it.Hp <= 0): player.remove(it)
    for i in range(len(player)):
        bar         = Image.open(var['ui']['bar'])
        bar         = bar.resize((bar.width, int(bar.height * 2)))
        health_pip  = Image.open(var['ui']['health_pip'])
        
        now         = player[len(player) - i - 1]
        
        if(now.move == 'idle'):
            img = now.idle
        elif(now.move == 'atk'):
            img = now.atk
        elif(now.move == 'assist'):
            img = now.assist
        else:
            img = now.miss
        img1        = health_pip.resize((int(health_pip.width * 16 * int(now.Hp) / int(now.MaxHp)), int(health_pip.height * 1.3)))
        offset      = [img.width // 2, img.height]

        bar.paste(img1, (3, img1.height // 2 - 3), img1)
        
        background.paste(img, ( 700 - 150 * (len(player) - i - 1) - offset[0], 700 - offset[1]), img)
        background.paste(bar, ( 650 - 160 * (len(player) - i - 1) , 670), bar)
    for it in enemy:
        if(it.Hp <= 0): enemy.remove(it)
    for i in range(len(enemy)):
        bar         = Image.open(var['ui']['bar'])
        bar         = bar.resize((bar.width, int(bar.height * 2)))
        health_pip  = Image.open(var['ui']['health_pip'])
        
        now         = enemy[len(enemy) - i - 1]
        if(now.move == 'idle'): img = now.idle
        elif(now.move == 'atk'): img = now.atk
        elif(now.move == 'assist'): img = now.assist
        else: img = now.miss
        
        img1        = health_pip.resize((int(health_pip.width * 16 * int(now.Hp) / int(now.MaxHp)), int(health_pip.height * 1.3)))
        offset      = [img.width // 2, img.height]

        bar.paste(img1, (3, img1.height // 2 - 3), img1)

        background.paste(img, ( 1200 + 150 * (len(enemy) - i - 1) - offset[0], 675 - offset[1]), img)
        background.paste(bar, ( 1130 + 160 * (len(enemy) - i - 1) , 670), bar)
    background.save('./img/bg.png')