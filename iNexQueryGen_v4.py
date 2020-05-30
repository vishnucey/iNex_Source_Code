import pyodbc
import pandas as pd
from pymongo import MongoClient
import time
import yaml
from datetime import date

congfig_file = 'config.yml'
loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
# Connect to mongodb which will act as the database for storing our metadata
uri= loaded_parameters['sqlquerygen']['uri']
myclient = MongoClient(uri)
db = myclient[loaded_parameters['sqlquerygen']['db']]



# Session Variables - date,Region,Agent,Line of Businesscd and timerange should always be lists
def sql_gen(sessiondict):
    data_cuts = []
    mycol = db["attributeMaster_d"]
    myquery = {"entity/intent": "ENTITY"}
    mydoc = mycol.find(myquery)
    for y in mydoc:
        data_cuts.append(str(y["attributeName"]))
        pass
    data_cuts = list(dict.fromkeys(data_cuts))
    print (data_cuts)
   
    
    try:
        mycol = db["timePeriod_d"]
        myquery = {"timePeriodDesc": sessiondict.get("timeperiod")}
        mydoc = mycol.find(myquery)
        for y in mydoc:
            pass
        time_period = y["timePeriod"]
        print(time_period)
    except Exception as e:
        print(e)
        
# 20/05 --calculation entity identification

    try:

        samplelist = [sessiondict.get("Loss ratio"),sessiondict.get("Renewal Policy Count")]
        calentity =[]
        for item in samplelist:
            if item is not None:
                calentity.append(item[0])
        print (calentity)
        entkey = (list(sessiondict.keys())[list(sessiondict.values()).index(calentity)])
    except Exception as e:
        print(e)        
    
    samplelist = []
    list_where_groupby = []

    try:
        for item in data_cuts:
            if sessiondict.get(str(item)) is not None:
                samplelist.append(item)

            if sessiondict.get("groupby") is not None:
                if item in sessiondict.get("groupby"):
                    samplelist.append(item)
    except Exception as e:
        print(e)
    print (samplelist)
#  to pick subject ID based on the intent  -- 20/05    
    try:
        mycol = db["subjectArea_d"]
        myquery = {"subjectArea": sessiondict.get("Intent")}
        mydoc = mycol.find(myquery)
        for y in mydoc:
            pass
        subjectid = y["id"]
        print(subjectid)
    except Exception as e:
        print(e)
        
        
    try:
        samplelist = list(dict.fromkeys(samplelist))
        list_where_groupby = samplelist
        list_where_groupby = [item for item in list_where_groupby if item not in entkey]
        # to ensure that we take the MaxSummaryLevels from Loss ratio too
        samplelist.append(sessiondict.get("Intent"))
        
        mycol = db["attributeMaster_d"]
        maxSummaryList = []
        for item in samplelist:
