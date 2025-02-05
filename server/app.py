from flask import Flask
import os 

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello from Flask & Docker</h1>'

@app.route('/player')
def get_player():
    pass

@app.route('/match/start')
def start_match():
    pass

@app.route('/match/players')
def get_match():
    pass

@app.route('/creature')
def get_creature():
    pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
