# -*- coding: utf-8 -*-
import xlrd
from collections import OrderedDict
import pymongo


def to_camel_case(snake_str):
    components = snake_str.split(' ')
    """We capitalize the first letter of each component except the first one , which is converted to lowercase
    with the 'title' method and join them together"""
    return (components[0]).lower() + ''.join(x.title() for x in components[1:])


# Open the workbook and select the first worksheet
wb = xlrd.open_workbook('resources/IC AISmart MetadataModel_v7.xlsx')



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
uri = "mongodb://inexbotcosmosdb:imiDU1weWpyt61akkwhmtzCVhNQcbO47KjU4MkDmRuZhFZQs7QbAva0g1fxNcyR5pMBX8pOIMf4htjdUNapJdA==@inexbotcosmosdb.documents.azure.com:10255/?ssl=true&replicaSet=globaldb"

myclient = pymongo.MongoClient(uri)
mydb = myclient["iNex_db"]

mydb.drop_collection("entityMaster_d")
mydb.drop_collection("attributeMaster_d")
mydb.drop_collection("attributeEntity_d")
mydb.drop_collection("join_d")


mydb.entityMaster_d.insert_many(generate_jsonList(wb.sheet_by_name("EntityMaster_d")))
mydb.attributeMaster_d.insert_many(generate_jsonList(wb.sheet_by_name("AttributeMaster_d")))
mydb.attributeEntity_d.insert_many(generate_jsonList(wb.sheet_by_name("AttributeEntity_d")))
mydb.join_d.insert_many(generate_jsonList(wb.sheet_by_name("Join_d")))



