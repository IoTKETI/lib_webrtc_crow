# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_Options
from selenium.webdriver.firefox.options import Options as firefox_Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
import paho.mqtt.client as mqtt
from pyvirtualdisplay import Display
import os
import sys
import time
import platform

drone = ''
host = ''

lib_mqtt_client = None
broker_ip = 'localhost'
port = 1883

control_topic = ''

argv = sys.argv
flag = 0

status = 'ON'
driver = None
display = None


def openWeb(url):
    global status
    global display
    global driver


    with Display(visible=False, size=(1920, 1080)) as disp:
        print('xvfb:', os.environ['DISPLAY'])
        with Display(visible=True, size=(1920, 1080)) as v_disp:
            if ('64' in platform.processor()):
                firefox_options = firefox_Options()
                firefox_options.set_preference("media.navigator.permission.disabled", True)
                driver = webdriver.Firefox(options=firefox_options)
            else:
                chrome_options = chrome_Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--single-process")
                chrome_options.add_argument("--disable-dev-shm-usage")

                chrome_options.add_experimental_option("prefs", {
                    "profile.default_content_setting_values.media_stream_mic": 1,
                    "profile.default_content_setting_values.media_stream_camera": 1
                })
                chrome_options.add_argument("--use-fake-ui-for-media-stream")  # 권한 요청 자동 승인
                
                capabilities = DesiredCapabilities.CHROME
                capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}

                driver = webdriver.Chrome(service=Service('/usr/lib/chromium-browser/chromedriver'), options=chrome_options, desired_capabilities=capabilities)

            print(url)
            driver.get(url)
            control_web()
    '''
    if ('64' in platform.processor()):
        firefox_options = firefox_Options()
        firefox_options.set_preference("media.navigator.permission.disabled", True)
        driver = webdriver.Firefox(options=firefox_options)
    else:
        chrome_options = chrome_Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--single-process")
        chrome_options.add_argument("--disable-dev-shm-usage")
    
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1
        })
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # 권한 요청 자동 승인
    
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}
    
        driver = webdriver.Chrome(service=Service('/usr/lib/chromium-browser/chromedriver'), options=chrome_options, desired_capabilities=capabilities)
    '''

    print(url)
    driver.get(url)
    control_web()


def control_web():
    global broker_ip
    global port
    global sendSource

    msw_mqtt_connect(broker_ip)

    if len(sendSource) > 2:
        if sendSource[1] == 'screen' or sendSource[1] == 'window':
            import pyautogui
            time.sleep(5)
            print('press key')
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('enter')

    while True:
        pass


def msw_mqtt_connect(server):
    global lib_mqtt_client
    global control_topic
    global sendSource

    lib_mqtt_client = mqtt.Client()
    lib_mqtt_client.on_connect = on_connect
    lib_mqtt_client.on_disconnect = on_disconnect
    lib_mqtt_client.on_subscribe = on_subscribe
    lib_mqtt_client.on_message = on_message
    lib_mqtt_client.connect(server, 1883)
    control_topic = '/MUV/control/lib_webrtc_crow/Control/' + sendSource[0]
    print(control_topic)
    lib_mqtt_client.subscribe(control_topic, 0)

    lib_mqtt_client.loop_start()

    return lib_mqtt_client


def on_connect(client, userdata, flags, rc):
    print('[msg_mqtt_connect] connect to ', broker_ip)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    global control_topic
    global driver
    global flag
    global status
    global display
    global webRtcUrl

    if msg.topic == control_topic:
        con = msg.payload.decode('utf-8').upper()
        if con == 'ON':
            print('recieved ON message')
            if flag == 0:
                flag = 1
                openWeb(webRtcUrl)
            elif flag == 1:
                flag = 0
            status = 'ON'
        elif con == 'OFF':
            print('recieved OFF message')
            driver.quit()
            driver = None
            flag = 0
            status = 'OFF'
            # display.stop()


if __name__ == '__main__':
    webRtcUrl = 'https://'
    # https: // {0} / drone?id = {2} & audio = true & gcs = {1}
    host = argv[1]  # argv[1]  # {{WebRTC_URL}} : "webrtc.server.com:7598"
    drone = argv[2]  # argv[2]  # {{Drone_Name}} : "drone_name"
    gcs = argv[3]  # argv[3]  # {{GCS_Name}} : "gcs_name"
    # argv[4] # {{Source}} : "camera=webcam" or "camera1=rtsp-rtsp://192.168.1.1/stream0" or "camera2=screen"
    Source = argv[4]

    webRtcUrl = webRtcUrl + host
    if '7598' in host:
        webRtcUrl = webRtcUrl + '/drone?id=' + drone + '&gcs=' + gcs
        sendSource = Source.split('=')

        if sendSource[1] == 'webcam':
            webRtcUrl = webRtcUrl + '&audio=true'
        elif sendSource[1] == 'screen' or sendSource[1] == 'window':
            webRtcUrl = webRtcUrl + '&sendSource=' + sendSource[1] + '&audio=true'
        elif 'rtsp' in sendSource[1]:
            rtspUrl = Source.split('-')[1]
            webRtcUrl = webRtcUrl + '&rtspUrl=' + rtspUrl + '&audio=true'
        else:
            webRtcUrl = webRtcUrl + '&audio=true'
    elif '7720' in host:
        webRtcUrl = webRtcUrl + '/publisher?droneName=' + drone + '&gcsId=' + gcs + '&cameraName=camera'
        # TODO: rtsp 연동
    else:
        webRtcUrl = webRtcUrl + '/pub?id=' + drone + '&gcs=' + gcs

        sendSource = Source.split('=')
        webRtcUrl = webRtcUrl + '&streamId=' + sendSource[0]

    time.sleep(1)
    openWeb(webRtcUrl)

    status = 'ON'
    flag = 1

# python3 -m PyInstaller -F lib_webrtc_crow.py
