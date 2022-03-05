
class TransactionPool:

    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def transaction_exists(self, transaction):
        for pool_transaction in self.transactions:
            if pool_transaction.equals(transaction):
                return True

        return False

    def remove_from_pool(self, transactions):
        new_pool_transaction = map(lambda t : t not in transactions, self.transactions)
        new_pool_transaction = []

        for pool_transaction in self.transactions:
            insert = True
            for transaction in transactions:
                if pool_transaction.equals(transaction):
                    insert = False

            if insert:
                new_pool_transaction.append(pool_transaction)

        self.transactions = new_pool_transaction

    def forger_required(self):
        return len(self.transactions) >= 50
