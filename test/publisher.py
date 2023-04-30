from time import sleep

from paho.mqtt import client as mqtt_client
import config


class MQTTPublisher:

    def __init__(self):
        self.data = {"voltage": [{"name": "sockets_cellar",
                                  "value": 160,
                                  "direction": "+",
                                  "minValue": 160,
                                  "maxValue": 270,
                                  "step": 12},
                                 {"name": "sockets_common",
                                  "value": 200,
                                  "direction": "+",
                                  "minValue": 160,
                                  "maxValue": 270,
                                  "step": 12},
                                 {"name": "sockets_kitchen",
                                  "value": 250,
                                  "direction": "-",
                                  "minValue": 160,
                                  "maxValue": 270,
                                  "step": 12},
                                 ],
                     "openClose": [{"name": "window",
                                    "value": 0,
                                    "direction": "+",
                                    "minValue": 0,
                                    "maxValue": 1,
                                    "step": 1,
                                    "skip": 20,
                                    "left": 15},
                                   {"name": "backyard",
                                    "value": 1,
                                    "direction": "+",
                                    "minValue": 0,
                                    "maxValue": 1,
                                    "step": 1,
                                    "skip": 20,
                                    "left": 15},
                                   {"name": "entrance",
                                    "value": 0,
                                    "direction": "+",
                                    "minValue": 0,
                                    "maxValue": 1,
                                    "step": 1,
                                    "skip": 20,
                                    "left": 15}
                                   ],
                     "illumination": [{"name": "lum_bedroom",
                                       "value": 160,
                                       "direction": "+",
                                       "minValue": 5,
                                       "maxValue": 1200,
                                       "step": 35},
                                      {"name": "lum_livingroom",
                                       "value": 550,
                                       "direction": "+",
                                       "minValue": 5,
                                       "maxValue": 1200,
                                       "step": 35},
                                      {"name": "lum_bathroom",
                                       "value": 256,
                                       "direction": "+",
                                       "minValue": 5,
                                       "maxValue": 1200,
                                       "step": 48},
                                      {"name": "lum_kitchen",
                                       "value": 250,
                                       "direction": "-",
                                       "minValue": 5,
                                       "maxValue": 1200,
                                       "step": 60},
                                      ],
                     "temperature": [{"name": "temp_boiler",
                                      "value": 56,
                                      "direction": "+",
                                      "minValue": 40,
                                      "maxValue": 90,
                                      "step": 0.5},
                                     {"name": "temp_floor",
                                      "value": 20,
                                      "direction": "+",
                                      "minValue": 5,
                                      "maxValue": 60,
                                      "step": 1,
                                      "skip": 5,
                                      "left": 3}, ]}
        self.client = mqtt_client.Client("asdfghjkllkjhgfdsasdfghjklk")
        self.client.on_connect = self.onConnect
        self.client.connect(config.sensorsServer, config.sensorsServerPort)
        self.client.loop_start()

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def publish(self):
        for sensorType, sensorsData in self.data.items():
            for sensor in sensorsData:
                if "left" in sensor.keys():
                    if sensor["left"] > 0:
                        sensor["left"] -= 1
                        continue
                    else:
                        sensor["left"] = sensor["skip"]
                print(f"sensors/{sensorType}/{sensor['name']}: {sensor['value']}")
                result = self.client.publish(f"{config.publishTopic}/{sensorType}/{sensor['name']}", sensor["value"])
                if sensor["direction"] == "+":
                    sensor["value"] += sensor["step"]
                elif sensor["direction"] == "-":
                    sensor["value"] -= sensor["step"]

                if sensor["maxValue"] <= sensor["value"]:
                    sensor["direction"] = "-"
                    sensor["value"] = sensor["maxValue"]
                elif sensor["minValue"] >= sensor["value"]:
                    sensor["direction"] = "+"
                    sensor["value"] = sensor["minValue"]


if __name__ == '__main__':
    publisher = MQTTPublisher()
    while 1:
        publisher.publish()
        sleep(1)
