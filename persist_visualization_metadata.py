# -*- coding: utf-8 -*-
import xlrd
from collections import OrderedDict
import pymongo
import yaml
congfig_file = 'config.yml'
loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
vismetadataloc= loaded_parameters['persistmetadata_vis']['metadataloc']

def to_camel_case(snake_str):
    components = snake_str.split(' ')
    # We capitalize the first letter of each component except the first one , which is converted to lowercase
    # with the 'title' method and join them together.
    return (components[0]).lower() + ''.join(x.title() for x in components[1:])


# Open the workbook and select the first worksheet

wb = xlrd.open_workbook('vismetadataloc')



def generate_jsonList(sheetNo):
    entity_list=[]
    # Iterate through each row in worksheet and fetch values into dict
    for rownum in range(1, sheetNo.nrows):
        entityDict = OrderedDict()
        row_values = sheetNo.row_values(rownum)
        # Iterate through each column in worksheet
        for colNum  in range(0,sheetNo.ncols):
            attrValue=to_camel_case(sheetNo.col_values(colNum)[0])
            entityDict[attrValue] = row_values[colNum]

        entity_list.append(entityDict)
    return entity_list


#Insert into MongoDB
uri= loaded_parameters['persistmetadata_vis']['uri']


myclient = pymongo.MongoClient(uri)

mydb = myclient[loaded_parameters['persistmetadata_vis']['db']]



mydb.drop_collection("visualizationMetadata")


mydb.visualizationMetadata.insert_many(generate_jsonList(wb.sheet_by_name("Sheet1")))




