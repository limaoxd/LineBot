import configparser
from ctypes.wintypes import HPALETTE
from dataclasses import dataclass
import os, random
from tkinter import *
from xml.dom import minidom
from xml.dom.minidom import Element
from PIL import ImageTk, Image
from cv2 import detail_AffineBestOf2NearestMatcher, detail_ImageFeatures
from matplotlib import pyplot as plt
from torch import instance_norm

config = configparser.ConfigParser()
config.read('config.ini')

win = Tk()
win.geometry("1920x720")

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

background  = Image.open(config['scene']['crypts'] + '/' + random.choice(os.listdir(config['scene']['crypts'])))

player = []
profession  = ['alchemist', 'archer', 'bounty', 'hunter', 'jester', 'knight', 'tank', 'vestal']

def add_player(id, carrer_num):
    idle    = Image.open(config['character'][profession[carrer_num]] + 'A' + '.png')
    atk     = Image.open(config['character'][profession[carrer_num]] + 'A_atk' + '.png')
    assist  = Image.open(config['character'][profession[carrer_num]] + 'A_assist' + '.png')
    miss    = Image.open(config['character'][profession[carrer_num]] + 'A_miss' + '.png')

    img     = idle.resize((idle.width // 2, idle.height // 2))
    img1    = atk.resize((atk.width // 2, atk.height // 2))
    img2    = assist.resize((assist.width // 2, assist.height // 2))
    img3    = miss.resize((miss.width // 2, miss.height // 2))
    idle    = img
    atk     = img1
    assist  = img2
    miss    = img3
    
    MaxHp   = config['health'][profession[carrer_num]]
    Hp      = MaxHp
    damage  = config['damage'][profession[carrer_num]]
    defence = config['defence'][profession[carrer_num]]
    Maxmind = config['mind'][profession[carrer_num]]
    mind    = 0

    player.append(Career(id, idle, atk, assist, miss, MaxHp, Hp, damage, defence, Maxmind, mind, False))

def gen_player():
    for i in range(len(player)):
        bar         = Image.open(config['ui']['bar'])
        health_pip  = Image.open(config['ui']['health_pip'])
        img         = player[len(player) - i - 1].idle
        bar        = bar.resize((bar.width, int(bar.height * 2)))
        img1        = health_pip.resize((int(health_pip.width * 16.875), int(health_pip.height * 2)))
        
        offset      = [img.width // 2, img.height]

        img1.paste(bar, (0, 0), bar)
        
        background.paste(img, ( 700 - 150 * (len(player) - i - 1) - offset[0], 675 - offset[1]), img)
        background.paste(img1, ( 650 - 160 * (len(player) - i - 1) , 670), img1)

add_player('U780cf4964974b409f73cdfb48bd3b305', 5)
add_player('U780cf4964974b409f73cdfb48bd3b305', 2)
add_player('U780cf4964974b409f73cdfb48bd3b305', 0)
add_player('U780cf4964974b409f73cdfb48bd3b305', 4)

gen_player()

background.save('./build/bg.png')
img = ImageTk.PhotoImage(background)

label = Label(win, image = img, width=1920, height=720)
label.pack()

win.mainloop()