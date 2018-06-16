from twisted.internet.protocol import Protocol, ServerFactory, ReconnectingClientFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
from klein import Klein
from src.utils import json_response, cors_header
import random
import json
import binascii


PEERS_LIST = [
    "localhost:5001",
    "localhost:5002"
]


class Node:

    __LEAD = None
    app = Klein()
    Peers = []
    port = None

    def __init__(self):
        self.node_id = random.randint(1294967200, 4294967200)

    @staticmethod
    def instance():
        if Node.__LEAD is None:
            Node.__LEAD = Node()
        return Node.__LEAD

    def set_port(self, port):
        self.port = port

    def start(self, port=5001):
        self.port = port
        self.__init_server()
        self.__connect_to_peers(PEERS_LIST)

    def __init_server(self):
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(MyServerFactory())

    def __connect_to_peers(self, peers):
        for peer in peers:
            host, port = peer.split(":")
            reactor.connectTCP(host, int(port), MyFactory())

    @app.route('/')
    @json_response
    @cors_header
    def home(self, request):

        if len(self.Peers) > 0:
            msg = request.content.read().decode("utf-8")
            for peer in self.Peers:
                peer.send_message(msg)

        return {
            "result": True
        }


class MyProtocol(Protocol):

    def __init__(self):
        self.node = Node.instance()
        self.remote_node_id = random.randint(1294967200, 4294967200)

    def connectionMade(self):
        print("Connection from", self.transport.getPeer())
        self.node.Peers.append(self)

    def dataReceived(self, data):
        data = binascii.unhexlify(data).decode('utf-8')
        print("data received", data)

    def send_message(self, message):
        message = bytes(json.dumps({"node_id": self.node.node_id, "message": message}), 'utf-8')
        self.transport.write(binascii.hexlify(message))


class MyServerFactory(ServerFactory):
    protocol = MyProtocol


class MyFactory(ReconnectingClientFactory):
    protocol = MyProtocol

    maxRetries = 1

    def clientConnectionFailed(self, connector, reason):
        print("%s:%s" % (connector.host, connector.port))
