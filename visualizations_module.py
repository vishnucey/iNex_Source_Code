import pandas as pd
from io import StringIO
import re
import pymongo
import os
from datetime import datetime as dt
from cosmosdb_connection import *
import json
import yaml



# congfig_file = 'config.yml'
# loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
# uri= loaded_parameters['vismodule']['uri']

uri = "mongodb://inexbotcosmosdb:imiDU1weWpyt61akkwhmtzCVhNQcbO47KjU4MkDmRuZhFZQs7QbAva0g1fxNcyR5pMBX8pOIMf4htjdUNapJdA==@inexbotcosmosdb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"

client = pymongo.MongoClient(uri)
inexDB = client.iNex_db

def invokeD3(session,df,cutsList):
    global inexDB

    multipleValues=[]
    singleValue=[]
    print('df---', df)
    if df is None:
        print('data frame none')
        response = {'error': 0, 'message': 'No output has been generated from SQL query',
                    'speechOutput': 'No output has been generated from SQL query'}
        vizType = "nil"

    elif df.empty:
        print('data empty')
        response = {'error': 0, 'message': 'No output has been generated from SQL query',
                    'speechOutput': 'No output has been generated from SQL query'}
        vizType = "nil"


    else:
        if len(df.axes[0]) == 0:
            vizType = "nil"
            response = {'error': 0, 'message': 'No output has been generated from SQL query',
                        'speechOutput': 'No output has been generated from SQL query'}

        elif len(df.axes[0]) !=0:

            for cut in cutsList:
                if cut in df.keys():
                    if len(df[cut].unique())!=1:
                        multipleValues.append(cut)
                    else:
                        singleValue.append(cut)

            


            if len(df.axes[0]) == 1:

                message = " "
                accFlag=0
                # if session.get('combined')=='true':
                #     message = message + "combined "
                if session.get('timeperiod') is not None:
                    message=message + session['timeperiod']
                print(session)

                if session.get('Renewal Policy Count')==['renewal policy count']:
                    message =message+" "+'Renewal Policy Count'
                elif session.get('Loss ratio')==['loss ratio']:
                    message=message+" "+'Loss ratio'

                #session['Intent'] = 'Renewal Policy Count'

                #message=message+ " "+session['Intent']
                print("length", len(df.axes[1]))
                print("IN AXES = 1")
                print (df)
                for i in range(len(df.axes[1]) - 1):
                    if df.keys()[i] == 'Account Date' and session.get('timeperiod')!='QTD':
                        accFlag=1
                        print (df['Account Date'])
                        for n in df['Account Date'].unique():
                            print('in acct date')
                            print (n)
                            if session.get('time_range') is not None:
                                print('time range null')
                                if 'till' in session['time_range'] or 'until' in session['time_range'] or 'as of' in \
                                        session['time_range']:
                                    message = message + " till " + dt.strptime(str(n), "%Y%m").strftime("%B %Y")
                                else:
                                    print('in else 1')
                                    message = message + " for " + dt.strptime(str(n), "%Y%m").strftime("%B %Y")
                            else:
                                print('in else 2')
                                message = message + " for " + dt.strptime(str(n), "%Y%m").strftime("%B %Y")

                    elif df.keys()[i] == 'Account Date' and session.get('timeperiod') == 'QTD':
                        accFlag=1
                        qList=['03','06','09','12']
                        for accDate in df['Account Date'].unique():
                            print('acctDtae--',accDate)
                            for qtrIndex in range(qList.__len__()):
                                if qList[qtrIndex]==str(accDate)[4:6]:
                                    message = message + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                        message=message.rstrip(',')



                    elif df.keys()[i] not in 'Account Date':
                        message = message + " for " + str(df.iloc[0, i])

                    # if i+1 !=len(df.axes[1])-1:
                    #     message=message + ', '
                    # else:
                    #     message = message + ' '
                if accFlag==0:
                    if len(session.get('Account Date'))==1:
                        n=session.get('Account Date')[0]
                        message=message+" for "+dt.strptime(str(n), "%Y%m").strftime("%B %Y")

                message = message + ' is ' + str(df.iloc[0, len(df.axes[1]) - 1])

               # if session.get('Intent').lower()=='loss ratio':
                print (session)
                if session.get('Loss ratio')==['loss ratio']:
                    message=message+'%'
                    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ MESSAGE $$$$$$$$$$$$$$$$$$$')
                    print(message)
                #response = {'message': message,'speechOutput':message}
                response = message

                vizType="text"
                print(message)

            elif len(df.axes[0]) == 2:
                print ("length of df axes == 2")
                vizType = "table"
                response=""
                temp_string=""
                templist=[]
                if len(singleValue)!= 0:
                    print("inside singleValue loop")
                    for i in singleValue:
                        if i == "Account Date":
                            if session.get('timeperiod')!='QTD':
                                item =str(df[i].unique()).replace("[","").replace("]","")
                                item = dt.strptime(str(item), "%Y%m").strftime("%B %Y")
                                temp_string = temp_string +" in " +item
                                temp_string=temp_string.replace("'","")+" , "

                            elif session.get('timeperiod') == 'QTD':
                                qList=['03','06','09','12']
                                for accDate in df[i].unique():
                                    print('acctDtae--',accDate)
                                    for qtrIndex in range(qList.__len__()):
                                        if qList[qtrIndex]==str(accDate)[4:6]:
                                            temp_string = temp_string + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                                temp_string=temp_string.rstrip(',')
                        else:
                            temp_string = temp_string +" in " +str(df[i].unique()).replace("[","").replace("]","") 
                            temp_string=temp_string.replace("'","")+" , " 
                print(multipleValues)
                if len(multipleValues)!= 0:
                    for item in multipleValues:
                        if item == "Account Date":
                            print ("inside Account Date")
                            if session.get('timeperiod') != 'QTD':
                                for item in session.get("Account Date"):
                                    item = dt.strptime(str(item), "%Y%m").strftime("%B %Y")
                                    templist.append(item)
                                templist.sort()
                                if session.get("time_range") is None:
                                    print("session.get(time_range) is None:")
                                    temp_string = temp_string + " for time period in "
                                    s = ", "
                                    s = s.join(templist)
                                    # s = s.replace(",", ",'")
                                    temp_string = temp_string + s
                                    print("temp_string --",temp_string)
                                elif "previous" in session.get("time_range") or "past" in session.get("time_range") or "last" in session.get("time_range") or "from" in session.get("time_range") or "since" in session.get(
                                            "time_range") or "staring" in session.get(
                                            "time_range") or "to" in session.get("time_range") or "till" in session.get("time_range") or "until" in session.get(
                                            "time_range") or "before" in session.get(
                                            "time_range") or "between" in session.get("time_range"):
                                    temp_string = temp_string + " for time period between " + str(templist[0]) + " and " + str(templist[-1]) + " "
                                else:
                                    print("inside else condition")
                                    temp_string = temp_string + " for time period in "
                                    s = "',"
                                    s = s.join(templist)
                                    s = s.replace(",", ", ")
                                    temp_string = temp_string + s
                            elif session.get('timeperiod') == 'QTD':
                                qList=['03','06','09','12']
                                for accDate in df["Account Date"].unique():
                                    print('acctDtae--',accDate)
                                    for qtrIndex in range(qList.__len__()):
                                        if qList[qtrIndex]==str(accDate)[4:6]:
                                            temp_string = temp_string + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                                temp_string=temp_string.rstrip(',')
                        else:
                            print("In multile list except for Account Date")
                            if session.get("groupby") is not None:
                                if item not in session.get("groupby"):
                                    temp_string = temp_string  + " in "
                                    s = ","
                                    s = s.join(session.get(str(item)))
                                    # s = s.replace(",", ",'")
                                    temp_string =  temp_string + s + " "
                            else:
                                temp_string = temp_string  + " in "
                                s = ","
                                s = s.join(session.get(str(item)))
                                # s = s.replace(",", ",'")
                                temp_string =  temp_string + s + " "
                intent=str(session.get('Intent'))
                print ("the temp_string is ---",temp_string)
                if(intent == 'Agent Performance'):
                    if (session.get('Renewal Policy Count')==['renewal policy count']):
                        intent = 'Renewal Policy Count '
                    elif(session.get('Loss ratio')==['loss ratio']):
                        intent = 'Loss ratio '
                response = intent +temp_string
                print ("the response is ---",response)
            ##If row count of SQL output >2 and for single cut, generate respective visualization and tabular structure
            elif len(df.axes[0]) > 2:
                print ("inside length greater than 2")
                print('multipleValueList',multipleValues)
                print('singleValueList',singleValue)
                temp_string=""
                if len(multipleValues)==1:
                    if len(singleValue)!= 0:
                        print("inside singleValue loop")
                        for i in singleValue:
                            if i == "Account Date":
                                if session.get('timeperiod')!='QTD':
                                    item =str(df[i].unique()).replace("[","").replace("]","")
                                    item = dt.strptime(str(item), "%Y%m").strftime("%B %Y")
                                    temp_string = temp_string +" in " +item
                                    temp_string=temp_string.replace("'","")+" , "
                                elif session.get('timeperiod') == 'QTD':
                                    qList=['03','06','09','12']
                                    for accDate in df[i].unique():
                                        print('acctDtae--',accDate)
                                        for qtrIndex in range(qList.__len__()):
                                            if qList[qtrIndex]==str(accDate)[4:6]:
                                                temp_string = temp_string + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                                    temp_string=temp_string.rstrip(',')
                            else:
                            # print (session.get(str(item[0])))
                                temp_string = temp_string +" in " +str(df[i].unique()).replace("[","").replace("]","") 
                                temp_string=temp_string.replace("'","")+" , "
                    print ("when multipleValues == 1")
                    attr=multipleValues[0]
                    print(multipleValues[0])
                    templist=[]
                    if multipleValues[0] == "Account Date":
                        print ("inside Account Date")
                        if session.get('timeperiod') != 'QTD':
                            for item in session.get("Account Date"):
                                item = dt.strptime(str(item), "%Y%m").strftime("%B %Y")
                                templist.append(item)
                            templist.sort()
                            if session.get("time_range") is None:
                                print("session.get(time_range) is None:")
                                temp_string = " for time period in "
                                s = ","
                                s = s.join(templist)
                                # s = s.replace(",", ", ")
                                temp_string = temp_string + s +" "
                                print("temp_string --",temp_string)
                            elif "previous" in session.get("time_range") or "past" in session.get("time_range") or "last" in session.get("time_range") or "from" in session.get("time_range") or "since" in session.get(
                                        "time_range") or "staring" in session.get(
                                        "time_range") or "to" in session.get("time_range") or "till" in session.get("time_range") or "until" in session.get(
                                        "time_range") or "before" in session.get(
                                        "time_range") or "between" in session.get("time_range"):
                                temp_string = " for time period between " + str(templist[0]) + " and " + str(templist[-1]) + " "
                            else:
                                print("inside else condition")
                                temp_string = " in "
                                s = ","
                                s = s.join(templist)
                                # s = s.replace(",", ",'")
                                temp_string = temp_string + s+"'"
                        elif session.get('timeperiod') == 'QTD':
                            qList=['03','06','09','12']
                            for accDate in df["Account Date"].unique():
                                print('acctDtae--',accDate)
                                for qtrIndex in range(qList.__len__()):
                                    if qList[qtrIndex]==str(accDate)[4:6]:
                                        temp_string = temp_string + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                            temp_string=temp_string.rstrip(',')

                    else:
                        print ("IN else condition except for Account date")
                        if session.get("groupby") is not None:
                            if multipleValues[0] not in session.get("groupby"):
                                temp_string = temp_string  + " in "
                                s = ","
                                s = s.join(session.get(str(multipleValues[0])))
                                # s = s.replace(",", ",'")
                                temp_string =  temp_string + s + " "
                        else:
                            temp_string = temp_string  + " in "
                            s = ","
                            s = s.join(session.get(str(multipleValues[0])))
                            # s = s.replace(",", ",'")
                            temp_string =  temp_string + s + " "        
                    intent=str(session.get('Intent'))
                    
                    samplelist = [session.get("Loss ratio"),session.get("Renewal Policy Count")]
                    calentity =[]
                    for item in samplelist:
                        if item is not None:
                            calentity.append(item[0])
                    print (calentity)
                    entkey = (list(session.keys())[list(session.values()).index(calentity)]) 
                    
                    dbContent = inexDB.visualizationMetadata_d.find({"entity": entkey,"attribute":attr})

                    for n in dbContent:
                        print('type----',n['visualizationtype'])
                        vizType=n['visualizationtype']
                        print(vizType)
                        #response = intent + " "+temp_string
                        response = entkey + " "+temp_string
                        if (singleValue.__len__()!=0 and cutsList.__len__()>1) or (cutsList.__len__()==1 and singleValue.__len__()==0):
                            print ("inside loop")
                            for i in singleValue:
                                if i=='Account Date':
                                    print ("inside Account date in multiple value list")
                                    n=str(df[i].unique()).replace("[","").replace("]","")
                                    convertedValue=dt.strptime(str(n), "%Y%m").strftime("%B %Y")
                                    # response=response + " " + convertedValue +" ,"
                                else:
                                    pass
                                #     response = response +" and for " +str(df[i].unique()).replace("[","").replace("]","") 
                                # response=response.replace("'","")

                                df.drop([i], axis=1, inplace=True)
                        else:
                            #if cutsList.__len__()==1:
                            response=""
                            vizType='table'



                else:
                    print ("when multipleValues != 1")
                    vizType="table"
                    temp_string=""
                    templist=[]
                    response = ""
                    if len(singleValue)!= 0:
                        print("inside singleValue loop")
                        for i in singleValue:
                            if i == "Account Date":
                                if session.get('timeperiod') != 'QTD':
                                    item =str(df[i].unique()).replace("[","").replace("]","")
                                    item = dt.strptime(str(item), "%Y%m").strftime("%B %Y")
                                    temp_string = temp_string +" in " +item
                                    temp_string=temp_string.replace("'","")+" , "
                                elif session.get('timeperiod') == 'QTD':
                                    qList=['03','06','09','12']
                                    for accDate in df[i].unique():
                                        print('acctDtae--',accDate)
                                        for qtrIndex in range(qList.__len__()):
                                            if qList[qtrIndex]==str(accDate)[4:6]:
                                                temp_string = temp_string + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                                    temp_string=temp_string.rstrip(',')
                            else:
                            # print (session.get(str(item[0])))
                                temp_string = temp_string +" in " +str(df[i].unique()).replace("[","").replace("]","") 
                                temp_string=temp_string.replace("'","")+" , "
                    for item in multipleValues:
                        if item == "Account Date":
                            print ("inside Account Date")
                            if session.get('timeperiod') != 'QTD':
                                for item in session.get("Account Date"):
                                    item = dt.strptime(str(item), "%Y%m").strftime("%B %Y")
                                    templist.append(item)
                                templist.sort()
                                if session.get("time_range") is None:
                                    print("session.get(time_range) is None:")
                                    temp_string = temp_string + " for time period in "
                                    s = ", "
                                    s = s.join(templist)
                                    # s = s.replace(",", ",'")
                                    temp_string = temp_string + s
                                    print("temp_string --",temp_string)
                                elif "previous" in session.get("time_range") or "past" in session.get("time_range") or "last" in session.get("time_range") or "from" in session.get("time_range") or "since" in session.get(
                                            "time_range") or "staring" in session.get(
                                            "time_range") or "to" in session.get("time_range") or "till" in session.get("time_range") or "until" in session.get(
                                            "time_range") or "before" in session.get(
                                            "time_range") or "between" in session.get("time_range"):
                                    temp_string = temp_string + " for time period between " + str(templist[0]) + " and " + str(templist[-1]) + " "
                                else:
                                    print("inside else condition")
                                    temp_string = temp_string + " for time period in "
                                    s = "',"
                                    s = s.join(templist)
                                    s = s.replace(",", ", ")
                                    temp_string = temp_string + s
                            elif session.get('timeperiod') == 'QTD':
                                qList=['03','06','09','12']
                                for accDate in df["Account Date"].unique():
                                    print('acctDtae--',accDate)
                                    for qtrIndex in range(qList.__len__()):
                                        if qList[qtrIndex]==str(accDate)[4:6]:
                                            temp_string = temp_string + " for " + str(accDate)[0:4] + " quarter " + str(qtrIndex + 1) + ","
                                temp_string=temp_string.rstrip(',')
                        else:
                            print("In multile list except for Account Date")
                            if session.get("groupby") is not None:
                                if item not in session.get("groupby"):
                                    temp_string = temp_string  + " in "
                                    s = ","
                                    s = s.join(session.get(str(item)))
                                    # s = s.replace(",", ",'")
                                    temp_string =  temp_string + s + " "
                            else:
                                temp_string = temp_string  + " in "
                                s = ","
                                s = s.join(session.get(str(item)))
                                # s = s.replace(",", ",'")
                                temp_string =  temp_string + s + " "
                        intent=str(session.get('Intent'))
                        
                print ("the temp_string is ---",temp_string)
                response = entkey +temp_string
                #response = intent +temp_string
                print ("the response is ---",response)


    print("Before returning -----",vizType,response)
    try:
        response = response.strip().rstrip(',')
        print (response)
        totallist = multipleValues + singleValue
        if session.get("groupby") is not None:
            temp = ""
            for item in totallist:
                if item in session.get("groupby"):
                    temp = temp + item + ","
            response = response + " by " + temp.lower()
            response = response.strip().rstrip(',')
        if session.get('combined')=='true':
            response='the combined '+response
        else:
            response='the ' +response
    except:
        pass
    return vizType,response,df