# 20/05           
            myquery = {"$and": [{"$or":[{"subjectArea": "DT"},{"subjectArea": str(subjectid)}]},{"attributeName": str(item)},{"timePeriod": str(time_period)}]}
            print(myquery)
            mydoc = mycol.find(myquery)
            for y in mydoc:
                pass
     
            maxSummaryList.append(int(y["maxSummaryLevel"]))

        min_summary = min(maxSummaryList)
        
        for item in calentity:
            myquery = {"$and": [{"attributeName": str(entkey)},{"subjectArea": str(subjectid)}, {"timePeriod": str(time_period)},{"maxSummaryLevel": min_summary}]}
            print (myquery)
            mydoc = mycol.find(myquery)
            for y in mydoc:
                pass
            intent_aliasName = y["alias"]   
            print (intent_aliasName)

        mycol = db["attributeEntity_d"]

        for item in calentity:
        # 20/05           
            myquery = {"$and": [{"attributeName": str(entkey)},{"summaryLevel": min_summary},{"timePeriod": str(time_period)}]}
            print (myquery)
            
            mydoc = mycol.find(myquery)
            for y in mydoc:
                pass
            
            intent_entity_id = y["entityId"]
            select_column = y["columnNamePhysical"]
            print (intent_entity_id)
            print(select_column)


        
        ID = {}
        fieldNameMapping = {}
        samplelist.remove(sessiondict.get("Intent"))
        samplelist = [item for item in samplelist if item not in entkey]
        print (samplelist)
        try:
            for item in samplelist:
                myquery = {
                    "$and": [{"attributeName": item}, {"summaryLevel": min_summary}, {"timePeriod": time_period}]}
                mydoc = mycol.find(myquery)
                for y in mydoc:
                    if y is not None:
                        ID[(str(item) + "_entityId")] = y["entityId"]
                        fieldNameMapping[str(y["entityId"])] = y["columnNamePhysical"]
                    pass
        except Exception as e:
            print(e)
        Query = "SELECT " + select_column + " AS " + intent_aliasName + " FROM "         
        print (Query)
        coll = db["attributeEntity_d"]
        attributelist=[]
        entityIdlist=[]
        tableNamelist=[]
        fieldNamelist=[]
        columnNamelist=[]
        mappingInfodict={}
        print("Hello")
        
        for n in list_where_groupby:
            
            tempJson = {}
            for x in coll.find({"attributeName": n, "summaryLevel": min_summary, "timePeriod": time_period}):
                tempJson["attribute"] = n
                tempJson["entityId"] = x["entityId"]
                tempJson["tableName"] = x["entityName"]
                tempJson["fieldName"] = x["columnNamePhysical"].split('.')[1]
                tempJson["columnName"] = x["columnNamePhysical"]
                print('tempColl to be inserted to mapping Info---------',tempJson)        
        
                mappingInfodict[n]=x["columnNamePhysical"]
                attributelist.append(n)
                entityIdlist.append(x["entityId"])
                tableNamelist.append(x["entityName"])
                fieldNamelist.append(x["columnNamePhysical"].split('.')[1])
                columnNamelist.append(x["columnNamePhysical"])
        df_mapping = {'attribute': attributelist, 'entityId': entityIdlist, 'tableName':tableNamelist, 'fieldName':fieldNamelist, 'columnName':columnNamelist}
        df_mappinginfo = pd.DataFrame(data=df_mapping)
        
        
        # Read entityMaster Collection, get entityNamePhysical where entityId= intent_entity_id and save to entityNamePhysical to the variable select_table
        
        mycol = db["entityMaster_d"]
        myquery = {"entityId": intent_entity_id}
        mydoc = mycol.find(myquery)
        for y in mydoc:
            pass
        select_table = y["entityNamePhysical"]
        tableNameMapping = {}
        for keys in fieldNameMapping:
            myquery = {"entityId": keys}
            mydoc = mycol.find(myquery)
            for y in mydoc:
                pass
            tableNameMapping[str(keys)] = y["entityNamePhysical"]
        Query = Query + select_table + " " + intent_entity_id
    except Exception as e:
        print(e)
    
    # Iterate for keys in ID dictionary that are not null,
    try:
        mycol = db["join_d"]
    except Exception as e:
        print(e)
    try:
        for key in ID:
            if key is not None:
                myquery = {"$and": [{"entityId": ID[key]}, {"joinEntityId": intent_entity_id}]}
                mydoc = mycol.find(myquery)
                for y in mydoc:
                    if y is not None:
                        join_key = y["joinKey"]
                        join_tableName = tableNameMapping[ID[key]]
                        Query = Query + " INNER JOIN " + join_tableName + " " + ID[key] + " ON " + join_key
    except Exception as e:
        print(e)


    try:
        data_cuts = [item for item in data_cuts if item not in entkey]
        for item in data_cuts:


            if sessiondict.get(str(item)) is not None:


                if item in mappingInfodict:
                    columnName = mappingInfodict[item]
                if item != "Account Date":
                    if len(sessiondict.get(str(item))) == 1:
                        tempstring = str(columnName) + " = '" + str(sessiondict.get(str(item))[0]) + "' "
                      

                    else:
                        tempstring = str(columnName) + " in ('"
                        s = "',"
                        s = s.join(sessiondict.get(str(item)))
                        s = s.replace(",", ",'")
                        tempstring = tempstring + s + "') "
                      

                else:
                    if sessiondict.get("timeperiod") != "MTD":
                        if len(sessiondict.get(str(item))) == 1:
                            tempstring = str(columnName) + " = " + str(sessiondict.get(str(item))[0]) + " "
                           

                        else:
                            temp = []
                            for item1 in sessiondict.get(str(item)):
                                temp.append(item1)
                            temp.sort()
                            tempstring = str(columnName) + " in ('"
                            s = "',"
                            s = s.join(temp)
                            s = s.replace(",", ",'")
                            tempstring = tempstring + s + "') "
                           


                    else:
                        if len(sessiondict.get(str(item))) == 1:
                            if sessiondict.get("time_range") is None:
                                tempstring = str(columnName) + " = " + str(sessiondict.get(str(item))[0]) + " "
                                

                            elif "from" in sessiondict.get("time_range") or "since" in sessiondict.get("time_range") or "starting" in sessiondict.get("time_range"):
                                tempstring = str(columnName) + " >='" + str(sessiondict.get(str(item))[0]) + "' "
                              

                            elif "to" in sessiondict.get("time_range") or "till" in sessiondict.get(
                                    "time_range") or "until" in sessiondict.get(
                                    "time_range") or "before" in sessiondict.get("time_range"):
                                tempstring = str(columnName) + " <='" + str(sessiondict.get(str(item))[0]) + "' "
                              


                            else:
                                tempstring = str(columnName) + " = " + str(sessiondict.get(str(item))[0]) + " "
                            


                        else:
                            # Sorting the valuesin the list
                            temp = []
                            for item1 in sessiondict.get(str(item)):
                                temp.append(item1)
                            temp.sort()
                            
                            pass
                            if sessiondict.get("time_range") is None:
                                tempstring = str(columnName) + " in ('"
                                s = "',"
                                s = s.join(temp)
                                s = s.replace(",", ",'")
                                tempstring = tempstring + s + "') "
                             




                            elif "previous" in sessiondict.get("time_range") or "past" in sessiondict.get("time_range") or "last" in sessiondict.get("time_range"):
                                
                                temp[-1] = str(int(temp[-1])-1)
                                tempstring = str(columnName) + " BETWEEN '" + temp[0] + "' AND '" + temp[-1] + "' "




                            elif "from" in sessiondict.get("time_range") or "since" in sessiondict.get(
                                    "time_range") or "staring" in sessiondict.get(
                                    "time_range") or "to" in sessiondict.get("time_range") or "till" in sessiondict.get("time_range") or "until" in sessiondict.get(
                                    "time_range") or "before" in sessiondict.get(
                                    "time_range") or "between" in sessiondict.get("time_range"):
                                tempstring = str(columnName) + " BETWEEN '" + temp[0] + "' AND '" + temp[-1] + "' "


                            else:
                                tempstring = str(columnName) + " in ('"
                                s = "',"
                                s = s.join(temp)
                                s = s.replace(",", ",'")
                                tempstring = tempstring + s + "') " 
                                print ("Hello0" + tempstring)


                if "WHERE" in Query:
                    print (tempstring)
                    Query = Query + "AND " + tempstring


                else:
                    Query = Query + " WHERE " + tempstring


    except Exception as e:
        print(e)


    # Filter query generation (12-05-2020)
    try:
        mycol = db["attributeMaster_d"]
        for items in calentity:
            myquery = {"$and": [{"attributeName": str(entkey)}, {"timePeriod": str(time_period)}]}
            result = mycol.find( myquery )
            for y in result:
                pass
        sec = y["filter"]
        print (sec)

        if (("WHERE" in Query) & (len(sec)!=0)):
            Query = Query + " AND " + sec +" "
            #print (Query)
        elif(("WHERE" not in Query) & (len(sec)!=0)):
            Query = Query + " WHERE " + sec +" "
            #print ("Else loop")       
        print (Query)

    except Exception as e:
        print(e)

    # Groupby query generation
    try:
        if sessiondict.get("combined") is not 'true':

            select_tempstring = ""
            for item in list_where_groupby:
                if item in mappingInfodict:
                    columnName = mappingInfodict[item]

                select_tempstring = select_tempstring + str(columnName) + " ,"

            groupby_tempstring = select_tempstring[:-1]
            Query = Query.replace("SELECT", str("SELECT " + select_tempstring))
            Query = Query + "GROUP BY " + groupby_tempstring
    except Exception as e:
        print(e)

    # connecting to SQL database
    try:
        congfig_file = 'config.yml'
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

        try:
            renamedict ={}
            for key in df.keys():

                for x in db.attributeMaster_d.find({"alias": key}):
                    renamedict[key] =x['attributeName']
                tempdf =df_mappinginfo.loc[df_mappinginfo['fieldName'] == key]

                if tempdf.empty == False:
                    renamedict[key] = str(tempdf["attribute"].values[0])


            for key in df.keys():
                df = df.rename(columns={key: renamedict[key]})
            if 'Loss ratio' in df.columns:
                df = df.rename(columns = {"Loss ratio" : "Loss ratio(%)"})
        except Exception as e:
            df = None        
        
    except Exception as e:
        print(e)
    #print (samplelist)
    
    return df,list_where_groupby
    
#def main():
#    a,b = sql_gen({'_permanent': True, 'Intent': 'Agent Performance', 'Renewal Policy Count': ['renewal policy count'], 'groupby': ['Coverage'], 'combined': None, 'vizType': None, 'fileName': None, 'timeperiod': 'MTD', 'Account Date': ['202004'], 'Region': None, 'Line of Business': None, 'Agent': None, 'time_range': None, 'Loss ratio': None, 'Coverage': None})
#    print(a,b)
#
#if __name__=="__main__":
#    main()
    