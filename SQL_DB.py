
import yaml
import pyodbc
import calendar
import pandas as pd
from pymongo import MongoClient
from os.path import dirname, join
from flask import *



def sql_connection_new(Query):
    congfig_file = 'config.yml'
    loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
    DRIVER = loaded_parameters['sqlquerygen']['DRIVER']
    SERVER = loaded_parameters['sqlquerygen']['SERVER']
    DATABASE = loaded_parameters['sqlquerygen']['DATABASE']
    UID = loaded_parameters['sqlquerygen']['UID']
    PWD = loaded_parameters['sqlquerygen']['PWD']
    connection_string ='DRIVER={'+DRIVER+'};SERVER='+SERVER+';DATABASE='+DATABASE+';UID='+UID+';PWD='+PWD
    cnxn = pyodbc.connect(connection_string)
    #Query = 'SELECT * FROM DBO.CONVERSATION'
    # print("Query--", Query)
    df = pd.read_sql(Query, cnxn)
    # print(df)
    return df

def framing_buttons(Query, Qlevel,agnt) :
    data=sql_connection_new(Query)
    # print(data)
    tempMSG = list(data[Qlevel])
    datalist = []
    # print(tempMSG)
    if (Qlevel == 'agnt_name'):
        tempMSG.append('ALL')


    action_list = []
    for i in tempMSG : 
        #print(i)
        action_dict = {}
        action_dict['text'] = i
        action_dict['trigger'] = i
        # print(action_dict)
        action_list.append(action_dict)
        # print(action_list)

    # print(action_list)
    
    if (Qlevel == 'LEVEL1'):
        response = {'message': 'Please find the available solutions below',
                    # 'data':tempJSON,
                    'actions': action_list
                    }
                    
    elif (Qlevel == 'agnt_name'):
        response = {'message': 'Please find the list of top 5 agents based on premium',
                    # 'data':tempJSON,
                    'actions': action_list
                    }
    elif (Qlevel == 'LEVEL2'):
        response = {'message': 'LEVEL3',
                    # 'data':tempJSON,
                    'actions': action_list
                    }  

    elif (Qlevel == 'LEVEL3'):
        response = {'message': 'Please select a particular solution for ' + agnt,
                    # 'data':tempJSON,
                    'actions': action_list
                    }  
    elif (Qlevel == 'LEVEL4'):
        response = {'message': 'Please select from below KPI for detailed analysis',
                    # 'data':tempJSON,
                    'actions': action_list
                    }                      
    return jsonify(response)
        #except:
    #    print("Exception in SQL Connection!!!")  

def distinct_level(LEVEL) :
    Query_n = "SELECT DISTINCT "+ LEVEL +" FROM DBO.CONVERSATION"
    data=sql_connection_new(Query_n)
    values = list(data[LEVEL])
    # print(values)
    return values

def distinct_data(LEVEL) :
    Qlevel = 'agnt_name'
    Query = "select  distinct top 5  AG.agnt_name from fact_prem_tran FP inner join DIM_AGENT AG on FP.agnt_id = AG.agnt_id where AG.AGNT_NAME <>' '"
    data=sql_connection_new(Query)
    tempMSG = list(data[Qlevel])

    tempMSG.append('ALL')

    return tempMSG
    

    