

# check if query is valid and set default values if needed
def validate(query):    
    for var in required:
        if var in query.model_dump().keys():
            val = query.var # TODO
            if val is None:
                return False
            elif var == 'lat' and (-90 > val or val > 90):
                return False
            elif var == 'lon' and (-180 > val or val > 180):
                return False
            elif var == 'peakpower' and (0 >= val or val > 100000000):
                return False
            elif var == 'angle' and (0 > val or val > 90):
                return False
            elif var == 'aspect' and (-180 > val or val > 180):
                return False                
        else:
            return False    
    for key, val in optional_default.items():
        if key in query.keys():
            if key is None:
                query[key] = val
            elif key == 'loss' and (0 > query[key] or query[key] > 100):
                return False
            elif key == 'outputformat' and not isinstance(query[key], str):
                return False
            elif key == 'mounting' and not isinstance(query[key], str):
                return False
            elif key == 'startyear' and (2005 > query[key] or query[key] > 2020):
                return False
            elif key == 'endyear' and ((2005 > query[key] or query[key] > 2020) or query[key] < query['startyear']):
                return False
            elif key == 'usehorizon' and (0 > query[key] or query[key] > 1):
                return False
            elif key == 'pvcalculation' and (0 > query[key] or query[key] > 1):
                return False
        else:
            query[key] = val
    return True
