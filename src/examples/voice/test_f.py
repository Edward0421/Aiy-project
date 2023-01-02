#!/usr/bin/env python3
# Copyright 2017 Google Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# coding=utf-8

"""A demo of the Google CloudSpeech recognizer."""
import argparse
import locale
import logging
import openpyxl
import datetime
import re
from openpyxl.styles import Font, colors, Alignment
from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
from gtts import gTTS
from pydub import AudioSegment
from aiy.voice import audio
from queue import Queue
import sqlite3
import os
import threading
import queue
import sqlite3
import time
import sys
import os
from pydub import AudioSegment
from pydub.utils import which
from aiy.voice import audio
import youtube_dl
import vlc
import pafy
from bottle import route, run, template
import urllib.request as ur
import json
from urllib import parse
import urllib
import pyaudio
import wave
import random

event = threading.Event()
output_control = threading.Event()
say_control = threading.Event()

#----------------------------------------------------------------------------#

def outputsay(text):
    tts = gTTS(text, lang = 'zh-TW') # 把文字變成gtts內建的物件
    tts.save('output.mp3') # 把得到的語音存成 output.mp3
    sound = AudioSegment.from_mp3('output.mp3') # 把 output.mp3 讀出
    sound.export('output.wav', format='wav') # 轉存成 output.wav
    audio.play_wav('output.wav') # 把 wav 用 VoiceKit 播出來

def say(text):
    while True:
        if output_control.is_set():
            continue
        else:
            say_control.set()
            tts = gTTS(text, lang = 'zh-TW') # 把文字變成gtts內建的物件
            tts.save('output.mp3') # 把得到的語音存成 output.mp3
            sound = AudioSegment.from_mp3('output.mp3') # 把 output.mp3 讀出
            sound.export('output.wav', format='wav') # 轉存成 output.wav
            audio.play_wav('output.wav') # 把 wav 用 VoiceKit 播出來
            break
    say_control.clear()

def output_say(text):
    tts = gTTS(text, lang = 'zh-TW') # 把文字變成gtts內建的物件
    tts.save('output.mp3') # 把得到的語音存成 output.mp3
    sound = AudioSegment.from_mp3('output.mp3') # 把 output.mp3 讀出
    sound.export('output.wav', format='wav') # 轉存成 output.wav
    audio.play_wav('output.wav') # 把 wav 用 VoiceKit 播出來

def get_hints(language_code):
    if language_code.startswith('en_'):
        return ('turn on the light',
                'turn off the light',
                'blink the light',
                'goodbye')
    return None

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Assistant service example.')
parser.add_argument('--language', default=locale_language())
args = parser.parse_args()

logging.info('Initializing for language %s...', args.language)
hints = get_hints(args.language)
client = CloudSpeechClient()

#----------------------------------------------------------------------------#

music_flag = 0
sign = 2
state = 2

video = None
best = None
playurl = None
Instance = None
player = None
Media = None


def Data(year, month, day, hour, min, name, notice):
    id = 0
    flag = 0
    conn = sqlite3.connect('rasp.db')
    notice = str(notice)
    month = month.zfill(2)
    day = day.zfill(2)
    hour = hour.zfill(2)
    min = min.zfill(2)
    time = year + month + day + hour + min
    cursor = conn.cursor()
    results = cursor.execute("SELECT * FROM MUSICBOX")
    conn.commit()
    for item in results:
        if item == None:
            flag = 1
            break
        id = item[0]
    if flag == 1:
        id = id
    else:
        id = str(int(id) + 1)
    cursor.execute("INSERT INTO MUSICBOX VALUES ('"+id+"','"+year+"','"+month+"','"+day+"','"+hour+"','"+min+"','"+time+"','"+name+"','"+notice+"')")
    conn.commit()
    say('行程建立成功')
    cursor.close()
    conn.close()

def present_time():
    curtime = []
    curtime.append(datetime.datetime.now().strftime("%Y"))
    curtime.append(datetime.datetime.now().strftime("%m"))
    curtime.append(datetime.datetime.now().strftime("%d"))
    curtime.append(datetime.datetime.now().strftime("%H"))
    curtime.append(datetime.datetime.now().strftime("%M"))
    curtime.append(datetime.datetime.now().strftime("%S"))
    return curtime

