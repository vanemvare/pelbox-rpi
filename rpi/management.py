from flask import Blueprint, jsonify, request
from environs import Env
import logging
import psycopg2
import json
import jwt

from rpi.member import Member
from rpi.pelbox_member import PelBox

from rpi import common
from rpi.keycloak import Keycloak

logging.basicConfig()
log = logging.getLogger()
logging.root.setLevel(logging.NOTSET)
logging.basicConfig(level=logging.NOTSET)

management = Blueprint("management", __name__)

env = Env()
env.read_env()

keycloak = Keycloak(env.str("ADMIN_CLIENT_SECRET"), env.str("MEMBER_CLIENT_SECRET"), env.str("KEYCLOAK_HOST"))

try:
    log.info(f"Connecting to {env.str('DB_NAME')} database from Raspberry Pi")
    conn = psycopg2.connect(host=env.str("DB_HOST"),
                            port=env.str("DB_PORT"),
                            database=env.str("DB_NAME"),
                            user=env.str("DB_USER"),
                            password=env.str("DB_PASSWORD"))
    log.info(f"Connected to {env.str('DB_NAME')} database")
except Exception as e:
    log.critical(e)

@management.route("/ping", methods=["GET"])
def pong():
    try:
        data_json = dict(request.headers)
        data_json = {key: None if data_json[key] == "" else data_json[key] for key in data_json}

        logged_in, status_code = keycloak.is_member_logged(data_json["Access-Token"])
        if status_code == 200 and logged_in:
            username = jwt.decode(data_json["Access-Token"], verify=False)["preferred_username"]
            member_details = common.get_member_details(username)
            member = Member.new(*member_details)

            pelbox_settings = common.get_pelbox_settings(member.id)
            pelbox = PelBox.new(*pelbox_settings)

            status = pelbox.user_security_key != None and pelbox.user_security_key == env.str("APP_SECRET")
            common.set_box_connected(pelbox.user_security_key, member.id, status)

            return jsonify({"success": status}), 200, {"ContentType":"application/json"}
        elif status_code == 200 and not logged_in:
            return jsonify({"success": False, "message": f"Member is not logged in"}), 401, {"ContentType":"application/json"}
        else:
            return jsonify({"success": False, "message": f"Something went wrong"}), 500, {"ContentType":"application/json"}
    except KeyError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "Missing arguments"}), 400, {"ContentType":"application/json"}
    except json.decoder.JSONDecodeError as e:
        log.critical(e)
        return jsonify({"success": False, "error": "JSON is badly formatted"}), 400, {"ContentType":"application/json"}