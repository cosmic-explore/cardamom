import os
import redis
from flask import Flask, Response, request
from flask_session import Session


TURN_CHANNEL = "new turn"

app = Flask(__name__)

#configure redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')
app.secret_key = os.getenv('SECRET_KEY', default='DEV_SECRET_KEY')
server_session = Session(app)
redis_connection = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

def event_stream(channel):
    print(f"starting listener for {channel}")
    redis_listener = redis_connection.pubsub()
    redis_listener.subscribe(channel)
    for pub in redis_listener.listen():
        # convert to str because data must be bytes
        yield str(pub["data"])

@app.route('/')
def hello_world():
    return '<h1>Hello from Flask & Docker</h1>'

@app.route('/match/join', methods=['POST'])
def join_match():
    print("joining match")
    # return Response(status=204)
    return Response(event_stream(TURN_CHANNEL), mimetype="text/event-stream")

@app.route('/match/submit', methods=['POST'])
def submit_commands():
    commands = request.form["commands"]
    redis_connection.publish(TURN_CHANNEL, commands)
    return Response(status=204)

@app.route('/login', methods=['POST'])
def login():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
