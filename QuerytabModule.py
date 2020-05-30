

# Session Variables - date,Region,Agent,Line of Businesscd and timerange should always be lists
#sessiondict = {'_permanent': True, 'Intent': 'Agent Performance', 'timeperiod': 'MTD', 'Account Date': ['202004'], 'time_range': ['previous month'], 'combined': None, 'groupby': None, 'vizType': None, 'fileName': None, 'Region': None, 'Line of Business': None, 'Agent': 'ALL'}



import pyodbc
import pandas as pd
from pymongo import MongoClient
import time
import yaml
from datetime import date

def querytab(sessiondict):
    congfig_file = 'config.yml'
    loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
    # Connect to mongodb which will act as the database for storing our metadata
    uri= loaded_parameters['sqlquerygen']['uri']
    myclient = MongoClient(uri)
    db = myclient[loaded_parameters['sqlquerygen']['db']]
    
    mycol = db["query_d"]
    if str(sessiondict.get("Agent")) == 'ALL':
        sub = {"$and": [{"subjectArea": str(sessiondict.get("Intent"))},{"user": str(sessiondict.get("Agent"))}]}
        result = mycol.find( sub )
        for y in result:
            pass
        query = y["query"]
        #print(query)
        
    elif str(sessiondict.get("Agent")) != 'ALL':
    
        sub = {"$and": [{"subjectArea": str(sessiondict.get("Intent"))},{"user": "X"}]}
        result = mycol.find( sub )
        for y in result:
            pass
        query = y["query"]
        #print(query)
    
    else:
        print("Subject Area not available in the query module")
        
    agent_name = str(sessiondict.get("Agent"))
    if agent_name != 'ALL':
        Query = query % agent_name
    else:
        Query = query
    print(Query)
    
    try:
        congfig_file = 'config.yml'
        list_where_groupby = None
        loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
        DRIVER = loaded_parameters['sqlquerygen']['DRIVER']
        SERVER = loaded_parameters['sqlquerygen']['SERVER']
        DATABASE = loaded_parameters['sqlquerygen']['DATABASE']
        UID = loaded_parameters['sqlquerygen']['UID']
        PWD = loaded_parameters['sqlquerygen']['PWD']
        connection_string ='DRIVER={'+DRIVER+'};SERVER='+SERVER+';DATABASE='+DATABASE+';UID='+UID+';PWD='+PWD
        cnxn = pyodbc.connect(connection_string)
        print("Query--", Query)
        df = pd.read_sql(Query, cnxn)
        
    except Exception as e:
        print(e)
    
    #print(df)
    return df,list_where_groupby
    
def main():
    a=querytab({'_permanent': True, 'Intent': 'Agent Performance', 'timeperiod': 'MTD', 'Account Date': ['202004'], 'time_range': ['previous month'], 'combined': None, 'groupby': None, 'vizType': None, 'fileName': None, 'Region': None, 'Line of Business': None, 'Agent': 'Uninsurable brokers'})
    print(a)

if __name__=="__main__":
    main()