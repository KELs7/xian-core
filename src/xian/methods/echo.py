from cometbft.abci.v1beta1.types_pb2 import ResponseEcho


def echo(self, req) -> ResponseEcho:
    r = ResponseEcho()
    return r
