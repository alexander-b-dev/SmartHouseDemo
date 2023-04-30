from paho.mqtt import client as mqtt_client
import config
from thresholdManager import ThresholdManager


class SensorsWatcher:
    def __init__(self, queue, event):
        self.client = mqtt_client.Client(config.sensorsServerClientId)
        self.client.on_connect = self.connectDone
        self.client.connect(config.sensorsServer, config.sensorsServerPort, keepalive=120)
        self.client.on_message = self.processMessage

        self.alerts = []
        self.thresholdMgr = ThresholdManager()
        self.queue = queue
        self.event = event

    def connectDone(self, pahoClient, userdata, flags, rc):
        self.client.subscribe(config.sensorsTopic)

    def processMessage(self, pahoClient, userdata, msg):
        if self.event.is_set():
            self.thresholdMgr.updateData()
            self.event.clear()
        sensor = msg.topic
        value = msg.payload.decode()
        # print(sensor, value)
        outOfBounds = self.thresholdMgr.outOfBounds(sensor, value)
        if self.queue.full():
            sensorsData = self.queue.get()
        else:
            sensorsData = dict({"alerts": set(), "data": dict()})

        sensorsData["data"][sensor] = (value, outOfBounds)

        if outOfBounds:
            if sensor not in self.alerts:
                self.alerts.append(sensor)
                sensorsData["alerts"].add(sensor)
        else:
            if sensor in self.alerts:
                self.alerts.remove(sensor)

        self.queue.put(sensorsData)

    def runWatcher(self):
        self.client.loop_forever()


def runWatcher(queue, event):
    watch = SensorsWatcher(queue, event)
    watch.runWatcher()


if __name__ == "__main__":
    def connectDone(pahoClient, userdata, flags, rc):
        client.subscribe(config.sensorsTopic)

    def processMessage(pahoClient, userdata, msg):
        sensor = msg.topic
        value = msg.payload.decode()
        print(sensor, value)

    client = mqtt_client.Client(config.sensorsServerClientId)
    client.on_connect = connectDone
    client.connect(config.sensorsServer, config.sensorsServerPort, keepalive=120)
    # client.subscribe(config.sensorsTopic)
    client.on_message = processMessage
    client.loop_forever()
