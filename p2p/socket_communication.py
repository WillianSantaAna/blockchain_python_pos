from p2pnetwork.node import Node
from p2p.peer_discovery_handler import PeerDiscoveryHandler
from p2p.socket_connector import SocketConnector
from node.blockchain_utils import BlockchainUtils
import json
import socket


class SocketCommunication(Node):

    def __init__(self, host, port):
        super(SocketCommunication, self).__init__(host, port, None)
        self.peers = []
        self.peer_discovery_handler = PeerDiscoveryHandler(self)
        self.socket_connector = SocketConnector(host, port)

    def connect_to_first_node(self):
        with open('p2p/static_nodes.json', 'r') as file:
            static_nodes = json.load(file)

        static_nodes = [SocketConnector(
            socket.gethostbyname(node['host']), node['port']) for node in static_nodes['nodes']]

        if not True in [node.equals(self.socket_connector) for node in static_nodes]:
            for static_node in static_nodes:
                print(f"Try connection with host: {static_node.host} port: {static_node.port}")
                self.connect_with_node(static_node.host, static_node.port)

    def start_socket_communication(self, node):
        self.node = node
        self.start()
        self.peer_discovery_handler.start()
        self.connect_to_first_node()

    def inbound_node_connected(self, connected_node):
        self.peer_discovery_handler.handshake(connected_node)

    def outbound_node_connected(self, connected_node):
        my_ip = self.socket_connector.host
        if my_ip == '127.0.0.1' or my_ip == 'localhost':
            self.node.request_my_public_ip(connected_node)
        else:
            self.peer_discovery_handler.handshake(connected_node)

    def node_message(self, connected_node, message):
        message = BlockchainUtils.decode(json.dumps(message))

        if message.message_type == 'PUBLIC_IP_REQUEST':
            self.node.handle_public_ip_request(connected_node)
        elif message.message_type == 'PUBLIC_IP':
            my_public_ip = message.data
            self.node.handle_my_public_ip(connected_node, my_public_ip)
        elif message.message_type == 'DISCOVERY':
            self.peer_discovery_handler.handle_message(connected_node, message)
        elif message.message_type == 'TRANSACTION':
            transaction = message.data
            self.node.handle_transaction(transaction)
        elif message.message_type == 'BLOCK':
            block = message.data
            self.node.handle_block(block)
        elif message.message_type == 'TRANSACTIONPOOLREQUEST':
            self.node.handle_transaction_pool_request(connected_node)
        elif message.message_type == 'TRANSACTIONPOOL':
            transanction_pool = message.data
            self.node.handle_transaction_pool(transanction_pool)
        elif message.message_type == 'BLOCKCHAINREQUEST':
            self.node.handle_blockchain_request(connected_node)
        elif message.message_type == 'BLOCKCHAIN':
            blockchain = message.data
            self.node.handle_blockchain(blockchain)

    def send(self, receiver, message):
        self.send_to_node(receiver, message)

    def broadcast(self, message):
        self.send_to_nodes(message)
