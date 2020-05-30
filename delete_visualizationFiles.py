import time
import os
import yaml
congfig_file = 'config.yml'
loaded_parameters = yaml.safe_load(open(congfig_file,'rb'))
files_loc= loaded_parameters['delete_vis_files']['list_of_files']
print(str(time.time()-10000))



list_of_files = os.listdir(files_loc)
print(list_of_files)
for each_file in list_of_files:
    if each_file.startswith('visualization'):  #since its all type str you can simply use startswith
        fileTime=each_file.replace("visualization","").replace(".csv","")
        print(float(fileTime))
        print(fileTime)
        if float(fileTime)<time.time()-10000:
            os.remove(files_loc+'visualization'+fileTime+'.csv')
