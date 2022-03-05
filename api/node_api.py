from flask_classful import FlaskView, route
from flask import Flask, jsonify, request
from node.blockchain_utils import BlockchainUtils
from waitress import serve


node = None


class NodeAPI(FlaskView):

    def __init__(self):
        self.app = Flask(__name__)

    def start(self, api_port):
        NodeAPI.register(self.app, route_base='/')
        serve(self.app, host='127.0.0.1', port=api_port)

    def inject_node(self, inject_node):
        global node
        node = inject_node

    @route('/info', methods=['GET'])
    def info(self):
        return {'result': 'conn with flask'}, 200

    @route('/blockchain', methods=['GET'])
    def blockchain(self):
        return node.blockchain.to_json(), 200

    @route('/blocks', methods=['GET'])
    def blocks(self):
        blocks = {k: [{k: {"count": len(v), "reward": sum([t['gas_fee'] for t in v])} if k == "transactions" else v for (k, v) in block.items(
        )} for block in v] for (k, v) in node.blockchain.to_json().items()}

        return blocks, 200

    @route('/block/<block_count>/transactions', methods=['GET'])
    def block_transactions(self, block_count):
        blocks = [{k: v for (k, v) in block.items()}
                  for block in node.blockchain.to_json()['blocks']]
        try:
            transactions = {
                "transactions": blocks[int(block_count)]["transactions"]}
            return transactions, 200
        except (IndexError, TypeError):
            return {"msg": "Block not found"}, 404

    @route('/transaction_pool', methods=['GET'])
    def transaction_pool(self):
        transactions = {"transactions": [transaction.to_json(
        ) for transaction in node.transaction_pool.transactions]}

        return transactions, 200

    @route('/transaction', methods=['POST'])
    def transaction(self):
        values = request.get_json()

        if not 'transaction' in values:
            return 'missing transaction values', 400

        transaction = BlockchainUtils.decode(values['transaction'])
        node.handle_transaction(transaction)

        response = {'message': 'Received transaction'}

        return jsonify(response), 201

    @route('/balance', methods=['POST'])
    def balance(self):
        json = request.get_json()
        public_key = json['public_key']
        balance = node.blockchain.account_model.get_balance(public_key)

        return {'result': {'balance': balance}}, 200

    @route('/balances', methods=['GET'])
    def balances(self):
        balances = node.blockchain.account_model.balances

        return {'result': {'balances': balances}}, 200
