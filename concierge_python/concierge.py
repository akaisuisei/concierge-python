import json
import requests
import paho.mqtt.client as mqtt
import utils
def p_subscribe(topic):
    def wrapper(func):
        if (func):
            return
        func(topic, name)
    return wrapper

class Topic():
    class Led():
        _led = 'concierge/feedback/led/{}/'
        _add_image = '{}/add/'.format(_led)
        _animation = '{}/animation'.format(_led)
        _rotary = '{}/rotary'.format(_led)
        _stop = '{}/stop'.format(_led)
        _swipe = '{}/swipe'.format(_led)
        _timer = '{}timer'.format(_led)
        _time = '{}timer'.format(_led)
        _weather = '{}weather'.format(_led)
        @staticmethod
        def add_image(siteId):
            return Topic.Led._add_image.format(siteId) + "#"
        @staticmethod
        def add_image_send(siteId, dir_, name):
            img = Topic.Led._add_image.format(siteId)
            return "{}{}/{}".format(img, dir_, name)
        @staticmethod
        def animation(siteId):
            return Topic.Led._animation.format(siteId)
        @staticmethod
        def rotary(siteId):
            return Topic.Led._rotary.format(siteId)
        @staticmethod
        def stop(siteId):
            return Topic.Led._stop.format(siteId)
        @staticmethod
        def swipe(siteId):
            return Topic.Led._swipe.format(siteId)
        @staticmethod
        def timer(siteId):
            return Topic.Led._timer.format(siteId)
        @staticmethod
        def time(siteId):
            return Topic.Led._time.format(siteId)
        @staticmethod
        def weather(siteId):
            return Topic.Led._weather.format(siteId)
    class Apps:
        _live = 'concierge/apps/live'
        _view = 'concierge/apps/{}/view'
        livePing = '{}/ping'.format(_live)
        livePong = '{}/pong'.format(_live)
        _viewPing = '{}/ping'.format(_view)
        _viewPong = '{}/pong'.format(_view)
        @staticmethod
        def viewPong(appId):
            return _viewPong.format(appId)
        @staticmethod
        def viewPing(appId):
            return _viewPing.format(appId)
    class Command():
        _rotary = 'concierge/commands/remote/rotary'
        _swipe = 'concierge/commands/remote/swipe'
        @staticmethod
        def rotary(siteId):
            return Topic.Command._rotary.format(siteId)
        @staticmethod
        def swipe(siteId):
            return Topic.Command._swipe.format(siteId)

class Concierge:
    def __init__(self, hostname, siteId = "default", start = True):
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.connect(hostname)
        self.topics = []
        self._siteId =  siteId
        if start:
            self._client.loop_forever()

    def loop_forever(self):
        self._client.loop_forever()

    def subscribe(self, topic, func = None):
        self._client.subscribe(topic)
        self.topics += [topic]
        if (func):
            self._client.message_callback_add(topic, func)

    def subscribePing(self, func = None):
        if (func):
            self._client.message_callback_add(Topic.Apps.livePing, func)
    def subscribeView(self, func):
            self.subscribe(Topic.Apps.viewPing(self._siteId), func)

    def subscribeTime(self, func):
            self.subscribe(Topic.Led.time(self._siteId), func)
    def subscribeTimer(self, func):
            self.subscribe(Topic.Led.timer(self._siteId), func)
    def subscribeAnimation(self, func):
            self.subscribe(Topic.Led.animation(self._siteId), func)
    def subscribeWeather(self, func):
            self.subscribe(Topic.Led.weather(self._siteId), func)
    def subscribeStop(self, func):
            self.subscribe(Topic.Led.stop(self._siteId), func)
    def subscribeRotary(self, func):
            self.subscribe(Topic.Led.rotary(self._siteId), func)
    def subscribeSwipe(self, func):
            self.subscribe(Topic.Led.swipe(self._siteId), func)
    def subscribeImage(self, func):
            self.subscribe(Topic.Led.add_image(self._siteId), func)

    def publish(self, topic, msg):
        print("{} on {}".format(msg, topic))
        self._client.publish(topic, msg)

    def publishTimer(self, duration):
        self.publish(Topic.timerLed, json.dumps({"duration":duration}))

    def publishView(self, _id, payload):
        payload = {"result": payload}
        self.publish(Topic.getViewPong(_id), json.dumps(payload))

    def publishPong(self, app):
        payload = json.dumps({"result": app })
        self.publish(Topic.Apps.pong, payload)

    def publishTime(self, value):
        self.publish(Topic.Led.time, json.dumps({"duration":duration}))

    def publishWeather(self, cond, temp):
        self.publish(Topic.Led.weather(self._siteId), json.dumps({
            "weather": cond,
            "temp": temp
        }))

    def publishStopLed(self):
        self.publish(Topic.Led.stop(self._siteId), '')
    def publishRotary(self, value):
        self.publish(Topic.Led.rotary(self._siteId), value)
    def publishSwipe(self, value):
        self.publish(Topic.Led.swipe(self._siteId), value)

    def play_wave(self, siteId, requestId, filename):
        utils.play_wave(self._client, siteId, requestId, filename)
    def startHotword(self, modelId = 'default'):
        self.publish("hermes/hotword/default/detected",
                   json.dumps({"siteId" : self.siteId,
                               "modelId" : modelId}))
    def stopHotword(self, sessionId):
        self.publish("hermes/asr/stopListening",
                   json.dumps({"siteId" : self.siteId,
                               "sessionId" : sessionId}))
    def publishImage(self, filename, dir_, name):
        with open(filename, "r") as f:
            content = f.read()
            client.publish(Topic.Led.add_image_send(self.siteId, dir_, name),
                           bytearray(content))

    def on_connect(self, client, userdata, flags, rc):
        for t in self.topics:
            client.subscribe(t)

    def on_message(self, client, userdata, msg):
        print(msg.topic)

    def disconnect(self):
        self._client.disconnect()

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

