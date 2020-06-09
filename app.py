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

from authorization import authorization,authorization_role, unauth_fn

agent_wf = []
current_dir = dirname(__file__)
congfig_file = join(current_dir, "./config.yml")
loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
SECRET_KEY = loaded_parameters['application']['SECRET_KEY']
mongodb_link = loaded_parameters['application']['mongodb']
sessionVariablesList = loaded_parameters['application']['sessionVariablesList']
# global payload

payload_global = "chakka"
role_global ='ALL'
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


# @app.route('/visualization/barchart')
# def barVisualization():
#     return render_template('barchart.html', vi=visualizationCode(session.get('vizType'), session.get('fileName')))


# @app.route('/visualization/linechart')
# def lineVisualization():
#     return render_template('linechart.html', vi=visualizationCode(session.get('vizType'), session.get('fileName')))


# @app.route('/visualization/table')
# def tableVisualization():
#     return render_template('table.html', vi=visualizationCode('table', session.get('fileName')))


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


# @app.route('/invoke_stt')
# def background_process_test():
#     return jsonify(stt())


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
    user_input = user_input_i
    #session['User'] = 'Manager'
    session['LEVEL1'] = distinct_level('LEVEL1')
    session['LEVEL2'] = distinct_level('LEVEL2')
    session['LEVEL3'] = distinct_level('LEVEL3')
    jwt_token = request.headers.get('Authorization', None)
    print("****USER INPUT********")
    print(user_input_i)
    jwt_token_str = str(jwt_token)
    ## For initializing the user and authentication 
    if 'xxxxx' in user_input_i:

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
        session['Agent Portfolio'] = None
       

        if jwt_token :
            print("Token Received")
            try:
                global payload_global
                global role_global
                payload = jwt.decode(jwt_token_str[7:],verify=False)
                payload_global = payload
                # payload_n = payload
                print(payload['given_name'])
                user_name = str(payload['given_name'])   
                access,role = authorization_role(payload)
                print(access)
                print(role)
                role_global=role
                session['User']=role_global
                if access=='User is not authorized':
                    response ={'message': 'You do not have access to the requested module'}
                    return jsonify(response)
                elif access=='User is authorized':
                    response = {'message': 'Hi {}, my name is iNex, I am here to provide answers to your data analysis related questions. \
                        What would you like to find out today? If you need help ask for "Solutions"'.format(user_name)}
                    return jsonify(response)



            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                user_name = 'No user'
                return jsonify({'message': 'Token is invalid'})

    # elif (scenario is not None and level is not None and level >= 0):


    #     session['Intent'] = None
    #     session['Account Date'] = None
    #     session['Region'] = None
    #     session['Agent'] = None
    #     session['Line of Business'] = None
    #     session['timeperiod'] = None
    #     session['time_range'] = None
    #     session['groupby'] = None
    #     session['fileName'] = None
    #     session['combined'] = None
    #     session['vizType'] = None
    #     session['Loss ratio'] = None
    #     session['Renewal Policy Count'] = None
    #     session['Coverage'] = None
    #     session['Agent Portfolio'] = None

    #     response = {'message': 'Hi {}, my name is iNex, I am here to provide answers to your data analysis related questions. \
    #     What would you like to find out today? If you need help ask for "Samples"'.format(user_name)}
    #     return jsonify(response)
       
        

        # if type(response) is int:
        #     session.clear()
        #     response = {
        #         'message': 'Hi, my name is iNex, I am here to provide answers to your data analysis related questions. What would you like to find out today? If you need help ask for "Samples".',
        #         'speechOutput': 'Hi, my name is iNex, I am here to provide answers to your data analysis related questions. What would you like to find out today? If you need help ask for "Samples".'

        #     }

        # if 'drawChart' not in response.keys():
        #     response['drawChart'] = False

        # return jsonify(response)

    else:
        user_input_sl = sanitize_lowertext(str(user_input))
        datalist = distinct_data('LEVEL2')
        session['Agent Portfolio'] = None
        
        if k.respond(user_input_sl):

            if 'dedeed' in sanitize_lowertext(k.respond(user_input_sl)):
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
                defaultTimePeriodList.append('202005')
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
            session['Agent Portfolio'] = None

            
            user_name = str(payload_global['given_name'])
            
            response = {'message': 'Hi {}, my name is iNex, I am here to provide answers to your data analysis related questions. \
                         What would you like to find out today? If you need help ask for "Solutions"'.format(user_name)}



