########### Python 3.6 #############
import requests
import json
import datetime as dt
from WordToNum.word_to_num import WordToNum
import time
from functions import *
import yaml
from os.path import dirname, join

def luisEndpointCall(query):
    current_dir = dirname(__file__)
    congfig_file = join(current_dir, "./config.yml")
    loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
    baseUrl = loaded_parameters['callendpoint']['baseurl']

    headers = {
        #'Subscription-Key': 'b6905fe73efb4928821f25f31a38cb36'
        'Ocp-Apim-Subscription-Key': '1dd6d69148094b60bb41369a71be537a'
        #'Ocp-Apim-Subscription-Key': 'b6905fe73efb4928821f25f31a38cb36'
        #'Ocp-Apim-Subscription-Key': 'bf3aa0822d9e4b4ca5b0dcc7040d3de8'
    }

    params = {

        'q': 'Agent Performance '+query,
        # Optional request parameters, set to default values
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
        'show-all-intents':'true',
    }

    outDict = {}
    topScoringIntent = "";

    dateList = []
    endDateList=[]
    statesList = []
    agentsList = []
    lobList = []
    timeRange=[]
    groupByList=[]
    monthList=[]
    sessionMonths = []
    sessionYears=[]
    currPrevList=[]
    greetingList=[]
    finalDateList=[]
    ordinalList=[]
    numberList=[]
    quarterList=[]
    quarterMonth=[]
    yearList=[]
    lossratioList=[]
    renewalpolicycountList=[]
    agentportfolioList=[]
    newbusinesscountList = []


    r = requests.get(baseUrl, headers=headers, params=params)
    outJson = r.json()
    print(outJson)
    backupDate = dt.datetime.now().strftime('%Y')

    topScoringIntent = outJson['topScoringIntent']['intent']
    print('################ TOP SCORING INTENT')
    print(topScoringIntent)
    
    if float(outJson['topScoringIntent']['score'])>=0.46:
        if ('loss ratio' in topScoringIntent):
            outDict['Intent'] = "Loss ratio"
            if "YTD" or "MTD" or "QTD" in topScoringIntent:
                outDict['timeperiod']=topScoringIntent.replace("loss ratio","").replace(" ","").replace("[","").replace(")","")
        elif topScoringIntent != 'None':
            outDict['Intent'] = outJson['topScoringIntent']['intent']
        else:
            outDict['Intent'] = None
    else:
        outDict['Intent'] = None

    if 'year' in sanitize_lowertext(query):
        outDict['timeperiod']='YTD'
    elif 'quarter' in sanitize_lowertext(query):
        outDict['timeperiod']='QTD'
    else:
        outDict['timeperiod'] = 'MTD'


    for i in range(0, len(outJson['entities'])):

        if "builtin.geographyV2" in outJson['entities'][i]['type']:
            statesList.append(outJson['entities'][i]['entity'])
        if outJson['entities'][i]['type'] == 'agent':
            agentsList.append(outJson['entities'][i]['entity'])
        if outJson['entities'][i]['type'] == 'Loss ratio':
            lossratioList.append(outJson['entities'][i]['entity'])
        if outJson['entities'][i]['type'] == 'Renewal Policy Count':
            renewalpolicycountList.append(outJson['entities'][i]['entity'])
        if outJson['entities'][i]['type'] == 'New Business Policy Count':
            newbusinesscountList.append(outJson['entities'][i]['entity'])          
        if outJson['entities'][i]['type'] == 'Agent Portfolio':
            agentportfolioList.append(outJson['entities'][i]['entity'])
            
        if outJson['entities'][i]['type'] == 'LOB':
            lobList.append(outJson['entities'][i]['entity'])
        



        if outJson['entities'][i]['type'] == 'groupBy':
            
            if 'agent' in sanitize_lowertext(outJson['entities'][i]['entity']):
                print('in agent loop')
                groupByList.append("Agent")
            if 'region' in sanitize_lowertext(outJson['entities'][i]['entity']) or 'state' in sanitize_lowertext(outJson['entities'][i]['entity']) or 'location' in sanitize_lowertext(outJson['entities'][i]['entity']):
                groupByList.append("Region")
            if 'lob' in sanitize_lowertext(outJson['entities'][i]['entity']) or 'line of business' in sanitize_lowertext(outJson['entities'][i]['entity']):
                groupByList.append("Line of Business")
            if 'coverage' in sanitize_lowertext(outJson['entities'][i]['entity']) or 'Coverage' in sanitize_lowertext(outJson['entities'][i]['entity']):
                groupByList.append("Coverage")
                

        if outJson['entities'][i]['type'] == 'combined':
            outDict['combined']='true'

        # Parse timex key of prebuilt satatimeV2 entity
        if outJson['entities'][i]['type'] == 'builtin.datetimeV2.daterange':
            valueLength=outJson['entities'][i]['resolution']['values'].__len__()
            for j in range(0,valueLength):
                dateValues=outJson['entities'][i]['resolution']['values'][j]['timex']
                date=dateValues[0:4]
                if date!='XXXX':
                    backupDate=date;

                if '(' in dateValues:
                    startDate=dateValues.replace('(','').replace(')','').split(',')[0].split('-')[0] + dateValues.replace('(','').replace(')','').split(',')[0].split('-')[1]
                    endDate= dateValues.replace('(','').replace(')', '').split(',')[1].split('-')[0] + dateValues.replace('(','').replace(')', '').split(',')[1].split('-')[1]

                    dateList.append(startDate)
                    dateList.append(endDate)
                else:
                    if not('-' in dateValues):
                        dateList.append(dateValues)
                    else:
                        dateList.append(dateValues.split('-')[0] + dateValues.split('-')[1])


        finalDateList=[]

        for n in dateList:

            n=n.replace('XXXX',backupDate);
            finalDateList.append(n)



        if outJson['entities'][i]['type'] == 'currentPrevious':


            entityValue=outJson['entities'][i]['entity']
            timeRange.append(entityValue)
            currPrevList.append(entityValue)


        if outJson['entities'][i]['type'] == 'dateRangeCategory':
            timeRange.append(outJson['entities'][i]['entity'])

        if outJson['entities'][i]['type'] == 'builtin.ordinal':
            ordinalList.append(outJson['entities'][i]['entity'])

        if outJson['entities'][i]['type'] == 'builtin.number':
            numValue=outJson['entities'][i]['entity']
            if is_int_try(numValue)==True:
                if int(numValue)<10:
                    numberList.append(numValue)
            elif is_int_try(numValue)==False:
                numberList.append(WordToNum().to_num(numValue))



        if outJson['entities'][i]['type'] == 'quarter':
            quarterList.append(outJson['entities'][i]['entity'])
        if outJson['entities'][i]['type'] == 'year':
            yearList.append(outJson['entities'][i]['entity'])
        if outJson['entities'][i]['type'] == 'month':
            monthBool=True



    monthFlag=0
    for m in currPrevList:
        if 'month' in m:
            monthFlag=1
            break


    if monthFlag==1:
        for eValue in currPrevList:
            if 'current' in eValue or 'present' in eValue or 'this' in eValue:

                sessionMonths.append(dt.datetime.now().strftime('%Y') + dt.datetime.now().strftime('%m'))
                # If entity contains the word 'previous', get previous month from today's date and append to sessionMonths list
            if 'previous' in eValue or 'past' in eValue or 'last' in eValue:

                # to get previous month, replace the day of current date with 1 and subtract 1
                lastMonth = dt.date.today().replace(day=1) - dt.timedelta(days=1)
                sessionMonths.append(lastMonth.strftime('%Y') + lastMonth.strftime('%m'))




    finalDateList=finalDateList.__add__(sessionMonths)



    yearFlag=0
    for y in currPrevList:
        if 'year' in y:
            yearFlag=1
            break

    if yearFlag==1:
        for eValue in currPrevList:
            if 'current' in eValue or 'present' in eValue or 'this' in eValue:
                sessionYears.append(dt.datetime.now().strftime('%Y')+dt.datetime.now().strftime('%m'))

            if 'previous' in eValue or 'past' in eValue or 'last' in eValue:
                lastMonth = dt.date.today().replace(day=1) - dt.timedelta(days=366)
                sessionYears.append(lastMonth.strftime('%Y')+'12')





    finalDateList=finalDateList.__add__(sessionYears)

    finalDateList = list(dict.fromkeys(finalDateList))

    if topScoringIntent=='loss ratio QTD' and quarterList.__len__()!=0:
        yearLength = yearList.__len__()

        quarters = ['03', '06', '09', '12']

        for quart in quarterList:

            if quart=='q1':
                quarterMonth.append(quarters[0])
            if quart=='q2':
                quarterMonth.append(quarters[1])
            if quart=='q3':
                quarterMonth.append(quarters[2])
            if quart=='q4':
                quarterMonth.append(quarters[3])


        for ord in ordinalList:

            if ord=='first' and numberList.__len__()==0:
                quarterMonth.append(quarters[0])
            elif ord=='first' and numberList.__len__()!=0:

                for nl in range(0,int(numberList[0])):
                    quarterMonth.append(quarters[nl])

            if ord=='second':
                quarterMonth.append(quarters[1])
            if ord=='third':
                quarterMonth.append(quarters[2])
            if ord=='fourth':
                quarterMonth.append(quarters[3])
            if ord=='first' and numberList.__len__()!=0:
                num=numberList[0]

        if yearLength==0:

            currYear=dt.datetime.now().strftime('%Y')
            finalDateList = []
            for qMonth in quarterMonth:

                qDate = currYear + qMonth
                finalDateList.append(qDate)
        elif yearLength == 1:
            currYear=yearList[0]
            finalDateList = []
            for qMonth in quarterMonth:
                qDate = currYear + qMonth
                finalDateList.append(qDate)


        else:
            finalDateList=[]
            if yearLength==quarterMonth.__len__():
                for yl in range(0,yearLength):
                    finalDateList.append(yearList[yl]+quarterMonth[yl])

        if currPrevList.__len__()!=0:
            finalDateList=[]

            for cp in currPrevList:
                day = int(dt.date.today().strftime('%d'))
                # month = int(dt.date.today().strftime('%m'))
                #Hardcoding default month value
                month = int('07')
                year = int(dt.date.today().strftime('%Y'))
                prevQuarterDate = previous_quarter(dt.date(year, month, day))
                if (cp=='past' or cp=='previous' or cp=='last') and numberList.__len__()==0:
                    if yearLength == 0:
                        print('in first curr prev')
                        finalDateList.append(str(prevQuarterDate).split('-')[0]+str(prevQuarterDate).split('-')[1])
                    else:
                        for yl in yearList:
                            finalDateList.append(yl+'12')
                elif (cp=='past' or cp=='previous' or cp=='last') and numberList.__len__()==0 and yearLength!=0:

                    for yl in yearList:
                        finalDateList.append(yl+'12')

                elif (cp == 'past' or cp == 'previous' or cp == 'last') and numberList.__len__() != 0:

                    if yearLength==0:
                        finalDateList.append(prevQuarterDate.split('-')[0] + prevQuarterDate.split('-')[1])
                        for jj in range(numberList[0]-1):
                            prevDates = [time.localtime(time.mktime((prevQuarterDate.year, prevQuarterDate.month - 3, 1, 0, 0, 0, 0, 0, 0)))[:2]]
                            replacedOut = str(prevDates).replace('[', '').replace(']', '').replace('(', '').replace(')', '')
                            prevQuarterDate = dt.date(int(replacedOut.split(',')[0]),int(replacedOut.split(',')[1]), 1)
                            finalDateList.append(str(prevQuarterDate).split('-')[0] + str(prevQuarterDate).split('-')[1])

                    if yearLength != 0:
                        finalDateList=[]

                        for yl in yearList:
                            qNo=3
                            for nl in reversed(range(int(numberList[0]))):
                                finalDateList.append(yl+quarters[qNo])
                                qNo=qNo-1

    modifiedDateList=[]
    for finalDate in finalDateList:
        if len(finalDate)==4:
            if finalDate==dt.date.today().strftime('%Y'):
                finalDate=finalDate + dt.date.today().strftime('%m')
            else:
                finalDate=finalDate +'12'
        modifiedDateList.append(finalDate)

    modifiedDateList = list(dict.fromkeys(modifiedDateList))

    if finalDateList.__len__() != 0:
        outDict['Account Date'] = modifiedDateList
    else:
        outDict['Account Date'] = None
    if timeRange.__len__() != 0:
        outDict['time_range'] = timeRange
    else:
        outDict['time_range'] = None

    if statesList.__len__()!=0:
        outDict['Region'] = statesList
    else:
        outDict['Region'] = None

    if agentsList.__len__()!=0:
        outDict['Agent']= agentsList
    else:
        outDict['Agent'] = None
        

    if lossratioList.__len__()!=0:
        outDict['Loss ratio']= lossratioList
    else:
        outDict['Loss ratio'] = None
    
    if renewalpolicycountList.__len__()!=0:
        outDict['Renewal Policy Count']= renewalpolicycountList
    else:
        outDict['Renewal Policy Count'] = None

    if newbusinesscountList.__len__()!=0:
        outDict['New Business Policy Count']= newbusinesscountList
    else:
        outDict['Renewal Policy Count'] = None 
 
    if agentportfolioList.__len__()!=0:
        outDict['Agent Portfolio']= agentportfolioList
    else:
        outDict['Agent Portfolio'] = None

    if lobList.__len__()!=0:
        outDict['Line of Business'] = lobList
    else:
        outDict['Line of Business'] =None
    if groupByList.__len__()!=0:
        outDict['groupby']= groupByList
    else:
        outDict['groupby']=None


    print('----------OutDict',outDict)
    return outDict


#def main():
#    a = luisEndpointCall("agent performance what is the renewal policy count by coverage")
#    print(a)
#
#if __name__=="__main__":
#    main()