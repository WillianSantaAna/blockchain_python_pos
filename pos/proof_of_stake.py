
from node.blockchain_utils import BlockchainUtils
from pos.lot import Lot
from math import ceil


class ProofOfStake:

    def __init__(self):
        self.stakers = {}
        self.set_genesis_node_stake()

    def set_genesis_node_stake(self):
        genesis_public_key = open('keys/genesis_public_key.pem', 'r').read()
        self.stakers[genesis_public_key] = 1

    def update(self, public_key_string, stake):
        if public_key_string in self.stakers.keys():
            self.stakers[public_key_string] += stake
        else:
            self.stakers[public_key_string] = stake

    def get(self, public_key_string):
        if public_key_string in self.stakers.keys():
            return self.stakers[public_key_string]
        else:
            return None

    def validator_lots(self, seed):
        lots = []

        max_stake = max(self.stakers.values())
        for validator in self.stakers.keys():
            for stake in range(ceil(self.get(validator) / (abs(max_stake) / 100))):
                lots.append(Lot(validator, stake + 1, seed))

        return lots

    def winner_lot(self, lots, seed):
        least_offset = None
        winner_lot = None
        reference_hash_int_value = int(
            BlockchainUtils.hash(seed).hexdigest(), 16)

        for lot in lots:
            lot_int_value = int(lot.lot_hash(), 16)
            offset = abs(lot_int_value - reference_hash_int_value)

            if least_offset is None or offset < least_offset:
                least_offset = offset
                winner_lot = lot

        return winner_lot

    def forger(self, last_block_hash):
        lots = self.validator_lots(last_block_hash)
        winner_lot = self.winner_lot(lots, last_block_hash)

        return winner_lot.public_key_string
