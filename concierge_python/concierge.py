from events import Events
import json
import requests
import paho.mqtt.client as mqtt
import concierge_python.utils
def p_subscribe(topic):
    def wrapper(func):
        if (func):
            return
        func(topic, name)
    return wrapper

class Topic():
    class Led():
        _led = 'concierge/feedback/led/{}/'
        _add_image = '{}add/'.format(_led)
        _animation = '{}animation'.format(_led)
        _rotary = '{}rotary'.format(_led)
        _stop = '{}stop'.format(_led)
        _swipe = '{}swipe'.format(_led)
        _timer = '{}timer'.format(_led)
        _time = '{}time'.format(_led)
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
            return Topic.Apps._viewPong.format(appId)
        @staticmethod
        def viewPing(appId):
            return Topic.Apps._viewPing.format(appId)
    class Command():
        _rotary = 'concierge/commands/remote/rotary'
        _swipe = 'concierge/commands/remote/swipe'
        @staticmethod
        def rotary(siteId):
            return Topic.Command._rotary.format(siteId)
        @staticmethod
        def swipe(siteId):
            return Topic.Command._swipe.format(siteId)
    class Utils():
        _play = 'hermes/audioServer/{}/playBytes/#'
        @staticmethod
        def getPlay(site_id):
            return Topic.Utils._play.format(site_id)

