import yaml
import pyodbc
import calendar
import pandas as pd
from functions import *
from pymongo import MongoClient
from os.path import dirname, join

def sql_connection():
    current_dir = dirname(__file__)
    congfig_file = join(current_dir, "./config.yml")
    loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
    uri= loaded_parameters['detarepo_spl']['uri']


    myclient = MongoClient(uri)
    db = myclient[loaded_parameters['detarepo_spl']['db']]
    DRIVER = loaded_parameters['detarepo_spl']['DRIVER']
    SERVER = loaded_parameters['detarepo_spl']['SERVER']
    DATABASE = loaded_parameters['detarepo_spl']['DATABASE']
    UID = loaded_parameters['detarepo_spl']['UID']
    PWD = loaded_parameters['detarepo_spl']['PWD']
    connection_string ='DRIVER={'+DRIVER+'};SERVER='+SERVER+';DATABASE='+DATABASE+';UID='+UID+';PWD='+PWD
    cnxn = pyodbc.connect(connection_string)
    data_cuts = []
    mycol = db["attributeMaster"]
    myquery = {"entity/intent": "ENTITY"}
    mydoc = mycol.find(myquery)
    for y in mydoc:
        data_cuts.append(str(y["attributeName"]))
        pass
    data_cuts = list(dict.fromkeys(data_cuts))
    data_cuts.remove("Account Date")

    coll = db["attributeEntity"]
    data1 = []
    temp = []
    for item in data_cuts:
        myquery = {"$and": [{"attributeName": str(item)}, {"timePeriod": "M"}]}
        mydoc = coll.find(myquery)
        for y in mydoc:
            pass
        tablename = y["entityName"]
        entityId = y["entityId"]
        columnNamePhysicaltemp = y["columnNamePhysical"]
        columnNamePhysical = columnNamePhysicaltemp.replace(str(entityId + "."), "")
        query1 = 'SELECT DISTINCT ' + columnNamePhysical + ' FROM ' + tablename + ' WHERE ' + columnNamePhysical + ' IS NOT NULL '
        temp = list(pd.read_sql(query1, cnxn).values.flatten())
        data1 = data1 + temp
    data4 = list(calendar.month_name)
    data = data1 + data4
    data = [clean_text(item) for item in data]
    data = remove_duplicates(data)
    while ("" in data):
        data.remove("")
    return data




def remove_duplicates(l):
    return list(set(l))

def clean_text(raw_text):
    regex = re.compile('[^a-zA-Z\s:]')
    # First parameter is the replacement, second parameter is your input string
    filtered_text = regex.sub('', raw_text)
    # Eliminate multiple spaces
    filtered_text = re.sub(r'[\s]+', ' ', filtered_text)
    # Strip out terminal and leading spaces
    return filtered_text.strip()




