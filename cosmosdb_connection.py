import pymongo
import yaml

def inex_connection(coll):
    congfig_file = 'config.yml'
    loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
    uri= loaded_parameters['cosmosdb_connection']['uri']
    client = pymongo.MongoClient(uri)
    db=client.iNex_db
    collObj=db[coll]
    return collObj
