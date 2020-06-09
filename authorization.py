from flask import *

def authorization(payload,session):
    
    user_json ={
  "product": "iNex Authorization Model",
  "version": 1,
  "releaseDate": "2020-05-06T00:00:00.000Z",
  "role": [
    {
      "rolename": "Manager",
      "App_Access": "ALL"
    },
    {
      "rolename": "Agent",
      "App_Access": "Agent"
    },
    {
      "rolename": "Staff",
      "App_Access": "Limited"
    }
  ],
  "user": [
    {
      "ID": "IN011306872",
      "name": "Vishnu",
      "role": "Manager",
      "email": "c.vishnu@gds.ey.com",
      "dateOfBirth": "1992-09-25T00:00:00.000Z",
      "Active": "True",
      "datasecurity": [
        {
          "attribute": "Region",
          "value": [
            "california","new york"
          ]
        },
        {
          "attribute": "LOB",
          "value": [
            "Home Owners"
          ]
        }
      ]
    },
    {
      "ID": "IN011306787",
      "name": "Cerin Thomas",
      "email": "cerin.thomas@gds,ey.com",
      "dateOfBirth": "1992-09-25T00:00:00.000Z",
      "Active": "True",
      "datasecurity": [
        {
          "attribute": "Region",
          "value": [
            "california","new york"
          ]
        },
        {
          "attribute": "LOB",
          "value": [
            "Home Owners"
          ]
        }
      ]
    }
  ]
}
    #print(payload)
    loc=[]
    data_sec='True'
    for i in user_json['user'] :
        name = i['name']
        active =i['Active']
        print("LINE 72************************")
        print(payload)
        if name == payload['given_name'] and active=='True':
        #print(i['role'])
        #print(i['datasecurity']) 
            for j in i['datasecurity']:
                print(j['attribute'])
                if j['attribute'] == 'Region':
                  print(j['value'])
                  loc.append(j['value'])
                  # loc = j['value']
                if j['attribute'] == 'LOB':
                  lob= j['value']
                #print(j['value'])
            print("*******LOC****")
            print(loc[0])
            print([session['Region']][0])
            if session['Region'] is None :
              session['Region'] = loc[0]
            # elif not (d in loc[0] for d in [session['Region']][0]):
            #   print("Error")
            elif not any(d not in loc[0] for d in [session['Region']][0]):
              print("Exist")
            else :
              print("not valid")
              data_sec='False'
         

            
            print(session)
            print(data_sec)
            return(session,data_sec)  
         

        else :
          session='Not Valid'
          data_sec='False'
          return(session,data_sec) 

        

def unauth_fn(response) :
  # response ={'message': }
  return jsonify(response)        
   


def authorization_role(payload):
    
    user_json ={
  "product": "iNex Authorization Model",
  "version": 1,
  "releaseDate": "2020-05-06T00:00:00.000Z",
  "role": [
    {
      "rolename": "Manager",
      "App_Access": "ALL"
    },
    {
      "rolename": "Agent",
      "App_Access": "Agent"
    },
    {
      "rolename": "Staff",
      "App_Access": "Limited"
    }
  ],
  "user": [
    {
      "ID": "IN011306872",
      "name": "Vishnu",
      "role": "Manager",
      "email": "c.vishnu@gds.ey.com",
      "dateOfBirth": "1992-09-25T00:00:00.000Z",
      "Active": "True",
      "datasecurity": [
        {
          "attribute": "Region",
          "value": [
            "california","new york"
          ]
        },
        {
          "attribute": "LOB",
          "value": [
            "Home Owners"
          ]
        }
      ]
    },
    {
      "ID": "IN011306787",
      "name": "Cerin",
      "role": "Manager",
      "email": "cerin.thomas@gds,ey.com",
      "dateOfBirth": "1992-09-25T00:00:00.000Z",
      "Active": "True",
      "datasecurity": [
        {
          "attribute": "Region",
          "value": [
            "california","new york"
          ]
        },
        {
          "attribute": "LOB",
          "value": [
            "Home Owners"
          ]
        }
      ]
    }
  ]
}

    for i in user_json['user'] :
        name = i['name']
        active =i['Active']
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(payload)
        if name == payload['given_name'] and active=='True':
          Access = "User is authorized"
          print(i['role'])
          print(Access)
          role = i['role']
          return Access,role

    else: 
      Access = "User is not authorized"
      print(Access)
      role = "No Access"
      print(role)
      return Access,role
      
         
         # if name != payload['given_name']:
         #  Access = "User is not authorized"
         #  print(Access)
         #  role = None
         #  return Access,role



          #for j in i['role']:
           # print(j['rolename'])

        #print(i['datasecurity']) 
            # for j in i['datasecurity']:
            #     print(j['attribute'])
            #     if j['attribute'] == 'Region':
            #     #print(j['value'])
            #         loc = j['value']
            #     if j['attribute'] == 'LOB':
            #     #print(j['value'])
            #         lob= j['value']


#payload = {'aud': '806ee140-3c6f-427e-bcbf-edddacc038a3', 'iss': 'https://sts.windows.net/82c658fa-8307-4e9b-9393-fe85aa2d601e/', 'iat': 1591595325, 'nbf': 1591595325, 'exp': 1591599225, 'aio': 'AVQAq/8PAAAAsZClcvnKmEt2cyb3CcnqYZprxw3Z1fVwWUtB0evSvkzC+eTj2GgIMIUS9Uc4PjtqneNOPDsFGT79a6zxOKnqOIoferuOi28ZvM9EcZMtRVk=', 'amr': ['pwd'], 'email': 'vishnuc95@gmail.com', 'family_name': 'C', 'given_name': 'Vishnu', 'idp': 'live.com', 'ipaddr': '137.97.86.254', 'name': 'Vishnu', 'nonce': '3deab945-276f-417c-b94e-c2b318c778c4', 'oid': '0fea9e2b-eabe-466f-bb26-c093eb6eff47', 'sub': 'FLu-PYqxvqnHoa9-azvJXB05iJYD7_LwzJG8ScibT_s', 'tid': '82c658fa-8307-4e9b-9393-fe85aa2d601e', 'unique_name': 'live.com#vishnuc95@gmail.com', 'uti': '_SI4xvvsGUOBYYz4yShBAA', 'ver': '1.0'}
#session = {'Account Date': ['202005'], 'Agent': None, 'Agent Portfolio': None, 'Coverage': None, 'Intent': 'Agent Performance', 'LEVEL1': ['Adjuster Performance', 'Agent Performance', 'Executive Analysis'], 'LEVEL2': ["\r\nselect  distinct top 5  AG.agnt_name from fact_prem_tran FP\r\ninner join DIM_AGENT AG on FP.agnt_id = AG.agnt_id\r\nwhere AG.AGNT_NAME <>' '", 'ALL', 'list', 'Sales Performacnce', 'Sales Performance'], 'LEVEL3': [None, 'Agent Portfolio', 'All', 'Claim Activity', 'Daily Sales', 'In force policy count', 'New business policy Amount', 'New business policy count', 'Renewal policy cout'], 'Line of Business': None, 'Loss ratio': None, 
#'Region':['Georgia','new york'],'Renewal Policy Count': ['renewal policy count'], 'User': 'C_LEVEL', '_permanent': True, 'combined': None, 'fileName': None, 'groupby': None, 'level': None, 'time_range': ['last'], 'timeperiod': 'MTD', 'vizType': None}
#authorization_role(payload)
#authorization(payload,session)