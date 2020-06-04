import aiml
import time
import yaml
import azure_tts
import traceback
from flask import *
#from flask_cors import CORS
from datarepo_sql import *
from call_endpoint import *
#from speechservices import *
from phonetic_module import *
from visualizations_module import *
from datetime import timedelta
from LossRatio import LossRatio
import datetime as appdatetime
from iNexQueryGen_v4 import sql_gen
from werkzeug.serving import run_simple
from functions import sanitize_lowertext
from os.path import dirname, join
from SQL_DB import *
import jwt


current_dir = dirname(__file__)
congfig_file = join(current_dir, "./config.yml")
loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
SECRET_KEY = loaded_parameters['application']['SECRET_KEY']
mongodb_link = loaded_parameters['application']['mongodb']
sessionVariablesList = loaded_parameters['application']['sessionVariablesList']

app = Flask(__name__)
#CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY
app.debug = True
Bot1 = LossRatio()




RESET_KEYWORDS = ['reset', 'restart', 'stop', 'quit', 'main menu']
client = pymongo.MongoClient(mongodb_link)
db = client.iNex_db


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=20)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>')
def index_css_8(path):
    return send_from_directory('templates', path)


@app.route('/visualization/barchart')
def barVisualization():
    return render_template('barchart.html', vi=visualizationCode(session.get('vizType'), session.get('fileName')))


@app.route('/visualization/linechart')
def lineVisualization():
    return render_template('linechart.html', vi=visualizationCode(session.get('vizType'), session.get('fileName')))


@app.route('/visualization/table')
def tableVisualization():
    return render_template('table.html', vi=visualizationCode('table', session.get('fileName')))


@app.route('/mobile')
def mobile():
    return render_template('mobile.html')


@app.route('/level')
def show_session():
    x = (session.get('scenario'), session.get('level'))
    return jsonify(x)


@app.route('/clear-session')
def clear_session():
    session['level'] = None
    return jsonify('Session cleared')


@app.route('/invoke_stt')
def background_process_test():
    return jsonify(stt())


@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data_tts = request.get_json()
    text_input = data_tts['text']
    tts_fn = azure_tts.TextToSpeech(text_input)
    tts_fn.get_token()
    audio_response = tts_fn.save_audio()
    return audio_response


def bot_respond(user_input):

    if (session['scenario'] == 2):
        return Bot1.respond(user_input)


