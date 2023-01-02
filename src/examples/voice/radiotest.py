#!/usr/bin/env python3
from bottle import route, run, template
import os
from aiy.board import Board, Led

def playradio(url):
    action = "killall mplayer"  
    os.system(action)
    action = "mplayer " + url + " > /dev/null &"  
    os.system(action)
'''
#@route('/1')
def radio1():
    url = "http://live.leanstream.co/ICRTFM-MP3?args=tunein_mp3"
    playradio(url)
    run(host='0.0.0.0', port=3000)
    print (1)
    with Board() as board:
                while True:
                    board.button.when_pressed
                    board.led.state = BLINK
                    stop()
    return template('music.html')

#@route('/2')
def radio2():
    url = "http://stream.superfm99-1.com.tw:8555/"  
    playradio(url)
    return template('music.html')
    
#@route('/3')
def radio3():
    url = "http://asiafm.rastream.com/asiafm-fly"  
    playradio(url)
    return template('music.html')
''' 
#@route('/stop')
def stop():
    action = "killall mplayer"  
    os.system(action)
    return template('music.html')
'''
@route('/')
def index():
    return template('music.html')
''' 

url = "http://live.leanstream.co/ICRTFM-MP3?args=tunein_mp3"
playradio(url)
print (1)
with Board() as board:
    while True:
        board.button.wait_for_press()
        board.led.state = Led.ON
        stop()
        board.button.wait_for_release()
        board.led.state = Led.OFF
run(host='0.0.0.0', port=3000)
