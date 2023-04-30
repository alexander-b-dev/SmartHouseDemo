import os

key = 'oYc0pBzKdJ1cJdlruOcKftiGLD0Ozk4RadmqhVCcij8RkrkKhr2A7euquuUY9xDKHFJchiaQkmY'
debug = True
sensorsServer = "broker.hivemq.com"
sensorsServerPort = 1883
sensorsServerClientId = 'SmartHouseDemo'
publishTopic = "sensorsRadmqhVCcij8RkrkKhr2A7"
sensorsTopic = "sensorsRadmqhVCcij8RkrkKhr2A7/#"
databasePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DB/db.sqlite3")

sensorsValues = {"voltage": lambda x: f"{x} V",
                 "openClose": lambda x: "Closed" if x == "1" else "Opened",
                 "illumination": lambda x: f"{x} Lux",
                 "temperature": lambda x: f"{x} °C"}

sensorDefaultThreshold = {"voltage": ["<", 170],
                          "openClose": ["=", 0],
                          "illumination": [">", 800],
                          "temperature": [">", 50]}

sensorsPicsOk = {"voltage": "voltage_orange.png",
                 "openClose": "door_open_orange.png",
                 "illumination": "lightbulb_orange.png",
                 "temperature": "temperature_orange.png"}

sensorsPicsNotOk = {"voltage": "voltage_black.png",
                    "openClose": "door_open_black.png",
                    "illumination": "lightbulb_black.png",
                    "temperature": "temperature_black.png"}
