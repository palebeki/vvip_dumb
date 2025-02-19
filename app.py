from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
from waitress import serve
import json, time, os

# Environment Variables
HOST = "0.0.0.0"
PORT = 9090

# Main Configurations
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def load_object(target):
    a = open('./object/' + target, 'r')
    return json.load(a)

@app.after_request
def after_request(response):
    delay = int(load_config()['delay'])/1000  # Delay in seconds
    time.sleep(delay)
    return response


CONFIG_FILE = 'config.json'
DATA_FILE = 'recentdata.json'

def load_config():
    """Load the configuration from the JSON file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"profilerespond": "0", "participaterespond": "0"}

def save_config(profilerespond, participaterespond, delay):
    """Save the configuration to the JSON file."""
    config = {
        "profilerespond": profilerespond,
        "participaterespond": participaterespond,
        "delay": delay
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_data():
    """Load the JSON data from the file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return None

def save_data(data):
    """Save the received JSON data to a file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

## DUMB Configurator server
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        profilerespond = request.form.get('profilerespond')
        participaterespond = request.form.get('participaterespond')
        delay = request.form.get('delay')
        save_config(profilerespond, participaterespond, delay)

    config = load_config()
    json_data = load_data()  # Load JSON data from the file
    return render_template('index.html', config=config, json_data=json_data)

@app.route('/post_json', methods=['POST'])
def post_json():
    print(request.get_data())
    if request.is_json:
        data = request.get_json()  # Get the JSON data
        save_data(data)  # Save the JSON data to a file
        return jsonify({"message": "Data saved successfully"}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400

#### Application Routes

## Profile page
@app.route('/dummy/profile')
def get_profile():
    match load_config()['profilerespond']:
        case '0':
            return load_object('./profile/profile_empty.json')
        case '1':
            return load_object('./profile/profile_validation.json')
        case '2':
            return load_object('./profile/profile_verified.json')
        
## Program page
@app.route('/dummy/program')
def get_program():
    return load_object('./program/programlist.json')

## Program page
@app.route('/dummy/leaderboard')
def get_leaders():
    return load_object('./leaderboard/localleader.json')



# main function
if __name__ == "__main__":
    print(f'Running Backend dummy for gardan on {PORT} ')
    serve(app, host=HOST, port=PORT, threads=2)