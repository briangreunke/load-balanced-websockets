import os

from loguru import logger
import socketio


client = socketio.Client()

@client.on("broadcast")
def process_broadcast(data):
  """Fires on broadcast messages"""
  logger.info(f"Broadcast: {data}")

@client.on("gm")
def process_say(data):
  """Fires on 'Good Morning' messages"""
  logger.info(f"Said: {data}")


if __name__ == "__main__":
  url = os.environ.get("WS_URL")
  client.connect(url)
  client.emit("join", {"to": "1"})  # Join the first room
  client.emit("join", {"to": "2"})  # Join the second room
