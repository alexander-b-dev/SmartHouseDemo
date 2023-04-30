import config
import sqlite3


class SmartHouseClient:

    def __init__(self, userId=-1):
        self.config = dict()
        self.name = "Default User"
        if userId == -1:
            self.userId = self.createNewUser()
        else:
            self.getExistingUser(userId)
        self.getUserConfig()

    @staticmethod
    def createNewUser():
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        cursor.execute("insert into users (name) values ('Default User')")
        con.commit()
        cursor.execute("select id, name from users order by id desc limit 1")
        userData = cursor.fetchone()
        con.close()
        return userData[0]

    def getExistingUser(self, userId):
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        cursor.execute("select id, name from users where id=?", (userId,))
        userData = cursor.fetchone()
        self.userId = userId
        self.name = userData[1]
        con.close()

    def updateUserName(self, name):
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        cursor.execute("update users set name = ? where id=?", (name, self.userId))
        con.commit()
        self.name = name
        con.close()

    def getUserConfig(self):
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        cursor.execute("select id, sensor, alias, visibility from user_settings where user = ?", (self.userId,))
        confData = cursor.fetchall()
        for conf in confData:
            self.config.update({conf[1]: {"alias": conf[2], "visibility": conf[3], "id": conf[0]}})

    def updateUserConfig(self, sensor, alias, visibility=True):
        con = sqlite3.connect(config.databasePath)
        cursor = con.cursor()
        data = self.config.setdefault(sensor, {})
        data.update({"alias": alias, "visibility": visibility})
        if "id" not in self.config[sensor].keys():
            cursor.execute("insert into user_settings (user, sensor, alias, visibility) values (?,?,?,?)",
                           (self.userId, sensor, data["alias"], data["visibility"]))
            con.commit()
            cursor.execute("select id from user_settings order by id desc limit 1")
            data["id"] = cursor.fetchone()[0]
        else:
            cursor.execute('''update user_settings 
                              set alias = ?,
                              visibility = ?
                              where id = ?''',
                           (data["alias"], data["visibility"], data["id"]))
            con.commit()
        con.close()
