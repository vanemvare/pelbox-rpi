import json

class PelBox:
    def __init__(self, data):
        data_json = json.loads(data.decode("utf-8"))

        self.id = data_json["id"]
        self.security_key = data_json["security_key"]
        self.user_security_key = data_json["user_security_key"]
        self.member_id = data_json["member_id"]
        self.host = data_json["host"]
        self.connected = data_json["connected"]

    @staticmethod
    def new(id, security_key, user_security_key, host, member_id, connected):
        new_data = {
            "id": id,
            "security_key": security_key,
            "user_security_key": user_security_key, 
            "member_id": member_id,
            "host": host,
            "connected": connected
        }

        pelbox = PelBox(json.dumps(new_data).encode("utf-8"))
        return pelbox

    def json_data(self):
        return {
            "id": self.id,
            "security_key": self.security_key,
            "user_security_key": self.user_security_key,
            "host": self.host,
            "member_id": self.member_id,
            "connected": self.connected
        }