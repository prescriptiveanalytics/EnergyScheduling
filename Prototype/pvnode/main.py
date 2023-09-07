from fastapi import FastAPI, Response
import pvgis_connector
import configuration_model
import generator_model
import dill as pickle

app = FastAPI()

@app.get("/")
def read_root():
    return { "Name": "pv api" }

@app.post("/config/")
def create_config(config: configuration_model.Configuration):
    model_dict = pvgis_connector.create_model(config)
    # create model of dict
    print('create model...')
    model = generator_model.PVGisGenerator('anlage1', model_dict)
    # serialize and return model as binary
    print('return model...')
    tmp = pickle.dumps(model)
    return Response(content=tmp)