class myThread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        if self.name == 'schedule':
            schedule()
        elif self.name == 'music':
            music()
        elif self.name == 'calculator':
            calculator()
        elif self.name == 'radio':
            radio()
        elif self.name == 'weather':
            weather()
        elif self.name == 'output':
            output()
        elif self.name == 'game':
            game()
        elif self.name == 'record':
            record()

def game():
    #隨機生成題目
    event.clear()
    ans = random.sample(range(0,10),4)
    print (ans)
    A = 0
    B = 0
    a = "0"
    b = "0"
    fail = 0
    print ('每次猜題會有10秒思考時間')
    #可以改成有次數限制次數
    for count in range(1,11):
        times = 10 - count
        times = str(times)
        say('剩餘次數'+times)
        say('輸入4個數字，且不重複')
        time.sleep(10)
        say('請輸入')
       #轉成語音輸入數字say()
        input_ans = client.recognize(language_code=args.language,hint_phrases=hints)
        #防呆，超過4個數或數字重複
        while len(input_ans) != 4 or len(set(input_ans)) != 4:
            #轉成語音輸入數字
            say('輸入錯誤')
            say('重新輸入4個數字，且不重複')
            time.sleep(10)
            say('請輸入')
            input_ans =  client.recognize(language_code=args.language,hint_phrases=hints)
        input_list = list(map(int,list(input_ans)))
        A = 0
        B = 0
        a = "0"
        b = "0"
        print (input_list)
        for i in input_list:
            if i in ans:
                if input_list.index(i) == ans.index(i):
                    A+=1
                    a = str(A)
                else:
                    B+=1
                    b = str(B)

        #轉成語音say()
        say(a+'A'+b+'B')
        #print(input_ans,":",A,"A",B,"B",sep="")
        if A == 4:
            fail = 1
            #轉成語音say()
            input_ans = str(input_ans)
            say('恭喜答對 '+input_ans)
            #print("Bingo", input_ans)
            break
    if fail == 0:
        #轉成語音say()
        n_1 = str(ans[0])
        n_2 = str(ans[1])
        n_3 = str(ans[2])
        n_4 = str(ans[3])
        say('失敗，正確答案是'+n_1+n_2+n_3+n_4)
        #print("Fail.The answer is ",ans[0],ans[1],ans[2],ans[3])
    event.set()
    workQueue.get()

