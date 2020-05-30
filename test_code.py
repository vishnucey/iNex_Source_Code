import aiml
import time
import yaml
import azure_tts
import traceback
from flask import *
from flask_cors import CORS
from datarepo_sql import *
from call_endpoint import *
from speechservices import *
from phonetic_module import *
from visualizations_module import *
from datetime import timedelta
from LossRatio import LossRatio
import datetime as appdatetime
from iNexQueryGen_v4 import sql_gen
from werkzeug.serving import run_simple
from functions import sanitize_lowertext
from os.path import dirname, join

current_dir = dirname(__file__)
congfig_file = join(current_dir, "./config.yml")
loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
SECRET_KEY = loaded_parameters['application']['SECRET_KEY']
mongodb_link = loaded_parameters['application']['mongodb']
sessionVariablesList = loaded_parameters['application']['sessionVariablesList']

sessionVariablesList = loaded_parameters['application']['sessionVariablesList']
greetingaiml = loaded_parameters['application']['greetingaiml']
inexaiml = loaded_parameters['application']['inexaiml']

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.debug = True

RESET_KEYWORDS = ['reset', 'restart', 'stop', 'quit', 'main menu']
client = pymongo.MongoClient(mongodb_link)
db = client.iNex_db


app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>')
def index_css_8(path):
    return send_from_directory('templates', path)

@app.route('/level')
def show_session():
    x = (session.get('scenario'), session.get('level'))
    return jsonify(x)


@app.route('/clear-session')
def clear_session():
    session['level'] = None
    return jsonify('Session cleared')


@app.route('/converse', methods=['POST'])
def converse():
    print("IN CONVERSE")
	#level = session.get('level')
    response = {}
    wasAnswered = True

    k = aiml.Kernel()
    k.learn(greetingaiml)
    k.learn(inexaiml)

    user_input = request.form['userInput']

    print("User input is: {}".format(user_input))
    #print("Session Level is : {}".format(str(level)))

    if(sanitize_lowertext(user_input) in RESET_KEYWORDS):
        session.clear()

    if user_input ==":)":
        response = {
            'message': 'Hey There!! You seem happy today. What can I help you with?',
            
                }
        return jsonify(response)
    user_input_sl = sanitize_lowertext(str(user_input))
    print("Input SL is : {0}".format(user_input_sl))
    print(k.respond(user_input_sl))
    if 'vishnu' in user_input_sl:
        response = {'message':"Hallo bla bla blaaaaaaa"}
    
    
    
    # if not (k.respond(user_input)) and user_input_sl not in RESET_KEYWORDS:
    #     print("------Passing to LUIS----")
    #     sessionDict = luisEndpointCall(user_input)
    #     print(sessionDict)
    #     return jsonify(response)

    # if user_input =="What is the renewal policy count for hawaii":
    # 	print("------Invoking entity and intent recognition module----")
    # 	sessionDict = luisEndpointCall(user_input)
    # 	print(sessionDict)
    # 	return jsonify(response)

    
    if k.respond(user_input_sl):

        if 'sample' in sanitize_lowertext(k.respond(user_input_sl)):
            response = {
                'message': 'Please find below sample questions you may ask. Please choose any one from below options or type in your specific questions.',
                'actions': [
                    {'text': 'Agent Performance', 'trigger': 'Agent Performance'},
                    {'text': 'Executive Analysis', 'trigger': 'Executive Analysis'},
                    {'text': 'Adjustor Performance', 'trigger': 'Adjustor Performance'}
                ],
                'speechOutput': 'Please find below sample questions you may ask. Please choose any one from below options or type in your specific questions Loss ratio for previous month, Loss ratio for Hawaii, Loss ratio trend by agent ',
                }
        return jsonify(response)

    if k.respond(user_input_sl):
         if 'hallo' in sanitize_lowertext(k.respond(user_input_sl)):
                response = {
                'message': 'Please find below sample questions you may ask. Please choose any one from below options or type in your specific questions.',
                'actions': [
                    {'text': 'Agent Performance', 'trigger': 'Agent Performance'},
                    {'text': 'Executive Analysis', 'trigger': 'Executive Analysis'},
                    {'text': 'Adjustor Performance', 'trigger': 'Adjustor Performance'}
                ],
                'speechOutput': 'Please find below sample questions you may ask. Please choose any one from below options or type in your specific questions Loss ratio for previous month, Loss ratio for Hawaii, Loss ratio trend by agent ',
                }
    return jsonify(response)

if __name__ == '__main__':
    app.run(port=9080, debug=True)