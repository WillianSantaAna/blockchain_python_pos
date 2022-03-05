# generate random ids
from uuid import uuid1
from time import time
from copy import deepcopy


class Transaction:

    def __init__(self, sender_public_key, receiver_public_key, amount, type):
        self.sender_public_key = sender_public_key
        self.receiver_public_key = receiver_public_key
        self.amount = amount
        self.gas_fee = amount * 0.006
        self.type = type
        self.id = uuid1().hex  # to hexadecimal
        self.timestamp = time()
        # only the private key will be able to create transactions
        self.signature = ''

    def to_json(self):
        return self.__dict__

    def sign(self, signature):
        self.signature = signature

    def payload(self):
        json_representation = deepcopy(self.to_json())
        json_representation['signature'] = ''

        return json_representation

    def equals(self, transaction):
        return self.id == transaction.id
