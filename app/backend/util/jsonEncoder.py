from json import JSONEncoder
from datetime import date, datetime as dt
import numpy as np



class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
    
        if isinstance(obj, dt):
            return obj.strftime("%d-%m-%Y")
        
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")

        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, 
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()

        return JSONEncoder.default(self, obj)