def schedule():
    event.clear()
    print ('in process')
    curtime = present_time()
    year = 0
    month = 0
    day = 0
    hour = 0
    min = 0
    noticetime = 0
    process = []
    say('請問要加入刪除或是查詢行程')
    while True:
        response = client.recognize(language_code=args.language,hint_phrases=hints)
        if response is None:
            print ('NULL')
            continue
        print (response)
        if response == '加入':
            while True:
                say('請問形成年份是否為' + curtime[0] + ' 本行事曆最久提供至隔年')
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                if 'yes' == response or '沒錯' == response or '是' == response or '答對' == response or '賓果' == response or '正確' == response or '對' == response:
                    print (response)
                    year = str(2022)
                elif 'no' == response or '錯' == response or '不是' == response or '答錯' == response or '否' == response:
                    print (response)
                    year = str(2023)
                else:
                    print (response)
                    say('很抱歉 我聽不清楚請再重新輸入一次')
                    continue
                while True:
                    say('請問行程的日期')
                    schedule = client.recognize(language_code=args.language,hint_phrases=hints)
                    print (schedule)
                    if schedule is None:
                        continue
                    timelist = [int(timelist) for timelist in re.findall(r'-?\d+', schedule)]
                    print (timelist)
                    if len(timelist) != 2:
                        say('很抱歉 我聽不清楚請重新輸入')
                        continue
                    break
                #月防呆
                if '取消' == schedule:
                    say('好的 正在為您取消行程建立')
                    event.set()
                    sys.exit(0)
                if timelist[0] < 1 or timelist[0] > 12:
                    say('很抱歉 您輸入的日期超出範圍')
                    continue
                #日防呆
                if timelist[0] == 1 or timelist[0] == 3 or timelist[0] == 5 or timelist[0] == 7 or timelist[0] == 8 or timelist[0] == 10 or timelist[0] == 12:
                    if timelist[1] < 1 or timelist[1] > 31:
                        say('很抱歉 您輸入的日期超出範圍')
                        continue
                elif timelist[0] == 4 or timelist[0] == 6 or timelist[0] == 9 or timelist[0] == 11:
                    if timelist[1] < 1 or timelist[1] > 30:
                        say('很抱歉 您輸入的日期超出範圍')
                        continue
                if timelist[0] == 2:
                    if (curyear % 4 == 0) and (curyear % 100 != 0) or (curyear % 400) == 0:
                        if timelist[1] < 1 or timelist[1] > 29:
                            say('很抱歉 您輸入的日期超出範圍')
                            continue
                    else:
                        if timelist[1] < 1 or timelist > 28:
                            say('很抱歉 您輸入的日期超出範圍')
                            continue
                #與當下時間做比較
                if year == curtime[0]:
                    if str(timelist[0]) < curtime[1]:
                        say('很抱歉 您輸入的日期不符合範圍')
                        continue
                    if str(timelist[0]) == curtime[1] and str(timelist[1]) < curtime[2]:
                        say('很抱歉 您輸入的日期不符合範圍')
                        continue
                month = str(timelist[0])
                day = str(timelist[1])
                print ('month = ', month)
                print ('day = ', day)
                #沒有錯誤，跳出輸入迴圈
                break
            while True:
                say('請問行程幾點幾分')
                schedule = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                timelist = [int(timelist) for timelist in re.findall(r'-?\d+', schedule)]
                print (timelist)
                if '取消' in schedule:
                    say('好的 正在為您取消行程建立')
                    event.set()
                    sys.exit(0)
                #時防呆
                if timelist[0] < 0 or timelist[0] > 24:
                    say('很抱歉 您輸入的時間超出範圍')
                    continue
                #分防呆
                if len(timelist) != 2:
                    if(timelist[1] < 0 or timelist[1] > 60):
                        say('很抱歉 您輸入的時間超出範圍')
                        continue
                    else:
                        timelist[1] = 0
                #與當下時間做比較
                if month == curtime[1] and day == curtime[2]:
                    if str(timelist[0]) < curtime[3]:
                        say('很抱歉 您輸入的時間超出範圍')
                        continue
                    if str(timelist[0]) == curtime[3] and str(timelist[1]) < curtime[4]:
                        say('很抱歉 您輸入的時間超出範圍')
                        continue
                hour = str(timelist[0])
                min = str(timelist[1])
                print ('hour = ', hour)
                print ('min = ', min)
                break
            while True:
                say('請問您的行程是')
                schedule = client.recognize(language_code=args.language,hint_phrases=hints)
                if schedule is None:
                    continue
                if '取消' in schedule:
                    say('好的 正在為您取消行程建立')
                    event.set()
                    sys.exit(0)
                say('請問您的行程是否為'+ schedule)
                judge = client.recognize(language_code=args.language,hint_phrases=hints)
                if judge is None:
                    continue
                if 'yes' == judge  or '沒錯' == judge or '是' == judge or '答對' == judge or '賓果' == judge or '正確' == judge or '對' == judge:
                    print (judge)
                    process = schedule
                    break
                elif 'no' == judge or '錯' == judge or '不是' == judge or '答錯' == judge or '否' == judge:
                    print (judge)
                    say('很抱歉 請再說一次您的行程')
                    continue
                else:
                    print (judge)
                    say('很抱歉 請再說一次您的行程')
                    continue
            while True:
                say('請問您想讓行程提早多久播報呢')
                notice = client.recognize(language_code=args.language,hint_phrases=hints)
                if notice is None:
                    continue
                timelist = [int(timelist) for timelist in re.findall(r'-?\d+', notice)]
                print (timelist)
                if len(timelist) == 2:
                    noticetime = timelist[0] * 60 + timelist[1]
                    break
                elif len(timelist) == 1:
                    if '時' in notice:
                        noticetime = timelist[0] * 60
                        break
                    elif '分' in notice:
                        noticetime = timelist[0]
                        break
                    else:
                        say('很抱歉 我聽不清楚 請重新輸入')
                        continue
                else:
                    say('很抱歉 我聽不清楚 請重新輸入')
                    continue
                noticetime = str(noticetime)
                print (noticetime)
            Data(year, month, day, hour, min, process, noticetime)
            break
        elif response == '刪除':
            conn = sqlite3.connect('rasp.db')
            list = [[0] * 50 for i in range (5)]
            k = 0
            flag = 0
            while True:
                say('請問要刪除的行程為')
                text = client.recognize(language_code=args.language, hint_phrases=hints)
                if text is None:
                    continue
                if '取消' == text:
                    say('好的 正在為您取消行程刪除')
                    event.set()
                    sys.exit(0)
                say('請問欲刪除的行程是否為'+ text)
                judge = client.recognize(language_code=args.language,hint_phrases=hints)
                if 'yes' == judge  or '沒錯' == judge or '是' == judge or '答對' == judge or '賓果' == judge or '正確' == judge or '對' == judge:
                    print (judge)
                    cursor = conn.cursor()
                    results = cursor.execute("SELECT * FROM MUSICBOX")
                    for item in results:
                        if item[7] == text:
                            flag = flag + 1
                            list[0][k] = item[2] #month
                            list[1][k] = item[3] #day
                            list[2][k] = item[4] #hour
                            list[3][k] = item[5] #min
                            list[4][k] = item[0] #id
                            k = k + 1
                    if flag == 0:
                        say('很抱歉 我在行程中找不到'+ text)
                        break
                    elif flag == 1:
                        print ('Before change')
                        results = cursor.execute("SELECT * FROM MUSICBOX")
                        for item in results:
                            print (item)
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM MUSICBOX WHERE name = '"+text+"'")
                        conn.commit()
                    else:
                        say ('我在資料庫中找到' + str(k) + '筆有關' + text + '的資料')
                        say ('它們分別是')
                        for j in range(k):
                            say('ID' + list[4][j] + '號' + list[0][j] + '月' + list[1][j] + '日' + list[2][j] + '時' + list[3][j] + '分')
                            time.sleep(1)
                        say ('請問您想要刪除的行程為ID幾號')
                        while True:
                            flag2 = 0
                            delete = client.recognize(language_code=args.language,hint_phrases=hints)
                            num = [int(num) for num in re.findall(r'-?\d+', delete)]
                            print (delete)
                            print (num)
                            if delete is None:
                                print ('NULL')
                                continue
                            if len(num) < 1:
                                print('NULL')
                                continue
                            elif '取消' in delete:
                                event.set()
                                workQueue.get()
                                sys.exit(0)
                            print (str(num[0]))
                            for a in range(k):
                                print ("hello")
                                print (str(list[4][a]))
                                if str(num[0]) ==  str(list[4][a]):
                                    print ('in if')
                                    flag2 = 1
                                    break
                            print ("flag2 = " + str(flag2))
                            if flag2 == 1:
                                say ('正在為您刪除第' + str(num[0]) + '筆行程')
                                print ('Before change')
                                for item in results:
                                    print (item)
                                cursor = conn.cursor()
                                results = cursor.execute("SELECT * FROM MUSICBOX")
                                strnum = str(num[0])
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM MUSICBOX WHERE ID = '"+strnum+"'")
                                conn.commit()
                                break
                            else:
                                say ('很抱歉我聽不清楚 請重新輸入')
                                continue
                    say('行程刪除成功')
                    print ('After change')
                    results = cursor.execute("SELECT * FROM MUSICBOX")
                    for item in results:
                        print (item)
                    break
                #elif 'no' or '錯' or '不是' or '答錯' or '否' in judge:
                    #print (judge)
                    #say('行程刪除失敗 請重新輸入')
                    #continue
                else:
                    print (judge)
                    say('行程刪除失敗 請重新輸入')
                    continue
            cursor.close()
            conn.close()
            break
        elif response == '查詢':
            flag = 0
            conn = sqlite3.connect("rasp.db")
            cursor = conn.cursor()
            while True:
                say('請問您需要查詢哪一天的行程')
                schedule = client.recognize(language_code=args.language,hint_phrases=hints)
                timelist = [int(timelist) for timelist in re.findall(r'-?\d+', schedule)]
                if schedule is None:
                    say('很抱歉 我聽不清楚 請重新輸入')
                    print ('NULL')
                    continue
                if '取消' in schedule:
                    say('好的 正在為您取消行程查詢')
                    break
                print (timelist)
                results = cursor.execute("SELECT * FROM MUSICBOX")
                for item in results:
                    if item[2] == str(timelist[0]).zfill(2) and item[3] == str(timelist[1]).zfill(2):
                        flag = 1
                        say(item[4] + '點' + item[5] + '分有行程' + item[7])
                results = cursor.execute("SELECT * FROM MUSICBOX")
                for item in results:
                    print (item)
                if flag == 0:
                    say('很抱歉 我在這天找不到任何的行程')
                    break
            cursor.close()
            conn.close()
            break
        else:
            say('很抱歉 我聽不清楚 請重新輸入')
            continue
    event.set()
    workQueue.get()


