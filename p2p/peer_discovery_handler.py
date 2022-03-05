import threading
import time
import json
from node.message import Message
from node.blockchain_utils import BlockchainUtils
from p2p.socket_connector import SocketConnector
import socket


class PeerDiscoveryHandler:

    def __init__(self, node):
        self.socket_communication = node

    def start(self):
        status_thread = threading.Thread(target=self.status, args=())
        status_thread.start()

        discovery_thread = threading.Thread(target=self.discovery, args=())
        discovery_thread.start()

    def status(self):
        while True:
            print(
                f"Current connection ...")
            for peer in self.socket_communication.peers:
                print(str(peer.host) + ':' + str(peer.port))
            time.sleep(10)

    def discovery(self):
        while True:
            my_ip = self.socket_communication.socket_connector.host
            if my_ip != '127.0.0.1' and my_ip != 'localhost':
                handshake_message = self.handshake_message()
                self.socket_communication.broadcast(handshake_message)
            time.sleep(10)

    def handshake(self, connect_node):
        handshake_message = self.handshake_message()
        self.socket_communication.send(connect_node, handshake_message)

    def handshake_message(self):
        own_connector = self.socket_communication.socket_connector
        own_peers = self.socket_communication.peers
        data = own_peers
        message_type = 'DISCOVERY'
        message = Message(own_connector, message_type, data)
        encode_message = BlockchainUtils.encode(message)

        return encode_message

    def handle_message(self, sender_connector, message):
        time.sleep(1)
        peers_socket_connector = SocketConnector(
            sender_connector.host, message.sender_connector.port)
        peers_peer_list = message.data
        new_peer = True

        for peer in self.socket_communication.peers:
            if peer.equals(peers_socket_connector):
                new_peer = False

        if new_peer:
            self.socket_communication.peers.append(peers_socket_connector)

        with open('p2p/static_nodes.json', 'r') as file:
            static_nodes = json.load(file)

        static_nodes = [SocketConnector(
            socket.gethostbyname(node['host']), node['port']) for node in static_nodes['nodes']]
        nodes_outbound = [SocketConnector(
            node.host, node.port) for node in self.socket_communication.nodes_outbound]

        if not True in [node.equals(self.socket_communication.socket_connector) for node in static_nodes]:
            for static_node in static_nodes:
                if not True in [node.equals(static_node) for node in nodes_outbound]:
                    self.socket_communication.connect_with_node(
                        static_node.host, static_node.port)

            for peers_peer in peers_peer_list:
                peer_known = True in [node.equals(
                    peers_peer) for node in nodes_outbound + self.socket_communication.peers]

                if not peer_known and not peers_peer.equals(self.socket_communication.socket_connector):
                    print(
                        f"Try connection with host: {peers_peer.host} port: {peers_peer.port}")
                    self.socket_communication.connect_with_node(
                        peers_peer.host, peers_peer.port)
        else:
            if self.socket_communication.node.blockchain.blocks[-1].block_count <= 1:
                self.socket_communication.node.request_chain()
                self.socket_communication.node.request_pool()
