class SocketConnector:

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def equals(self, connector):
        return connector.host == self.host and connector.port == self.port