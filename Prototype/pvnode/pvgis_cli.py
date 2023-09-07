import requests
import sys
from configuration_model import ConfigurationEntry, Configuration
import dill as pickle

# set filename from args
filename = sys.argv[1]

# fetch all pv configurations and split into list of str
conf_list = []
for i in range(2, len(sys.argv)):
    conf = str.split(sys.argv[i], ',')
    prop_dict = {}
    for j in conf:
        prop = str.split(j, '=')
        prop_dict[prop[0]] = float(prop[1])
    conf_list.append(prop_dict)

# initialize configuration entries 
configs = []
for i in conf_list:
    new_conf = ConfigurationEntry(lat=i["lat"], lon=i["lon"], peakpower=i["peakpower"], angle=i["angle"], aspect=i["aspect"])
    configs.append(new_conf)
    
# create Configuration List  
configuration = Configuration(configuration=configs)

r = requests.post("http://localhost:9000/config/", data=configuration.model_dump_json(), stream=True)

result_model = pickle.loads(r.raw.data)
print('Successfully created model.')

# save model with pickle
with open(filename, 'wb') as f:
    pickle.dump(result_model, f)