#### Wire frame update portion start ####


        elif ((session['User'] == role_global) and user_input=='Solutions'):
                Query = "SELECT DISTINCT LEVEL1 FROM DBO.CONVERSATION WHERE USER_NAME ="+"'"+session['User']+"'"
                Qlevel = 'LEVEL1' 
                response = framing_buttons(Query, Qlevel,'Agent')
                return response
        elif (user_input in session['LEVEL1']):
            if (user_input == 'Agent Performance'):
                Query = "select  distinct top 5  AG.agnt_name from fact_prem_tran FP inner join DIM_AGENT AG on FP.agnt_id = AG.agnt_id where AG.AGNT_NAME <>' '"
                Qlevel = 'agnt_name'
                response = framing_buttons(Query, Qlevel,'Agent')
                
                return response
            else:
                Query = "SELECT DISTINCT LEVEL2 FROM DBO.CONVERSATION WHERE LEVEL1 ="+"'"+user_input+"'"
                Qlevel = 'LEVEL2'
                response = framing_buttons(Query, Qlevel,'Agent')
                return response

                #Query = "SELECT DISTINCT LEVEL2 FROM DBO.CONVERSATION WHERE LEVEL1 ="+"'"+user_input+"'"
                #Query = "select  distinct top 5  AG.agnt_name from fact_prem_tran FP inner join DIM_AGENT AG on FP.agnt_id = AG.agnt_id where AG.AGNT_NAME <>' '"
                #Qlevel = 'agnt_name'
                #response = framing_buttons(Query, Qlevel)
                #return response
        elif (user_input in datalist):
           Query = "SELECT DISTINCT LEVEL3 FROM DBO.CONVERSATION WHERE LEVEL2 = 'list'" 
           Qlevel = 'LEVEL3'
           agent_name = user_input
           agent_wf.append(agent_name)
           print(session)
           response = framing_buttons(Query, Qlevel,agent_name)
           return response
        
        
        elif (user_input in session['LEVEL2']) :

                Query = "SELECT DISTINCT LEVEL3 FROM DBO.CONVERSATION WHERE LEVEL2 ="+"'"+user_input+"'"
                Qlevel = 'LEVEL3'

                response = framing_buttons(Query, Qlevel,'Agent')
                return response
        elif (user_input == 'Click') :
            Query = "SELECT DISTINCT LEVEL4 FROM DBO.CONVERSATION WHERE LEVEL3 = 'Agent Portfolio'"
            Qlevel = 'LEVEL4'
            response = framing_buttons(Query, Qlevel,'Agent')
            return response

        else : 
            print ("********************************************************************************")
            #print (session['Agent_wireframe'])
        #### Wire frame update portion end ####   

        ##elif not (k.respond(user_input)) and user_input_sl not in RESET_KEYWORDS: ## Commanted as a part of new wireframe logic


            #try:
            #    data=sql_connection()
            #    if data.__len__()!=0:
            #        user_input = phonetic(data, user_input)
            #except:
            #    print("Exception in phonetic similarity module!!!")
            #    traceback.print_exc()

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
                    defaultTimePeriodList.append("202005")
                    session['Account Date'] = defaultTimePeriodList
                for sessionVar in sessionVariablesList:
                    if str(session.get(sessionVar)) == 'None' or session.get(sessionVar) is None:
                        session[sessionVar] = None
                print("*************Input dictionary to query authorization module**********************")
                #print(payload_global)
                session_n,data_sec = authorization(payload_global,session)
                if (data_sec=='False'):
                    response ={'message': 'You do not have access to the requested module'}
                    return jsonify(response)
                        #break
                    #unauth_fn(response)
                    sys.exit()
                try:
                    print("*************Input dictionary to query generation module**********************")
                    if (session_n['Agent Portfolio']) != None:
                        #print(session)
                        #print ("*******************************************************")
                        #print (agent_wf)
                        #print ("*******************************************************")
                        agnt = agent_wf[-1]
                        session_n['Agent'] = agnt
                        print(session_n)
                        sqlOutDF,cutsList = querytab(session_n)
                        
                    else:
                        sqlOutDF,cutsList = sql_gen(session_n)

                except:
                    print("Exception in SQL query execution module!!!!")
                    traceback.print_exc()


                vizType,response,templateOutputDF = invokeD3(session_n, sqlOutDF, cutsList)

                if 'error' not in response:
                    session_n['vizType']=vizType
                    tempmsg = response
                    if vizType=='text':
                        tempJSON =templateOutputDF.to_json(orient='records')
                        newTempMsg=tempmsg[0].upper()+tempmsg[1:]
                        response = {'message': newTempMsg,'speechOutput':tempmsg,'data' :tempJSON,'vizType':vizType }


                    elif vizType not in 'text' and vizType not in 'table':
                        fName = "visualization" + str(time.time()) + ".csv"
                        session_n['fileName'] = fName
                        tempJSON =templateOutputDF.to_json(orient='records')
                        templateOutputDF.to_csv(r'./static/' + session_n.get('fileName'), index=False)
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
                        session_n['fileName'] = fName
                        tempJSON =templateOutputDF.to_json(orient='records')
                        templateOutputDF.to_csv(r'./static/' + session_n.get('fileName'), index=False)
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
                print(session_n)
                
                print("session variables are  ")
                print("file Name----->" + str(session_n.get('fileName')))
                print("intent----->" + str(session_n.get('Intent')) + ", state---------->" + str(
                    session_n.get('Region')))
                print(" date---------" + str(session_n.get('Account Date')) + ", agent---------" + str(
                    session_n.get('Agent')))
                print(" LOB---------" + str(
                    session_n.get('Line of Business')) + ", groupBy----------" + str(session_n.get('groupby')))
                print("timeRange----->" + str(session_n.get('timeRange')))
                


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

if __name__ == '__main__':
    app.run()



    #app.run(host='10.53.155.133',port=9080, debug=True, ssl_context=('/home/pocuser/ssl.cert','/home/pocuser/ssl.key'))
    #app.run(host='10.53.155.133',port=9080,debug=True, ssl_context=('adhoc'),threaded=True)
    #app.run(port=9080,debug=True)