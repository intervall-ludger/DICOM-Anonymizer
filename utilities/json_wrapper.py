import json


def try_serialize(obj):
    if isinstance(obj, dict):
        return {key: try_serialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [try_serialize(element) for element in obj]
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)