def visualizationCode(vizType,fileName):
    print("in visualization code")
    print(fileName)
    if vizType=='table':
        script="<script>\n" \
        " d3.text(\"/static/"+fileName+"\", function(datasetText) {\n"\
        "var parsedCSV = d3.csv.parseRows(datasetText);\n"\
        "var sampleHTML = d3.select(\"#viz\")\n"\
        ".append(\"table\")\n"\
        ".style(\"border-collapse\", \"collapse\")\n"\
        ".style(\"border\", \"2px black solid\")\n"\
        ".selectAll(\"tr\")\n"\
        ".data(parsedCSV)\n"\
        ".enter().append(\"tr\")\n\n"\
        ".selectAll(\"td\")\n"\
        ".data(function(d){return d;})\n"\
        ".enter().append(\"td\")\n"\
        ".on(\"mouseover\", function(){d3.select(this).style(\"background-color\", \"aliceblue\")})\n"\
        ".on(\"mouseout\", function(){d3.select(this).style(\"background-color\", \"white\")})\n"\
        ".text(function(d){return d;})\n"\
        "});\n  </script>"


    elif vizType=='linechart':
        script="<script src=\"http://d3js.org/d3.v3.min.js\"></script>\n"\
        "<script>\n" \
        " var margin = {top: 50, right: 30, bottom: 30, left: 50}, \n" \
        "width = 768 - margin.left - margin.right,\n" \
        "height = 400 - margin.top - margin.bottom; \n" \
        "var parseDate = d3.time.format(\"%Y%m\").parse; \n" \
        "var x = d3.time.scale().range([0, width]); \n" \
        "var y = d3.scale.linear().range([height, 0]); \n" \
        "var xAxis = d3.svg.axis().scale(x)\n" \
        ".orient(\"bottom\").ticks(10)\n" \
        ".innerTickSize(-height)\n" \
        ".outerTickSize(0)\n" \
        ".tickPadding(10);\n" \
        "var ticks = y.ticks(),\n" \
        "lastTick = ticks[ticks.length - 1],\n" \
        "newLastTick = lastTick + (ticks[1] - ticks[0]);\n" \
        "if (lastTick < y.domain()[1]){\n" \
        "ticks.push(newLastTick);}\n" \
        "y.domain([y.domain()[0], newLastTick]);\n" \
        "var yAxis = d3.svg.axis().scale(y)\n" \
        ".orient(\"left\").ticks(10)\n" \
        ".innerTickSize(-width)\n" \
        ".outerTickSize(0)\n" \
        ".tickPadding(10)\n"\
        ".tickValues(ticks);\n"\
        "var svg = d3.select(\"body\")\n"\
        ".append(\"svg\")\n" \
        ".attr(\"width\", width + margin.left + margin.right)\n" \
        ".attr(\"height\", height + margin.top + margin.bottom)\n" \
        ".append(\"g\")\n"\
        ".attr(\"transform\", \"translate(\" + margin.left + \",\" + margin.top + \")\");\n"\
        "d3.csv(\"/static/"+fileName+"\", function(error, data) {\n"\
        "var headers = d3.keys(data[0])\n"\
        "var valueline = d3.svg.line()\n"\
        ".x(function(d) { return x(d[headers[0]]); })\n"\
        ".y(function(d) { return y(d[headers[1]]); });\n"\
        "data.forEach(function(d) {\n"\
        "d[headers[0]] = parseDate(d[headers[0]]);\n"\
        "d[headers[1]] = +d[headers[1]];\n"\
        "});\n"\
        "x.domain(d3.extent(data, function(d) { return d[headers[0]]; }));\n"\
        "y.domain([0, d3.max(data, function(d) { return d[headers[1]]; })]);\n"\
        "svg.append(\"path\")\n"\
        ".attr(\"class\", \"line\")\n"\
        ".attr(\"d\", valueline(data));\n"\
        "svg.append(\"g\")\n"\
        ".attr(\"class\", \"x axis\")\n"\
        ".attr(\"transform\", \"translate(0,\" + height + \")\")\n"\
        ".call(xAxis);\n" \
        "svg.append(\"text\")\n" \
        ".attr(\"x\", width / 2 ) \n" \
        ".attr(\"y\",0 - (margin.top / 2))\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"text-anchor\", \"middle\")\n" \
        ".attr(\"font-size\", \"16px\")\n" \
        ".attr(\"font-weight\", \"bold\")\n" \
        ".text(headers[1]+\" by \"+ headers[0]);\n" \
        "svg.append(\"g\")\n"\
        ".attr(\"class\", \"y axis\")\n"\
        ".call(yAxis)\n" \
        ".append(\"text\")\n" \
        ".attr(\"transform\", \"rotate(-90)\")\n" \
        ".attr(\"y\", -20)\n" \
        ".attr(\"dy\", \"-1.5em\")\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"12px\")\n" \
        ".style(\"text-anchor\", \"end\")\n" \
        ".text(headers[1]);\n" \
        "svg.append(\"g\")\n" \
        ".classed(\"labels-group\", true)\n" \
        ".selectAll(\"text\")\n" \
        ".data(data)\n" \
        ".enter().append(\"text\")\n" \
        ".classed(\"label\", true)\n" \
        ".attr({\n" \
        "\"x\": function(d, i) {\n" \
        "return x(d[headers[0]]);\n" \
        "},\n" \
        "\"y\": function(d, i) {\n" \
        "return y(d[headers[1]]);\n" \
        "},\n" \
        "})\n" \
        ".text(function(d, i) {\n" \
        "return d[headers[1]];\n" \
        "});\n" \
        "svg.append(\"text\")\n"\
        ".attr(\"transform\", \"translate(\" + (width + 3) + \",\" + y(data[0][headers[1]]) + \")\")\n"\
        ".attr(\"dy\", \".35em\")\n"\
        ".attr(\"text-anchor\", \"start\")\n"\
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"12px\")\n" \
        ".style(\"fill\", \"white\")\n"\
        ".text(headers[1]);\n"\
        "});\n"\
        "</script>"


    elif vizType=='barchart':
        script="<script src=\"http://d3js.org/d3.v3.min.js\"></script>\n"\
        "<script>\n" \
        "var margin = {top: 100, right: 50, bottom: 250, left: 150},\n"\
        "width = 1000 - margin.left - margin.right,\n"\
        "height = 700 - margin.top - margin.bottom;\n"\
        "var x = d3.scale.ordinal().rangeRoundBands([0, width*1.1], .5);\n"\
        "var y = d3.scale.linear().range([height, 0]);\n"\
        "var xAxis = d3.svg.axis().scale(x)\n" \
        ".orient(\"bottom\");\n" \
        "var yAxis = d3.svg.axis().scale(y)\n" \
        ".orient(\"left\")\n" \
        ".innerTickSize(-width)\n" \
        ".outerTickSize(0)\n" \
        ".tickPadding(10);\n" \
        "var svg = d3.select(\"body\").append(\"svg\")\n"\
        ".attr(\"width\", width + margin.left + margin.right)\n"\
        ".attr(\"height\", height + margin.top + margin.bottom)\n"\
        ".append(\"g\")\n"\
        ".attr(\"transform\",\n"\
        "\"translate(\" + margin.left + \",\" + margin.top + \")\");\n"\
        "d3.csv(\"/static/"+fileName+"\", function(error, data) {\n" \
        "var headers = d3.keys(data[0])\n" \
        "if (error) {\n" \
        "throw error;\n" \
        "}\n" \
        "data.forEach(function(d)\n"\
        "{\n"\
        "d[headers[1]] = +d[headers[1]];\n"\
        "});\n"\
        "x.domain(data.map(function(d)\n"\
        "{\n"\
        "return d[headers[0]];\n"\
        "}));\n"\
        "y.domain([0, d3.max(data, function(d) {\n"\
        "return d[headers[1]]*1.1;\n"\
        "})]);\n"\
        "svg.append(\"g\")\n"\
        ".attr(\"class\", \"x axis\")\n"\
        ".attr(\"transform\", \"translate(0,\" + height + \")\")\n"\
        ".call(xAxis)\n" \
        ".selectAll(\"text\")\n" \
        ".style(\"text-anchor\", \"end\")\n" \
        ".attr(\"dx\", \"-.8em\")\n" \
        ".attr(\"dy\", \".15em\")\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"12px\")\n" \
        ".attr(\"transform\", \"rotate(-45)\")\n" \
        ";\n" \
        "svg.append(\"text\")\n" \
        ".attr('transform',\"translate(\" + (width ) + \" ,\" +(height + margin.top + 20) + \")\")\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"13px\")\n" \
        ".style(\"text-anchor\", \"end\")\n" \
        ".attr(\"font-weight\", \"bold\")\n" \
        ".text(headers[0]+' -->');\n" \
        "svg.append(\"g\")\n"\
        ".attr(\"class\", \"y axis\")\n"\
        ".call(yAxis)\n"\
        ".append(\"text\")\n"\
        ".attr(\"transform\", \"rotate(-90)\")\n"\
        ".attr(\"y\", -50)\n"\
        ".attr(\"dy\", \"-2em\")\n"\
        ".style(\"text-anchor\", \"middle\")\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"13px\")\n" \
        ".attr(\"font-weight\", \"bold\")\n" \
        ".text(headers[1]+\" -->\");\n" \
        "svg.append(\"text\")\n" \
        ".attr(\"x\", width / 2 ) \n"\
        ".attr(\"y\",0 - (margin.top / 2))\n"\
        ".attr(\"text-anchor\", \"middle\")\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"16px\")\n" \
        ".attr(\"font-weight\", \"bold\")\n" \
        ".text(headers[1]+\" by \"+ headers[0]);\n" \
        "svg.selectAll(\".bar\")\n"\
        ".data(data)\n"\
        ".enter()\n"\
        ".append(\"rect\")\n"\
        ".style(\"fill\", \"#ffe600\")\n"\
        ".style(\"stroke\", \"grey\")\n"\
        ".attr(\"class\", \"bar\")\n"\
        ".attr(\"x\", function(d)\n"\
        "{\n"\
        "return x(d[headers[0]]);\n"\
        "})\n"\
        ".attr(\"width\", x.rangeBand())\n"\
        ".attr(\"y\", function(d)\n"\
        "{\n"\
        "return y(d[headers[1]]);\n"\
        "})\n"\
        ".attr(\"height\", function(d)\n"\
        "{\n"\
        "return height - y(d[headers[1]]); });\n" \
        "svg.selectAll(\"text.bar\")\n" \
        ".data(data)\n" \
        ".enter().append(\"text\")\n" \
        ".attr(\"class\", \"bar\")\n" \
        ".attr(\"text-anchor\", \"middle\")\n" \
        ".attr(\"font-family\", \"eyinterstate\")\n" \
        ".attr(\"font-size\", \"12px\")\n" \
        ".attr(\"x\", function(d)\n" \
        "{\n"\
        "return x(d[headers[0]]) + x.rangeBand() / 2;})\n" \
        ".attr(\"y\", function(d)\n" \
        "{\n" \
        "return 15 ;})\n" \
        ".text(function(d)\n" \
        "{\n" \
        "return d[headers[1]];});\n" \
        "function type(d)\n" \
        "{\n" \
        "y(d[headers[1]]) = +y(d[headers[1]]);\n" \
        "return d;\n" \
        "}\n"\
        "});\n"\
	    "</script>"


    return script

