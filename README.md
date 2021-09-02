# Load balanced Websockets
This is a simple example of how to load a web application which uses websockets.

This example contains:
- Flask
- Flask-SocketIO
- nginx
- Redis

and everything runs locally inside of Docker containers

## Architecture

The project builds:
- 2 clients (Python scripts inside of Docker containers) which connect to ..
- an Nginx proxy configured for Websockets and load balances requests to ..
- 2 application servers (Flask apps inside of Docker containers) which uses ..
- a Redis cache

The two Python clients connect to, and emit messages to, the proxy, which forwards the request to the application server(s), which process the requests

The proxy also exposes port 80 so you can browse to the application yourself.

The web applications are using [Flask-SocketIO]() which is configured to use a `message_queue` in Redis.
This allows the multi-instance application to work with Websockets.

## Run
```
docker-compose up
```

View the logs using
```
docker logs --follow websockets-webapp-1
docker logs --follow client_1
```

Browse to the page at http://localhost
