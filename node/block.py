from copy import deepcopy
from time import time


class Block:

    def __init__(self, transactions, last_hash, forger, block_count):
        self.transactions = transactions
        self.last_hash = last_hash
        self.forger = forger
        self.block_count = block_count
        self.timestamp = time()
        self.signature = ''

    def to_json(self):
        json_representation = deepcopy(self.__dict__)
        json_representation['transactions'] = [transaction.to_json() for transaction in json_representation['transactions']]

        return json_representation

    def sign(self, signature):
        self.signature = signature

    def payload(self):
        json_representation = deepcopy(self.to_json())
        json_representation['signature'] = ''

        return json_representation

    @staticmethod
    def genesis():
        genesis_block = Block([], 'genesis_hash', 'genesis', 0)
        genesis_block.timestamp = 0

        return genesis_block