def music():
    event.clear()
    flag = 0
    global music_flag
    global video
    global best
    global playurl
    global Instance
    global player
    global Media
    url = []
    musiclist = [[0] * 10 for i in range (3)]
    while True:
        say('請問你要播甚麼歌')
        musicname = client.recognize(language_code=args.language,hint_phrases=hints)
        print (musicname)
        if musicname is None:
            continue
        if '取消' in musicname:
            say('好的 正在為您取消播放音樂')
            event.set()
            sys.exit(0)
        else:
            conn = sqlite3.connect('rasp.db')
            cursor = conn.cursor()
            results = cursor.execute("SELECT * FROM music")
            for item in results:
                if item[0] == musicname:
                    print ("qazwsxedc789456123")
                    musiclist[0][flag] = item[0]
                    musiclist[1][flag] = item[1]
                    musiclist[2][flag] = item[2]
                    flag = flag + 1
        if flag == 0:
            print ("資料庫查無此音樂")
            say('資料庫查無此音樂')
            while True:
                say('請問要繼續查詢資料庫或是結束音樂功能')
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    say('很抱歉 我聽不清楚 請重新輸入')
                    print ('NULL')
                    continue
                elif response == '繼續查詢':
                    break
                elif response == '結束音樂功能':
                    event.set()
                    sys.exit(0)
            continue
        elif flag == 1:
            url = musiclist[2][0]
            break
        else:
            name = []
            say('資料庫中有' + flag + '筆歌名為' + musiclist[0][0] + '的資料 請問你要點播的歌手是')
            for i in range (flag):
                say('musiclist[1][i]')
                time.sleep(2)
            while True:
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    say('很抱歉 我聽不清楚 請重新輸入')
                    print ('NULL')
                    continue
                else:
                    name = response
                    break
            for i in range (flag):
                if name == musiclist[1][i]:
                    url = musiclist[2][i]
                    break
            break
    cursor.close()
    conn.close()
    print ("123")
    say('正在為您播放' + musicname)
    print (url)
    video = pafy.new(url)
    best = video.getbest()
    playurl = best.url
    Instance = vlc.Instance("--verbose=0","--no-xlib")
    player = Instance.media_player_new()
    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)

    player.play()
    player.audio_set_volume(50)
    while True:
        music_flag = 3
        with Board() as board:
            board.button.wait_for_press()
            start = time.time()
            board.led.state = Led.ON
            board.button.wait_for_release()
            end = time.time()
            board.led.state = Led.OFF
            state = float(format(end-start))
            if state > float(2):
                player.stop()
                player.release()
                music_flag = 6
                break
            else:  #pause or play
                if player.is_playing():
                    player.pause()
                    music_flag = 4
                else:
                    player.play()
                    music_flag = 3

    video = None
    best = None
    playurl = None
    Instance = None
    player = None
    Media = None

    event.set()
    workQueue.get()

