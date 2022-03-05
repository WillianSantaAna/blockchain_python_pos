from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from node.blockchain_utils import BlockchainUtils
from node.transaction import Transaction
from node.block import Block


class Wallet:

    def __init__(self):
        self.key_pair = RSA.generate(2048)

    def from_key(self, file):
        key = ''
        with open(file, 'r') as key_file:
            key = RSA.import_key(key_file.read())

        self.key_pair = key

    def export_key(self):
        with open('keys/private_key.pem', 'w') as file:
            file.write(self.key_pair.export_key('PEM').decode('utf-8'))
        with open('keys/public_key.pem', 'w') as file:
            file.write(self.key_pair.public_key().export_key('PEM').decode('utf-8'))

    # create signatures
    def sign(self, data):
        data_hash = BlockchainUtils.hash(data)
        signature_scheme_object = PKCS1_v1_5.new(self.key_pair)
        signature = signature_scheme_object.sign(data_hash)

        return signature.hex()

    @staticmethod  # For signing we need the privatekey, Validating we always need the public_key
    def signature_valid(data, signature, public_key_string):
        signature = bytes.fromhex(signature)
        data_hash = BlockchainUtils.hash(data)
        public_key = RSA.import_key(public_key_string)
        signature_scheme_object = PKCS1_v1_5.new(public_key)
        signature_valid = signature_scheme_object.verify(data_hash, signature)

        return signature_valid

    def public_key_string(self):
        public_key_string = self.key_pair.public_key().exportKey('PEM').decode('utf-8')

        return public_key_string

    def create_transaction(self, receiver, amount, type):
        transaction = Transaction(
            self.public_key_string(), receiver, amount, type)
        signature = self.sign(transaction.payload())
        transaction.sign(signature)

        return transaction

    def create_block(self, transactions, last_hash, block_count):
        block = Block(transactions, last_hash,
                      self.public_key_string(), block_count)
        signature = self.sign(block.payload())
        block.sign(signature)

        return block
