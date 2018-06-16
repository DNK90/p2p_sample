from src.p2p import Node
from twisted.internet import reactor


node = Node.instance().start(5002)
Node.instance().app.run(host="localhost", port=4999)
reactor.run()
