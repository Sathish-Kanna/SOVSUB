from hashlib import sha256

import json
import time


class Block:
    def __init__(self, height, transactions, cumulated, timestamp, previous_hash, nonce=0, hash=None):
        self.height = height
        self.transactions = transactions
        self.cumulated = cumulated
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()


class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 5

    def __init__(self, chain=[]):
        self.unconfirmed_transactions = []
        self.chain = chain

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has height 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(height=0, transactions=[], cumulated={"nota": 0}, timestamp=0,
                              previous_hash=sha256("0".encode()).hexdigest(), nonce=117240)

        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = sha256("0".encode()).hexdigest()
        for block in chain:
            if not isinstance(block, Block):
                block = Block(**block)
            block_hash = block.hash
            # assign None to the hash field to recompute the hash again
            # using `compute_hash` method.
            block.hash = None

            if not cls.is_valid_proof(block, block_hash) or previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        cmlt = eval(str(last_block.cumulated))
        for transaction in self.unconfirmed_transactions:
            vot = eval(transaction).get("voted")
            if vot in cmlt:
                cmlt[vot] += 1
            else:
                cmlt[vot] = 1

        new_block = Block(height=last_block.height + 1,
                          transactions=self.unconfirmed_transactions,
                          cumulated=cmlt,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []
        return True
