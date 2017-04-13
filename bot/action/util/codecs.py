import json


class Codec:
    def __init__(self, decode_func=lambda x: x, encode_func=lambda x: x):
        self.decode = decode_func
        self.encode = encode_func


class Codecs:
    INT = Codec(int, str)
    STRING = Codec(str, str)
    LINE_LIST = Codec(lambda s: s.splitlines(), "\n".join)
    JSON = Codec(json.loads, json.dumps)
