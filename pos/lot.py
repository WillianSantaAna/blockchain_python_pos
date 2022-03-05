from node.blockchain_utils import BlockchainUtils


class Lot:

    def __init__(self, public_key_string, iteration, last_block_hash):
        self.public_key_string = public_key_string
        self.iteration = iteration
        self.last_block_hash = last_block_hash

    def lot_hash(self):
        hash_data = self.public_key_string + self.last_block_hash

        for _ in range(self.iteration):
            hash_data = BlockchainUtils.hash(hash_data).hexdigest()

        return hash_data