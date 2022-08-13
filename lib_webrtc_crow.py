# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import paho.mqtt.client as mqtt
from pyvirtualdisplay import Display

import sys
import os
import time

drone = ''
host = ''

broker_ip = 'localhost'
port = 1883

argv = sys.argv
flag = 0

status = 'ON'


def openWeb(host, drone):
    global driver
    global status

    chrome_options = Options()
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1
    })

    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}

    display = Display(visible=0, size=(1920, 1080))
    display.start()

    if sys.platform.startswith('win'):  # Windows
        print('Running LIB on Windows')
        driver = webdriver.Chrome(service=Service('C:/Users/dnjst/Downloads/chromedriver'), options=chrome_options,
                                  desired_capabilities=capabilities)
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):  # Linux and Raspbian
        print('Running LIB on Linux/Rasbian')
        driver = webdriver.Chrome(service=Service('/usr/lib/chromium-browser/chromedriver'), options=chrome_options,
                                  desired_capabilities=capabilities)
    elif sys.platform.startswith('darwin'):  # MacOS
        print('Running browser on MacOS')
        driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=chrome_options,
                                  desired_capabilities=capabilities)

    driver.get("https://{0}/drone?id={1}&audio=true".format(host, drone))
    control_web(driver)


def control_web(driver):
    global broker_ip
    global port

    msw_mqtt_connect(broker_ip, port)

    while True:
        pass


def msw_mqtt_connect(broker_ip, port):
    global lib_mqtt_client
    global control_topic

    lib_mqtt_client = mqtt.Client()
    lib_mqtt_client.on_connect = on_connect
    lib_mqtt_client.on_disconnect = on_disconnect
    lib_mqtt_client.on_subscribe = on_subscribe
    lib_mqtt_client.on_message = on_message
    lib_mqtt_client.connect(broker_ip, port)
    control_topic = '/MUV/control/lib_webrtc_crow/Control'
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
    global con
    global driver
    global flag
    global status

    if msg.topic == control_topic:
        con = msg.payload.decode('utf-8')
        if con == 'ON':
            print('recieved ON message')
            if flag == 0:
                flag = 1
                openWeb(host, drone)
            elif flag == 1:
                flag = 0
            status = 'ON'
        elif con == 'OFF':
            print('recieved OFF message')
            driver.quit()
            driver = None
            flag = 0
            status = 'OFF'


if __name__ == '__main__':
    host = argv[1]  # argv[1]  # {{WebRTC_URL}} : "webrtc.server.com:8883"
    drone = argv[2]  # argv[2]  # {{Drone_Name}} : "drone_name"

    time.sleep(1)

    openWeb(host, drone)
    status = 'ON'
    flag = 1

# python3 -m PyInstaller -F lib_webrtc_crow.py
