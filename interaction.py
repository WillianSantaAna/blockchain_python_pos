from node.transaction import Transaction
from node.wallet import Wallet
from node.blockchain_utils import BlockchainUtils
import requests


def post_transaction(sender, receiver, amount, type):
    transaction = sender.create_transaction(receiver.public_key_string(), amount, type)

    url = 'http://localhost:5000/transaction'
    package = {'transaction': BlockchainUtils.encode(transaction)}
    request = requests.post(url, json=package)
    print(request.text)


if __name__ == '__main__':

    genesis = Wallet()
    genesis.from_key("keys/genesis_private_key.pem")
    # alice = Wallet()
    # alice.from_key("keys/staker_private_key.pem")
    # exchange = Wallet()
    # exchange.from_key("keys/private_key.pem")

    # post_transaction(exchange, genesis, 994000000, 'EXCHANGE')
    # post_transaction(exchange, bob, 100, 'EXCHANGE')
    # # post_transaction(exchange, alice, 10, 'EXCHANGE')
    # # post_transaction(exchange, bob, 10, 'EXCHANGE')

    # post_transaction(w1, w1, 1, 'STAKE')
    # post_transaction(w2, w2, 1, 'STAKE')
    # post_transaction(genesis, genesis, 10000, 'STAKE')

    # post_transaction(genesis, w1, 10, 'TRANSFER')
    # post_transaction(genesis, w2, 10, 'TRANSFER')
    # post_transaction(genesis, w3, 10, 'TRANSFER')
