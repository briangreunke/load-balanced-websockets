from gevent import monkey
monkey.patch_all()

import os

from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, rooms
from loguru import logger
import redis


REDIS_HOSTNAME = os.environ.get("REDIS_HOST")  # Container name from the Docker Compose file

# Hard code some "rooms"
# * "EVERYONE" is to indicate a broadcast
EVERYONE = "0"
TO_OPTIONS = {
    EVERYONE: "Everyone",
    "1": "Red",
    "2": "Blue"
}

app = Flask(__name__)

socket_io_kwargs = {}
db = None
if REDIS_HOSTNAME:
    # If Redis is included, we can use it as a message queue
    # This allows websockets to scale acroos multiple instances of the web application
    db = redis.StrictRedis(REDIS_HOSTNAME, 6379, 0)
    connection_string = f"redis://{REDIS_HOSTNAME}"
    socket_io_kwargs["message_queue"] = connection_string

socketio = SocketIO(app, **socket_io_kwargs)
logger.info(f"Using a message queue at {connection_string}")

# Flask routes
@app.route("/headers")
def show_headers():
    """View the headers. Specifically the ones modified by the reverse proxy"""
    logger.info(request.headers)
    for h in request.headers:
        logger.info(f"{h[0]}: {h[1]}")
    return jsonify({k:v for k, v in request.headers.items()})

@app.route("/")
def render_good_morning():
    return render_template("good-morning.html")

# WS listeners
@socketio.on("connect")
def on_connect():
    """Fires when a client connects"""
    logger.info(f"{request.sid} Connected")
    
@socketio.on("disconnect")
def on_disconnect():
    """Fires when a client disconnects"""
    logger.info(f"{request.sid} Disconnected")

@socketio.on("join")
def on_join(data):
    """Fires when a client emits to 'join'
    
    The server then 'joins' the client to a room"""
    logger.info(f"Joining: {data}")
    to = data["to"]
    if to in TO_OPTIONS.keys():
        join_room(to)
        logger.info(f"Rooms: {rooms()}")
    else:
        logger.warning(f"{to} not in TO_OPTIONS")

@socketio.on("leave")
def on_leave(data):
    """Fires when a client emits to 'leave'
    
    The server then 'removes' the client from the room"""
    logger.info(f"Leaving: {data}")
    to = data["to"]
    if to in TO_OPTIONS.keys():
        leave_room(to)
        logger.info(f"Rooms: {rooms()}")
    else:
        logger.warning(f"{to} not in TO_OPTIONS")

@socketio.on("say")
def say_good_morning(greeting):
    """Fires when a client 'says' Good Morning to a room"""
    name = greeting.get("name")
    to = greeting.get("to")
    # If a 'broadcast' message is received, emit it back out w/ the 'broadcast' flag to True
    # This will emit to ALL rooms
    if to == EVERYONE:
        socketio.emit("broadcast", {"name": name}, broadcast=True)
    else:
        # If the room is valid, emit back to everyone who joined the specific room
        if to in TO_OPTIONS.keys():
            socketio.emit("gm", {"name": name, "to": TO_OPTIONS[to]}, to=to)

@socketio.on("broadcast")
def log_broadcast(bcast):
    """Fires when a broadcast msg is received"""
    logger.info("Broadcast received: {bcast}")


if __name__ == '__main__':
    logger.info(f'Listening on 0.0.0.0:5000 for Server {(os.environ.get("SERVER_NUM", None) or "UNKNOWN")}')
    socketio.run(app, "0.0.0.0", port=5000)
