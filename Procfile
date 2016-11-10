worker: python manage.py runworker --only-channels=http.* --only-channels=websocket.* -v2
web: daphne chat.asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2