def calculator():
    event.clear()
    say('請問您要哪種計算方式')
    while True:
        type = client.recognize(language_code=args.language,hint_phrases=hints)
        print (type)
        if type is None:
            continue
        if '取消' in type:
            say('好的 正在為您取消計算機')
            event.set()
            sys.exit(0)
        if '加法' in type:
            while True:
                say('請問算式是')
                calculate = client.recognize(language_code=args.language,hint_phrases=hints)
                if calculate is None:
                    continue
                numlist = [int(numlist) for numlist in re.findall(r'-?\d+', calculate)]
                print (numlist)
                if len(numlist) != 2:
                    say('很抱歉我聽不清楚 請重新再說一遍')
                    continue
                num1 = str(numlist[0])
                num2 = str(numlist[1])
                say('請問您是否要計算' + num1 + '加' + num2)
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                if 'yes' or '沒錯' or '是' or '答對' or '賓果' or '正確' or '對' in response:
                    ans = numlist[0] + numlist[1]
                    num3 = str(ans)
                    say('答案是' + num3)
                else:
                    continue
                break
        elif '減法' in type or '剪髮' in type:
            while True:
                say('請問算式是')
                calculate = client.recognize(language_code=args.language,hint_phrases=hints)
                if calculate is None:
                    continue
                numlist = [int(numlist) for numlist in re.findall(r'-?\d+', calculate)]
                print (numlist)
                if len(numlist) != 2:
                    say('很抱歉我聽不清楚 請重新再說一遍')
                    continue
                num1 = str(numlist[0])
                num2 = str(numlist[1])
                say('請問您是否要計算' + num1 + '減' + num2)
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                if 'yes' or '沒錯' or '是' or '答對' or '賓果' or '正確' or '對' in response:
                    ans = numlist[0] - numlist[1]
                    num3 = str(ans)
                    say('答案是' + num3)
                else:
                    continue
                break
        elif '乘法' in type:
            while True:
                say('請問算式是')
                calculate = client.recognize(language_code=args.language,hint_phrases=hints)
                if calculate is None:
                    continue
                numlist = [int(numlist) for numlist in re.findall(r'-?\d+', calculate)]
                print (numlist)
                if len(numlist) != 2:
                    say('很抱歉我聽不清楚 請重新再說一遍')
                    continue
                num1 = str(numlist[0])
                num2 = str(numlist[1])
                say('請問您是否要計算' + num1 + '乘以' + num2)
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                if 'yes' or '沒錯' or '是' or '答對' or '賓果' or '正確' or '對' in response:
                    ans = numlist[0] * numlist[1]
                    num3 = str(ans)
                    say('答案是' + num3)
                else:
                    continue
                break
        elif '除法' in type:
            while True:
                say('請問算式是')
                calculate = client.recognize(language_code=args.language,hint_phrases=hints)
                if calculate is None:
                    continue
                numlist = [int(numlist) for numlist in re.findall(r'-?\d+', calculate)]
                print (numlist)
                if len(numlist) != 2:
                    say('很抱歉我聽不清楚 請重新再說一遍')
                    continue
                num1 = str(numlist[0])
                num2 = str(numlist[1])
                say('請問您是否要計算' + num1 + '除以' + num2)
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                if 'yes' or '沒錯' or '是' or '答對' or '賓果' or '正確' or '對' in response:
                    ans1 = numlist[0] / numlist[1]
                   # ans2 = numlist[0] % numlist[1]
                    num3 = str(ans1)
                   # num4 = str(ans2)
                   # if ans2 == 0:
                    say('答案是' + num3)
                    #else:
                       # say('答案是' + num3 + '餘' + num4)
                else:
                    continue
                break
        elif '指數' in type:
            while True:
                say('請問算式是')
                calculate = client.recognize(language_code=args.language,hint_phrases=hints)
                if calculate is None:
                    continue
                numlist = [int(numlist) for numlist in re.findall(r'-?\d+', calculate)]
                print (numlist)
                if len(numlist) != 2:
                    say('很抱歉我聽不清楚 請重新再說一遍')
                    continue
                num1 = str(numlist[0])
                num2 = str(numlist[1])
                say('請問您是否要計算' + num1 + '的' + num2 + '次方')
                response = client.recognize(language_code=args.language,hint_phrases=hints)
                if response is None:
                    continue
                if 'yes' or '沒錯' or '是' or '答對' or '賓果' or '正確' or '對' in response:
                    ans = numlist[0] ** numlist[1]
                    num3 = str(ans)
                    say('答案是' + num3)
                else:
                    continue
                break
        else:
            say('很抱歉 請再說一次計算方式')
            continue
        break
    event.set()
    workQueue.get()

