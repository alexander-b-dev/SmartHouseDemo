import re

import config
import sqlite3


class ThresholdManager:

    def __init__(self):
        self.data = dict()
        self.updateData()

    def updateThreshold(self, sensor, condition, value):
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        if sensor in self.data.keys():
            cursor.execute("update thresholds set condition = ?, value = ? where sensor = ?",
                           (condition, value, sensor))
        else:
            cursor.execute("insert into thresholds (sensor, condition, value) values (?, ?, ?)",
                           (sensor, condition, value))
        con.commit()
        con.close()
        self.updateData()

    def updateData(self):
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        cursor.execute("select sensor, condition, value from thresholds")
        thresholdsData = cursor.fetchall()
        con.close()
        for threshold in thresholdsData:
            self.data[threshold[0]] = {"condition": threshold[1],
                                       "value": threshold[2]}

    def outOfBounds(self, sensor, value):
        if value == "":
            return True
        condition, threshold = self.getThreshold(sensor)
        if re.match(r"\d+(\.\)d)?", value):
            value = float(re.match(r"\d+(\.\)d)?", value).group())
            if condition == "<":
                return value < float(threshold)
            elif condition == ">":
                return value > float(threshold)
            elif condition == "=":
                return abs(value - float(threshold)) < 0.1
        else:
            return value == threshold

    def setDefaultThreshold(self, sensor):
        sensorType = sensor.split("/")[1]
        self.data[sensor] = dict()
        self.data[sensor]["condition"] = config.sensorDefaultThreshold[sensorType][0]
        self.data[sensor]["value"] = config.sensorDefaultThreshold[sensorType][1]

    def getThreshold(self, sensor):
        if sensor not in self.data:
            self.setDefaultThreshold(sensor)
        return self.data[sensor]["condition"], self.data[sensor]["value"]