class Concierge:
    def __init__(self, hostname, siteId = "default", start = True):
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.connect(hostname)
        self.topics = []
        self._siteId =  siteId
        self.event = Events(('on_ping',
                             'on_view',
                             'on_time',
                             'on_timer',
                             'on_animation',
                            'on_weather',
                            'on_stop',
                            'on_rotary',
                            'on_swipe',
                            'on_image',
                            'on_asr_start',
                            'on_asr_stop',
                            'on_play_bytes'))
        if start:
            self._client.loop_start()

    def loop_forever(self):
        self._client.loop_forever()


    def disconnect(self):
        self._client.disconnect()

    """
    Mqtt callback
    """

    def on_connect(self, client, userdata, flags, rc):
        for t in self.topics:
            client.subscribe(t)

    @staticmethod
    def get_value(json_payload, key = 'value'):
        try:
            data = json.loads(json_payload)
        except:
            return None
        return data.get(key, None)
    def _on_play_bytes(self, client, userdata, msg):
        self.event.on_play_bytes(msg.payload, msg.topic.split('/')[-1])

    def _on_asr_start(self, client, userdata, msg):
        self.event.on_asr_start(client, userdata, msg)
    def _on_asr_stop(self, client, userdata, msg):
        self.event.on_asr_stop(client, userdata, msg)
    def _on_ping(self, client, userdata, msg):
        self.event.on_ping()
    def _on_stop(self, client, userdata, msg):
        self.event.on_stop()
    def _on_view(self, client, userdata, msg):
        self.event.on_view()
    def _on_time(self, client, userdata, msg):
        duration = Concierge.get_value(msg.payload, 'duration')
        value = Concierge.get_value(msg.payload, 'value')
        self.event.on_time(duration, value)
    def _on_animation(self, client, userdata, msg):
        duration = Concierge.get_value(msg.payload, 'duration')
        animation = Concierge.get_value(msg.payload, 'animation')
        self.event.on_animation(animation, duration)
    def _on_timer(self, client, userdata, msg):
        duration = Concierge.get_value(msg.payload, 'value')
        self.event.on_timer(duration)
    def _on_rotary(self, client, userdata, msg):
        self.event.on_rotary(int(msg.payload))
    def _on_swipe(self, client, userdata, msg):
        self.event.on_swipe(msg.payload)
    def _on_weather(self, client, userdata, msg):
        temp = Concierge.get_value(msg.payload, 'temp')
        cond = Concierge.get_value(msg.payload, 'weather')
        self.event.on_weather(temp, cond)

    def _on_image(self, client, userdata, msg):
        tmp = msg.topic.split('/')
        name = tmp [-1]
        directory = tmp[-2]
        if (tmp[-3] != 'add'):
            return
        image = msg.payload
        self.event.on_image(name, directory, image)
    """
    Subscribe
    """
    def subscribe(self, topic, func = None):
        if topic not in self.topics:
            self.topics += [topic]
            self._client.subscribe(topic)
        if (func):
            self._client.message_callback_add(topic, func)
    def subscribeAsrStart(self, func):
        if (func):
            self.event.on_asr_start += func
            self.subscribe("hermes/dialogueManager/sessionStarted", self._on_asr_start)
    def subscribeAsrStop(self, func):
        if (func):
            self.event.on_asr_stop += func
            self.subscribe('hermes/asr/stopListening', self._on_asr_stop)
    def subscribeAnimation(self, func):
        if (func):
            self.event.on_animation += func
            self.subscribe(Topic.Led.animation(self._siteId), self._on_animation)
    def subscribePing(self, func = None):
        if (func):
            self.event.on_ping += func
            self.subscribe(Topic.Apps.livePing, self._on_ping)

    def subscribeView(self, app_id, func):
        if (func):
            self.event.on_view += func
            self.subscribe(Topic.Apps.viewPing(app_id), self._on_view )

    def subscribeTime(self, func):
        if (func):
            self.event.on_time += func
            self.subscribe(Topic.Led.time(self._siteId), self._on_time)
    def subscribeTimer(self, func):
        if (func):
            self.event.on_timer += func
            self.subscribe(Topic.Led.timer(self._siteId), self._on_timer)
    def subscribeWeather(self, func):
        if (func):
            self.event.on_weather += func
            self.subscribe(Topic.Led.weather(self._siteId), self._on_weather)
    def subscribeStop(self, func):
        if (func):
            self.event.on_stop += func
            self.subscribe(Topic.Led.stop(self._siteId), self._on_stop)
    def subscribeRotary(self, func):
        if (func):
            self.event.on_rotary += func
            self.subscribe(Topic.Led.rotary(self._siteId), self._on_rotary)
    def subscribeSwipe(self, func):
        if (func):
            self.event.on_swipe += func
            self.subscribe(Topic.Led.swipe(self._siteId), self._on_swipe)
    def subscribeImage(self, func):
        if (func):
            self.event.on_image += func
            self.subscribe(Topic.Led.add_image(self._siteId), self._on_image)
    def subscribePlayBytes(self, func, siteId = None):
        if siteId is None:
            siteId = self._siteId
        if (func):
            self.event.on_play_bytes += func
            self.subscribe(Topic.Utils.getPlay(siteId),
                           self._on_play_bytes)

    """
    Publish
    """


    def publish(self, topic, msg):
        print("{} on {}".format(msg, topic))
        self._client.publish(topic, msg)

    def publishTimer(self, duration, siteId = None):
        if (siteId is None):
            siteId = self._siteId
        self.publish(Topic.Led.timer(siteId), json.dumps({"value":duration}))

    def publishView(self, _id, payload):
        payload = {"result": payload}
        self.publish(Topic.Apps.viewPong(_id), json.dumps(payload))

    def publishPong(self, app):
        payload = json.dumps({"result": app })
        self.publish(Topic.Apps.pong, payload)

    def publishTime(self, value = 0, duration = 10, siteId = None):
        if (siteId is None):
            siteId = self._siteId
        self.publish(Topic.Led.time(siteId), json.dumps({"duration":duration,
                                                 "value" : value}))

    def publishWeather(self, cond, temp, siteId = None):
        if (siteId is None):
            siteId = self._siteId
        self.publish(Topic.Led.weather(siteId), json.dumps({
            "weather": cond,
            "temp": temp
        }))

    def publishStopLed(self, siteId = None):
        if (siteId is None):
            siteId = self._siteId
        self.publish(Topic.Led.stop(siteId), '')
    def publishRotary(self, value, siteId = None):
        if (siteId is None):
            siteId = self._siteId
        self.publish(Topic.Led.rotary(siteId), value)
    def publishSwipe(self, value, siteId = None):
        if (siteId is None):
            siteId = self._siteId
        self.publish(Topic.Led.swipe(siteId), value)

    def publishImage(self, filename, dir_, name, siteId = None):
        if (siteId is None):
            siteId = self._siteId

        with open(filename, "r") as f:
            content = f.read()
            client.publish(Topic.Led.add_image_send(siteId, dir_, name),
                           bytearray(content))
    """
    utilities
    """

    def play_wave(self, siteId, requestId, filename):
        utils.play_wave(self._client, siteId, requestId, filename)
    def startHotword(self, modelId = 'default'):
        self.publish("hermes/hotword/{}/detected".format(self._siteId),
                   json.dumps({"siteId" : self._siteId,
                               "modelId" : modelId}))
    def stopHotword(self, sessionId):
        self.publish("hermes/asr/stopListening",
                   json.dumps({"siteId" : self._siteId,
                               "sessionId" : sessionId}))
    def getIdFromRoom(self, room, default = None):
        try:
            tmp = requests.get("http://localhost:3000/devices/search/{}".format(room));
            if (not tmp.ok):
                return default
            data = json.loads(tmp.text)
            data = data.get('result', None)
            return [x.replace('@mqtt', '') for x in data]
        except :
            return default
    @staticmethod
    def getLang(default = "FR"):
        try:
            tmp = requests.get("http://localhost:3000/assistant/lang");
            if (not tmp.ok):
                return default
            return json.loads(tmp.text).upper().encode('ascii', 'ignore')
        except :
            return default