def playradio(url):
    action = "killall mplayer"
    os.system(action)
    action = "mplayer " + url + " > /dev/null &"
    os.system(action)

def radio1():
    url = "http://live.leanstream.co/ICRTFM-MP3?args=tunein_mp3"
    playradio(url)
    with Board() as board:
        while True:
            board.button.wait_for_press()
            board.led.state = Led.BLINK
            stop()
            board.led.state = Led.OFF
            break

    #return template('music.html')

def radio2():
    action = "killall mplayer"
    os.system(action)
    url = "http://asiafm.rastream.com/asiafm-fly"
    playradio(url)
    with Board() as board:
        while True:
            board.button.wait_for_press()
            board.led.state = Led.ON
            stop()
            board.button.wait_for_release()
            board.led.state = Led.OFF
            break
    #run(host='0.0.0.0', port=8080)
    #return template('music.html')

'''def radio3():
    url = "https://www.espn.com/radio/play/_/s/espn"
    playradio(url)
    run(host='0.0.0.0', port=8080)
    return template('music.html')'''

def stop():
    action = "killall mplayer"
    os.system(action)

def radio():
    event.clear()
    say('請問您要收聽一號電台ICRT,二號電台Asia FM哪一個電台呢')
    while True:
        radioID = client.recognize(language_code=args.language,hint_phrases=hints)
        print(radioID)
        if radioID is None:
            continue
        if '取消' in radioID:
            say('好的 正在為您取消收音機')
            event.set()
            sys.exit(0)
        if '一號' in radioID or '1號' in radioID:
            radio1()
        elif '二號' in radioID or '2號' in radioID:
            radio2()
        '''elif '三號' in radioID or '3號' in radioID:
            radio3()
            while True:
                response = client.recognize(language_code=args.language,hint_phrases=hints)

                if response is None:
                    continue
                if response == '停止':
                    stop()
                    break'''
        break
    event.set()
    workQueue.get()

