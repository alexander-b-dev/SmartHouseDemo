import json
import multiprocessing

from flask import Flask, render_template, request, make_response, url_for
from flask_socketio import SocketIO

from thresholdManager import ThresholdManager
from watcher import runWatcher
import config
from client import SmartHouseClient


def create_app():
    app = Flask(__name__, static_folder=r'WEB\static', template_folder=r'WEB\templates')
    app.config['DEBUG'] = config.debug
    app.config['SECRET_KEY'] = config.key

    socketio = SocketIO(app)

    app.actualData = dict()
    app.queue = multiprocessing.Queue(maxsize=1)
    app.event = multiprocessing.Event()
    app.watcherProcess = multiprocessing.Process(target=runWatcher, args=(app.queue, app.event))
    app.watcherProcess.start()

    @app.route('/', methods=["GET"])
    def index():
        clientId = request.cookies.get("clientId", -1)
        client = SmartHouseClient(clientId)
        if clientId == -1:
            resp = make_response(render_template("index.html", user=client.name))
            resp.set_cookie("clientId", str(client.userId))
            return resp
        else:
            return render_template("index.html", user=client.name)

    @app.route("/user/config", methods=["GET"])
    def userConfig():
        clientData = SmartHouseClient(request.cookies.get("clientId", -1))
        if request.method == 'GET':
            return json.dumps({"userName": clientData.name, "sensorsConfig": clientData.config})

    @app.route("/user/config/sensor", methods=["PUT"])
    def modifyConf():
        clientData = SmartHouseClient(request.cookies.get("clientId", -1))
        if request.method == 'PUT':
            newData = request.json
            clientData.updateUserConfig(newData["sensor"], newData["alias"], newData["visibility"])
            return "", 200
        return "", 405

    @app.route("/user/config/name", methods=["PUT"])
    def modifyName():
        clientData = SmartHouseClient(request.cookies.get("clientId", -1))
        if request.method == 'PUT':
            newName = request.json["name"]
            clientData.updateUserName(newName)
            return "", 200
        return "", 405

    @app.route("/threshold/<sensor>", methods=["GET", "PUT"])
    def manageThreshold(sensor):
        sensor = sensor.replace("~", "/")
        mgr = ThresholdManager()
        if request.method == 'GET':
            return json.dumps(mgr.getThreshold(sensor))
        if request.method == 'PUT':
            mgr.updateThreshold(sensor, request.json["condition"], request.json["value"])
            app.event.set()
            return "", 200
        return "", 405

    @app.route('/data', methods=["GET"])
    def data():
        if not app.queue.empty():
            newData = app.queue.get()
            app.actualData.update(newData["data"])
            socketio.emit("JSON", json.dumps(list(newData["alerts"])))
        dataToClient = dict()
        for sensor, value in app.actualData.items():

            sensorType = sensor.split("/")[1]
            sensorData = {
                "value": config.sensorsValues[sensorType](value[0]),
                "img": url_for('static', filename=config.sensorsPicsNotOk[sensorType]) if value[1]
                else url_for('static', filename=config.sensorsPicsOk[sensorType]),
                "name": sensor,
                "alert": value[1]
            }

            temp = dataToClient.setdefault(sensor.split("/")[1], [])
            temp.append(sensorData)

        return json.dumps({"sensorTypes": dataToClient})

    return app


if __name__ == '__main__':
    multiprocessing.freeze_support()
    flask_app = create_app()
    flask_app.run(host="0.0.0.0", port=5000)
