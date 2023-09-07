import requests
import json
import configuration_model
import dill as pickle

e0 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=0)
e1 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=180)
e2 = configuration_model.ConfigurationEntry(lat=48.399, lon=14.513, peakpower=1, angle=22, aspect=-180)
configuration = configuration_model.Configuration(configuration=[e0, e1, e2])

r = requests.post("http://localhost:9000/config/", data=configuration.model_dump_json(), stream=True)

print(r)
print(type(r.raw.data))
result_model = pickle.loads(r.raw.data)
print(result_model.get_generation(1693915384))
print(type(result_model))