@app.route('/converse', methods=['POST'])
def converse():

    congfig_file = 'config.yml'
    loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
    tabularLink = loaded_parameters['application']['tabularLink']
    vlink = loaded_parameters['application']['vlink']

    sessionVariablesList = loaded_parameters['application']['sessionVariablesList']
    greetingaiml = loaded_parameters['application']['greetingaiml']
    inexaiml = loaded_parameters['application']['inexaiml']
    wasAnswered=True

    k = aiml.Kernel()
    k.learn(greetingaiml)
    k.learn(inexaiml)
    scenario = session.get('scenario')
    level = session.get('level')
    user_input_i = request.form['userInput']
    response = {}
    print("User input is: {}".format(user_input_i))
    print("Session Level is : {}".format(str(level)))
    #Intent_AG = 'Agent Performance '
    #user_input = Intent_AG+user_input_i
    user_input = user_input_i
    print("User input is: {}".format(user_input))
    session['User'] = 'C_LEVEL'
    session['LEVEL1'] = distinct_level('LEVEL1')
    session['LEVEL2'] = distinct_level('LEVEL2')
    session['LEVEL3'] = distinct_level('LEVEL3')
    print(session['LEVEL1'])
	jwt_token = request.headers.get('Authorization', None)
    print(jwt_token)
    print(type(jwt_token))
    user_input_i = request.form['userInput']
    print(user_input_i)

    jwt_token_str = str(jwt_token)

    if 'xxxxx' in user_input_i:
        if jwt_token :
            print("in if")
            try:
                payload = jwt.decode(jwt_token_str[7:],verify=False)
                print(payload['given_name'])
                user_name = str(payload['given_name'])
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                user_name = 'No user'
                return jsonify({'message': 'Token is invalid'})
    
        response = {'message': 'Hi {}, my name is iNex, I am here to provide answers to your data analysis related questions. \
        What would you like to find out today? If you need help ask for "Samples"'.format(user_name)}
        return jsonify(response)



    elif (scenario is not None and level is not None and level >= 0):


        session['Intent'] = None
        session['Account Date'] = None
        session['Region'] = None
        session['Agent'] = None
        session['Line of Business'] = None
        session['timeperiod'] = None
        session['time_range'] = None
        session['groupby'] = None
        session['fileName'] = None
        session['combined'] = None
        session['vizType'] = None
        session['Loss ratio'] = None
        session['Renewal Policy Count'] = None
        session['Coverage'] = None

        if type(response) is int:
            session.clear()
            response = {
                'message': 'Hi, my name is iNex, I am here to provide answers to your data analysis related questions. What would you like to find out today? If you need help ask for "Samples".',
                'speechOutput': 'Hi, my name is iNex, I am here to provide answers to your data analysis related questions. What would you like to find out today? If you need help ask for "Samples".'

            }

        if 'drawChart' not in response.keys():
            response['drawChart'] = False

        return jsonify(response)

    else:

        user_input_sl = sanitize_lowertext(str(user_input))

        if k.respond(user_input_sl):

            if 'sample' in sanitize_lowertext(k.respond(user_input_sl)):
                response = {
                    'message': 'Please find below sample questions you may ask. Please choose any one from below options or type in your specific questions.',
                    'actions': [
                        {'text': 'Loss ratio for previous month', 'trigger': 'Loss ratio for previous month'},
                        {'text': 'Loss ratio for Hawaii', 'trigger': 'Loss ratio for Hawaii'},
                        {'text': 'Loss ratio trend by agent', 'trigger': 'Loss ratio trend by agent'}
                    ],
                    'speechOutput': 'Please find below sample questions you may ask. Please choose any one from below options or type in your specific questions Loss ratio for previous month, Loss ratio for Hawaii, Loss ratio trend by agent ',
                    }
            elif 'location' in sanitize_lowertext(k.respond(user_input_sl)):
                defaultTimePeriodList=[]
                session['Intent']='Loss ratio'
                session['timeperiod']='YTD'
                #Hardcoding the default month
                # lastMonth = appdatetime.date.today().replace(day=1) - appdatetime.timedelta(days=1)
                #lastMonth = int('07')
                # defaultTimePeriodList.append(appdatetime.datetime.now().strftime('%Y') + lastMonth.strftime('%m'))
                #defaultTimePeriodList.append('201907')
                defaultTimePeriodList.append('202003')
                session['Account Date'] = defaultTimePeriodList
                response = {'message': k.respond(user_input_sl),'speechOutput':k.respond(user_input_sl)}
                
            else:
                response = {'message': k.respond(user_input_sl),'speechOutput':k.respond(user_input_sl)}

        elif user_input_sl in RESET_KEYWORDS:

            session['Intent'] = None
            session['Account Date'] = None
            session['Region'] = None
            session['Agent'] = None
            session['Line of Business'] = None
            session['timeperiod'] = None
            session['time_range'] = None
            session['groupby'] = None
            session['fileName']=None
            session['combined'] = None
            session['vizType'] = None
            session['Loss ratio'] = None
            session['Renewal Policy Count'] = None
            session['Coverage'] = None
            response = {
                'message': 'Hi, my name is iNex, I am here to provide answers to your data analysis related questions. What would you like to find out today? If you need help ask for "Samples".',
                'speechOutput': 'Hi, my name is iNex, I am here to provide answers to your data analysis related questions. What would you like to find out today? If you need help ask for "Samples".'
            }



