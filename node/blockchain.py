from node.block import Block
from node.blockchain_utils import BlockchainUtils
from node.account_model import AccountModel
from pos.proof_of_stake import ProofOfStake


class Blockchain:

    def __init__(self):
        self.blocks = [Block.genesis()]
        self.account_model = AccountModel()
        self.pos = ProofOfStake()

    def add_block(self, block):
        self.execute_transactions(block.transactions, block.forger)
        self.blocks.append(block)

    def to_json(self):
        return {'blocks': [block.to_json() for block in self.__dict__['blocks']]}

    def block_count_valid(self, block):
        return self.blocks[-1].block_count == block.block_count - 1 and len(self.blocks) == block.block_count

    def last_block_hash_valid(self, block):
        last_blockchain_block_hash = BlockchainUtils.hash(
            self.blocks[-1].payload()).hexdigest()

        return last_blockchain_block_hash == block.last_hash

    def transaction_covered(self, transaction):
        if transaction.type == 'EXCHANGE':
            return True

        sender_balance = self.account_model.get_balance(
                transaction.sender_public_key)

        if transaction.type == 'UNSTAKE':
            sender_stake = self.pos.get(transaction.sender_public_key)

            return sender_stake >= transaction.amount and sender_balance >= transaction.gas_fee and transaction.amount > 0
        else:
            return sender_balance >= (transaction.amount + transaction.gas_fee) and transaction.amount > 0

    def get_covered_transaction_set(self, transactions):
        covered_transactions = []

        for transaction in transactions:
            if self.transaction_covered(transaction):
                covered_transactions.append(transaction)
            else:
                print('transaction is not covered by sender')

        return covered_transactions

    def execute_transactions(self, transactions, forge_public_key_string):
        for transaction in transactions:
            self.execute_transaction(transaction, forge_public_key_string)

    def execute_transaction(self, transaction, forge_public_key_string):
        sender = transaction.sender_public_key
        receiver = transaction.receiver_public_key
        amount = abs(transaction.amount)
        gas_fee = transaction.gas_fee

        if transaction.type == 'STAKE':
            if sender == receiver:
                self.pos.update(sender, amount)
                self.account_model.update_balance(sender, -amount)
        elif transaction.type == 'UNSTAKE':
            if sender == receiver:
                self.pos.update(sender, -amount)
                self.account_model.update_balance(sender, amount)
        else:
            self.account_model.update_balance(sender, -amount)
            self.account_model.update_balance(receiver, amount)

        self.account_model.update_balance(sender, -gas_fee)
        self.account_model.update_balance(forge_public_key_string, gas_fee)

    def next_forger(self):
        last_block_hash = BlockchainUtils.hash(
            self.blocks[-1].payload()).hexdigest()
        next_forger = self.pos.forger(last_block_hash)

        return next_forger

    def create_block(self, transaction_from_pool, forger_wallet):
        covered_transactions = self.get_covered_transaction_set(
            transaction_from_pool)
        self.execute_transactions(covered_transactions, forger_wallet.public_key_string())

        new_block = forger_wallet.create_block(covered_transactions, BlockchainUtils.hash(
            self.blocks[-1].payload()).hexdigest(), len(self.blocks))

        self.blocks.append(new_block)

        return new_block

    def transaction_exists(self, transaction):
        for block in self.blocks:
            for block_transaction in block.transactions:
                if transaction.equals(block_transaction):
                    return True

        return False

    def forger_valid(self, block):
        forger_public_key = self.pos.forger(block.last_hash)
        proposed_block_forger = block.forger

        return forger_public_key == proposed_block_forger

    def transactions_valid(self, transactions):
        covered_transactions = self.get_covered_transaction_set(transactions)

        return len(covered_transactions) == len(transactions)
