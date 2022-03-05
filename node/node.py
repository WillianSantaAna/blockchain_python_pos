from copy import deepcopy
from node.blockchain_utils import BlockchainUtils
from node.transaction_pool import TransactionPool
from node.wallet import Wallet
from node.blockchain import Blockchain
from p2p.socket_communication import SocketCommunication
from api.node_api import NodeAPI
from node.message import Message
import json
import jsonpickle
import time


class Node:

    def __init__(self, host, port):
        self.p2p = None
        self.host = host
        self.port = int(port)
        self.transaction_pool = TransactionPool()
        self.wallet = Wallet()
        self.blockchain = Blockchain()
        # with open("database/genesis.json", "r") as db:
        #     self.handle_blockchain(jsonpickle.loads(json.load(db)))
        with open("node.json", "r") as file:
            conf = json.load(file)
            self.conf = conf["config"]
            if self.conf["private_key_path"] is not None:
                self.wallet.from_key(self.conf["private_key_path"])
            else:
                self.wallet.export_key()

    def start_p2p(self):
        self.p2p = SocketCommunication(self.host, self.port)
        self.p2p.start_socket_communication(self)
        self.start_api()

    def start_api(self):
        self.api = NodeAPI()
        self.api.inject_node(self)
        self.api.start(self.conf["flask_port"])

    def handle_transaction(self, transaction):
        time.sleep(1)
        data = transaction.payload()
        signature = transaction.signature
        signer_public_key = transaction.sender_public_key
        amount_valid = transaction.amount > 0
        signature_valid = Wallet.signature_valid(
            data, signature, signer_public_key)
        transaction_existis = self.transaction_pool.transaction_exists(
            transaction)
        transaction_in_blockchain = self.blockchain.transaction_exists(
            transaction)

        if not transaction_existis and not transaction_in_blockchain and signature_valid and amount_valid:
            self.transaction_pool.add_transaction(transaction)
            message = Message(self.p2p.socket_connector,
                              'TRANSACTION', transaction)
            encode_message = BlockchainUtils.encode(message)

            self.p2p.broadcast(encode_message)

            forger_required = self.transaction_pool.forger_required()

            if forger_required:
                self.forge()

    def handle_block(self, block):
        time.sleep(1)
        forger = block.forger
        block_hash = block.payload()
        signature = block.signature

        block_count_valid = self.blockchain.block_count_valid(block)
        last_block_hash_valid = self.blockchain.last_block_hash_valid(block)
        forger_valid = self.blockchain.forger_valid(block)
        transactions_valid = self.blockchain.transactions_valid(
            block.transactions)
        signature_valid = Wallet.signature_valid(block_hash, signature, forger)

        if not block_count_valid:
            self.request_chain()

        if last_block_hash_valid and forger_valid and transactions_valid and signature_valid and block_count_valid:
            self.blockchain.add_block(block)
            self.transaction_pool.remove_from_pool(block.transactions)
            message = Message(self.p2p.socket_connector, 'BLOCK', block)
            encode_message = BlockchainUtils.encode(message)
            self.p2p.broadcast(encode_message)

            with open('database/blockchain.json', 'w') as file:
                json.dump(BlockchainUtils.encode(self.blockchain), file)

    def request_pool(self):
        message = Message(self.p2p.socket_connector, 'TRANSACTIONPOOLREQUEST', None)
        encode_message = BlockchainUtils.encode(message)
        self.p2p.broadcast(encode_message)

    def request_my_public_ip(self, connected_node):
        message = Message(self.p2p.socket_connector, 'PUBLIC_IP_REQUEST', None)
        encode_message = BlockchainUtils.encode(message)
        self.p2p.send(connected_node, encode_message)

    def handle_public_ip_request(self, requesting_node):
        message = Message(self.p2p.socket_connector, 'PUBLIC_IP', requesting_node.host)
        encode_message = BlockchainUtils.encode(message)
        self.p2p.send(requesting_node, encode_message)

    def handle_my_public_ip(self, connected_node, my_public_ip):
        print("handling my public ip ...")
        self.p2p.socket_connector.host = my_public_ip
        self.p2p.peer_discovery_handler.handshake(connected_node)

    def request_chain(self):
        message = Message(self.p2p.socket_connector, 'BLOCKCHAINREQUEST', None)
        encode_message = BlockchainUtils.encode(message)
        self.p2p.broadcast(encode_message)

    def handle_transaction_pool_request(self, requesting_node):
        message = Message(self.p2p.socket_connector, 'TRANSACTIONPOOL', self.transaction_pool)
        encode_message = BlockchainUtils.encode(message)
        self.p2p.send(requesting_node, encode_message)

    def handle_blockchain_request(self, requesting_node):
        message = Message(self.p2p.socket_connector,
                          'BLOCKCHAIN', self.blockchain)
        encode_message = BlockchainUtils.encode(message)
        self.p2p.send(requesting_node, encode_message)

    def handle_transaction_pool(self, transanction_pool):
        for transanction in transanction_pool.transactions:
            self.handle_transaction(transanction)

    def handle_blockchain(self, blockchain):
        local_blockchain_copy = deepcopy(self.blockchain)
        local_block_count = len(local_blockchain_copy.blocks)
        receiver_chain_block_count = len(blockchain.blocks)

        if local_block_count < receiver_chain_block_count:
            for n, block in enumerate(blockchain.blocks):
                if n >= local_block_count:
                    local_blockchain_copy.add_block(block)
                    self.transaction_pool.remove_from_pool(block.transactions)

            self.blockchain = local_blockchain_copy

    def forge(self):
        forger = self.blockchain.next_forger()

        if forger == self.wallet.public_key_string():
            print('i am the next forger')
            block = self.blockchain.create_block(
                self.transaction_pool.transactions, self.wallet)
            self.transaction_pool.remove_from_pool(block.transactions)
            message = Message(self.p2p.socket_connector, 'BLOCK', block)
            encode_message = BlockchainUtils.encode(message)
            self.p2p.broadcast(encode_message)
        else:
            print('i am NOT the next forger')
