from gevent import monkey
monkey.patch_all()

from datetime import datetime
import html
import json
import os

from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO
from loguru import logger
import redis


LOG_NAMESPACE = "/logs"

app = Flask(__name__)
db = redis.StrictRedis('cache', 6379, 0)
socketio = SocketIO(app, message_queue='redis://cache')


@app.route('/logs')
def render_log():
    logger.info(request.headers)
    all_entries = [l.decode() for l in db.lrange("log_entries", 0, -1)]
    all_entries = [json.loads(e) for e in all_entries]
    return render_template('log.html', all_log_entries=all_entries)

@app.route("/clear")
def clear_db():
    db.flushdb()
    logger.info("Flushed cache")
    return redirect(url_for("render_log"))
    return render_template('log.html', all_log_entries=[json.loads(l.decode()) for l in db.lrange("log_entries", 0, -1)])

@socketio.on('log', namespace=LOG_NAMESPACE)
def add_new_log(new_entry):
    logger.info(new_entry['content'])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_str = html.escape(new_entry['content'])
    entry = json.dumps({"date": now, "content": entry_str})
    entries = db.rpush("log_entries", entry)
    socketio.emit('log', {'date': now, 'content': entry_str}, namespace=LOG_NAMESPACE)


if __name__ == '__main__':
    logger.info(f'Listening on 0.0.0.0:5000 for Server {(os.environ.get("SERVER_NUM", None) or "UNKNOWN")}')
    socketio.run(app, "0.0.0.0", port=5000)
