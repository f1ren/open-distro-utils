import json


def debug(msg, **kwargs):
    print(json.dumps({
        'msg': msg,
        'kwargs': kwargs
    }))
