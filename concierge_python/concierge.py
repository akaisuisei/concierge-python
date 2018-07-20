import json
import requests
import paho.mqtt.client as mqtt
import utils

class Topic():

    live = 'concierge/apps/live'
    view = 'concierge/apps/{}/view'
    livePing = '{}/ping'.format(live)
    livePong = '{}/pong'.format(live)
    viewPing = '{}/ping'.format(view)
    viewPong = '{}/pong'.format(view)
    led = 'concierge/feedback/led/default/'
    timerLed = '{}timer'.format(led)
    timeLed = '{}timer'.format(led)
    weatherLed = '{}weather'.format(led)
    @staticmethod
    def getViewPong(appId):
        return Topic.viewPong.format(appId)

    @staticmethod
    def getViewPing(appId):
        return Topic.viewPing.format(appId)

class Concierge:
    def __init__(self, hostname):
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.connect(hostname)
        self._client.loop_start()
        self.topics = []
        self.subscribe(Topic.livePing, self.on_ping)

    def subscribe(self, topic, func = None):
        self._client.subscribe(topic)
        self.topics += [topic]
        if (func):
            self._client.message_callback_add(topic, func)
    def subscribePing(self, func = None):
        if (func):
            self._client.message_callback_add(Topic.livePing, func)

    def subscribeView(self, id, func):
        if (func and id and id != ""):
            self.subscribe(Topic.getViewPing(id), func)

    def unsubscribe(self, topic):
        self._client.unsubscribe(topic)

    def publish(self, topic, msg):
        print("{} on {}".format(msg, topic))
        self._client.publish(topic, msg)

    def publishTimer(self, duration):
        self.publish(Topic.timerLed, json.dumps({"duration":duration}))

    def publishView(self, id, payload):
        payload = {"result": payload}
        self.publish(Topic.getViewPong(id), json.dumps(payload))

    def publishPong(self, app):
        payload = json.dumps({"result": app })
        self.publish(Topic.livePong, payload)
    def publishTime(self, value):
        self.publish(Topic.timeLed, json.dumps({"duration":duration}))

    def publishWeather(self, cond, temp):
        self.publish(Topic.timeLed, json.dumps({
            "weather": cond,
            "temp": temp
        }))

    def publishStopLed(self):
        self.publish('concierge/feedback/led/default/stop', '')

    def on_connect(self, client, userdata, flags, rc):
        for t in self.topics:
            client.subscribe(t)

    def on_ping(self, client, userdata, msg):
        print(msg.payload)

    def on_message(self, client, userdata, msg):
        print(msg.topic)
    def play_wave(self, siteId, requestId, filename):
        utils.play_wave(self._client, siteId, requestId, filename)

    @staticmethod
    def getLang(default = "FR"):
        try:
            tmp = requests.get("http://localhost:3000/assistant/lang");
            print(tmp)
            if (not tmp.ok):
                return default
            return json.loads(tmp.text).upper().encode('ascii', 'ignore')
        except :
            return default