#### Wire frame update portion start ####

        elif ((session['User'] == 'C_LEVEL') and user_input=='KPI'):
                Query = "SELECT DISTINCT LEVEL1 FROM DBO.CONVERSATION WHERE USER_NAME ="+"'"+session['User']+"'"
                Qlevel = 'LEVEL1' 
                response = framing_buttons(Query, Qlevel)
                return response
        elif (user_input in session['LEVEL1']):
                Query = "SELECT DISTINCT LEVEL2 FROM DBO.CONVERSATION WHERE LEVEL1 ="+"'"+user_input+"'"
                Qlevel = 'LEVEL2'
                response = framing_buttons(Query, Qlevel)
                return response
        elif (user_input in session['LEVEL2']) :
                Query = "SELECT DISTINCT LEVEL3 FROM DBO.CONVERSATION WHERE LEVEL2 ="+"'"+user_input+"'"
                Qlevel = 'LEVEL3'
                response = framing_buttons(Query, Qlevel)
                return response

        else : 
        #### Wire frame update portion end ####   

        ##elif not (k.respond(user_input)) and user_input_sl not in RESET_KEYWORDS: ## Commanted as a part of new wireframe logic


            try:
                data=sql_connection()
                if data.__len__()!=0:
                    user_input = phonetic(data, user_input)
            except:
                print("Exception in phonetic similarity module!!!")
                traceback.print_exc()

            try:
                print("------Invoking entity and intent recognition module----")
                sessionDict = luisEndpointCall(user_input)
            except:
                print("Exception in entity and intent recognition module!!!!")
                traceback.print_exc()


            setFlag=0
            for i in sessionDict.keys():

                if sessionDict.get(i) is not None:

                    setFlag=1
                    break




            if setFlag==1:

                for i in sessionDict.keys():
                    if sessionDict[i]:
                        if i == 'Account Date':
                            session['timeperiod'] = sessionDict.get('timeperiod')

                        if i is not 'timeperiod':
                            session[str(i)] = sessionDict.get(i)
                print('############################## SESSION ###############################')
                print(session)
                session['combined']=sessionDict.get('combined')
                session['groupby'] = sessionDict.get('groupby')
                session['vizType'] = sessionDict.get('vizType')
                session['fileName'] = sessionDict.get('fileName')


                if session.get('Account Date') is None:

                    defaultTimePeriodList = []
                    session['timeperiod'] = sessionDict.get('timeperiod')
                    # Commenting out setting default date to previous month#
                    # lastMonth = appdatetime.date.today().replace(day=1) - appdatetime.timedelta(days=1)
                    # defaultTimePeriodList.append(appdatetime.datetime.now().strftime('%Y') + lastMonth.strftime('%m'))
                    ##hardcoding July as default month
                    #defaultTimePeriodList.append("201907")
                    defaultTimePeriodList.append("202003")
                    session['Account Date'] = defaultTimePeriodList
                print('############################## SESSION _ 2 ###############################')
                print(session)
                for sessionVar in sessionVariablesList:
                    if str(session.get(sessionVar)) == 'None' or session.get(sessionVar) is None:
                        session[sessionVar] = None
                print('############################## SESSION _ 3 ###############################')
                print(session)
                try:
                    print("*************Input dictionary to query generation module**********************")
                    print(session)
                    sqlOutDF,cutsList = sql_gen(session)

                except:
                    print("Exception in SQL query execution module!!!!")
                    traceback.print_exc()


                vizType,response,templateOutputDF = invokeD3(session, sqlOutDF, cutsList)

                if 'error' not in response:
                    session['vizType']=vizType
                    print("###################################### RESPONSE ##########################")
                    print(response)
                    tempmsg = response
                    if vizType=='text':
                        tempJSON =templateOutputDF.to_json(orient='records')
                        newTempMsg=tempmsg[0].upper()+tempmsg[1:]
                        response = {'message': newTempMsg,'speechOutput':tempmsg,'data' :tempJSON,'vizType':vizType }


                    elif vizType not in 'text' and vizType not in 'table':
                        fName = "visualization" + str(time.time()) + ".csv"
                        session['fileName'] = fName
                        tempJSON =templateOutputDF.to_json(orient='records')
                        templateOutputDF.to_csv(r'./static/' + session.get('fileName'), index=False)
                        print(templateOutputDF.to_json(orient='records'))

                        vlink = vlink + vizType
                        #messageText=' Please click ' + '<a href ="' + vlink + '" target="_blank"> here</a>' + ' to view the visualization for '+ response.rstrip(',')+ '.\n You can alternately view the data in tabular format' + '<a href ="' + tabularLink + '" target="_blank"> here </a>'
                        #webbrowser.open_new_tab(vlink)
                        messageText='Visualization for '+ response.rstrip(',')
                        response = {
                            'message': messageText,
                            'speechOutput': 'Please click on the links provided, to view the visualization.',
                            'data' :templateOutputDF.to_json(orient='records'),
                            'drawChart':True,
                            'vizType':vizType
                        }

                    elif vizType=='table':
                        fName = "visualization" + str(time.time()) + ".csv"
                        session['fileName'] = fName
                        tempJSON =templateOutputDF.to_json(orient='records')
                        templateOutputDF.to_csv(r'./static/' + session.get('fileName'), index=False)
                        print(templateOutputDF.to_json(orient='records'))
                        response = {
                           # 'message': 'Please click ' + '<a href ="' + tabularLink + '" target="_blank"> here</a>' + ' to view data for '+tempmsg+ ' in table format.',
                           'message': 'Data for '+tempmsg+ '.',
                           # 'speechOutput': 'Please click on the link provided, to view the response in tabular format.',
                            'data':templateOutputDF.to_json(orient='records'),
                            'drawChart': True,
                            'vizType':vizType
                        }
                    else:
                        response = {
                            'error':0,
                            'message': 'No response received form SQL',
                            'speechOutput': 'No response received form SQL',
                            'data':"No data",
                            'vizType':vizType
                        }

                print("Visual Type :", vizType)
                print(session)
                
                print("session variables are  ")
                print("file Name----->" + str(session.get('fileName')))
                print("intent----->" + str(session.get('Intent')) + ", state---------->" + str(
                    session.get('Region')))
                print(" date---------" + str(session.get('Account Date')) + ", agent---------" + str(
                    session.get('Agent')))
                print(" LOB---------" + str(
                    session.get('Line of Business')) + ", groupBy----------" + str(session.get('groupby')))
                print("timeRange----->" + str(session.get('timeRange')))
                


            else:
                response={
                    'error':0,
                    'message':'Unfortunately, I couldn\'t find an answer to your question.Do you want ask any of the below questions:',
                    'actions': [
                        {'text': 'Loss ratio for previous month', 'trigger': 'Loss ratio for previous month'},
                        {'text': 'Loss ratio for Hawaii', 'trigger': 'Loss ratio for Hawaii'},
                        {'text': 'Loss ratio trend by agent', 'trigger': 'Loss ratio trend by agent'}

                ],'data':"No data",
                    'speechOutput': 'Unfortunately, I couldn\'t find an answer to your question. Do you want ask any of the below questions: Loss Ratio for previous month, Loss ratio for Hawaii, Loss ratio trend by agent'

                }

        if 'error' in response:
            wasAnswered = False
            tempColl=db["errorLog"]
            msg = {
                "questionText": user_input,
                "date": appdatetime.datetime.utcnow(),
                "wasAnswered": wasAnswered
            }
            tempColl.insert_one(msg)

        if 'drawChart' not in response.keys():
            response['drawChart'] = False


        return jsonify(response)


if __name__ == "__main__":
    app.run()



    #app.run(host='10.53.155.133',port=9080, debug=True, ssl_context=('/home/pocuser/ssl.cert','/home/pocuser/ssl.key'))
    #app.run(host='10.53.155.133',port=9080,debug=True, ssl_context=('adhoc'),threaded=True)
    #app.run(port=9080,debug=True)