def weather():
    event.clear()
    say('請問您要播報哪裡的氣溫呢')
    while True:
        location = client.recognize(language_code=args.language,hint_phrases=hints)
        print(location)
        #location.encode('utf-8')
        if location is None:
            continue
        if '取消' in location:
            say('好的 正在為您取消氣溫播報')
            event.set()
            sys.exit(0)
        else:
            url='https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0001-001?Authorization=CWB-837D91EA-55ED-40C3-B5B3-2B97A191C650&format=JSON&locationName='+urllib.parse.quote(location)+'&elementName=TEMP'
            #url.encode('utf-8')
            site = ur.urlopen(url)
            page = site.read()
            contents = page.decode()
            data = json.loads(contents)
            temp = data['records']['location'][0]['weatherElement'][0]['elementValue']
            print(temp)
            say('氣溫為' + temp + '度')
        break
    event.set()
    workQueue.get()

def record():
    event.clear()
    say('請問您的錄音檔要取名為什麼呢')
    while True:
        name = client.recognize(language_code=args.language,hint_phrases=hints)
        print (name)
        if name is None:
            continue
        if '取消' in name:
            say('好的 正在為您取消錄音')
            event.set()
            sys.exit(0)
        say('請問您的錄音要幾秒')
        while True:
            response = client.recognize(language_code=args.language,hint_phrases=hints)
            if response is None:
                continue
            print(response)
            secondlist = [int(timelist) for timelist in re.findall(r'-?\d+', response)]
            print (secondlist)
            second = secondlist[0]
            chunk = 1024                     # 記錄聲音的樣本區塊大小
            sample_format = pyaudio.paInt16  # 樣本格式，可使用 paFloat32、paInt32、paInt24、paInt16、paInt8、paUInt8、paCustomFormat
            channels = 2                     # 聲道數量
            fs = 44100                       # 取樣頻率，常見值為 44100 ( CD )、48000 ( DVD )、22050、24000、12000 和 11025。
            seconds = float(second)                    # 錄音秒數
            filename = name +'.wav'      # 錄音檔名
            print(filename)

            p = pyaudio.PyAudio()            # 建立 pyaudio 物件
            break

        print("開始錄音...")
        say('開始錄音')

        # 開啟錄音串流
        stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)

        frames = []                      # 建立聲音串列

        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)          # 將聲音記錄到串列中
            '''stream.stop_stream()             # 停止錄音
            stream.close()                   # 關閉串流
            p.terminate()
            break'''

        '''data = stream.read(chunk)
            frames.append(data)          # 將聲音記錄到串列中

        stream.stop_stream()             # 停止錄音
        stream.close()                   # 關閉串流
        p.terminate()'''

        print('錄音結束...')
        say('錄音結束')

        wf = wave.open(filename, 'wb')   # 開啟聲音記錄檔
        wf.setnchannels(channels)        # 設定聲道
        wf.setsampwidth(p.get_sample_size(sample_format))  # 設定格式
        wf.setframerate(fs)              # 設定取樣頻率
        wf.writeframes(b''.join(frames)) # 存檔
        wf.close()

        break

    event.set()
    workQueue.get()


threadList = ["process", "music", "search", "iot", "calculator", "radio", "weather", "record", "game"]
workQueue = queue.Queue(10)
threads = []
threadID = 1

def output():
    global music_flag
    global video
    global best
    global playurl
    global Instance
    global player
    global Media
    output_time = 0
    while True:
        conn = sqlite3.connect('rasp.db')
        cursor = conn.cursor()
        results = cursor.execute("SELECT * FROM MUSICBOX")
        curtime = present_time()
        time_now = curtime[0] + curtime[1].zfill(2) + curtime[2].zfill(2) + curtime[3].zfill(2) + curtime[4].zfill(2)
        sign = 2
        for item in results:
            if time_now > item[6]:
                cursor.execute("DELETE from MUSICBOX where id = '"+item[0]+"'")
                conn.commit()
                output_time = 0
        results = cursor.execute("SELECT * FROM MUSICBOX")
        for item in results:
            if curtime[0] == item[1] and curtime[1] == item[2] and curtime[2] == item[3]:
                hour = 0
                min = int(item[8])
                while True:
                    if int(item[8]) > 59:
                        min = int(item[8]) - 60
                        hour = hour + 1
                    else:
                        break
                fnlhr = int(curtime[3]) + hour
                fnlmn = int(curtime[4]) + min
                if fnlmn > 59:
                    fnlhr = fnlhr + 1
                    fnlmn = fnlmn - 60
                if item[4] == str(fnlhr) and item[5] == str(fnlmn):
                    if output_time == 0:
                        output_control.set()
                        if music_flag == 3:
                            player.pause()
                            time.sleep(1)
                            say('提醒您 您的行程' + item[7] + '即將到來')
                            print ('提醒您 您的行程' + item[7] + '即將到來')
                            time.sleep(1)
                            player.play()
                        else:
                            while True:
                                if say_control.is_set():
                                    continue
                                else:
                                    outputsay('提醒您 您的行程' + item[7] + '即將到來')
                                    print ('提醒您 您的行程' + item[7] + '即將到來')
                                    break
                        output_time = output_time + 1
                        output_control.clear()
        cursor.close()
        conn.close()


if __name__== '__main__':

    t = myThread("output")
    workQueue.put(t)
    t.start()


    radio_flag = 0
    event.set()
    while True:
        while output_control.is_set():
            if thread.name == 'radio':
                if thread.is_alive():
                    radio_falg = 1
                    thread.join()
        if radio_flag == 1:
            radio_flag = 0
            thread.run()
        while event.is_set():
            print ('1')
            response = client.recognize(language_code=args.language, hint_phrases=hints)
            print ('2')
            print (response)
            if response is None:
                continue
            if '智慧音箱' in response:
                say('請問您需要甚麼功能')
                while event.is_set():
                    function = client.recognize(language_code=args.language, hint_phrases=hints)
                    if function is None:
                        continue
                    if '行程'in function:
                        thread = myThread("schedule")
                        workQueue.put(thread)
                        thread.start()
                    elif '音樂' in function:
                        thread = myThread("music")
                        workQueue.put(thread)
                        thread.start()
                    elif '計算機' in function:
                        thread = myThread("calculator")
                        workQueue.put(thread)
                        thread.start()
                    elif '收音機' in function:
                        thread = myThread("radio")
                        workQueue.put(thread)
                        thread.start()
                    elif '天氣' in function:
                        thread = myThread("weather")
                        workQueue.put(thread)
                        thread.start()
                    elif '遊戲' in function:
                        thread = myThread("game")
                        workQueue.put(thread)
                        thread.start()
                    elif '錄音' in function:
                        thread = myThread("record")
                        workQueue.put(thread)
                        thread.start()
                    elif '搜尋' in function:
                         print ('in 搜尋')
                    elif '連線' in function:
                         print ('in iot')
                    elif '時間' in function:
                        say('現在時間為'+ datetime.datetime.now().strftime("%H") + '點' + datetime.datetime.now().strftime("%M") + '分')
                    elif '再見' in function:
                        os._exit(0)
                    else:
                        say('很抱歉 請您再重新說一次')
                        continue

